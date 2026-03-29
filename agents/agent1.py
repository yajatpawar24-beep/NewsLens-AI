"""
Agent 1: Source Intelligence Agent
====================================

Extracts structured insights from Economic Times articles using Claude API.
Outputs: entities, timeline, key metrics, sentiment, and main theme.
"""

import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_aws import ChatBedrock


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class Entity(BaseModel):
    """Represents an entity extracted from the article"""
    name: str = Field(description="Name of the entity")
    type: str = Field(description="Type: company, person, policy, metric, organization")
    context: str = Field(description="Brief context about the entity")


class TimelineEvent(BaseModel):
    """Represents a significant event in the timeline"""
    date: str = Field(description="Date in YYYY-MM-DD format")
    event: str = Field(description="Description of the event")
    impact: str = Field(description="Impact level: High, Medium, Low")


class Relationship(BaseModel):
    """Represents a relationship between two entities"""
    source: str = Field(description="Source entity name")
    target: str = Field(description="Target entity name")
    type: str = Field(description="Relationship type: competes_with, partners_with, invests_in, acquires, regulates, supplies_to, leads, owns")
    strength: float = Field(description="Relationship strength: 0.0 (weak) to 1.0 (strong)")


class ArticleInsights(BaseModel):
    """Complete structured insights from an article"""
    entities: List[Entity] = Field(description="Key entities mentioned")
    timeline: List[TimelineEvent] = Field(description="Chronological events")
    relationships: List[Relationship] = Field(description="Relationships between entities", default_factory=list)
    key_metrics: Dict[str, str] = Field(description="Important numbers and metrics")
    sentiment: str = Field(description="Overall sentiment: positive, negative, neutral")
    main_theme: str = Field(description="Main theme or topic of the article")


# ============================================================================
# Source Intelligence Agent
# ============================================================================

