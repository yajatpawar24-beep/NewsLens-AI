"""
Test Suite for Agent 3: Briefing Synthesis Agent
=================================================

Tests for multi-article briefing creation and audio generation.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from agents.agent3 import BriefingSynthesisAgent


@pytest.mark.unit
class TestBriefingSynthesisAgent:
    """Unit tests for Briefing Synthesis Agent"""

    def test_agent_initialization(self, mock_env_vars):
        """Test agent initializes correctly"""
        with patch('agents.agent3.ChatAnthropic'), \
             patch('agents.agent3.OpenAI'):
            agent = BriefingSynthesisAgent()
            assert agent is not None
            assert hasattr(agent, 'llm')
            assert hasattr(agent, 'tts_client')

    def test_synthesize_briefing_structure(self, sample_articles, sample_insights, mock_env_vars):
        """Test briefing output structure"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI'):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": "Test summary",
                "key_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
                "insights": {
                    "contradictions": [],
                    "consensus": ["Consensus 1"]
                },
                "questions": ["Question 1?", "Question 2?", "Question 3?"]
            })
            mock_chat.return_value = mock_llm

            agent = BriefingSynthesisAgent()
            article_texts = [a["text"] for a in sample_articles]
            insights = {"article1": sample_insights, "article2": sample_insights}

            briefing = agent.synthesize_briefing(article_texts, insights)

            # Validate structure
            assert isinstance(briefing, dict)
            assert "summary" in briefing
            assert "key_points" in briefing
            assert "insights" in briefing
            assert "questions" in briefing

    def test_executive_summary_length(self, sample_articles, sample_insights, mock_env_vars):
        """Test executive summary is appropriate length (300-400 words)"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI'):
            mock_llm = MagicMock()
            summary = " ".join(["word"] * 350)  # 350 words
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": summary,
                "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {"contradictions": [], "consensus": []},
                "questions": ["Q1?", "Q2?", "Q3?"]
            })
            mock_chat.return_value = mock_llm

            agent = BriefingSynthesisAgent()
            briefing = agent.synthesize_briefing([sample_articles[0]["text"]], {})

            # Check summary exists and has content
            assert len(briefing["summary"]) > 0
            word_count = len(briefing["summary"].split())
            assert word_count > 50, "Summary too short"

    def test_key_points_count(self, sample_articles, mock_env_vars):
        """Test exactly 5 key points are generated"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI'):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": "Summary",
                "key_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
                "insights": {"contradictions": [], "consensus": []},
                "questions": ["Q1?", "Q2?", "Q3?"]
            })
            mock_chat.return_value = mock_llm

            agent = BriefingSynthesisAgent()
            briefing = agent.synthesize_briefing([sample_articles[0]["text"]], {})

            assert len(briefing["key_points"]) == 5

    def test_follow_up_questions_count(self, sample_articles, mock_env_vars):
        """Test exactly 3 follow-up questions are generated"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI'):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": "Summary",
                "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {"contradictions": [], "consensus": []},
                "questions": ["Question 1?", "Question 2?", "Question 3?"]
            })
            mock_chat.return_value = mock_llm

            agent = BriefingSynthesisAgent()
            briefing = agent.synthesize_briefing([sample_articles[0]["text"]], {})

            assert len(briefing["questions"]) == 3

    def test_cross_article_insights(self, sample_articles, mock_env_vars):
        """Test cross-article analysis identifies contradictions and consensus"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI'):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": "Summary",
                "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {
                    "contradictions": ["Article A says X, Article B says Y"],
                    "consensus": ["All articles agree on Z"]
                },
                "questions": ["Q1?", "Q2?", "Q3?"]
            })
            mock_chat.return_value = mock_llm

            agent = BriefingSynthesisAgent()
            article_texts = [a["text"] for a in sample_articles]
            briefing = agent.synthesize_briefing(article_texts, {})

            assert "insights" in briefing
            assert "contradictions" in briefing["insights"]
            assert "consensus" in briefing["insights"]

    def test_generate_audio_briefing(self, sample_briefing, temp_data_dir, mock_env_vars):
        """Test audio generation"""
        with patch('agents.agent3.ChatAnthropic'), \
             patch('agents.agent3.OpenAI') as mock_openai:
            # Mock TTS client
            mock_tts = MagicMock()
            mock_response = MagicMock()
            mock_response.stream_to_file = MagicMock()
            mock_tts.audio.speech.create.return_value = mock_response
            mock_openai.return_value = mock_tts

            agent = BriefingSynthesisAgent()

            briefing_text = sample_briefing["summary"]
            output_path = str(temp_data_dir / "audio" / "test.mp3")

            audio_path = agent.generate_audio_briefing(briefing_text, output_path)

            # Verify TTS was called
            assert mock_tts.audio.speech.create.called
            assert audio_path == output_path

    def test_audio_generation_parameters(self, mock_env_vars, temp_data_dir):
        """Test audio generation uses correct parameters"""
        with patch('agents.agent3.ChatAnthropic'), \
             patch('agents.agent3.OpenAI') as mock_openai:
            mock_tts = MagicMock()
            mock_response = MagicMock()
            mock_response.stream_to_file = MagicMock()
            mock_tts.audio.speech.create.return_value = mock_response
            mock_openai.return_value = mock_tts

            agent = BriefingSynthesisAgent()
            output_path = str(temp_data_dir / "audio" / "test.mp3")

            agent.generate_audio_briefing("Test text", output_path)

            # Check call parameters
            call_args = mock_tts.audio.speech.create.call_args
            assert call_args is not None
            assert call_args.kwargs.get("model") == "tts-1"
            assert call_args.kwargs.get("voice") == "onyx"

    def test_empty_articles_handling(self, mock_env_vars):
        """Test handling of empty article list"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI'):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": "No articles provided",
                "key_points": ["No data" for _ in range(5)],
                "insights": {"contradictions": [], "consensus": []},
                "questions": ["" for _ in range(3)]
            })
            mock_chat.return_value = mock_llm

            agent = BriefingSynthesisAgent()
            briefing = agent.synthesize_briefing([], {})

            assert isinstance(briefing, dict)
            assert "summary" in briefing

    @pytest.mark.requires_api
    def test_real_audio_generation(self, sample_briefing, temp_data_dir):
        """Test real audio generation with OpenAI TTS"""
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("Requires OpenAI API key")

        agent = BriefingSynthesisAgent()
        output_path = str(temp_data_dir / "audio" / "real_test.mp3")

        audio_path = agent.generate_audio_briefing(sample_briefing["summary"], output_path)

        # Verify file was created
        assert Path(audio_path).exists()
        assert Path(audio_path).stat().st_size > 0


@pytest.mark.integration
class TestAgent3Integration:
    """Integration tests for Agent 3"""

    def test_full_briefing_pipeline(self, sample_articles, sample_insights, temp_data_dir, mock_env_vars):
        """Test complete briefing generation pipeline"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI') as mock_openai:
            # Mock LLM
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": "Complete briefing summary",
                "key_points": [f"Point {i}" for i in range(1, 6)],
                "insights": {
                    "contradictions": ["Contradiction 1"],
                    "consensus": ["Consensus 1", "Consensus 2"]
                },
                "questions": [f"Question {i}?" for i in range(1, 4)]
            })
            mock_chat.return_value = mock_llm

            # Mock TTS
            mock_tts = MagicMock()
            mock_response = MagicMock()
            mock_response.stream_to_file = MagicMock()
            mock_tts.audio.speech.create.return_value = mock_response
            mock_openai.return_value = mock_tts

            agent = BriefingSynthesisAgent()

            # Generate briefing
            article_texts = [a["text"] for a in sample_articles]
            briefing = agent.synthesize_briefing(article_texts, {"article1": sample_insights})

            # Generate audio
            audio_path = str(temp_data_dir / "audio" / "briefing.mp3")
            audio_file = agent.generate_audio_briefing(briefing["summary"], audio_path)

            # Validate complete output
            assert isinstance(briefing, dict)
            assert all(key in briefing for key in ["summary", "key_points", "insights", "questions"])
            assert audio_file == audio_path

    def test_multi_article_consensus_detection(self, mock_env_vars):
        """Test consensus detection across multiple articles"""
        with patch('agents.agent3.ChatAnthropic') as mock_chat, \
             patch('agents.agent3.OpenAI'):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = json.dumps({
                "summary": "All articles agree on economic growth",
                "key_points": ["P1", "P2", "P3", "P4", "P5"],
                "insights": {
                    "contradictions": [],
                    "consensus": [
                        "All articles report positive GDP growth",
                        "Inflation remains under control"
                    ]
                },
                "questions": ["Q1?", "Q2?", "Q3?"]
            })
            mock_chat.return_value = mock_llm

            agent = BriefingSynthesisAgent()

            articles = [
                "GDP grows by 7% this quarter",
                "Economic indicators show 7% growth",
                "Analysts confirm 7% GDP expansion"
            ]

            briefing = agent.synthesize_briefing(articles, {})

            assert len(briefing["insights"]["consensus"]) > 0
