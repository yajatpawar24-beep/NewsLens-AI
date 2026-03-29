# NewsLens AI - Technical Architecture
## Multi-Modal Business Intelligence Platform

**Version**: 1.0.0
**Last Updated**: March 29, 2026
**Author**: Yajat Pawar, PCCOE Pune

---

## System Overview

NewsLens AI is a production-grade multi-modal business intelligence platform that transforms Economic Times articles into interactive briefings with automatic visualization and audio narration. The system reduces reading time from 25 minutes to 3 minutes (8x faster) through intelligent aggregation, synthesis, and multi-modal output generation.

**Core Capabilities**:
- Multi-source article aggregation with semantic search
- Cross-article intelligence with contradiction detection
- Auto-generated interactive visualizations
- Professional audio narration
- Real-time briefing generation (<10 seconds)
- Shareable links and PDF export

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            NEWSLENS AI ARCHITECTURE                              │
│                         3-Agent System + LangGraph Orchestration                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────────┐
│                                  USER INTERFACE                                    │
│                         React 18 + TypeScript + TailwindCSS                        │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  InputForm   │  │  Briefing     │  │  Entity      │  │  Visualization│        │
│  │              │  │  Display      │  │  Graph       │  │  Grid         │        │
│  │ - URL input  │  │ - Summary     │  │ - Network    │  │ - Charts      │        │
│  │ - Discovery  │  │ - Key points  │  │ - Relations  │  │ - Timeline    │        │
│  └──────────────┘  └───────────────┘  └──────────────┘  └──────────────┘        │
│                                                                                     │
│  ┌──────────────┐  ┌───────────────┐                                              │
│  │  AudioPlayer │  │  QAChat       │                                              │
│  │              │  │               │                                              │
│  │ - Waveform   │  │ - RAG Chat    │                                              │
│  │ - Controls   │  │ - Context     │                                              │
│  └──────────────┘  └───────────────┘                                              │
└───────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTP/REST API
                                          │ (axios client)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND SERVER                                 │
│                              (api/main.py - 430 lines)                              │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  API ENDPOINTS:                                                                    │
│  ┌────────────────────────────────────────────────────────────────────┐           │
│  │ POST   /api/generate          → Generate briefing                  │           │
│  │ POST   /api/find-related      → Semantic article discovery         │           │
│  │ POST   /api/briefing/save     → Save briefing (UUID)               │           │
│  │ GET    /api/briefing/{id}     → Retrieve briefing                  │           │
│  │ POST   /api/export/pdf        → Generate PDF export                │           │
│  │ GET    /api/audio/{filename}  → Serve audio file                   │           │
│  │ POST   /api/qa/ask            → Q&A with RAG                       │           │
│  │ GET    /api/health            → Health check                       │           │
│  └────────────────────────────────────────────────────────────────────┘           │
│                                                                                     │
│  SERVICES:                                                                          │
│  ┌────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐           │
│  │ Semantic Search    │  │ PDF Generator        │  │ QA Service       │           │
│  │ (MPNet 768D)       │  │ (reportlab)          │  │ (ChromaDB RAG)   │           │
│  │ 469 lines          │  │ 233 lines            │  │ 202 lines        │           │
│  └────────────────────┘  └─────────────────────┘  └──────────────────┘           │
└───────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ Invokes
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          LANGGRAPH ORCHESTRATOR                                     │
│                         (orchestrator.py - 558 lines)                               │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  STATE MANAGEMENT:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐              │
│  │ NewsLensState (TypedDict):                                       │              │
│  │   - article_urls: List[str]                                      │              │
│  │   - raw_articles: List[Dict]                                     │              │
│  │   - insights: Dict                                               │              │
│  │   - visualizations: List[str]                                    │              │
│  │   - briefing: Dict                                               │              │
│  │   - audio_path: str                                              │              │
│  └─────────────────────────────────────────────────────────────────┘              │
│                                                                                     │
│  WORKFLOW NODES:                                                                    │
│  ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌───────┐             │
│  │  fetch  │──▶│ extract │──▶│visualize │──▶│synthesize──▶│ audio │             │
│  │         │   │         │   │          │   │         │   │       │             │
│  │ Scrape  │   │ Agent 1 │   │ Agent 2  │   │ Agent 3 │   │ Polly │             │
│  │ Articles│   │ Insights│   │ Charts   │   │ Summary │   │ TTS   │             │
│  └─────────┘   └─────────┘   └──────────┘   └─────────┘   └───────┘             │
│       │             │              │              │             │                  │
│       │             │              │              │             │                  │
│       ▼             ▼              ▼              ▼             ▼                  │
│  Beautiful    Pydantic      React        Claude API      AWS Polly               │
│   Soup        Models       Artifacts                                              │
│                                                                                     │
│  ERROR HANDLING:                                                                    │
│  - Retry logic (3 attempts with exponential backoff)                               │
│  - Fallback templates for visualizations                                           │
│  - Partial extraction on field failures                                            │
│  - Graceful degradation for audio generation                                       │
└───────────────────────────────────────────────────────────────────────────────────┘
                │                    │                    │
                ▼                    ▼                    ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│     AGENT 1:         │  │     AGENT 2:         │  │     AGENT 3:         │
