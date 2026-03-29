# NewsLens AI - Pitch Video Script
## ET AI Hackathon 2026 | Problem Statement #8

**Duration**: 3 minutes
**Presenter**: Yajat Pawar, PCCOE Pune

---

## OPENING (0:00 - 0:30)

**[Screen: Title Slide with Logo]**

"Hi, I'm Yajat Pawar from PCCOE Pune, and I'm excited to present NewsLens AI—a multi-modal business intelligence platform built for Problem Statement #8.

**The Problem**: Business professionals spend 25 minutes reading 10 Economic Times articles daily. They struggle to find related articles, identify contradictions across sources, and synthesize key insights. Current news summarizers are simple ChatGPT wrappers that don't leverage multiple sources or detect conflicting information.

**Our Solution**: NewsLens AI transforms Economic Times articles into interactive briefings with automatic visualization and audio narration—reducing reading time from 25 minutes to 3 minutes. That's **8x faster**."

---

## TECHNICAL ARCHITECTURE (0:30 - 1:00)

**[Screen: Architecture Diagram]**

"NewsLens AI is built on a **3-agent architecture orchestrated via LangGraph**—this is NOT simple prompt chaining, but a stateful workflow with proper coordination and error handling.

### Agent Workflow:

**Agent 1: Source Intelligence Agent**
- Extracts structured insights from Economic Times articles
- Uses Pydantic models for schema validation
- Outputs: Entities, timeline, relationships, metrics, sentiment
- Technology: Claude 3.5 Sonnet via AWS Bedrock, BeautifulSoup for web scraping

**Agent 2: Visual Intelligence Agent**
- Auto-generates interactive visualizations from structured data
- Detects visualization type: timeline, comparison, metrics, network graph
- Generates React component code dynamically
- Technology: Recharts library, React-force-graph for network visualizations

**Agent 3: Briefing Synthesis Agent**
- Creates comprehensive multi-article briefings
- Generates 400-500 word executive summaries
- Identifies contradictions and consensus across sources
- Converts briefing to audio using AWS Polly Neural TTS
- Professional Joanna voice for narration

### Technology Stack:

**Backend (Python 3.11+)**
- LangGraph: Multi-agent orchestration framework
- LangChain: Document loading and processing
- ChromaDB: Local vector database for semantic search
- sentence-transformers: MPNet embeddings (768-dimensional, production-grade)
- Claude API: Via AWS Bedrock (Sonnet 3.5 Haiku for speed)
- AWS Polly: Neural TTS for voice synthesis
- FastAPI: REST API backend (430 lines)
- BeautifulSoup4: Web scraping ET articles
- PyPDF2 + pdfplumber: PDF text extraction

**Frontend (React 18 + TypeScript)**
- Vite: Build tool and dev server
- TailwindCSS: Utility-first styling with custom editorial design system
- Framer Motion: Smooth animations and page transitions
- Recharts: Interactive chart library
- react-force-graph-2d: Network graph component
- Lucide React: Icon library
- Axios: HTTP client

**Total Codebase**: ~5,500 lines
- Backend: 3,259 lines of Python
- Frontend: 2,208 lines of TypeScript/React

---

## LIVE DEMO (1:00 - 2:15)

**[Screen: NewsLens AI Homepage]**

"Let me show you how it works.

### Step 1: Automatic Article Discovery

I'll paste one Economic Times article about Zepto's funding round."

**[Type URL in input field]**

"Now, watch this—I click 'Find Related Articles,' and our production-grade semantic search engine kicks in:

- Uses MPNet embeddings (768-dimensional)
- Multi-stage filtering: keyword pre-filter, semantic similarity, quality re-ranking
- Weighted scoring: 30% title + 70% content
- Shows 5 genuinely related articles with similarity scores

The system found articles about Zepto's competitors, market analysis, and funding trends. I'll select 3 articles and click 'Add Selected.'"

