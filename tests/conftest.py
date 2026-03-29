"""
Pytest Configuration and Fixtures
==================================

Shared fixtures and configuration for all tests.
"""

import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_article():
    """Sample ET article for testing"""
    return {
        "url": "https://economictimes.indiatimes.com/news/economy/policy/union-budget-2026",
        "title": "Union Budget 2026: Finance Minister announces tax reforms",
        "text": """The Finance Minister presented the Union Budget 2026 today, announcing major tax reforms.
        The personal income tax slabs have been revised, with the basic exemption limit raised to Rs 3.5 lakh.
        The corporate tax rate for new manufacturing companies has been reduced to 15%.
        Infrastructure spending has been allocated Rs 10 lakh crore, focusing on highways, railways, and ports.
        The fiscal deficit is targeted at 4.5% of GDP for FY 2026-27.""",
        "date": "2026-02-01",
        "category": "budget",
        "metadata": {
            "author": "ET Bureau",
            "word_count": 85
        }
    }

@pytest.fixture
def sample_articles():
    """Multiple sample articles for testing"""
    return [
        {
            "url": "https://economictimes.indiatimes.com/article1",
            "title": "Union Budget 2026: Tax reforms announced",
            "text": "The Finance Minister announced major tax reforms in Budget 2026. Personal tax exemption raised to Rs 3.5 lakh.",
            "date": "2026-02-01",
            "category": "budget"
        },
        {
            "url": "https://economictimes.indiatimes.com/article2",
            "title": "Q4 Results: Tech companies report strong growth",
            "text": "Major tech companies reported strong Q4 results with revenue growth of 25% YoY. Profit margins improved to 20%.",
            "date": "2026-01-15",
            "category": "results"
        },
        {
            "url": "https://economictimes.indiatimes.com/article3",
            "title": "RBI maintains repo rate at 6.5%",
            "text": "The Reserve Bank of India kept the repo rate unchanged at 6.5% citing inflation concerns. Inflation target set at 4%.",
            "date": "2026-02-08",
            "category": "policy"
        }
    ]

@pytest.fixture
def sample_insights():
    """Sample structured insights from Agent 1"""
    return {
        "entities": [
            {"name": "Finance Minister", "type": "person", "context": "Presented Union Budget 2026"},
            {"name": "Rs 3.5 lakh", "type": "metric", "context": "Basic tax exemption limit"},
            {"name": "15%", "type": "metric", "context": "Corporate tax rate for manufacturing"}
        ],
        "timeline": [
            {"date": "2026-02-01", "event": "Union Budget 2026 presented", "impact": "Major tax reforms announced"},
            {"date": "2026-02-01", "event": "Tax exemption raised", "impact": "Relief for middle class"}
        ],
        "key_metrics": {
            "tax_exemption": "Rs 3.5 lakh",
            "corporate_tax": "15%",
            "infrastructure_spending": "Rs 10 lakh crore",
            "fiscal_deficit": "4.5% of GDP"
        },
        "sentiment": "positive",
        "main_theme": "Tax reforms and infrastructure investment"
    }

@pytest.fixture
def sample_briefing():
    """Sample briefing output from Agent 3"""
    return {
        "summary": """The Union Budget 2026 introduces significant tax reforms with the personal exemption
        limit raised to Rs 3.5 lakh and corporate tax reduced to 15% for manufacturing. Infrastructure
        allocation stands at Rs 10 lakh crore, targeting highways, railways, and ports. The government
        aims for a fiscal deficit of 4.5% of GDP.""",
        "key_points": [
            "Personal tax exemption raised to Rs 3.5 lakh",
            "Corporate tax reduced to 15% for new manufacturing",
            "Infrastructure spending: Rs 10 lakh crore",
            "Fiscal deficit target: 4.5% of GDP",
            "Focus on highways, railways, and ports"
        ],
        "insights": {
            "contradictions": [],
            "consensus": [
                "Tax reforms to boost consumption",
                "Infrastructure focus on connectivity"
            ]
        },
        "questions": [
            "What will be the impact on government revenue?",
            "How will manufacturing companies benefit?",
            "What are the specific infrastructure projects?"
        ]
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_claude_client():
    """Mock Claude API client"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "entities": [],
        "timeline": [],
        "key_metrics": {},
        "sentiment": "neutral",
        "main_theme": "Test"
    })
    mock_client.invoke.return_value = mock_response
    return mock_client

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI TTS client"""
    mock_client = MagicMock()
    mock_audio = MagicMock()
    mock_audio.stream_to_file = MagicMock()
    mock_client.audio.speech.create.return_value = mock_audio
    return mock_client

@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB collection"""
    mock_collection = MagicMock()
    mock_collection.count.return_value = 10
    mock_collection.query.return_value = {
        "documents": [["Sample article text"]],
        "metadatas": [[{"url": "test.com", "title": "Test"}]],
        "distances": [[0.5]]
    }
    return mock_collection

@pytest.fixture
def mock_embedding_model():
    """Mock sentence-transformers model"""
    mock_model = MagicMock()
    import numpy as np
    mock_model.encode.return_value = np.random.rand(384)  # all-MiniLM-L6-v2 dimension
    return mock_model


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory structure"""
    data_dir = tmp_path / "data"
    (data_dir / "articles").mkdir(parents=True)
    (data_dir / "chroma_db").mkdir(parents=True)
    (data_dir / "audio").mkdir(parents=True)
    (data_dir / "cache").mkdir(parents=True)
    return data_dir

@pytest.fixture
def sample_articles_file(temp_data_dir, sample_articles):
    """Create sample articles.json file"""
    articles_file = temp_data_dir / "articles" / "articles.json"
    with open(articles_file, 'w') as f:
        json.dump(sample_articles, f, indent=2)
    return articles_file

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set mock environment variables"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")


# ============================================================================
# Test Markers
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for workflows"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers", "requires_api: Tests that require API credentials"
    )
    config.addinivalue_line(
        "markers", "requires_data: Tests that require sample data"
    )


# ============================================================================
# Helper Functions
# ============================================================================

@pytest.fixture
def assert_valid_json():
    """Helper to validate JSON structure"""
    def _validate(data: dict, required_keys: List[str]):
        assert isinstance(data, dict), "Data must be a dictionary"
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
    return _validate

@pytest.fixture
def assert_valid_insights():
    """Helper to validate Agent 1 insights structure"""
    def _validate(insights: dict):
        required_keys = ["entities", "timeline", "key_metrics", "sentiment", "main_theme"]
        assert all(key in insights for key in required_keys), "Missing required insights keys"
        assert isinstance(insights["entities"], list), "Entities must be a list"
        assert isinstance(insights["timeline"], list), "Timeline must be a list"
        assert isinstance(insights["key_metrics"], dict), "Key metrics must be a dict"
        assert insights["sentiment"] in ["positive", "negative", "neutral"], "Invalid sentiment"
    return _validate
