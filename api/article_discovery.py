"""
Article Discovery Module
========================

Finds semantically similar articles using embeddings and cosine similarity.
"""

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
from urllib.parse import urljoin, urlparse
import time


class ArticleDiscovery:
    """Discovers related articles using semantic similarity"""

    def __init__(self):
        """Initialize with sentence transformer model"""
        print("📚 Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
        print("✅ Model loaded")

    def find_related_articles(
        self,
        base_url: str,
        base_text: str,
        max_articles: int = 3,
        similarity_threshold: float = 0.25
    ) -> List[Dict[str, str]]:
        """
        Find related articles to the base article.

        Args:
            base_url: URL of the original article
            base_text: Text content of the original article
            max_articles: Maximum number of related articles to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with 'url', 'title', 'similarity' keys
        """

        print(f"🔍 Finding related articles for: {base_url}")

        # Step 1: Get candidate articles from ET (increased limit for better diversity)
        candidates = self._get_candidate_articles(base_url, limit=30)
        print(f"  Found {len(candidates)} candidate articles")

        if not candidates:
            print("  ⚠️  No candidates found - using fallback articles")
            return self._get_fallback_articles(max_articles)

        # Step 2: Compute embeddings
        base_embedding = self.model.encode([base_text[:1000]])[0]  # First 1000 chars

        candidate_texts = [c['text'][:1000] for c in candidates]
        candidate_embeddings = self.model.encode(candidate_texts)

        # Step 3: Compute similarities
        similarities = cosine_similarity(
            [base_embedding],
            candidate_embeddings
        )[0]

        # Step 4: Rank and filter
        related = []
        for idx, sim in enumerate(similarities):
            # Skip if it's the same article or very low similarity
            candidate_url = candidates[idx]['url']
            if base_url in candidate_url or candidate_url in base_url:
                continue  # Don't return the same article

            if sim >= similarity_threshold:
                related.append({
                    'url': candidate_url,
                    'title': candidates[idx]['title'],
                    'similarity': float(sim),
                    'text_preview': candidates[idx]['text'][:200]
                })

        # Sort by similarity (descending)
        related.sort(key=lambda x: x['similarity'], reverse=True)

        print(f"  ✅ Found {len(related[:max_articles])} related articles")

        # FALLBACK: If no related articles found, return popular ET articles from sections
        if len(related) == 0:
            print(f"  ⚠️  No similar articles found - returning popular articles from ET sections")
            return self._get_fallback_articles(max_articles)

        return related[:max_articles]

    def _get_candidate_articles(self, base_url: str, limit: int = 20) -> List[Dict]:
        """Get candidate articles from Economic Times"""

        candidates = []

        try:
            # Parse base URL to get domain and section
            parsed = urlparse(base_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"

            # Extract section from base URL path
            path_parts = parsed.path.split('/')
            base_section = None

            # Detect section from URL (e.g., /tech/technology, /markets/stocks, etc.)
            if len(path_parts) >= 3:
                # URL format: /section/subsection/article-title/articleshow/ID
                potential_section = f"/{path_parts[1]}/{path_parts[2]}" if path_parts[2] else f"/{path_parts[1]}"
                base_section = potential_section

            # Strategy 1: Prioritize section from base URL, then related sections
            section_urls = []

            if base_section:
                # Add the same section first (highest relevance)
                section_urls.append(f"{base_domain}{base_section}")

            # Add complementary sections based on detected section
            if 'tech' in base_url or 'startup' in base_url:
                section_urls.extend([
                    f"{base_domain}/tech/technology",
                    f"{base_domain}/tech/startups",
                    f"{base_domain}/tech/artificial-intelligence"
                ])
            elif 'market' in base_url or 'stock' in base_url or 'company' in base_url:
                section_urls.extend([
                    f"{base_domain}/markets/stocks",
                    f"{base_domain}/news/company/corporate-trends",
                    f"{base_domain}/markets/stocks/earnings"
                ])
            else:
                # Default fallback
                section_urls.extend([
                    f"{base_domain}/tech/technology",
                    f"{base_domain}/tech/startups",
                    f"{base_domain}/markets/stocks",
                ])

            for section_url in section_urls:
                try:
                    response = requests.get(section_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0'
                    })
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find article links
                    links = soup.find_all('a', href=True)

                    for link in links:
                        href = link.get('href', '')

                        # Filter for article URLs
                        if 'articleshow' in href and base_url not in href:
                            # Make absolute URL
                            if href.startswith('/'):
                                full_url = urljoin(base_domain, href)
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue

                            # Get title
                            title = link.get_text(strip=True)

                            if title and len(title) > 10:
                                candidates.append({
                                    'url': full_url,
                                    'title': title,
                                    'text': ''  # Will fetch if needed
                                })

                        if len(candidates) >= limit:
                            break

                    if len(candidates) >= limit:
                        break

                except Exception as e:
                    print(f"    Error fetching {section_url}: {e}")
                    continue

                time.sleep(0.5)  # Be polite

            # Step 2: Fetch text for top candidates (increased for diversity)
            print(f"  Fetching text for {min(len(candidates), 20)} candidates...")
            for idx, candidate in enumerate(candidates[:20]):
                try:
                    response = requests.get(candidate['url'], timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0'
                    })
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract article text (ET-specific selectors)
                    article_body = soup.find('article') or soup.find('div', {'class': 'artText'})
                    if article_body:
                        text = article_body.get_text(separator=' ', strip=True)
                        candidate['text'] = text[:2000]  # First 2000 chars

                    time.sleep(0.3)  # Be polite

                except Exception as e:
                    print(f"    Error fetching article text: {e}")
                    continue

        except Exception as e:
            print(f"  ⚠️  Error getting candidates: {e}")

        return [c for c in candidates if c.get('text')]

    def _extract_article_text(self, url: str) -> str:
        """Extract text from article URL"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            soup = BeautifulSoup(response.text, 'html.parser')

            article_body = soup.find('article') or soup.find('div', {'class': 'artText'})
            if article_body:
                return article_body.get_text(separator=' ', strip=True)
        except:
            pass

        return ""

    def _get_fallback_articles(self, max_articles: int = 5) -> List[Dict[str, str]]:
        """Get popular articles from ET sections as fallback"""
        fallback_articles = []

        # Popular ET sections to pull from
        sections = [
            'https://economictimes.indiatimes.com/tech/technology',
            'https://economictimes.indiatimes.com/tech/startups',
            'https://economictimes.indiatimes.com/markets/stocks'
        ]

        try:
            for section_url in sections:
                if len(fallback_articles) >= max_articles:
                    break

                response = requests.get(section_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find article links
                links = soup.find_all('a', href=True)

                for link in links:
                    if len(fallback_articles) >= max_articles:
                        break

                    href = link.get('href', '')

                    if 'articleshow' in href:
                        # Make absolute URL
                        if href.startswith('/'):
                            full_url = 'https://economictimes.indiatimes.com' + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue

                        # Get title
                        title = link.get_text(strip=True)

                        if title and len(title) > 20:
                            # Check if already added
                            if not any(a['url'] == full_url for a in fallback_articles):
                                fallback_articles.append({
                                    'url': full_url,
                                    'title': title,
                                    'similarity': 0.20,  # Low similarity score to indicate it's a fallback
                                    'text_preview': f'Popular article from {section_url.split("/")[-1]} section'
                                })

                time.sleep(0.3)  # Be polite

        except Exception as e:
            print(f"  ⚠️  Error getting fallback articles: {e}")

        return fallback_articles[:max_articles]


# Global instance
_discovery_instance = None

def get_discovery_service() -> ArticleDiscovery:
    """Get or create article discovery service"""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = ArticleDiscovery()
    return _discovery_instance
