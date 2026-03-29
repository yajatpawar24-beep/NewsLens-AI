"""
NewsLens AI Orchestrator
=========================

LangGraph-based orchestration of the 3-agent pipeline.
Coordinates: fetch → extract → visualize → synthesize → audio
"""

import requests
from typing import TypedDict, List, Dict, Any
from bs4 import BeautifulSoup
from langgraph.graph import StateGraph, END
from agents.agent1 import SourceIntelligenceAgent
from agents.agent2 import VisualIntelligenceAgent
from agents.agent3 import BriefingSynthesisAgent


# ============================================================================
# State Definition
# ============================================================================

class NewsLensState(TypedDict):
    """State structure for the NewsLens pipeline"""
    article_urls: List[str]
    raw_articles: List[Dict[str, Any]]
    insights: Dict[str, Any]
    visualizations: List[str]
    briefing: Dict[str, Any]
    audio_path: str
    entity_graph: Dict[str, Any]  # Entity relationship graph data
    status: str


# ============================================================================
# NewsLens Orchestrator
# ============================================================================

class NewsLensOrchestrator:
    """
    Orchestrates the complete NewsLens AI pipeline using LangGraph.

    Pipeline: fetch → extract → visualize → synthesize → audio
    """

    def __init__(self):
        """Initialize agents and build workflow graph"""
        self.agent1 = SourceIntelligenceAgent()
        self.agent2 = VisualIntelligenceAgent()
        self.agent3 = BriefingSynthesisAgent()

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph StateGraph for the pipeline"""

        workflow = StateGraph(NewsLensState)

        # Add nodes
        workflow.add_node("fetch", self.fetch_articles)
        workflow.add_node("extract", self.extract_insights)
        workflow.add_node("visualize", self.generate_visualizations)
        workflow.add_node("synthesize", self.synthesize_briefing)
        workflow.add_node("audio", self.generate_audio)

        # Define edges (pipeline flow)
        workflow.set_entry_point("fetch")
        workflow.add_edge("fetch", "extract")
        workflow.add_edge("extract", "visualize")
        workflow.add_edge("visualize", "synthesize")
        workflow.add_edge("synthesize", "audio")
        workflow.add_edge("audio", END)

        return workflow.compile()

    def process(self, article_urls: List[str]) -> Dict[str, Any]:
        """
        Process articles through complete pipeline.

        Args:
            article_urls: List of Economic Times article URLs

        Returns:
            Complete briefing with visualizations and audio
        """

        # Initialize state
        initial_state: NewsLensState = {
            "article_urls": article_urls,
            "raw_articles": [],
            "insights": {},
            "visualizations": [],
            "briefing": {},
            "audio_path": "",
            "entity_graph": {"entities": [], "relationships": []},
            "status": "initialized"
        }

        # Run pipeline
        final_state = self.graph.invoke(initial_state)

        return final_state

    # ========================================================================
    # Node Functions
    # ========================================================================

    def fetch_articles(self, state: NewsLensState) -> Dict[str, Any]:
        """
        Node 1: Fetch articles from URLs.

        Args:
            state: Current pipeline state

        Returns:
            Updated state with raw_articles
        """

        raw_articles = []

        for url in state["article_urls"]:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = requests.get(url, timeout=15, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract title
                title = soup.find('h1')
                title_text = title.get_text().strip() if title else "Unknown Title"

                # Extract article content - Economic Times specific selectors
                content_parts = []
                content = ""

                # Strategy 1: Try <article> tag first (works for most ET articles)
                article_body = soup.find('article')
                if article_body:
                    # Get all text from article tag, but clean it up
                    full_text = article_body.get_text(separator=' ', strip=True)

                    # Filter out common ET footer/navigation text
                    excluded_phrases = [
                        'Subscribe to ET Prime',
                        'Download The Economic Times News App',
                        'Catch all the',
                        'Latest News Updates',
                        'Follow us on',
                        'Join the community',
                        'Also Read',
                        'More From',
                        'Read More'
                    ]

                    # Split into sentences and filter
                    sentences = full_text.split('.')
                    filtered_sentences = []
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > 15:  # Minimum sentence length (reduced from 20)
                            # Check if it's not navigation text
                            if not any(phrase in sentence for phrase in excluded_phrases):
                                filtered_sentences.append(sentence)

                    content = '. '.join(filtered_sentences[:70])  # First 70 sentences (increased from 50)

                    if len(content) < 300:  # Too short, try other methods
                        article_body = None
                        content = ""

                # Strategy 2: Try specific ET div classes (desktop)
                if not article_body:
                    selectors = [
                        ('div', {'class': 'artText'}),
                        ('div', {'itemprop': 'articleBody'}),
                        ('div', {'class': 'Normal'}),
                    ]

                    for tag, attrs in selectors:
                        article_body = soup.find(tag, attrs)
                        if article_body:
                            paragraphs = article_body.find_all('p')
                            content_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30]
                            if len(content_parts) > 3:
                                content = ' '.join(content_parts[:40])
                                break

                # Strategy 3: Fallback to all paragraphs
                if not content_parts and not article_body:
                    all_paragraphs = soup.find_all('p')
                    content_parts = [
                        p.get_text().strip() for p in all_paragraphs
                        if len(p.get_text().strip()) > 40
                        and 'cookie' not in p.get_text().lower()
                        and 'subscribe' not in p.get_text().lower()
                    ]
                    content = ' '.join(content_parts[:40])

                # Ensure we have content
                if 'content' not in locals() or not content:
                    content = ' '.join(content_parts[:40]) if content_parts else ""

                # Validate content quality - detect homepage redirects
                is_valid = True
                error_msg = ""

                if not content or len(content) < 200:
                    is_valid = False
                    error_msg = "Unable to extract article content. The URL may be invalid or redirecting to homepage. Please try a recent Economic Times article."
                elif title_text == "Unknown Title" or title_text == "Home":
                    is_valid = False
                    error_msg = "This URL appears to redirect to homepage. Please use a valid article URL from economictimes.indiatimes.com"
                elif soup.find('title') and 'Home' in soup.find('title').get_text():
                    is_valid = False
                    error_msg = "This URL redirects to homepage. Please use a current article link."

                raw_articles.append({
                    "url": url,
                    "title": title_text if is_valid else "Invalid URL",
                    "text": content if is_valid else error_msg,
                    "status": "fetched" if is_valid else "error"
                })

            except Exception as e:
                raw_articles.append({
                    "url": url,
                    "title": "Error",
                    "text": f"Failed to fetch: {str(e)}",
                    "status": "error"
                })

        return {
            **state,
            "raw_articles": raw_articles,
            "status": "fetched"
        }

    def extract_insights(self, state: NewsLensState) -> Dict[str, Any]:
        """
        Node 2: Extract insights using Agent 1.

        Args:
            state: Current pipeline state

        Returns:
            Updated state with insights
        """

        all_insights = []

        for article in state["raw_articles"]:
            if article.get("status") == "fetched":
                insights = self.agent1.extract_insights(article["text"])
                all_insights.append(insights)

        return {
            **state,
            "insights": {"articles": all_insights},
            "status": "extracted"
        }

    def generate_visualizations(self, state: NewsLensState) -> Dict[str, Any]:
        """
        Node 3: Generate visualizations using Agent 2.

        Args:
            state: Current pipeline state

        Returns:
            Updated state with visualizations
        """

        visualizations = []
        articles_insights = state["insights"].get("articles", [])
        raw_articles = state.get("raw_articles", [])

        print(f"📊 Generating visualizations for {len(articles_insights)} articles")

        # Generate MULTIPLE visualizations per article for richer output
        for idx, insights in enumerate(articles_insights):
            print(f"  Article {idx+1}: Generating multiple visualizations...")

            # 1. Entity cards (comparison view)
            entities_viz = self.agent2.generate_artifact_code('comparison', insights)
            visualizations.append(entities_viz)
            print(f"    ✅ Entity cards: {len(entities_viz)} chars")

            # 2. Timeline (if timeline data exists)
            if insights.get('timeline') and len(insights.get('timeline', [])) > 0:
                timeline_viz = self.agent2.generate_artifact_code('timeline', insights)
                visualizations.append(timeline_viz)
                print(f"    ✅ Timeline: {len(timeline_viz)} chars")

            # 3. Metrics dashboard (if metrics exist)
            if insights.get('key_metrics') and len(insights.get('key_metrics', {})) > 0:
                metrics_viz = self.agent2.generate_artifact_code('metrics', insights)
                visualizations.append(metrics_viz)
                print(f"    ✅ Metrics dashboard: {len(metrics_viz)} chars")

        # Generate CROSS-ARTICLE visualizations if multiple articles
        if len(articles_insights) > 1:
            print(f"🔗 Generating cross-article visualizations...")

            # 1. Aggregate timeline from all articles
            aggregated_timeline = self._aggregate_timeline(articles_insights, raw_articles)
            timeline_viz = self.agent2.generate_cross_article_timeline(aggregated_timeline)
            visualizations.append(timeline_viz)
            print(f"  ✅ Cross-article timeline generated")

            # 2. Aggregate entities with frequency
            aggregated_entities = self._aggregate_entities(articles_insights)
            entity_viz = self.agent2.generate_entity_network(aggregated_entities)
            visualizations.append(entity_viz)
            print(f"  ✅ Entity network generated")

            # 3. Sentiment comparison
            sentiment_data = self._aggregate_sentiment(articles_insights, raw_articles)
            sentiment_viz = self.agent2.generate_sentiment_comparison(sentiment_data)
            visualizations.append(sentiment_viz)
            print(f"  ✅ Sentiment comparison generated")

        print(f"✅ Total visualizations generated: {len(visualizations)}")

        return {
            **state,
            "visualizations": visualizations,
            "status": "visualized"
        }

    def synthesize_briefing(self, state: NewsLensState) -> Dict[str, Any]:
        """
        Node 4: Synthesize briefing using Agent 3.

        Args:
            state: Current pipeline state

        Returns:
            Updated state with briefing
        """

        articles_insights = state["insights"].get("articles", [])

        # IMPORTANT: Pass raw article text so Agent 3 can't hallucinate
        raw_articles = state.get("raw_articles", [])
        articles_with_text = []
        for i, insights in enumerate(articles_insights):
            if i < len(raw_articles):
                # For multi-article analysis, provide MORE context per article
                char_limit = 5000 if len(articles_insights) > 1 else 3000
                article_data = {
                    "insights": insights,
                    "raw_text": raw_articles[i].get("text", "")[:char_limit],  # More chars for multi-article
                    "title": raw_articles[i].get("title", ""),
                    "url": raw_articles[i].get("url", "")
                }
                articles_with_text.append(article_data)

        # Generate briefing with access to raw text
        briefing = self.agent3.synthesize_briefing(articles_with_text)

        # Aggregate entity relationships for graph visualization
        aggregated_entities = self._aggregate_entities(articles_insights)
        aggregated_relationships = self._aggregate_relationships(articles_insights)

        # Limit to top 20 entities
        top_entities = aggregated_entities.get("entities", [])[:20]
        entity_names = set(e['name'] for e in top_entities)

        # Transform entities: convert 'contexts' array to single 'context' string
        transformed_entities = []
        for entity in top_entities:
            contexts = entity.get('contexts', [])
            # Use the first non-empty context, or join all contexts
            context = next((c for c in contexts if c), '') if contexts else ''

            transformed_entities.append({
                'name': entity['name'],
                'type': entity['type'],
                'context': context,
                'frequency': entity.get('frequency', 1)
            })

        # Filter relationships to only include those with both source and target in entity list
        filtered_relationships = [
            rel for rel in aggregated_relationships
            if rel['source'] in entity_names and rel['target'] in entity_names
        ]

        entity_graph = {
            "entities": transformed_entities,
            "relationships": filtered_relationships
        }

        return {
            **state,
            "briefing": briefing,
            "entity_graph": entity_graph,
            "status": "synthesized"
        }

    def generate_audio(self, state: NewsLensState) -> Dict[str, Any]:
        """
        Node 5: Generate audio briefing using Agent 3.

        Args:
            state: Current pipeline state

        Returns:
            Updated state with audio_path
        """

        summary = state["briefing"].get("summary", "No summary available")

        # Generate audio file
        import tempfile
        from pathlib import Path

        audio_dir = Path("data/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)

        audio_path = str(audio_dir / "briefing.mp3")

        try:
            self.agent3.generate_audio_briefing(summary, audio_path)
        except Exception as e:
            audio_path = f"Error generating audio: {str(e)}"

        return {
            **state,
            "audio_path": audio_path,
            "status": "completed"
        }

    # ========================================================================
    # Cross-Article Aggregation Methods
    # ========================================================================

    def _aggregate_timeline(self, articles_insights: List[Dict], raw_articles: List[Dict]) -> List[Dict]:
        """Aggregate timeline events from all articles"""
        aggregated = []

        for idx, insights in enumerate(articles_insights):
            timeline = insights.get('timeline', [])
            source = raw_articles[idx].get('title', f'Article {idx+1}')[:50]  # First 50 chars

            for event in timeline:
                aggregated.append({
                    'date': event.get('date', ''),
                    'event': event.get('event', ''),
                    'impact': event.get('impact', 'Medium'),
                    'source': source,
                    'article_index': idx
                })

        # Sort by date
        aggregated.sort(key=lambda x: x['date'])

        return aggregated

    def _aggregate_entities(self, articles_insights: List[Dict]) -> Dict[str, Any]:
        """Aggregate entities with frequency counts"""
        entity_map = {}

        for idx, insights in enumerate(articles_insights):
            entities = insights.get('entities', [])

            for entity in entities:
                name = entity.get('name', '')
                entity_type = entity.get('type', 'entity')

                if name not in entity_map:
                    entity_map[name] = {
                        'name': name,
                        'type': entity_type,
                        'frequency': 0,
                        'contexts': [],
                        'article_indices': []
                    }

                entity_map[name]['frequency'] += 1
                entity_map[name]['contexts'].append(entity.get('context', ''))
                entity_map[name]['article_indices'].append(idx)

        # Convert to list and sort by frequency
        entities_list = list(entity_map.values())
        entities_list.sort(key=lambda x: x['frequency'], reverse=True)

        return {
            'entities': entities_list,
            'total_unique': len(entities_list)
        }

    def _aggregate_sentiment(self, articles_insights: List[Dict], raw_articles: List[Dict]) -> List[Dict]:
        """Aggregate sentiment data from all articles"""
        sentiment_data = []

        for idx, insights in enumerate(articles_insights):
            sentiment = insights.get('sentiment', 'neutral')
            source = raw_articles[idx].get('title', f'Article {idx+1}')[:40]

            # Convert sentiment to score
            sentiment_score = 0.5  # Default neutral
            if sentiment.lower() == 'positive':
                sentiment_score = 0.75
            elif sentiment.lower() == 'negative':
                sentiment_score = 0.25

            sentiment_data.append({
                'source': source,
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'article_index': idx
            })

        return sentiment_data

    def _aggregate_relationships(self, articles_insights: List[Dict]) -> List[Dict]:
        """Aggregate relationships across all articles"""
        relationship_map = {}

        for idx, insights in enumerate(articles_insights):
            relationships = insights.get('relationships', [])

            for rel in relationships:
                source = rel.get('source', '')
                target = rel.get('target', '')
                rel_type = rel.get('type', 'related_to')
                strength = rel.get('strength', 0.5)

                # Create unique key for this relationship
                key = f"{source}::{target}::{rel_type}"

                if key not in relationship_map:
                    relationship_map[key] = {
                        'source': source,
                        'target': target,
                        'type': rel_type,
                        'strength': strength,
                        'count': 0
                    }

                # Increase strength if mentioned in multiple articles
                relationship_map[key]['count'] += 1
                relationship_map[key]['strength'] = min(1.0, strength + (relationship_map[key]['count'] - 1) * 0.2)

        # Convert to list
        relationships_list = list(relationship_map.values())

        return relationships_list


# ============================================================================
# Helper Functions
# ============================================================================

def create_orchestrator() -> NewsLensOrchestrator:
    """Factory function to create orchestrator"""
    return NewsLensOrchestrator()