│  Source Intelligence │  │  Visual Intelligence │  │ Briefing Synthesis   │
│   (agent1.py)        │  │   (agent2.py)        │  │   (agent3.py)        │
│   331 lines          │  │   622 lines          │  │   392 lines          │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│                      │  │                      │  │                      │
│ INPUT:               │  │ INPUT:               │  │ INPUT:               │
│ - Raw article text   │  │ - Structured insights│  │ - Multi-article data │
│ - Article metadata   │  │   from Agent 1       │  │ - Cross-article      │
│                      │  │ - Data to visualize  │  │   aggregation        │
│ PROCESS:             │  │                      │  │                      │
│ - Entity extraction  │  │ PROCESS:             │  │ PROCESS:             │
│ - Timeline building  │  │ - Viz type detection │  │ - Synthesis across   │
│ - Relationship map   │  │ - Template selection │  │   sources            │
│ - Metrics extraction │  │ - React code gen     │  │ - Contradiction      │
│ - Sentiment analysis │  │ - Fallback handling  │  │   detection          │
│                      │  │                      │  │ - Summary generation │
│ OUTPUT:              │  │ OUTPUT:              │  │ - Audio script       │
│ - Structured JSON    │  │ - React Artifact     │  │                      │
│   (Pydantic models)  │  │   HTML/JSX code      │  │ OUTPUT:              │
│ - Entities list      │  │ - Interactive charts │  │ - Executive summary  │
│ - Timeline events    │  │ - Network graphs     │  │ - Key points (10)    │
│ - Key metrics        │  │ - Timeline viz       │  │ - Insights           │
│ - Sentiment          │  │ - Metrics dashboard  │  │ - Questions (8)      │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
         │                          │                          │
         ▼                          ▼                          ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │  AWS Bedrock     │  │  AWS Polly       │  │  ChromaDB        │         │
│  │  (Claude API)    │  │  (Neural TTS)    │  │  (Vector DB)     │         │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤         │
│  │ - Claude 3.5     │  │ - Voice: Joanna  │  │ - Local storage  │         │
│  │   Sonnet         │  │ - Engine: Neural │  │ - MPNet 768D     │         │
│  │ - Haiku for      │  │ - Cost: $0.015   │  │   embeddings     │         │
│  │   speed          │  │   per 1K chars   │  │ - Semantic search│         │
│  │ - Region: us-    │  │ - Output: MP3    │  │ - Persistent     │         │
│  │   east-1         │  │                  │  │   cache          │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Communication Flow

### 1. Article Discovery & Input Flow

```
User Interface (InputForm)
    │
    ├─▶ Paste URL(s)
    │   └─▶ Validation (check URL format)
    │
    └─▶ Click "Find Related"
        │
        └─▶ POST /api/find-related
            │
            ├─▶ Semantic Search Service
            │   ├─▶ Extract keywords (NER + frequency analysis)
            │   ├─▶ Keyword pre-filter (require 2+ shared)
            │   ├─▶ Generate embeddings (MPNet 768D)
            │   ├─▶ Compute cosine similarity
            │   ├─▶ Quality re-ranking (length + relevance)
            │   └─▶ Return top 5 articles (similarity > 0.35)
            │
            └─▶ Frontend displays results
                └─▶ User selects + clicks "Add Selected"
```

### 2. Briefing Generation Flow