class SourceIntelligenceAgent:
    """
    Agent 1: Extracts structured insights from news articles.

    Uses Claude API with Pydantic structured output to extract:
    - Entities (companies, people, policies, metrics)
    - Timeline of events
    - Key metrics and numbers
    - Sentiment analysis
    - Main theme
    """

    def __init__(self):
        """Initialize the agent with Claude API client"""
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={
                "temperature": 0.1,  # Very low temperature for deterministic output
                "max_tokens": 4096   # Prevent JSON truncation
            }
        )

        # Don't use structured output - parse manually instead
        # self.extractor = self.llm.with_structured_output(ArticleInsights)

    def extract_insights(self, article_text: str) -> Dict[str, Any]:
        """
        Extract structured insights from article text.

        Args:
            article_text: Full text of the news article

        Returns:
            Dictionary containing entities, timeline, metrics, sentiment, theme
        """

        # Check if article text is too short
        if len(article_text) < 100:
            return self._get_fallback_insights(article_text)

        try:
            # Load extraction prompt - simplified for better results
            prompt = self._get_simple_extraction_prompt(article_text)

            # Call Claude and parse JSON response
            response = self.llm.invoke(prompt)

            # Try to parse as JSON
            import json
            try:
                # Clean markdown code blocks if present
                content = response.content.strip()
                if content.startswith('```'):
                    content = content.split('```')[1]
                    if content.startswith('json'):
                        content = content[4:]
                    content = content.strip()

                # Find JSON boundaries if extra text
                if not content.startswith('{'):
                    start_idx = content.find('{')
                    end_idx = content.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        content = content[start_idx:end_idx+1]

                result = json.loads(content)
                # Clean up entity contexts to ensure proper grammar
                result = self._clean_entity_contexts(result)
                return result
            except json.JSONDecodeError as je:
                print(f"Agent 1 JSON parse error at char {je.pos}: {je.msg}")
                print(f"Response length: {len(response.content)}, Preview: {response.content[:500]}")
                # If JSON parsing fails, extract key info from text
                return self._parse_text_response(response.content, article_text)

        except Exception as e:
            print(f"Agent 1 extraction error: {e}")
            # Return fallback if extraction fails
            return self._get_fallback_insights(article_text)

    def _clean_entity_contexts(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up entity contexts to ensure proper grammar"""
        if 'entities' in result:
            for entity in result['entities']:
                if 'context' in entity:
                    context = entity['context']

                    # Remove ellipsis
                    context = context.rstrip('.')

                    # Remove trailing ellipsis
                    if context.endswith('...'):
                        context = context[:-3]
                    elif context.endswith('..'):
                        context = context[:-2]

                    # Ensure it ends with a period
                    if not context.endswith('.'):
                        context = context + '.'

                    # Fix common fragments - if it starts with a verb gerund without subject
                    if context.startswith(('investing', 'merging', 'launching', 'announcing', 'developing', 'creating', 'building')):
                        # This is likely a fragment, prepend entity name
                        context = f"{entity['name']} is {context}"

                    # Fix "the focus of the article" type meta-descriptions
                    if any(phrase in context.lower() for phrase in ['focus of the article', 'mentioned in', 'author of', 'discussed in']):
                        # Replace with generic but grammatical
                        context = f"{entity['name']} is a key entity discussed in the article."

                    entity['context'] = context

        # Add inferred relationships if too few were extracted
        if 'relationships' in result and 'entities' in result:
            relationships = result['relationships']
            entities = result['entities']

            # If very few relationships, infer competition between companies in same industry
            if len(relationships) < 3:
                companies = [e for e in entities if e.get('type') == 'company']

                # Add competition relationships between companies (they're likely competing)
                for i, comp1 in enumerate(companies):
                    for comp2 in companies[i+1:]:
                        # Check if relationship already exists
                        existing = any(
                            (r['source'] == comp1['name'] and r['target'] == comp2['name']) or
                            (r['source'] == comp2['name'] and r['target'] == comp1['name'])
                            for r in relationships
                        )

                        if not existing:
                            relationships.append({
                                'source': comp1['name'],
                                'target': comp2['name'],
                                'type': 'competes_with',
                                'strength': 0.5  # Implied competition
                            })

                        # Limit to avoid too many relationships
                        if len(relationships) >= 6:
                            break
                    if len(relationships) >= 6:
                        break

                result['relationships'] = relationships

        return result

    def _get_fallback_insights(self, article_text: str) -> Dict[str, Any]:
        """Provide fallback insights when extraction fails"""
        return {
            "entities": [
                {"name": "Article", "type": "organization", "context": "News article content"}
            ],
            "timeline": [
                {"date": "2026-03-29", "event": "Article published", "impact": "Medium"}
            ],
            "relationships": [],
            "key_metrics": {"Content Length": f"{len(article_text)} characters"},
            "sentiment": "neutral",
            "main_theme": "News article content"
        }

    def _get_simple_extraction_prompt(self, article_text: str) -> str:
        """Generate simplified extraction prompt for Claude"""
        # Truncate if too long
        text = article_text[:2500] if len(article_text) > 2500 else article_text

        return f"""Extract ALL key information from this news article and return as JSON. This article may be about business, technology, AI, blockchain, telecom, policy, or any other topic.

Article text:
{text}

Return JSON with this EXACT structure:
{{
  "entities": [
    {{"name": "Reliance", "type": "company", "context": "Reliance is investing Rs 30,000 crore to expand its telecom infrastructure across India"}},
    {{"name": "BSNL", "type": "company", "context": "BSNL is merging with MTNL to create a unified state-run telecom operator"}},
    {{"name": "Jio", "type": "company", "context": "Jio launched 5G services in 200 cities with plans to expand nationwide"}}
  ],
  "timeline": [
    {{"date": "YYYY-MM-DD", "event": "what happened", "impact": "High/Medium/Low"}}
  ],
  "relationships": [
    {{"source": "Reliance", "target": "Jio", "type": "owns", "strength": 0.9}},
    {{"source": "BSNL", "target": "MTNL", "type": "acquires", "strength": 0.9}},
    {{"source": "Jio", "target": "BSNL", "type": "competes_with", "strength": 0.7}}
  ],
  "key_metrics": {{
    "Funding": "amount if mentioned",
    "Revenue": "amount if mentioned",
    "Users": "number if mentioned",
    "Growth": "percentage if mentioned",
    "Any other numbers": "values mentioned"
  }},
  "sentiment": "positive/negative/neutral",
  "main_theme": "brief theme description (1 sentence)"
}}

CRITICAL GRAMMAR AND FORMATTING RULES:

Entity Context Rules (MUST FOLLOW):
✓ CORRECT FORMAT: "[Entity name] [verb in present/past tense] [specific action] [with numbers/details]"
✓ GOOD EXAMPLES:
  - "Reliance announced a Rs 30,000 crore investment in telecom infrastructure"
  - "BSNL merged with MTNL to form a unified state telecom operator"
  - "Cisco forecasts 177 million wearable devices globally by 2013"
  - "Apple launched the iPhone 15 with advanced AI capabilities"
  - "The government approved a new policy for spectrum allocation"

✗ WRONG - DO NOT WRITE LIKE THIS:
  - "author of the article..." (incomplete, has ellipsis)
  - "assuring to set things right..." (fragment, unclear subject)
  - "the focus of the article..." (meta-description, not entity action)
  - "collaborating in next generation..." (incomplete thought)
  - "state-run incumbent merging with..." (no subject verb agreement)

Entity Context MUST:
1. Be a complete grammatical sentence (subject + verb + object)
2. Use proper verb tenses (present, past, future - NOT gerunds without subjects)
3. Include specific numbers, amounts, or details when mentioned
4. Be 10-20 words long
5. NEVER end with ellipsis (...)
6. NEVER be a sentence fragment
7. NEVER be a meta-description like "mentioned in article" or "author of"

Other Extraction Rules:
- Extract EVERY company, person, organization, technology, product mentioned
- Entity types: company, person, policy, organization, technology, product
- Include ALL dates, events, numbers, percentages, amounts

RELATIONSHIP EXTRACTION (CRITICAL):
- Extract ALL relationships between entities mentioned in the article
- Look for explicit connections: partnerships, competition, ownership, investments, mergers, leadership
- Look for implicit connections: if two companies are in same industry/market, they likely compete
- Common patterns to detect:
  * "Company A owns Company B" → (A, B, owns, 0.9)
  * "Company A merged with Company B" → (A, B, acquires, 0.9)
  * "Person X is CEO of Company Y" → (X, Y, leads, 0.9)
  * "Company A competes with Company B" → (A, B, competes_with, 0.7)
  * "Company A partnered with Company B" → (A, B, partners_with, 0.8)
  * "Company A supplies to Company B" → (A, B, supplies_to, 0.7)
  * If multiple companies in same industry mentioned → add competes_with relationships
- Aim for at least 3-5 relationships per article
- Relationship types: competes_with, partners_with, invests_in, acquires, regulates, supplies_to, leads, owns, develops, uses
- Relationship strength: 0.3-0.5 = implied/indirect, 0.6-0.8 = discussed, 0.9-1.0 = explicit/central

Return ONLY valid JSON with perfect grammar in all context fields."""

    def _parse_text_response(self, text: str, article_text: str) -> Dict[str, Any]:
        """Parse text response if JSON parsing fails"""
        # Extract theme from first sentence of article
        first_sentences = ' '.join(article_text.split('.')[:2])

        return {
            "entities": [
                {"name": "Economic Times", "type": "organization", "context": "News source"}
            ],
            "timeline": [
                {"date": "2026-03-29", "event": "Article published", "impact": "Medium"}
            ],
            "relationships": [],
            "key_metrics": {"Article Length": f"{len(article_text)} characters"},
            "sentiment": "neutral",
            "main_theme": first_sentences[:100] if first_sentences else "News article"
        }


# ============================================================================
# Helper Functions
# ============================================================================

def create_agent() -> SourceIntelligenceAgent:
    """Factory function to create Source Intelligence Agent"""
    return SourceIntelligenceAgent()
