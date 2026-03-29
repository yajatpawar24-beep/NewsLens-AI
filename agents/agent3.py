"""
Agent 3: Briefing Synthesis Agent
===================================

Synthesizes multi-article briefings with cross-article analysis.
Generates audio narration using AWS Polly.
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
from langchain_aws import ChatBedrock
import boto3


# ============================================================================
# Briefing Synthesis Agent
# ============================================================================

class BriefingSynthesisAgent:
    """
    Agent 3: Synthesizes briefings from multiple article insights.

    Creates executive summaries, extracts key points, performs cross-article
    analysis (contradictions/consensus), and generates audio briefings.
    """

    def __init__(self):
        """Initialize the agent with Claude and AWS Polly clients"""
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={
                "temperature": 0.0,  # Zero temperature - maximum determinism
                "max_tokens": 4096   # Prevent JSON truncation
            }
        )

        # Initialize AWS Polly for text-to-speech
        self.polly_client = boto3.client(
            'polly',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )

    def synthesize_briefing(self, articles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize briefing from multiple article insights.

        Args:
            articles_data: List of dicts with 'insights', 'raw_text', 'title'

        Returns:
            Dictionary with summary, key_points, insights, questions
        """

        prompt = self._get_synthesis_prompt(articles_data)

        response = self.llm.invoke(prompt)

        # Parse JSON response - clean it first
        try:
            content = response.content.strip()

            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            # Find JSON object boundaries if there's extra text
            if not content.startswith('{'):
                # Look for first { and last }
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    content = content[start_idx:end_idx+1]

            # Try to parse
            briefing = json.loads(content)

            # Validate that we got actual content, not instructions
            if briefing.get('summary', '').startswith('[') or 'Write a' in briefing.get('summary', '')[:50]:
                print(f"⚠️  LLM returned template instead of content")
                raise json.JSONDecodeError("Template returned", content, 0)

        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  JSON parse error: {e}")
            print(f"Response content (first 300 chars): {response.content[:300]}")

            # Fallback: Use simple extraction from article
            briefing = self._generate_simple_briefing(articles_data)

        # CRITICAL: Validate against hallucinations
        briefing = self._validate_briefing(briefing, articles_data)

        return briefing

    def _validate_briefing(self, briefing: Dict[str, Any], articles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate briefing doesn't contain hallucinated content"""

        # Extract keywords from actual articles
        article_texts = [art.get('raw_text', '').lower() for art in articles_data]
        combined_text = ' '.join(article_texts)

        # Known hallucination keywords that should NOT appear unless in source
        hallucination_keywords = [
            'donald trump', 'metformin', 'alexa', 'spotify', 'oneplus nord',
            'gorilla glass', 'tirupati laddu', 'chromosome'
        ]

        briefing_text = json.dumps(briefing).lower()

        # Check for hallucinations
        for keyword in hallucination_keywords:
            if keyword in briefing_text and keyword not in combined_text:
                # Hallucination detected! Use simple extraction instead
                print(f"⚠️  Hallucination detected: '{keyword}' - using fallback")
                return self._generate_simple_briefing(articles_data)

        return briefing

    def _generate_simple_briefing(self, articles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate simple, safe briefing from article text directly"""
        if not articles_data:
            return {
                "summary": "No article data available",
                "key_points": [],
                "insights": {"contradictions": [], "consensus": []},
                "questions": []
            }

        article = articles_data[0]
        raw_text = article.get('raw_text', '')
        title = article.get('title', 'Unknown')
        insights = article.get('insights', {})

        # Extract first few sentences as summary
        sentences = raw_text.split('.')[:3]
        summary = '. '.join(sentences).strip() + '.'

        # Use actual entities as key points
        entities = insights.get('entities', [])
        key_points = [
            f"{e['name']} ({e['type']}): {e.get('context', '')}"
            for e in entities[:5]
        ]

        if not key_points:
            # Fallback: Use first 5 sentences
            key_points = [s.strip() + '.' for s in raw_text.split('.')[:5] if len(s.strip()) > 20]

        return {
            "summary": summary if len(summary) > 50 else raw_text[:300],
            "key_points": key_points[:5] if key_points else ["Article content available"],
            "insights": {
                "contradictions": [],
                "consensus": [f"Article discusses: {insights.get('main_theme', title)}"]
            },
            "questions": [
                f"What are the implications of {title.lower()}?",
                "What additional context would be helpful?",
                "What are the next steps or expected developments?"
            ]
        }

    def generate_audio_briefing(self, summary_text: str, output_path: str) -> str:
        """
        Generate audio narration of the briefing using AWS Polly.

        Args:
            summary_text: Text to convert to speech
            output_path: Path to save MP3 file

        Returns:
            Path to generated audio file
        """

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Generate speech using AWS Polly
        response = self.polly_client.synthesize_speech(
            Text=summary_text,
            OutputFormat='mp3',
            VoiceId='Joanna',  # Professional, neutral female voice
            Engine='neural'     # Use neural engine for better quality
        )

        # Save audio stream to file
        if 'AudioStream' in response:
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())

        return output_path

    def _get_synthesis_prompt(self, articles_data: List[Dict[str, Any]]) -> str:
        """Generate synthesis prompt with ACTUAL article text"""

        articles_content = self._format_articles_with_text(articles_data)
        num_articles = len(articles_data)

        # Different prompt for single vs multiple articles
        if num_articles == 1:
            return f"""Analyze this article and create a business briefing in JSON format.

ARTICLE:
{articles_content}

Return ONLY a valid JSON object (no markdown, no code blocks) with this EXACT structure:

{{
  "summary": "[Write a comprehensive 400-500 word executive summary. Start with the main announcement and who's involved. Include all specific numbers, percentages, and dates from the article. Explain why this matters and what happens next. Provide context and implications. Use only facts from the article above. Make it detailed and informative - this is the main content users will read.]",
  "key_points": [
    "[Point 1: Main announcement with specifics - 25-30 words]",
    "[Point 2: Key stakeholders and their roles - 25-30 words]",
    "[Point 3: Financial details with exact numbers - 25-30 words]",
    "[Point 4: Timeline and important dates - 25-30 words]",
    "[Point 5: Strategic rationale and objectives - 25-30 words]",
    "[Point 6: Market impact or competitive implications - 25-30 words]",
    "[Point 7: Technical details or operational changes - 25-30 words]",
    "[Point 8: Regulatory aspects or policy impact - 25-30 words]",
    "[Point 9: Future plans or next steps - 25-30 words]",
    "[Point 10: Expert opinions or market reaction - 25-30 words]"
  ],
  "insights": {{
    "contradictions": [],
    "consensus": [
      "[Confirmed fact 1 from the article]",
      "[Confirmed fact 2 from the article]",
      "[Confirmed fact 3 from the article]"
    ]
  }},
  "questions": [
    "[Strategic question 1 about competitive positioning?]",
    "[Strategic question 2 about financial implications?]",
    "[Strategic question 3 about execution risks?]",
    "[Strategic question 4 about market impact?]",
    "[Strategic question 5 about regulatory challenges?]",
    "[Strategic question 6 about stakeholder impact?]",
    "[Strategic question 7 about future opportunities?]",
    "[Strategic question 8 about industry trends?]"
  ]
}}

CRITICAL RULES:
- Replace ALL [...] brackets with actual content from the article
- Generate EXACTLY 10 key points (not fewer, not more)
- Each key point must be 25-30 words - substantial and informative
- Summary must be 400-500 words - comprehensive and detailed
- Use ONLY facts from the article - no external knowledge
- Include exact company names, numbers, percentages, dates from article
- NEVER say "The article does not discuss..." or "No mention of..."
- ONLY include points about topics that ARE in the article
- If you can't find content for a specific point category, adapt it to what the article DOES discuss
- Return raw JSON only - no ```json markers, no extra text"""

        else:
            # Multi-article prompt with contradiction detection
            return f"""You are analyzing {num_articles} DIFFERENT articles about related topics. Your job is to COMPARE and CONTRAST them.

ARTICLES:
{articles_content}

CRITICAL: You MUST reference content from ALL {num_articles} articles above. DO NOT focus only on Article 1.

Return ONLY a valid JSON object (no markdown, no code blocks) with this structure:

{{
  "summary": "[Write a 400-500 word CROSS-ARTICLE comparison summary. Structure: (1) Opening: What all {num_articles} articles discuss, (2) Article 1 perspective: Key points from first article, (3) Article 2 perspective: Different angle or additional details from second article, (4) Article 3+ perspective: If more articles, cover their unique contributions, (5) Comparison: Where articles agree and disagree, (6) Synthesis: Combined view of the situation. USE PHRASES LIKE 'Article 1 reports that...', 'Article 2 adds that...', 'While Article 1 focuses on X, Article 2 emphasizes Y']",
  "key_points": [
    "[Point 1: CONSENSUS - What ALL {num_articles} articles agree on (25-30 words)]",
    "[Point 2: From Article 1 - Unique detail or emphasis in first article (25-30 words)]",
    "[Point 3: From Article 2 - Unique detail or emphasis in second article (25-30 words)]",
    "[Point 4: From Article 3 - If applicable, unique detail from third article (25-30 words)]",
    "[Point 5: COMPARISON - How articles differ in their numbers/dates/facts (25-30 words)]",
    "[Point 6: Timeline synthesis - Events from all articles combined chronologically (25-30 words)]",
    "[Point 7: Stakeholders mentioned across articles (25-30 words)]",
    "[Point 8: Financial/business implications from all sources (25-30 words)]",
    "[Point 9: Market reaction or expert opinions across articles (25-30 words)]",
    "[Point 10: Future outlook synthesized from all sources (25-30 words)]"
  ],
  "insights": {{
    "contradictions": [
      "[CRITICAL: List SPECIFIC contradictions. Format: 'Article 1 (title) says X, but Article 2 (title) says Y'. Examples: 'Article 1 reports funding of $100M, Article 2 reports $120M', 'Article 1 says deal closes in Q2, Article 2 says Q3'. If truly NO contradictions found after checking ALL articles, leave empty array.]"
    ],
    "consensus": [
      "[Consensus fact 1 - confirmed across ALL {num_articles} articles]",
      "[Consensus fact 2 - confirmed across ALL {num_articles} articles]",
      "[Consensus fact 3 - confirmed across ALL {num_articles} articles]",
      "[Consensus fact 4 - confirmed across ALL {num_articles} articles]",
      "[Consensus fact 5 - confirmed across ALL {num_articles} articles]"
    ]
  }},
  "questions": [
    "[Question 1: Why do the articles present different angles on this story?]",
    "[Question 2: Which article provides the most comprehensive coverage?]",
    "[Question 3: What information appears in one article but not others?]",
    "[Question 4: How do the timelines across articles compare?]",
    "[Question 5: Which stakeholders are emphasized differently across sources?]",
    "[Question 6: What are the strategic implications highlighted by each article?]",
    "[Question 7: How do financial projections or numbers differ?]",
    "[Question 8: What questions remain unanswered even after reading all articles?]"
  ]
}}

CRITICAL INSTRUCTIONS FOR MULTI-ARTICLE ANALYSIS:
1. READ ALL {num_articles} ARTICLES COMPLETELY - Do not focus only on Article 1
2. REFERENCE EACH ARTICLE BY NAME in your summary - "Article 1 discusses...", "Article 2 reveals...", "Article 3 adds..."
3. COMPARE EXPLICITLY - Use phrases like "while", "however", "in contrast", "similarly", "both articles"
4. DETECT CONTRADICTIONS - Look for different numbers, dates, names, interpretations across articles
5. FIND CONSENSUS - What facts appear in ALL articles?
6. SYNTHESIZE - Create a unified view that incorporates insights from ALL sources
7. In key_points, ensure points 2, 3, 4 explicitly come from DIFFERENT articles
8. Use ONLY facts from the articles provided above - no external knowledge
9. Return raw JSON only - no ```json markers, no extra text

REMEMBER: You have {num_articles} articles - make sure your analysis reflects content from ALL of them, not just the first one!"""

    def _format_articles_with_text(self, articles_data: List[Dict[str, Any]]) -> str:
        """Format articles with ACTUAL text to prevent hallucination"""

        if not articles_data:
            return "No articles available."

        formatted = []
        for idx, article in enumerate(articles_data, 1):
            title = article.get('title', 'Unknown')
            raw_text = article.get('raw_text', '')

            formatted.append(f"""
===== ARTICLE {idx}: {title} =====

{raw_text}

===== END ARTICLE {idx} =====
""")

        return '\n'.join(formatted)

    def _format_insights(self, insights_list: List[Dict[str, Any]]) -> str:
        """Format insights for prompt - include more detail to prevent hallucination"""

        if not insights_list:
            return "No insights available."

        formatted = []
        for idx, insights in enumerate(insights_list, 1):
            entities = insights.get('entities', [])
            timeline = insights.get('timeline', [])
            metrics = insights.get('key_metrics', {})
            theme = insights.get('main_theme', 'N/A')
            sentiment = insights.get('sentiment', 'neutral')

            # Include detailed entity info
            entity_details = []
            for e in entities[:5]:
                entity_details.append(f"{e['name']} ({e['type']}): {e.get('context', '')}")

            # Include timeline details
            timeline_details = []
            for t in timeline[:3]:
                timeline_details.append(f"{t.get('date')}: {t.get('event')} (Impact: {t.get('impact')})")

            formatted.append(f"""
Article {idx}:
Theme: {theme}
Sentiment: {sentiment}

Entities Found:
{chr(10).join(['- ' + ed for ed in entity_details]) if entity_details else '- None'}

Timeline Events:
{chr(10).join(['- ' + td for td in timeline_details]) if timeline_details else '- None'}

Key Metrics:
{chr(10).join(['- ' + f"{k}: {v}" for k, v in metrics.items()]) if metrics else '- None'}
""")

        return '\n'.join(formatted)


# ============================================================================
# Helper Functions
# ============================================================================

def create_agent() -> BriefingSynthesisAgent:
    """Factory function to create Briefing Synthesis Agent"""
    return BriefingSynthesisAgent()