```
User clicks "Generate Briefing"
    │
    └─▶ POST /api/generate { article_urls: [...] }
        │
        └─▶ LangGraph Orchestrator.run()
            │
            ├─▶ NODE 1: fetch
            │   ├─▶ For each URL:
            │   │   ├─▶ BeautifulSoup.get(url)
            │   │   ├─▶ Extract <article> text
            │   │   ├─▶ Filter noise (footer, ads)
            │   │   └─▶ Store in state.raw_articles[]
            │   │
            │   └─▶ ChromaDB.add_documents()
            │       └─▶ Generate embeddings (MPNet)
            │
            ├─▶ NODE 2: extract (Agent 1)
            │   ├─▶ For each article:
            │   │   ├─▶ Claude API (Pydantic structured output)
            │   │   ├─▶ Extract: entities, timeline, metrics, sentiment
            │   │   └─▶ Validate schema
            │   │
            │   └─▶ Store in state.insights{}
            │
            ├─▶ NODE 3: visualize (Agent 2)
            │   ├─▶ Detect viz type (timeline/comparison/metrics/network)
            │   ├─▶ Select fallback template
            │   ├─▶ Generate React Artifact HTML
            │   └─▶ Store in state.visualizations[]
            │
            ├─▶ NODE 4: synthesize (Agent 3)
            │   ├─▶ Aggregate cross-article data
            │   │   ├─▶ Merge timelines
            │   │   ├─▶ Count entity frequency
            │   │   └─▶ Compare sentiment
            │   │
            │   ├─▶ Claude API (multi-article synthesis)
            │   │   ├─▶ Generate 400-500 word summary
            │   │   ├─▶ Extract 10 key points
            │   │   ├─▶ Detect contradictions
            │   │   ├─▶ Find consensus
            │   │   └─▶ Generate 8 questions
            │   │
            │   └─▶ Store in state.briefing{}
            │
            └─▶ NODE 5: audio (Agent 3)
                ├─▶ AWS Polly.synthesize_speech()
                │   ├─▶ Text: state.briefing.summary
                │   ├─▶ Voice: Joanna
                │   ├─▶ Engine: Neural
                │   └─▶ Output: MP3 stream
                │
                └─▶ Save to data/audio/briefing_{timestamp}.mp3
                    └─▶ Return full URL: http://localhost:8000/api/audio/...
```

### 3. Error Handling Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING LAYERS                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ LAYER 1: API Level (FastAPI)                                │
│   ├─▶ HTTP exception handling                               │
│   ├─▶ Request validation (Pydantic)                         │
│   └─▶ Return 4xx/5xx with error messages                    │
│                                                               │
│ LAYER 2: Orchestrator Level (LangGraph)                     │
│   ├─▶ Try-except blocks per node                            │
│   ├─▶ Retry logic (3 attempts, exponential backoff)         │
│   ├─▶ Partial state recovery                                │
│   └─▶ Graceful degradation (skip failed components)         │
│                                                               │
│ LAYER 3: Agent Level                                        │
│   ├─▶ Pydantic validation (Agent 1)                         │
│   ├─▶ Fallback templates (Agent 2)                          │
│   ├─▶ JSON parsing robustness (Agent 3)                     │
│   └─▶ Template detection (flag if LLM returns instructions) │
│                                                               │
│ LAYER 4: External Service Level                             │
│   ├─▶ AWS SDK auto-retry (boto3)                            │
│   ├─▶ Network timeout handling                              │
│   └─▶ Rate limit backoff                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Agent 1 Output Schema (Pydantic)

```python
class Entity(BaseModel):
    name: str
    type: str  # company/person/policy/metric
    context: str

class TimelineEvent(BaseModel):
    date: str
    event: str
    impact: str  # high/medium/low

class ArticleInsights(BaseModel):
    entities: List[Entity]
    timeline: List[TimelineEvent]
    key_metrics: Dict[str, str]
    sentiment: str
    main_theme: str
```

### Agent 3 Output Schema

```python
class Briefing(BaseModel):
    summary: str  # 400-500 words
    key_points: List[str]  # 10 items
    insights: Dict[str, List[str]]  # contradictions, consensus
    questions: List[str]  # 8 items
    session_id: str  # for Q&A chat
    audio_url: Optional[str]
```

### ChromaDB Schema

```python
Collection: "newslens_articles"
Embedding Model: sentence-transformers/all-mpnet-base-v2
Dimensions: 768
Metadata: {
    "url": str,
    "title": str,
    "date": str,
    "section": str,  # tech/markets/policy
    "word_count": int
}
```

---

## Performance Optimization

### Caching Strategy

```
┌─────────────────────────────────────────────────┐
│            MULTI-LEVEL CACHING                   │
├─────────────────────────────────────────────────┤
│                                                   │
│ L1: In-Memory Cache (FastAPI)                   │
│   └─▶ Recent briefings (LRU cache, 100 items)   │
│                                                   │
│ L2: Disk Cache (ChromaDB)                       │
│   └─▶ Article embeddings (persistent)           │
│                                                   │
│ L3: File System Cache                           │
│   ├─▶ Generated audio files (data/audio/)       │
│   └─▶ Saved briefings (data/briefings/)         │
└─────────────────────────────────────────────────┘
```

