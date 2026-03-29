"""
Test Suite for Agent 1: Source Intelligence Agent
==================================================

Tests for structured extraction of insights from articles.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from agents.agent1 import SourceIntelligenceAgent
from pydantic import ValidationError


@pytest.mark.unit
class TestSourceIntelligenceAgent:
    """Unit tests for Source Intelligence Agent"""

    def test_agent_initialization(self, mock_env_vars):
        """Test agent initializes correctly"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            agent = SourceIntelligenceAgent()
            assert agent is not None
            assert hasattr(agent, 'llm')

    def test_extract_insights_structure(self, sample_article, mock_env_vars, assert_valid_insights):
        """Test that extract_insights returns valid structure"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            # Mock LLM response
            mock_llm = MagicMock()
            mock_response = {
                "entities": [
                    {"name": "Finance Minister", "type": "person", "context": "Budget presenter"}
                ],
                "timeline": [
                    {"date": "2026-02-01", "event": "Budget presented", "impact": "Tax reforms"}
                ],
                "key_metrics": {"tax_exemption": "Rs 3.5 lakh"},
                "sentiment": "positive",
                "main_theme": "Tax reforms"
            }
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
            mock_chat.return_value = mock_llm

            agent = SourceIntelligenceAgent()
            insights = agent.extract_insights(sample_article["text"])

            # Validate structure
            assert_valid_insights(insights)

    def test_extract_entities(self, sample_article, mock_env_vars):
        """Test entity extraction from article"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            mock_llm = MagicMock()
            mock_response = {
                "entities": [
                    {"name": "Finance Minister", "type": "person", "context": "Presented budget"},
                    {"name": "Rs 3.5 lakh", "type": "metric", "context": "Tax exemption"},
                    {"name": "Union Budget 2026", "type": "policy", "context": "Annual budget"}
                ],
                "timeline": [],
                "key_metrics": {},
                "sentiment": "positive",
                "main_theme": "Budget"
            }
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
            mock_chat.return_value = mock_llm

            agent = SourceIntelligenceAgent()
            insights = agent.extract_insights(sample_article["text"])

            # Check entities
            assert len(insights["entities"]) >= 1
            assert all(isinstance(e, dict) for e in insights["entities"])
            assert all("name" in e and "type" in e for e in insights["entities"])

    def test_extract_timeline(self, sample_article, mock_env_vars):
        """Test timeline extraction from article"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            mock_llm = MagicMock()
            mock_response = {
                "entities": [],
                "timeline": [
                    {"date": "2026-02-01", "event": "Budget presented", "impact": "Tax reforms announced"},
                    {"date": "2026-02-01", "event": "Tax exemption raised", "impact": "Relief for middle class"}
                ],
                "key_metrics": {},
                "sentiment": "positive",
                "main_theme": "Budget"
            }
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
            mock_chat.return_value = mock_llm

            agent = SourceIntelligenceAgent()
            insights = agent.extract_insights(sample_article["text"])

            # Check timeline
            assert len(insights["timeline"]) >= 1
            for event in insights["timeline"]:
                assert "date" in event
                assert "event" in event
                assert "impact" in event

    def test_extract_key_metrics(self, sample_article, mock_env_vars):
        """Test key metrics extraction"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            mock_llm = MagicMock()
            mock_response = {
                "entities": [],
                "timeline": [],
                "key_metrics": {
                    "tax_exemption": "Rs 3.5 lakh",
                    "corporate_tax": "15%",
                    "fiscal_deficit": "4.5%"
                },
                "sentiment": "positive",
                "main_theme": "Budget"
            }
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
            mock_chat.return_value = mock_llm

            agent = SourceIntelligenceAgent()
            insights = agent.extract_insights(sample_article["text"])

            # Check metrics
            assert isinstance(insights["key_metrics"], dict)
            assert len(insights["key_metrics"]) >= 1

    def test_sentiment_analysis(self, mock_env_vars):
        """Test sentiment detection"""
        test_cases = [
            ("Great news! Economic growth surges.", "positive"),
            ("Market crashes amid recession fears.", "negative"),
            ("The policy remains unchanged.", "neutral")
        ]

        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            for text, expected_sentiment in test_cases:
                mock_llm = MagicMock()
                mock_response = {
                    "entities": [],
                    "timeline": [],
                    "key_metrics": {},
                    "sentiment": expected_sentiment,
                    "main_theme": "Test"
                }
                mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
                mock_chat.return_value = mock_llm

                agent = SourceIntelligenceAgent()
                insights = agent.extract_insights(text)

                assert insights["sentiment"] in ["positive", "negative", "neutral"]

    def test_empty_article_handling(self, mock_env_vars):
        """Test handling of empty article"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            mock_llm = MagicMock()
            mock_response = {
                "entities": [],
                "timeline": [],
                "key_metrics": {},
                "sentiment": "neutral",
                "main_theme": "No content"
            }
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
            mock_chat.return_value = mock_llm

            agent = SourceIntelligenceAgent()
            insights = agent.extract_insights("")

            # Should return valid structure even for empty input
            assert isinstance(insights, dict)
            assert "entities" in insights
            assert "sentiment" in insights

    @pytest.mark.requires_api
    def test_real_api_call(self, sample_article):
        """Test with real Claude API (requires credentials)"""
        # Skip if no API credentials
        import os
        if not os.getenv("AWS_ACCESS_KEY_ID"):
            pytest.skip("Requires AWS credentials")

        agent = SourceIntelligenceAgent()
        insights = agent.extract_insights(sample_article["text"])

        # Validate real response
        assert isinstance(insights, dict)
        assert "entities" in insights
        assert "sentiment" in insights


@pytest.mark.integration
class TestAgent1Integration:
    """Integration tests for Agent 1"""

    def test_multiple_articles_processing(self, sample_articles, mock_env_vars):
        """Test processing multiple articles"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            mock_llm = MagicMock()
            mock_response = {
                "entities": [{"name": "Test", "type": "company", "context": "Test"}],
                "timeline": [],
                "key_metrics": {},
                "sentiment": "neutral",
                "main_theme": "Test"
            }
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
            mock_chat.return_value = mock_llm

            agent = SourceIntelligenceAgent()
            results = []

            for article in sample_articles:
                insights = agent.extract_insights(article["text"])
                results.append(insights)

            # All articles processed successfully
            assert len(results) == len(sample_articles)
            assert all(isinstance(r, dict) for r in results)

    def test_cross_article_entity_extraction(self, sample_articles, mock_env_vars):
        """Test entity extraction across multiple articles"""
        with patch('agents.agent1.ChatAnthropic') as mock_chat:
            agent = SourceIntelligenceAgent()
            all_entities = []

            for article in sample_articles:
                mock_llm = MagicMock()
                mock_response = {
                    "entities": [
                        {"name": f"Entity from {article['title'][:20]}", "type": "company", "context": "Test"}
                    ],
                    "timeline": [],
                    "key_metrics": {},
                    "sentiment": "neutral",
                    "main_theme": article["title"]
                }
                mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
                mock_chat.return_value = mock_llm

                insights = agent.extract_insights(article["text"])
                all_entities.extend(insights["entities"])

            # Should extract entities from all articles
            assert len(all_entities) >= len(sample_articles)
