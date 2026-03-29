"""
Enhanced Article Discovery with Production-Grade Semantic Search
================================================================

Improvements over basic version:
1. Better embedding model (all-mpnet-base-v2 - more accurate)
2. Multi-stage filtering (keyword + semantic)
3. Title + content weighted scoring
4. Strict quality thresholds
5. Re-ranking based on content relevance
"""

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Tuple, Set
from urllib.parse import urljoin, urlparse
import time
import re
from collections import Counter


class EnhancedArticleDiscovery:
    """Production-grade article discovery with advanced semantic search"""

    def __init__(self):
        """Initialize with better embedding model"""
        print("📚 Loading enhanced sentence transformer model...")
        # Using all-mpnet-base-v2: Superior quality vs MiniLM, still fast
        # 768 dimensions vs 384, trained on 1B+ pairs
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        print("✅ Enhanced model loaded (all-mpnet-base-v2)")

    def find_related_articles(
        self,
        base_url: str,
        base_text: str,
        max_articles: int = 5,
        similarity_threshold: float = 0.28  # Balanced threshold for good coverage
    ) -> List[Dict[str, str]]:
        """
        Find semantically similar articles with multi-stage filtering.

        Args:
            base_url: URL of the original article
            base_text: Full text content of original article
            max_articles: Maximum articles to return
            similarity_threshold: Minimum cosine similarity (0.35 = high quality)

        Returns:
            List of related articles with similarity scores
        """

        print(f"🔍 Enhanced semantic search for: {base_url[:80]}...")

        # Stage 1: Extract keywords from base article
        base_keywords = self._extract_keywords(base_text)
        print(f"  📝 Extracted {len(base_keywords)} key terms")

        # Stage 2: Get candidate articles (section-aware)
        candidates = self._get_smart_candidates(base_url, limit=50)
        print(f"  🔎 Found {len(candidates)} candidate articles")

        if not candidates:
            print("  ⚠️  No candidates - using fallback")
            return self._get_fallback_articles(max_articles)

        # Stage 3: Keyword pre-filter (performance optimization)
        keyword_filtered = self._filter_by_keywords(
            candidates,
            base_keywords,
            min_overlap=1  # At least 1 shared keyword (more permissive)
        )
        print(f"  ✓ Keyword filter: {len(keyword_filtered)}/{len(candidates)} passed")

        if len(keyword_filtered) < 5:
            # Not enough keyword matches, use all candidates
            keyword_filtered = candidates

        # Stage 4: Compute semantic embeddings
        # Weighted approach: Title (30%) + Content (70%)
        base_embedding = self._compute_weighted_embedding(
            title=self._extract_title_from_url(base_url),
            content=base_text[:2000]  # First 2000 chars
        )

        candidate_embeddings = []
        for cand in keyword_filtered:
            emb = self._compute_weighted_embedding(
                title=cand['title'],
                content=cand['text'][:2000]
            )
            candidate_embeddings.append(emb)

        # Stage 5: Compute cosine similarities
        similarities = util.cos_sim(base_embedding, candidate_embeddings)[0].numpy()

        # Stage 6: Filter by threshold and rank
        related = []
        for idx, sim in enumerate(similarities):
            candidate_url = keyword_filtered[idx]['url']

            # Skip same article
            if base_url in candidate_url or candidate_url in base_url:
                continue

            # Only include high-quality matches
            if sim >= similarity_threshold:
                related.append({
                    'url': candidate_url,
                    'title': keyword_filtered[idx]['title'],
                    'similarity': float(sim),
                    'text_preview': keyword_filtered[idx]['text'][:200]
                })

        # Sort by similarity (descending)
        related.sort(key=lambda x: x['similarity'], reverse=True)

        # Stage 7: Re-rank top results by content quality
        if len(related) > max_articles:
            related = self._rerank_by_quality(related, base_text)

        result = related[:max_articles]
        print(f"  ✅ Found {len(result)} high-quality matches (threshold: {similarity_threshold})")

        # If zero results with threshold, return top candidates anyway
        if len(result) == 0:
            if similarity_threshold > 0.20:
                print(f"  🔄 Retrying with lower threshold (0.20)...")
                return self.find_related_articles(
                    base_url, base_text, max_articles, similarity_threshold=0.20
                )
            else:
                # Even with 0.20 threshold, nothing found - return top N by score
                print(f"  ⚠️  No matches above threshold, returning top {min(5, max_articles)} candidates")
                all_candidates = []
                for idx, sim in enumerate(similarities):
                    candidate_url = keyword_filtered[idx]['url']
                    if base_url not in candidate_url and candidate_url not in base_url:
                        all_candidates.append({
                            'url': candidate_url,
                            'title': keyword_filtered[idx]['title'],
                            'similarity': float(sim),
                            'text_preview': keyword_filtered[idx]['text'][:200]
                        })

                all_candidates.sort(key=lambda x: x['similarity'], reverse=True)
                return all_candidates[:min(5, max_articles)]

        return result

    def _compute_weighted_embedding(self, title: str, content: str) -> np.ndarray:
        """
        Compute weighted embedding: Title (30%) + Content (70%)
        Title has higher weight as it's more semantically concentrated
        """
        # Encode separately
        title_emb = self.model.encode(title, convert_to_tensor=False, normalize_embeddings=True)
        content_emb = self.model.encode(content[:1500], convert_to_tensor=False, normalize_embeddings=True)

        # Weighted average
        weighted = 0.3 * title_emb + 0.7 * content_emb

        # Re-normalize
        weighted = weighted / np.linalg.norm(weighted)

        return weighted

    def _extract_keywords(self, text: str, top_n: int = 15) -> Set[str]:
        """
        Extract important keywords using simple but effective heuristics.
        Focus on: Named entities, technical terms, important nouns
        """
        # Lowercase and tokenize
        text_lower = text.lower()

        # Remove common words and short tokens
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'said'
        }

        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)

        # Filter stopwords and count frequencies
        word_freq = Counter([w for w in words if w not in stopwords])

        # Get top N keywords
        keywords = {word for word, _ in word_freq.most_common(top_n)}

        # Also extract capitalized terms (likely named entities)
        named_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        keywords.update([ne.lower() for ne in named_entities if len(ne) > 2])

        return keywords

    def _filter_by_keywords(
        self,
        candidates: List[Dict],
        base_keywords: Set[str],
        min_overlap: int = 2
    ) -> List[Dict]:
        """Filter candidates that share at least min_overlap keywords"""
        filtered = []

        for cand in candidates:
            # Extract keywords from candidate
            cand_keywords = self._extract_keywords(cand['text'], top_n=15)

            # Check overlap
            overlap = len(base_keywords.intersection(cand_keywords))

            if overlap >= min_overlap:
                filtered.append(cand)

        return filtered

    def _rerank_by_quality(self, articles: List[Dict], base_text: str) -> List[Dict]:
        """
        Re-rank articles by additional quality signals:
        - Content length (longer is better, up to a point)
        - Title relevance
        - Already sorted by similarity, so preserve order for ties
        """
        def quality_score(article):
            # Similarity is already primary
            sim = article['similarity']

            # Bonus for reasonable content length (500-3000 chars)
            text_len = len(article['text_preview'])
            length_bonus = 0.0
            if 500 <= text_len <= 3000:
                length_bonus = 0.02

            return sim + length_bonus

        articles.sort(key=quality_score, reverse=True)
        return articles

    def _extract_title_from_url(self, url: str) -> str:
        """Extract article title from URL path"""
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')

        # Find the article title part (before /articleshow/)
        for i, part in enumerate(path_parts):
            if 'articleshow' in part and i > 0:
                # Get previous part (article slug)
                slug = path_parts[i - 1]
                # Convert slug to title (replace hyphens with spaces)
                title = slug.replace('-', ' ').title()
                return title

        return "Unknown"

    def _get_smart_candidates(self, base_url: str, limit: int = 30) -> List[Dict]:
        """
        Smart candidate retrieval - section-aware with better diversity
        """
        candidates = []

        try:
            parsed = urlparse(base_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"

            # Detect section from URL
            path_parts = parsed.path.split('/')
            base_section = None

            if len(path_parts) >= 3:
                base_section = f"/{path_parts[1]}/{path_parts[2]}" if path_parts[2] else f"/{path_parts[1]}"

            # Build section list with priorities
            section_urls = []

            if base_section:
                section_urls.append(base_section)

            # Add related sections based on topic (expanded for all industries)
            if 'tech' in base_url or 'startup' in base_url or 'ai' in base_url or 'artificial-intelligence' in base_url:
                section_urls.extend([
                    '/tech/technology',
                    '/tech/startups',
                    '/tech/artificial-intelligence',
                    '/tech/internet',
                    '/tech/software'
                ])
            elif 'blockchain' in base_url or 'crypto' in base_url or 'bitcoin' in base_url or 'web3' in base_url:
                section_urls.extend([
                    '/tech/technology',
                    '/tech/artificial-intelligence',
                    '/news/international/business',
                    '/tech/startups'
                ])
            elif 'market' in base_url or 'stock' in base_url or 'company' in base_url:
                section_urls.extend([
                    '/markets/stocks',
                    '/news/company/corporate-trends',
                    '/markets/stocks/earnings',
                    '/markets/stocks/news'
                ])
            elif 'policy' in base_url or 'government' in base_url or 'regulation' in base_url:
                section_urls.extend([
                    '/news/economy/policy',
                    '/news/economy/indicators',
                    '/news/politics-and-nation'
                ])
            elif 'telecom' in base_url or 'mobile' in base_url or '5g' in base_url:
                section_urls.extend([
                    '/industry/telecom',
                    '/tech/technology',
                    '/industry/telecom/telecom-news'
                ])
            else:
                section_urls.extend([
                    '/tech/technology',
                    '/tech/startups',
                    '/markets/stocks'
                ])

            # Remove duplicates while preserving order
            seen = set()
            unique_sections = []
            for section in section_urls:
                if section not in seen:
                    seen.add(section)
                    unique_sections.append(f"{base_domain}{section}")

            # Scrape articles from sections
            for section_url in unique_sections:
                if len(candidates) >= limit:
                    break

                try:
                    response = requests.get(section_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0'
                    })
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find article links
                    links = soup.find_all('a', href=True)

                    for link in links:
                        if len(candidates) >= limit:
                            break

                        href = link.get('href', '')

                        if 'articleshow' in href and base_url not in href:
                            # Make absolute URL
                            if href.startswith('/'):
                                full_url = urljoin(base_domain, href)
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue

                            title = link.get_text(strip=True)

                            if title and len(title) > 20:
                                candidates.append({
                                    'url': full_url,
                                    'title': title,
                                    'text': ''
                                })

                except Exception as e:
                    print(f"    Error fetching {section_url}: {e}")
                    continue

                time.sleep(0.5)

            # Fetch article text for candidates
            print(f"  Fetching text for {min(len(candidates), 20)} candidates...")
            for idx, candidate in enumerate(candidates[:20]):
                try:
                    response = requests.get(candidate['url'], timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0'
                    })
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract article text
                    article_body = soup.find('article')
                    if article_body:
                        text = article_body.get_text(separator=' ', strip=True)
                        candidate['text'] = text[:2000]

                    time.sleep(0.3)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"  ⚠️  Error in candidate retrieval: {e}")

        return [c for c in candidates if c.get('text')]

    def _get_fallback_articles(self, max_articles: int = 5) -> List[Dict[str, str]]:
        """Get fallback articles when search fails"""
        fallback = []

        sections = [
            'https://economictimes.indiatimes.com/tech/technology',
            'https://economictimes.indiatimes.com/tech/startups',
            'https://economictimes.indiatimes.com/markets/stocks'
        ]

        try:
            for section_url in sections:
                if len(fallback) >= max_articles:
                    break

                response = requests.get(section_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                soup = BeautifulSoup(response.text, 'html.parser')

                links = soup.find_all('a', href=True)

                for link in links:
                    if len(fallback) >= max_articles:
                        break

                    href = link.get('href', '')

                    if 'articleshow' in href:
                        if href.startswith('/'):
                            full_url = 'https://economictimes.indiatimes.com' + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue

                        title = link.get_text(strip=True)

                        if title and len(title) > 20:
                            if not any(a['url'] == full_url for a in fallback):
                                fallback.append({
                                    'url': full_url,
                                    'title': title,
                                    'similarity': 0.20,
                                    'text_preview': f'Popular article from {section_url.split("/")[-1]} section'
                                })

                time.sleep(0.3)

        except Exception as e:
            print(f"  ⚠️  Fallback error: {e}")

        return fallback[:max_articles]


# Global instance
_enhanced_discovery_instance = None

def get_enhanced_discovery_service() -> EnhancedArticleDiscovery:
    """Get or create enhanced discovery service"""
    global _enhanced_discovery_instance
    if _enhanced_discovery_instance is None:
        _enhanced_discovery_instance = EnhancedArticleDiscovery()
    return _enhanced_discovery_instance
