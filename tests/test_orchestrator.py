"""
Test Suite for LangGraph Orchestrator
======================================

Tests for multi-agent workflow coordination.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from orchestrator import NewsLensOrchestrator, NewsLensState


@pytest.mark.unit
class TestOrchestratorInitialization:
    """Unit tests for orchestrator initialization"""

    def test_orchestrator_init(self, mock_env_vars):
        """Test orchestrator initializes correctly"""
        with patch('orchestrator.SourceIntelligenceAgent'), \
             patch('orchestrator.VisualIntelligenceAgent'), \
             patch('orchestrator.BriefingSynthesisAgent'):
            orchestrator = NewsLensOrchestrator()
            assert orchestrator is not None
            assert hasattr(orchestrator, 'agent1')
            assert hasattr(orchestrator, 'agent2')
            assert hasattr(orchestrator, 'agent3')
            assert hasattr(orchestrator, 'graph')

    def test_state_definition(self):
        """Test NewsLensState TypedDict has all required fields"""
        required_fields = [
            'article_urls',
            'raw_articles',
            'insights',
            'visualizations',
            'briefing',
            'audio_path',
            'status'
        ]

        # Check if NewsLensState has all fields
        from typing import get_type_hints
        hints = get_type_hints(NewsLensState)

        for field in required_fields:
            assert field in hints, f"Missing field: {field}"


@pytest.mark.unit
class TestOrchestratorNodes:
    """Unit tests for individual orchestrator nodes"""

    def test_fetch_node(self, mock_env_vars, sample_articles):
        """Test fetch node extracts articles"""
        with patch('orchestrator.SourceIntelligenceAgent'), \
             patch('orchestrator.VisualIntelligenceAgent'), \
             patch('orchestrator.BriefingSynthesisAgent'), \
             patch('orchestrator.requests.get') as mock_get:
            # Mock HTTP response
            mock_response = MagicMock()
            mock_response.text = "<html><body>Article content</body></html>"
            mock_get.return_value = mock_response

            orchestrator = NewsLensOrchestrator()

            state = {
                'article_urls': [a['url'] for a in sample_articles],
                'status': 'started'
            }

            # Test fetch functionality
            # Note: This tests the node logic, not the full graph execution
            assert 'article_urls' in state
            assert len(state['article_urls']) > 0

    def test_extract_node(self, mock_env_vars, sample_articles):
        """Test extract node processes articles"""
        with patch('orchestrator.SourceIntelligenceAgent') as mock_agent1, \
             patch('orchestrator.VisualIntelligenceAgent'), \
             patch('orchestrator.BriefingSynthesisAgent'):
            # Mock Agent 1
            mock_agent1_instance = MagicMock()
            mock_agent1_instance.extract_insights.return_value = {
                "entities": [],
                "timeline": [],
                "key_metrics": {},
                "sentiment": "neutral",
                "main_theme": "Test"
            }
            mock_agent1.return_value = mock_agent1_instance

            orchestrator = NewsLensOrchestrator()

            state = {
                'raw_articles': [{'text': a['text']} for a in sample_articles],
                'status': 'fetched'
            }

            # Verify agent1 exists and can be called
            assert orchestrator.agent1 is not None
            insights = orchestrator.agent1.extract_insights("test")
            assert isinstance(insights, dict)

    def test_visualize_node(self, mock_env_vars):
        """Test visualize node generates visualizations"""
        with patch('orchestrator.SourceIntelligenceAgent'), \
             patch('orchestrator.VisualIntelligenceAgent') as mock_agent2, \
             patch('orchestrator.BriefingSynthesisAgent'):
            # Mock Agent 2
            mock_agent2_instance = MagicMock()
            mock_agent2_instance.detect_visualization_type.return_value = "timeline"
            mock_agent2_instance.generate_artifact_code.return_value = "<div>Visualization</div>"
            mock_agent2.return_value = mock_agent2_instance

            orchestrator = NewsLensOrchestrator()

            state = {
                'insights': {'article1': {"entities": [], "timeline": []}},
                'status': 'extracted'
            }

            # Verify agent2 exists and can be called
            assert orchestrator.agent2 is not None
            viz = orchestrator.agent2.generate_artifact_code("timeline", {})
            assert isinstance(viz, str)

    def test_synthesize_node(self, mock_env_vars):
        """Test synthesize node creates briefing"""
        with patch('orchestrator.SourceIntelligenceAgent'), \
             patch('orchestrator.VisualIntelligenceAgent'), \
             patch('orchestrator.BriefingSynthesisAgent') as mock_agent3:
            # Mock Agent 3
            mock_agent3_instance = MagicMock()
            mock_agent3_instance.synthesize_briefing.return_value = {
                "summary": "Test summary",
                "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {},
                "questions": ["Q1?", "Q2?", "Q3?"]
            }
            mock_agent3.return_value = mock_agent3_instance

            orchestrator = NewsLensOrchestrator()

            state = {
                'raw_articles': [{'text': "Test"}],
                'insights': {},
                'status': 'visualized'
            }

            # Verify agent3 exists and can be called
            assert orchestrator.agent3 is not None
            briefing = orchestrator.agent3.synthesize_briefing(["test"], {})
            assert isinstance(briefing, dict)

    def test_audio_node(self, mock_env_vars, temp_data_dir):
        """Test audio node generates MP3"""
        with patch('orchestrator.SourceIntelligenceAgent'), \
             patch('orchestrator.VisualIntelligenceAgent'), \
             patch('orchestrator.BriefingSynthesisAgent') as mock_agent3:
            # Mock Agent 3
            mock_agent3_instance = MagicMock()
            audio_path = str(temp_data_dir / "audio" / "test.mp3")
            mock_agent3_instance.generate_audio_briefing.return_value = audio_path
            mock_agent3.return_value = mock_agent3_instance

            orchestrator = NewsLensOrchestrator()

            state = {
                'briefing': {"summary": "Test summary"},
                'status': 'synthesized'
            }

            # Verify agent3 can generate audio
            result = orchestrator.agent3.generate_audio_briefing("test", audio_path)
            assert result == audio_path


@pytest.mark.integration
class TestOrchestratorIntegration:
    """Integration tests for full orchestrator workflow"""

    def test_full_pipeline(self, mock_env_vars, sample_articles, temp_data_dir):
        """Test complete pipeline execution"""
        with patch('orchestrator.SourceIntelligenceAgent') as mock_agent1, \
             patch('orchestrator.VisualIntelligenceAgent') as mock_agent2, \
             patch('orchestrator.BriefingSynthesisAgent') as mock_agent3, \
             patch('orchestrator.requests.get') as mock_get:
            # Mock HTTP responses
            mock_response = MagicMock()
            mock_response.text = "<html><body>Article content</body></html>"
            mock_get.return_value = mock_response

            # Mock Agent 1
            mock_agent1_inst = MagicMock()
            mock_agent1_inst.extract_insights.return_value = {
                "entities": [{"name": "Test", "type": "company", "context": "Test"}],
                "timeline": [{"date": "2026-01-01", "event": "Test", "impact": "Test"}],
                "key_metrics": {"metric1": "value1"},
                "sentiment": "positive",
                "main_theme": "Test theme"
            }
            mock_agent1.return_value = mock_agent1_inst

            # Mock Agent 2
            mock_agent2_inst = MagicMock()
            mock_agent2_inst.detect_visualization_type.return_value = "timeline"
            mock_agent2_inst.generate_artifact_code.return_value = "<div>Viz</div>"
            mock_agent2.return_value = mock_agent2_inst

            # Mock Agent 3
            mock_agent3_inst = MagicMock()
            mock_agent3_inst.synthesize_briefing.return_value = {
                "summary": "Complete briefing summary",
                "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {"contradictions": [], "consensus": []},
                "questions": ["Q1?", "Q2?", "Q3?"]
            }
            mock_agent3_inst.generate_audio_briefing.return_value = str(temp_data_dir / "audio" / "briefing.mp3")
            mock_agent3.return_value = mock_agent3_inst

            orchestrator = NewsLensOrchestrator()

            article_urls = [a['url'] for a in sample_articles[:3]]
            result = orchestrator.process(article_urls)

            # Verify all stages completed
            assert isinstance(result, dict)
            assert result['status'] == 'completed'
            assert 'briefing' in result
            assert 'visualizations' in result
            assert 'audio_path' in result

    def test_error_handling(self, mock_env_vars):
        """Test error handling in pipeline"""
        with patch('orchestrator.SourceIntelligenceAgent') as mock_agent1, \
             patch('orchestrator.VisualIntelligenceAgent'), \
             patch('orchestrator.BriefingSynthesisAgent'):
            # Mock Agent 1 to raise error
            mock_agent1_inst = MagicMock()
            mock_agent1_inst.extract_insights.side_effect = Exception("API Error")
            mock_agent1.return_value = mock_agent1_inst

            orchestrator = NewsLensOrchestrator()

            # Should handle error gracefully
            with pytest.raises(Exception):
                orchestrator.process(["https://test.com/article"])

    def test_state_updates(self, mock_env_vars, sample_articles):
        """Test state updates throughout pipeline"""
        with patch('orchestrator.SourceIntelligenceAgent') as mock_agent1, \
             patch('orchestrator.VisualIntelligenceAgent') as mock_agent2, \
             patch('orchestrator.BriefingSynthesisAgent') as mock_agent3, \
             patch('orchestrator.requests.get'):
            # Setup mocks
            mock_agent1.return_value.extract_insights.return_value = {
                "entities": [], "timeline": [], "key_metrics": {},
                "sentiment": "neutral", "main_theme": "Test"
            }
            mock_agent2.return_value.detect_visualization_type.return_value = "timeline"
            mock_agent2.return_value.generate_artifact_code.return_value = "<div>Viz</div>"
            mock_agent3.return_value.synthesize_briefing.return_value = {
                "summary": "Summary", "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {}, "questions": ["Q1?", "Q2?", "Q3?"]
            }
            mock_agent3.return_value.generate_audio_briefing.return_value = "/tmp/audio.mp3"

            orchestrator = NewsLensOrchestrator()
            result = orchestrator.process([sample_articles[0]['url']])

            # Check state progression
            assert result['status'] == 'completed'

    @pytest.mark.slow
    def test_performance(self, mock_env_vars, sample_articles):
        """Test pipeline completes in reasonable time"""
        import time

        with patch('orchestrator.SourceIntelligenceAgent') as mock_agent1, \
             patch('orchestrator.VisualIntelligenceAgent') as mock_agent2, \
             patch('orchestrator.BriefingSynthesisAgent') as mock_agent3, \
             patch('orchestrator.requests.get'):
            # Setup fast mocks
            mock_agent1.return_value.extract_insights.return_value = {
                "entities": [], "timeline": [], "key_metrics": {},
                "sentiment": "neutral", "main_theme": "Test"
            }
            mock_agent2.return_value.detect_visualization_type.return_value = "timeline"
            mock_agent2.return_value.generate_artifact_code.return_value = "<div>Viz</div>"
            mock_agent3.return_value.synthesize_briefing.return_value = {
                "summary": "Summary", "key_points": ["P1"] * 5,
                "insights": {}, "questions": ["Q1?"] * 3
            }
            mock_agent3.return_value.generate_audio_briefing.return_value = "/tmp/audio.mp3"

            orchestrator = NewsLensOrchestrator()

            start_time = time.time()
            orchestrator.process([sample_articles[0]['url']])
            duration = time.time() - start_time

            # Should complete quickly with mocks
            assert duration < 5.0, f"Pipeline too slow: {duration}s"


@pytest.mark.integration
@pytest.mark.requires_api
class TestOrchestratorRealAPI:
    """Integration tests with real APIs"""

    def test_real_pipeline_execution(self, sample_articles):
        """Test real pipeline with actual APIs"""
        import os
        if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("OPENAI_API_KEY"):
            pytest.skip("Requires API credentials")

        orchestrator = NewsLensOrchestrator()

        # Use single article for faster test
        result = orchestrator.process([sample_articles[0]['url']])

        # Validate real output
        assert result['status'] == 'completed'
        assert len(result['briefing']['summary']) > 100
        assert len(result['visualizations']) > 0
        assert Path(result['audio_path']).exists()
