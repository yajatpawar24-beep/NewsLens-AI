#!/bin/bash

# NewsLens AI - Repository Preparation Script
# Cleans up repository for GitHub submission

echo "======================================"
echo "NewsLens AI - Submission Preparation"
echo "======================================"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

echo "Step 1: Removing temporary and cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.DS_Store" -delete
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

echo "Step 2: Removing test and development files..."
rm -f test_everything.py
rm -f test_api.html
rm -f SESSION_SUMMARY.md
rm -f STATUS.md
rm -f CURRENT_STATUS_MAR29.md
rm -f TESTING.md

echo "Step 3: Cleaning frontend build artifacts..."
if [ -d "frontend/node_modules" ]; then
    echo "  - Removing node_modules (will need npm install later)"
    rm -rf frontend/node_modules
fi
rm -rf frontend/dist
rm -rf frontend/.vite

echo "Step 4: Creating placeholder directories..."
mkdir -p data/audio
mkdir -p data/briefings
mkdir -p data/chroma_db
touch data/audio/.gitkeep
touch data/briefings/.gitkeep
touch data/chroma_db/.gitkeep

echo "Step 5: Verifying essential files exist..."
essential_files=(
    "README.md"
    "CLAUDE.md"
    "ARCHITECTURE.md"
    "IMPACT_MODEL.md"
    "PITCH_VIDEO_SCRIPT.md"
    "SUBMISSION_CHECKLIST.md"
    "requirements.txt"
    ".env.example"
    ".gitignore"
    "orchestrator.py"
    "agents/agent1.py"
    "agents/agent2.py"
    "agents/agent3.py"
    "api/main.py"
    "frontend/package.json"
    "frontend/src/App.tsx"
)

missing_files=()
for file in "${essential_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "  ✅ All essential files present"
else
    echo "  ⚠️  Missing files:"
    for file in "${missing_files[@]}"; do
        echo "     - $file"
    done
fi

echo ""
echo "Step 6: Checking for sensitive data..."
if grep -r "AWS_ACCESS_KEY_ID=AK" . --exclude-dir=venv --exclude-dir=.git --exclude-dir=node_modules 2>/dev/null; then
    echo "  ⚠️  WARNING: Found potential API keys in files!"
    echo "  Please review and remove before committing."
else
    echo "  ✅ No obvious API keys found"
fi

echo ""
echo "Step 7: Repository statistics..."
echo "  - Python files: $(find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" | wc -l | tr -d ' ')"
echo "  - TypeScript files: $(find frontend/src -name "*.tsx" -o -name "*.ts" 2>/dev/null | wc -l | tr -d ' ')"
echo "  - Total lines (Python): $(find . -name "*.py" -not -path "*/venv/*" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')"
echo "  - Total lines (TypeScript): $(find frontend/src -name "*.tsx" -o -name "*.ts" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')"

echo ""
echo "Step 8: Creating example output..."
if [ ! -f "examples/example_briefing.json" ]; then
    mkdir -p examples
    cat > examples/example_briefing.json << 'EOF'
{
  "summary": "This is an example briefing output. In a real scenario, this would contain a 400-500 word executive summary synthesized from multiple Economic Times articles.",
  "key_points": [
    "First key insight from the articles",
    "Second important finding",
    "Third major development",
    "Fourth strategic implication",
    "Fifth market impact",
    "Sixth competitive analysis",
    "Seventh financial metric",
    "Eighth operational change",
    "Ninth regulatory update",
    "Tenth future outlook"
  ],
  "insights": {
    "contradictions": [
      "Article A reports X, but Article B states Y"
    ],
    "consensus": [
      "All sources agree on this major point"
    ]
  },
  "questions": [
    "What are the strategic implications?",
    "How will this affect market dynamics?",
    "What is the competitive response?",
    "What are the execution risks?",
    "How does this impact stakeholders?",
    "What are the regulatory considerations?",
    "What is the timeline for implementation?",
    "What are the financial projections?"
  ],
  "entity_graph": {
    "entities": [
      {"name": "Company A", "type": "company", "context": "Leading player in the market"},
      {"name": "CEO Name", "type": "person", "context": "Chief Executive Officer"},
      {"name": "Policy X", "type": "policy", "context": "New regulatory framework"}
    ],
    "relationships": [
      {"source": "Company A", "target": "CEO Name", "type": "leads", "strength": 0.9},
      {"source": "Policy X", "target": "Company A", "type": "regulates", "strength": 0.7}
    ]
  },
  "visualizations": [],
  "audio_url": "http://localhost:8000/api/audio/example.mp3",
  "session_id": "example-session-123"
}
EOF
    echo "  ✅ Created example_briefing.json"
else
    echo "  ✅ Example file already exists"
fi

echo ""
echo "======================================"
echo "Preparation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review the SUBMISSION_CHECKLIST.md"
echo "2. Test the application one final time:"
echo "   - cd api && uvicorn main:app --reload"
echo "   - cd frontend && npm install && npm run dev"
echo "3. Record your pitch video using PITCH_VIDEO_SCRIPT.md"
echo "4. Initialize git (if not already done):"
echo "   git init"
echo "   git add ."
echo "   git commit -m \"Initial submission for ET AI Hackathon 2026\""
echo "5. Create GitHub repository and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/NewsLens-AI.git"
echo "   git push -u origin main"
echo ""
echo "Good luck with your submission! 🚀"
echo ""
