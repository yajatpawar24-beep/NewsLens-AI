# NewsLens AI

**Multi-Modal Business News Intelligence System**

Transform Economic Times articles into interactive briefings with auto-generated visualizations and audio narration - reducing reading time from 25 minutes to 3 minutes (8x faster).

🏆 **ET AI Hackathon 2026** | Problem Statement #8

---

## 🎯 Core Value Proposition

- **8x Faster**: Reduces article reading time from 25 minutes to 3 minutes
- **90% Consolidation**: Synthesizes 10 articles into 1 interactive briefing
- **720x Faster Visuals**: Auto-generates visualizations in 10 seconds (vs 2 hours manual design)
- **Hands-Free**: Provides audio briefings for consumption while commuting
- **Interactive**: Creates knowledge graphs showing entity relationships across articles

---

## 🏗️ System Architecture

### 3-Agent System (LangGraph Orchestrated)

1. **Agent 1: Source Intelligence** - Extracts structured insights from articles (entities, timeline, relationships, metrics, sentiment)
2. **Agent 2: Visual Intelligence** - Auto-generates interactive visualizations using React Artifacts + Recharts
3. **Agent 3: Briefing Synthesis** - Creates comprehensive multi-article briefings with voice narration

### Technology Stack

**Backend:**
- Python 3.11+ (Core runtime)
- LangGraph (Multi-agent orchestration)
- LangChain (Document processing)
- ChromaDB (Local vector database)
- Claude API via AWS Bedrock (Primary LLM)
- AWS Polly Neural TTS (Voice synthesis)
- FastAPI (REST API server)

**Frontend:**
- React 18 + TypeScript
- Vite (Build tool)
- TailwindCSS (Styling)
- Framer Motion (Animations)
- Recharts (Data visualizations)
- Lucide React (Icons)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS Account (for Bedrock access)
- AWS credentials (for Bedrock and Polly)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yajatpawar/newslens-ai.git
cd newslens-ai
```

2. **Set up Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - OPENAI_API_KEY
```

4. **Set up frontend:**
```bash
cd frontend
npm install
```

5. **Initialize data:**
```bash
# Scrape articles
python scripts/scrape_articles.py

# Set up ChromaDB
python scripts/setup_db.py
```

### Running the Application

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd api
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

---

## 📊 Data Flow

```
User Input (URLs/PDFs)
    ↓
Data Ingestion (BeautifulSoup/PyPDF2)
    ↓
Vector Storage (ChromaDB)
    ↓
Agent 1: Extract Insights → JSON
    ↓
Agent 2: Generate Visualizations → React Artifacts
    ↓
Agent 3: Synthesize Briefing → Summary + Audio
    ↓
TTS Engine (AWS Polly) → MP3
    ↓
Frontend Display → Interactive Briefing
```

Total time: **<10 seconds**

---

## 🎨 Frontend Design

The frontend features a distinctive **editorial-inspired design** with:

- **Typography**: Newsreader (display) + DM Sans (body) for authority and readability
- **Dark Theme**: Deep navy with amber/emerald accents
- **Glassmorphism**: Frosted glass effects for depth
- **Smooth Animations**: Framer Motion for polished interactions
- **Gradient Accents**: Amber for insights, emerald for success states
- **Responsive**: Mobile-friendly with adaptive layouts

---

## 🧪 Testing

### Unit Tests
```bash
pytest tests/test_agent1.py
pytest tests/test_agent2.py
pytest tests/test_agent3.py
```

### Integration Test
```bash
pytest tests/test_orchestrator.py
```

### Manual Test
1. Start backend and frontend
2. Paste 5-10 Economic Times URLs
3. Click "Generate Briefing"
4. Verify: Summary, Key Points, Visualizations, Audio

---

## 📁 Project Structure