### Latency Breakdown

| Operation | Time | Strategy |
|-----------|------|----------|
| Article scraping | 2-3s | Parallel requests |
| Embedding generation | 1-2s | Batch processing, cache |
| Agent 1 extraction | 3-4s | Claude Haiku for speed |
| Agent 2 visualization | 1-2s | Template-based fallbacks |
| Agent 3 synthesis | 2-3s | Single API call |
| Audio generation | 1-2s | AWS Polly Neural |
| **Total** | **<10s** | **Parallel where possible** |

---

## Security Considerations

### Authentication & Authorization
- API keys stored in environment variables (never committed)
- CORS configuration for frontend origin
- Rate limiting on API endpoints (100 requests/min per IP)

### Data Privacy
- No user data stored (stateless briefing generation)
- Briefing IDs are random UUIDs (not sequential)
- Shared briefings read-only (no edit/delete)

### Input Validation
- URL validation (must start with http/https)
- Article URL whitelist (Economic Times domain only)
- PDF size limit (5MB max)
- Sanitize HTML output (prevent XSS)

---

## Deployment Architecture

### Local Development
```
Backend:  http://localhost:8000
Frontend: http://localhost:5173
ChromaDB: ./data/chroma_db/ (persistent)
```

### Production (Recommended)
```
Backend:  AWS EC2 / Google Cloud Run
Frontend: Vercel / Netlify
Database: ChromaDB persistent volume
CDN:      CloudFront for static assets
```

---

## Technology Justifications

### Why LangGraph over Simple Chains?
- **State Management**: Proper state tracking across nodes
- **Error Recovery**: Retry logic and fallback handling
- **Parallel Processing**: Multiple articles processed concurrently
- **Observability**: Built-in logging and debugging

### Why Claude API?
- **Quality**: Superior summarization and synthesis
- **Speed**: Haiku model for real-time performance
- **Structured Output**: Native Pydantic schema support
- **Cost**: AWS Bedrock credits available

### Why MPNet Embeddings?
- **Accuracy**: 768D vs 384D (2x dimensional space)
- **Performance**: State-of-the-art on STS benchmarks
- **Production-Ready**: Trained on 1B+ sentence pairs
- **Local**: No external API dependency

### Why React + TypeScript?
- **Type Safety**: Catch errors at compile time
- **Developer Experience**: IntelliSense, autocomplete
- **Ecosystem**: Rich library ecosystem (Recharts, Framer Motion)
- **Performance**: Virtual DOM for efficient updates

---

## Scalability Considerations

### Current Limitations
- Single-threaded Python backend (uvicorn)
- In-memory ChromaDB (no distributed)
- Sequential article processing per request

### Scaling Strategy
1. **Horizontal Scaling**: Deploy multiple backend instances behind load balancer
2. **Database**: Migrate ChromaDB to client-server mode
3. **Queue System**: RabbitMQ/Celery for async briefing generation
4. **CDN**: CloudFront for audio file distribution
5. **Caching**: Redis for shared cache across instances

### Projected Capacity
- **Current**: 10-20 concurrent users
- **With Scaling**: 1,000+ concurrent users
- **Bottleneck**: Claude API rate limits (adjust tiers)

---

## Monitoring & Observability

### Metrics to Track
- API endpoint latency (p50, p95, p99)
- Error rates by endpoint
- Agent success/failure rates
- ChromaDB query performance
- AWS API costs (Claude + Polly)

### Logging Strategy
- Structured JSON logs (timestamp, level, message, context)
- Separate log files per component (orchestrator, agents, API)
- Centralized logging (CloudWatch / Datadog)

---

## Conclusion

NewsLens AI demonstrates a production-grade multi-agent architecture that goes beyond simple prompt chaining. The system's key innovations—LangGraph orchestration, cross-article intelligence, and multi-modal output—create a comprehensive business intelligence platform that transforms how professionals consume news.

**Architecture Highlights**:
- 3-agent system with proper state management
- Production-grade semantic search (MPNet 768D)
- Multi-modal output (text + visualizations + audio)
- <10 second end-to-end latency
- Professional editorial design system
- Comprehensive error handling and retry logic

---

**Document Version**: 1.0.0
**Last Updated**: March 29, 2026
**Total Architecture LOC**: ~5,500 lines (3,259 backend + 2,208 frontend)
