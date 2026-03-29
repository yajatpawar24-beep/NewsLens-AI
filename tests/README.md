# NewsLens AI Test Suite

Comprehensive testing infrastructure for the NewsLens AI system.

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── test_agent1.py        # Agent 1 (Source Intelligence) tests
├── test_agent2.py        # Agent 2 (Visual Intelligence) tests
├── test_agent3.py        # Agent 3 (Briefing Synthesis) tests
├── test_orchestrator.py  # LangGraph orchestrator tests
└── test_integration.py   # End-to-end integration tests
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_agent1.py
```

### Run specific test class:
```bash
pytest tests/test_agent1.py::TestSourceIntelligenceAgent
```

### Run specific test:
```bash
pytest tests/test_agent1.py::TestSourceIntelligenceAgent::test_agent_initialization
```

### Run by marker:
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip tests requiring API
pytest -m "not requires_api"
```

### Run with verbose output:
```bash
pytest -v
```

### Run with coverage:
```bash
pytest --cov=agents --cov=api --cov-report=html
```

## Test Markers

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for workflows
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.requires_api` - Tests requiring API credentials
- `@pytest.mark.requires_data` - Tests requiring sample data

## Test Fixtures

### Data Fixtures
- `sample_article` - Single ET article
- `sample_articles` - Multiple articles (3)
- `sample_insights` - Structured insights from Agent 1
- `sample_briefing` - Complete briefing output

### Mock Fixtures
- `mock_claude_client` - Mock Claude API client
- `mock_openai_client` - Mock OpenAI TTS client
- `mock_chroma_collection` - Mock ChromaDB collection
- `mock_embedding_model` - Mock sentence-transformers model

### Environment Fixtures
- `temp_data_dir` - Temporary data directory
- `sample_articles_file` - articles.json file
- `mock_env_vars` - Mock environment variables

## Test Coverage

### Agent 1 Tests (test_agent1.py)
- ✅ Initialization
- ✅ Entity extraction
- ✅ Timeline extraction
- ✅ Key metrics extraction
- ✅ Sentiment analysis
- ✅ Empty article handling
- ✅ Multi-article processing

### Agent 2 Tests (test_agent2.py)
- ✅ Initialization
- ✅ Visualization type detection
- ✅ Artifact code generation
- ✅ Fallback templates
- ✅ Responsive design
- ✅ Empty data handling
- ✅ Multiple visualizations

### Agent 3 Tests (test_agent3.py)
- ✅ Initialization
- ✅ Briefing structure
- ✅ Executive summary length
- ✅ Key points count (5)
- ✅ Follow-up questions (3)
- ✅ Cross-article insights
- ✅ Audio generation
- ✅ TTS parameters

### Orchestrator Tests (test_orchestrator.py)
- ✅ Initialization
- ✅ State definition
- ✅ Individual nodes (fetch, extract, visualize, synthesize, audio)
- ✅ Full pipeline execution
- ✅ Error handling
- ✅ State updates
- ✅ Performance (<10s target)

### Integration Tests (test_integration.py)
- ✅ End-to-end workflow
- ✅ Multi-article consolidation
- ✅ ChromaDB integration
- ✅ Article retrieval
- ✅ API endpoints
- ✅ Performance benchmarks

## Writing New Tests

### Unit Test Template:
```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestMyComponent:
    def test_functionality(self, mock_env_vars):
        """Test description"""
        with patch('module.dependency'):
            # Test code
            assert result == expected
```

### Integration Test Template:
```python
import pytest

@pytest.mark.integration
class TestMyIntegration:
    def test_workflow(self, sample_data):
        """Test description"""
        # Setup
        # Execute
        # Validate
        assert condition
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt pytest
      - run: pytest -m "not requires_api"
```

## Best Practices

1. **Mock external dependencies** - Use mocks for APIs, databases, file I/O
2. **Use fixtures** - Share common setup via conftest.py
3. **Test edge cases** - Empty data, errors, timeouts
4. **Fast unit tests** - Keep unit tests fast (<1s each)
5. **Separate integration tests** - Mark slow/integration tests
6. **Clear assertions** - Use descriptive assertion messages
7. **Independent tests** - Each test should run in isolation

## Troubleshooting

### ImportError: No module named 'agents'
```bash
# Add parent directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### API Key Errors
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export OPENAI_API_KEY=your_key
pytest -m "not requires_api"  # Skip API tests
```

### ChromaDB Errors
```bash
# Clear ChromaDB data
rm -rf data/chroma_db/*
python scripts/setup_db.py
```

## Test Metrics

Target metrics for the test suite:

- **Coverage**: >80% code coverage
- **Unit test speed**: <1s per test
- **Integration test speed**: <5s per test
- **Total suite time**: <2 minutes
- **Success rate**: 100% (excluding requires_api on CI)

---

Last Updated: March 24, 2026
