"""
Integration Test Suite
=======================

End-to-end integration tests for the complete NewsLens AI system.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end workflow tests"""

    def test_complete_workflow(self, mock_env_vars, sample_articles, temp_data_dir):
        """Test complete workflow from URLs to briefing"""
        with patch('orchestrator.SourceIntelligenceAgent') as mock_agent1, \
             patch('orchestrator.VisualIntelligenceAgent') as mock_agent2, \
             patch('orchestrator.BriefingSynthesisAgent') as mock_agent3, \
             patch('orchestrator.requests.get'):
            # Setup complete mock pipeline
            mock_agent1.return_value.extract_insights.return_value = {
                "entities": [{"name": "Test Co", "type": "company", "context": "Tech"}],
                "timeline": [{"date": "2026-01-01", "event": "Launch", "impact": "High"}],
                "key_metrics": {"revenue": "$100M"},
                "sentiment": "positive",
                "main_theme": "Growth"
            }

            mock_agent2.return_value.detect_visualization_type.return_value = "timeline"
            mock_agent2.return_value.generate_artifact_code.return_value = """
            <div className="w-full h-96">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <Line type="monotone" dataKey="value" stroke="#8884d8" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            """

            mock_agent3.return_value.synthesize_briefing.return_value = {
                "summary": "This is a comprehensive briefing about market trends...",
                "key_points": [
                    "Point 1: Major growth observed",
                    "Point 2: New markets emerging",
                    "Point 3: Technology advancement",
                    "Point 4: Investment opportunities",
                    "Point 5: Future outlook positive"
                ],
                "insights": {
                    "contradictions": ["Some data conflicts"],
                    "consensus": ["All agree on growth"]
                },
                "questions": [
                    "What drives the growth?",
                    "How sustainable is this trend?",
                    "What are the risks?"
                ]
            }

            audio_path = str(temp_data_dir / "audio" / "briefing.mp3")
            mock_agent3.return_value.generate_audio_briefing.return_value = audio_path

            from orchestrator import NewsLensOrchestrator
            orchestrator = NewsLensOrchestrator()

            # Execute pipeline
            result = orchestrator.process([a['url'] for a in sample_articles[:3]])

            # Validate complete output
            assert result['status'] == 'completed'
            assert 'briefing' in result
            assert 'visualizations' in result
            assert 'audio_path' in result

            # Validate briefing content
            briefing = result['briefing']
            assert len(briefing['summary']) > 50
            assert len(briefing['key_points']) == 5
            assert len(briefing['questions']) == 3

            # Validate visualizations
            assert len(result['visualizations']) > 0
            assert all(isinstance(v, str) for v in result['visualizations'])

    def test_multi_article_consolidation(self, mock_env_vars, sample_articles):
        """Test consolidation of multiple articles"""
        with patch('orchestrator.SourceIntelligenceAgent') as mock_agent1, \
             patch('orchestrator.VisualIntelligenceAgent') as mock_agent2, \
             patch('orchestrator.BriefingSynthesisAgent') as mock_agent3, \
             patch('orchestrator.requests.get'):
            # Setup mocks
            mock_agent1.return_value.extract_insights.return_value = {
                "entities": [], "timeline": [], "key_metrics": {},
                "sentiment": "neutral", "main_theme": "Test"
            }
            mock_agent2.return_value.detect_visualization_type.return_value = "comparison"
            mock_agent2.return_value.generate_artifact_code.return_value = "<div>Chart</div>"
            mock_agent3.return_value.synthesize_briefing.return_value = {
                "summary": "Multi-article summary",
                "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {
                    "contradictions": ["Article A vs B"],
                    "consensus": ["All agree on X"]
                },
                "questions": ["Q1?", "Q2?", "Q3?"]
            }
            mock_agent3.return_value.generate_audio_briefing.return_value = "/tmp/audio.mp3"

            from orchestrator import NewsLensOrchestrator
            orchestrator = NewsLensOrchestrator()

            # Process multiple articles
            result = orchestrator.process([a['url'] for a in sample_articles])

            # Should consolidate all articles
            assert result['status'] == 'completed'
            assert 'insights' in result['briefing']
            assert 'consensus' in result['briefing']['insights']


@pytest.mark.integration
class TestDataPipeline:
    """Integration tests for data pipeline"""

    def test_chromadb_integration(self, temp_data_dir, sample_articles_file):
        """Test ChromaDB integration"""
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            import numpy as np
            mock_model.return_value.encode.return_value = np.random.rand(10, 384)

            from scripts.setup_db import ChromaDBSetup

            setup = ChromaDBSetup(
                persist_directory=str(temp_data_dir / "chroma_db"),
                collection_name="test_articles"
            )

            setup.create_collection(reset=True)
            articles = setup.load_articles(str(sample_articles_file))

            if articles:
                setup.index_articles(articles)
                stats = setup.get_stats()

                assert stats['count'] == len(articles)

    def test_article_retrieval(self, temp_data_dir, sample_articles_file):
        """Test article retrieval from ChromaDB"""
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            import numpy as np
            mock_model.return_value.encode.return_value = np.random.rand(10, 384)

            from scripts.setup_db import ChromaDBSetup
            import chromadb

            setup = ChromaDBSetup(
                persist_directory=str(temp_data_dir / "chroma_db"),
                collection_name="test_articles"
            )

            setup.create_collection(reset=True)
            articles = setup.load_articles(str(sample_articles_file))

            if articles:
                setup.index_articles(articles)

                # Test retrieval
                query_embedding = np.random.rand(384)
                results = setup.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=3
                )

                assert 'documents' in results
                assert len(results['documents'][0]) <= 3


@pytest.mark.integration
class TestAPIEndpoints:
    """Integration tests for FastAPI endpoints"""

    def test_generate_endpoint(self, mock_env_vars):
        """Test /api/generate endpoint"""
        with patch('api.main.NewsLensOrchestrator') as mock_orch:
            # Mock orchestrator
            mock_orch_inst = MagicMock()
            mock_orch_inst.process.return_value = {
                'status': 'completed',
                'briefing': {
                    'summary': 'Test summary',
                    'key_points': ['P1', 'P2', 'P3', 'P4', 'P5'],
                    'insights': {},
                    'questions': ['Q1?', 'Q2?', 'Q3?']
                },
                'visualizations': ['<div>Viz1</div>'],
                'audio_path': '/tmp/audio.mp3'
            }
            mock_orch.return_value = mock_orch_inst

            from fastapi.testclient import TestClient
            from api.main import app

            client = TestClient(app)

            response = client.post(
                "/api/generate",
                json={"article_urls": ["https://test.com/article1"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert 'summary' in data
            assert 'key_points' in data


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Performance integration tests"""

    def test_10_second_target(self, mock_env_vars, sample_articles):
        """Test that pipeline completes in < 10 seconds"""
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
                "summary": "Summary", "key_points": ["P"] * 5,
                "insights": {}, "questions": ["Q?"] * 3
            }
            mock_agent3.return_value.generate_audio_briefing.return_value = "/tmp/audio.mp3"

            from orchestrator import NewsLensOrchestrator
            orchestrator = NewsLensOrchestrator()

            start = time.time()
            result = orchestrator.process([sample_articles[0]['url']])
            duration = time.time() - start

            # Target: < 10 seconds end-to-end
            assert duration < 10.0, f"Too slow: {duration:.2f}s (target: <10s)"
            assert result['status'] == 'completed'
