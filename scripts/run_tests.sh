#!/bin/bash
# NewsLens AI Test Runner
# Convenient script to run different test configurations

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  NewsLens AI Test Suite${NC}"
echo -e "${BLUE}================================================${NC}"
echo

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing...${NC}"
    pip install pytest pytest-cov pytest-mock pytest-asyncio
fi

# Parse command line arguments
TEST_TYPE=${1:-"all"}

case $TEST_TYPE in
    "unit")
        echo -e "${GREEN}Running unit tests only...${NC}"
        pytest -m unit -v
        ;;
    "integration")
        echo -e "${GREEN}Running integration tests only...${NC}"
        pytest -m integration -v
        ;;
    "fast")
        echo -e "${GREEN}Running fast tests (no slow, no API)...${NC}"
        pytest -m "not slow and not requires_api" -v
        ;;
    "agent1")
        echo -e "${GREEN}Running Agent 1 tests...${NC}"
        pytest tests/test_agent1.py -v
        ;;
    "agent2")
        echo -e "${GREEN}Running Agent 2 tests...${NC}"
        pytest tests/test_agent2.py -v
        ;;
    "agent3")
        echo -e "${GREEN}Running Agent 3 tests...${NC}"
        pytest tests/test_agent3.py -v
        ;;
    "orchestrator")
        echo -e "${GREEN}Running orchestrator tests...${NC}"
        pytest tests/test_orchestrator.py -v
        ;;
    "coverage")
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest --cov=agents --cov=api --cov=orchestrator \
               --cov-report=html --cov-report=term-missing \
               -m "not requires_api"
        echo -e "${GREEN}Coverage report generated at: htmlcov/index.html${NC}"
        ;;
    "ci")
        echo -e "${GREEN}Running CI tests (no API required)...${NC}"
        pytest -m "not requires_api" -v --tb=short
        ;;
    "all")
        echo -e "${GREEN}Running all tests...${NC}"
        pytest -v
        ;;
    "help")
        echo "Usage: ./run_tests.sh [TEST_TYPE]"
        echo
        echo "Test types:"
        echo "  all           - Run all tests (default)"
        echo "  unit          - Run only unit tests"
        echo "  integration   - Run only integration tests"
        echo "  fast          - Run fast tests (skip slow and API tests)"
        echo "  agent1        - Run Agent 1 tests only"
        echo "  agent2        - Run Agent 2 tests only"
        echo "  agent3        - Run Agent 3 tests only"
        echo "  orchestrator  - Run orchestrator tests only"
        echo "  coverage      - Run tests with coverage report"
        echo "  ci            - Run CI tests (no API required)"
        echo "  help          - Show this help message"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Unknown test type: $TEST_TYPE${NC}"
        echo "Run './run_tests.sh help' for usage"
        exit 1
        ;;
esac

echo
echo -e "${GREEN}✅ Tests completed!${NC}"