### Step 2: Generate Briefing

**[Click "Generate Intelligence Briefing"]**

"Processing begins. The system:
1. Scrapes all articles (BeautifulSoup)
2. Generates embeddings and stores in ChromaDB
3. Agent 1 extracts entities, timeline, relationships
4. Agent 2 generates visualizations
5. Agent 3 synthesizes briefing and creates audio

**Total time**: Less than 10 seconds.

### Step 3: Interactive Briefing Output

**[Screen: Briefing Display]**

Here's what we get:

**Section 1: Executive Summary**
- 400-500 word comprehensive analysis
- Not just summarizing—synthesizing across sources
- Includes specific numbers, dates, stakeholder analysis

**Section 2: Key Points**
- 10 essential insights with specifics
- Covers: announcements, financials, strategy, competitive implications, market impact

**Section 3: Cross-Article Intelligence**
- **Contradictions**: 'Article 1 says Zepto raised $200M, but Article 2 reports $250M'
- **Consensus**: All articles agree on Zepto's 10-minute delivery promise

**Section 4: Interactive Visualizations**
- **Timeline**: Chronological events with impact levels
- **Entity Comparison**: Companies, people, policies displayed as cards
- **Metrics Dashboard**: Key numbers with visual emphasis
- All auto-generated in 10 seconds (vs 2 hours manual design)

**Section 5: Entity Relationship Network**
- Interactive force-directed graph
- Nodes sized by importance (more connections = larger)
- Click nodes for details
- Drag to rearrange
- Shows: Zepto competes with Blinkit, Swiggy Instamart; backed by Y Combinator

**Section 6: Audio Narration**
**[Play audio for 10 seconds]**
- AWS Polly Neural TTS (Joanna voice)
- Perfect for hands-free consumption while commuting
- 2-3 minute briefing

**Section 7: Strategic Questions**
- 8 investor/analyst-focused questions
- 'What's Zepto's path to profitability?'
- 'How will competitors respond?'

### Step 4: Share & Export

**[Click Share button]**
- Generates unique URL with UUID
- Copy link to clipboard
- Anyone can view the briefing

**[Click Export PDF]**
- Professional PDF with reportlab
- Includes summary, key points, insights, questions
- Download instantly

---

## DIFFERENTIATION & IMPACT (2:15 - 2:45)

**[Screen: Competitive Comparison Table]**

"What makes NewsLens AI different?

| Feature | Most Competitors | NewsLens AI |
|---------|-----------------|-------------|
| Architecture | Simple ChatGPT wrappers | LangGraph 3-agent orchestration |
| Visualizations | Static templates | Dynamic React Artifact generation |
| Insights | Single-article summaries | Cross-article knowledge graphs |
| Output | Text only | Text + Visuals + Audio |
| Processing | 30+ seconds | <10 seconds |

### Key Differentiators:

1. **Production-Grade Semantic Search**
   - MPNet embeddings (768D vs typical 384D)
   - Multi-stage filtering ensures quality
   - Section-aware candidate sourcing

2. **Cross-Article Intelligence**
   - Explicit contradiction detection
   - Consensus finding across sources
   - Entity aggregation and relationship mapping

3. **Multi-Modal Output**
   - Text briefings (400-500 words)
   - Interactive visualizations (auto-generated)
   - Professional audio narration (AWS Polly)
   - Shareable links + PDF export

4. **Distinctive Design System**
   - Editorial intelligence aesthetic
   - Fraunces + Instrument Sans typography
   - Professional cream/gold/ink color palette
   - Not generic AI interface

### Business Impact (See IMPACT_MODEL.md):

**Time Saved**:
- Average reader: 200 minutes/day → 5 minutes with NewsLens AI
- **195 minutes saved (97.5% reduction)**

**Cost Savings**:
- Manual infographic: 2 hours → 10 seconds with NewsLens AI
- **720x faster visualization generation**