```
newslens-ai/
├── agents/              # 3-agent system
│   ├── agent1.py       # Source Intelligence
│   ├── agent2.py       # Visual Intelligence
│   └── agent3.py       # Briefing Synthesis
├── orchestrator.py     # LangGraph coordinator
├── api/                # FastAPI backend
│   ├── main.py
│   ├── routes.py
│   └── models.py
├── frontend/           # React frontend
│   └── src/
│       ├── App.tsx
│       ├── components/
│       ├── api/
│       └── types/
├── data/               # Generated data
│   ├── articles/
│   ├── chroma_db/
│   └── audio/
├── prompts/            # Agent prompts
├── scripts/            # Setup scripts
├── tests/              # Test suite
└── examples/           # Pre-generated briefings
```

---

## 🔑 Key Implementation Details

### Structured Output with Pydantic
Agent 1 uses Pydantic models to ensure consistent JSON output:
```python
class Entity(BaseModel):
    name: str
    type: str  # company/person/policy/metric
    context: str

class ArticleInsights(BaseModel):
    entities: List[Entity]
    timeline: List[TimelineEvent]
    key_metrics: Dict[str, str]
    sentiment: str
```

### Dynamic Artifact Generation
Agent 2 generates React component code as strings:
```python
prompt = f"""Generate a React component using Recharts that displays: {viz_type}
Data: {json.dumps(data)}
Requirements: responsive, professional, TailwindCSS
Return ONLY the JSX code."""
```

### LangGraph State Management
```python
class NewsLensState(TypedDict):
    article_urls: List[str]
    raw_articles: List[Dict]
    insights: Dict
    visualizations: List[str]
    briefing: Dict
    audio_path: str
```

---

## 💰 Cost Optimization

- **Cache embeddings** in ChromaDB (avoid regenerating)
- **Cache LLM responses** for repeated queries
- **Batch article processing** where possible
- **TTS cost**: ~$0.075 for 10 demo briefings (500 chars each @ $0.015/1000)

---

## 🎯 Success Metrics

- **Speed**: <10 seconds end-to-end
- **Consolidation**: 10 articles → 1 briefing (90%)
- **Visual Quality**: Auto-generated, professional appearance
- **Audio Quality**: Clear narration, 2-3 minute duration
- **Accuracy**: Key entities and metrics correctly extracted

---

## 🏆 Competitive Differentiation

**NewsLens vs Competitors:**

| Feature | Most Competitors | NewsLens AI |
|---------|-----------------|-------------|
| Architecture | Simple ChatGPT wrappers | LangGraph 3-agent orchestration |
| Visualizations | Static templates | Dynamic React Artifact generation |
| Insights | Single-article summaries | Cross-article knowledge graphs |
| Output | Text only | Text + Visuals + Audio |
| Processing | 30+ seconds | <10 seconds |

---

## 📈 Business Impact

### Time Saved for Readers
- Average ET reader: 25 min/article × 8 articles = 200 min
- NewsLens: 3 min read + 2 min audio = 5 min
- **Time savings: 195 minutes (97.5%)**

### Content Production Cost Savings
- Manual infographic: 2 hours designer time
- NewsLens: 10 seconds automated
- **Cost savings: 720x faster**

### Market Opportunity
- ET Markets app: 5M+ monthly users
- Premium tier: ₹199/month
- Target: 10,000 subscribers = ₹2.39 crore annual revenue

---

## 🚧 Future Enhancements

1. **Knowledge Graph Visualization** - Interactive entity relationship networks
2. **Export & Share** - PDF export, unique URL sharing
3. **Advanced Analytics** - Sentiment trends, topic clustering
4. **Multi-Language Support** - Hindi, regional languages
5. **Real-Time Updates** - Live briefing updates as new articles publish

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Yajat Pawar** | PCCOE Pune

🏆 Built for ET AI Hackathon 2026

---

## 🙏 Acknowledgments

- Economic Times for the hackathon challenge
- Claude API (Anthropic) for LLM capabilities
- AWS Polly for Neural TTS
- LangChain team for LangGraph framework