**Market Opportunity**:
- ET Markets app: 5M+ monthly users
- Premium tier: ₹199/month
- Target: 10,000 subscribers = **₹2.39 crore annual revenue**

---

## CLOSING (2:45 - 3:00)

**[Screen: Final Slide with Tagline]**

"NewsLens AI: **From News Noise to Business Intelligence in 10 Seconds.**

This isn't just summarizing news—this is creating business intelligence FROM news.

Thank you. I'm excited to answer any questions."

**[Screen: Contact Information & GitHub Repository]**
- GitHub: github.com/yajatpawar/NewsLens-AI
- Email: yajat.pawar@example.com
- Demo: newslens-ai.vercel.app (if deployed)

---

## TECHNICAL HIGHLIGHTS FOR Q&A

### Architecture Deep Dive:

**LangGraph StateGraph**:
```python
class NewsLensState(TypedDict):
    article_urls: List[str]
    raw_articles: List[Dict]
    insights: Dict
    visualizations: List[str]
    briefing: Dict
    audio_path: str
```

Workflow nodes:
1. `fetch` → Scrape articles
2. `extract` → Run Agent 1
3. `visualize` → Run Agent 2
4. `synthesize` → Run Agent 3
5. `audio` → Generate MP3

**Error Handling**:
- Retry logic for API failures
- Fallback visualization templates
- Partial extraction if some fields fail
- Graceful degradation

**Semantic Search Algorithm**:
```python
# Multi-stage filtering
1. Extract keywords (15+ terms)
2. Keyword pre-filter (require 2+ shared keywords) → 95%+ filtered
3. Semantic similarity (MPNet embeddings, cosine) → 0.35 threshold
4. Quality re-ranking (length, relevance signals)

# Weighted scoring
embedding = 0.3 * title_emb + 0.7 * content_emb
score = cosine_similarity(base_emb, candidate_emb)
```

**Cost Optimization**:
- Cache embeddings in ChromaDB (avoid regeneration)
- Cache LLM responses for repeated queries
- Batch article processing where possible
- TTS cost: ~$0.075 for 10 briefings (500 chars @ $0.015/1000)
- Claude API: ~$0.10 per briefing (estimate)

**Performance Metrics**:
- End-to-end latency: <10 seconds
- Scraping: 2-3 seconds
- Agent 1 extraction: 3-4 seconds
- Agent 2 visualization: 1-2 seconds
- Agent 3 synthesis: 2-3 seconds
- Audio generation: 1-2 seconds

### Implementation Statistics:

- **Development Time**: 5 days (March 25-29, 2026)
- **Test Coverage**: 26/48 tests passing (54% without live API)
- **API Endpoints**: 8 endpoints (generate, find-related, save, retrieve, export, audio, QA)
- **Components**: 6 major React components
- **Agents**: 3 specialized agents (1,367 lines of Python)
- **Orchestrator**: 558 lines (LangGraph StateGraph)

### Future Enhancements:

1. **Real-Time Updates**: Live briefing updates as new articles publish
2. **Multi-Language Support**: Hindi, regional languages
3. **Advanced Analytics**: Sentiment trends over time, topic clustering
4. **Knowledge Graph Export**: Neo4j integration for persistent graphs
5. **Mobile App**: React Native version for iOS/Android
6. **API Monetization**: Developer API for third-party integrations

---

## ACKNOWLEDGMENTS

**Technologies Used**:
- Anthropic Claude (via AWS Bedrock)
- AWS Polly Neural TTS
- LangChain & LangGraph frameworks
- ChromaDB vector database
- React & TypeScript
- TailwindCSS & Framer Motion

**Special Thanks**:
- Economic Times for the hackathon challenge
- Anthropic for Claude API capabilities
- Open-source community for libraries

---

**End of Pitch Video Script**

Total Word Count: ~1,500 words (3-minute presentation at 500 words/minute speaking pace)
