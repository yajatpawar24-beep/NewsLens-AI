"""
FastAPI Backend for NewsLens AI
=================================

REST API for generating news briefings with visualizations and audio.
"""

import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path

# Import orchestrator, PDF generator, and article discovery
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from orchestrator import NewsLensOrchestrator
from api.pdf_generator import generate_briefing_pdf
from api.enhanced_article_discovery import get_enhanced_discovery_service
from api.qa_service import get_qa_service


# ============================================================================
# FastAPI App Configuration
# ============================================================================

app = FastAPI(
    title="NewsLens AI API",
    description="Generate AI-powered news briefings with visualizations",
    version="1.0.0"
)

# Configure CORS - allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including file://
    allow_credentials=False,  # Must be False when using allow_origins=*
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateRequest(BaseModel):
    """Request model for briefing generation"""
    article_urls: List[str]


class BriefingResponse(BaseModel):
    """Response model for generated briefing"""
    summary: str
    key_points: List[str]
    insights: Dict[str, Any]
    questions: List[str]
    visualizations: List[str]
    audio_url: str  # Changed from audio_path to audio_url
    entity_graph: Dict[str, Any]  # Entity relationship graph
    session_id: str  # Session ID for Q&A
    status: str


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "NewsLens AI API",
        "version": "1.0.0",
        "status": "online"
    }


@app.post("/api/generate", response_model=BriefingResponse)
async def generate_briefing(request: GenerateRequest):
    """
    Generate a news briefing from article URLs.

    Args:
        request: GenerateRequest with article_urls

    Returns:
        BriefingResponse with summary, visualizations, and audio
    """

    if not request.article_urls:
        raise HTTPException(status_code=400, detail="No article URLs provided")

    # Generate session ID for Q&A
    import uuid
    session_id = str(uuid.uuid4())[:8]

    # Initialize orchestrator
    orchestrator = NewsLensOrchestrator()

    try:
        # Process articles through pipeline
        result = orchestrator.process(request.article_urls)

        # Check if all articles failed to fetch
        raw_articles = result.get("raw_articles", [])
        all_failed = all(art.get("status") == "error" for art in raw_articles) if raw_articles else True

        if all_failed and raw_articles:
            # Get error message from first article
            error_msg = raw_articles[0].get("text", "Unable to extract article content")
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )

        # Extract briefing data
        briefing = result.get("briefing", {})

        # Index articles for Q&A
        raw_articles = result.get("raw_articles", [])
        if raw_articles:
            try:
                qa_service = get_qa_service()
                qa_service.index_articles(raw_articles, session_id)
            except Exception as e:
                print(f"Warning: Failed to index articles for Q&A: {e}")

        # Convert audio_path to audio_url (full URL for CORS)
        audio_path = result.get("audio_path", "")
        audio_url = ""
        if audio_path and not audio_path.startswith("Error"):
            # Extract filename from path (e.g., "data/audio/briefing.mp3" → "briefing.mp3")
            filename = Path(audio_path).name
            # Return full URL so frontend can access from different port
            audio_url = f"http://localhost:8000/api/audio/{filename}"

        return BriefingResponse(
            summary=briefing.get("summary", ""),
            key_points=briefing.get("key_points", []),
            insights=briefing.get("insights", {}),
            questions=briefing.get("questions", []),
            visualizations=result.get("visualizations", []),
            audio_url=audio_url,  # Return audio_url instead of audio_path
            entity_graph=result.get("entity_graph", {"entities": [], "relationships": []}),
            session_id=session_id,  # Session ID for Q&A
            status=result.get("status", "error")
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is (for proper error codes)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating briefing: {str(e)}"
        )


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve audio file.

    Args:
        filename: Name of the audio file

    Returns:
        Audio file as FileResponse
    """

    audio_path = Path("data/audio") / filename

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=filename
    )


@app.post("/api/briefing/save")
async def save_briefing(briefing: BriefingResponse):
    """
    Save a briefing for sharing.

    Args:
        briefing: BriefingResponse to save

    Returns:
        Dict with briefing_id
    """

    # Generate unique ID
    briefing_id = str(uuid.uuid4())[:8]  # Short ID for cleaner URLs

    # Create briefings directory
    briefings_dir = Path("data/briefings")
    briefings_dir.mkdir(parents=True, exist_ok=True)

    # Add metadata
    briefing_data = briefing.dict()
    briefing_data["id"] = briefing_id
    briefing_data["created_at"] = datetime.now().isoformat()

    # Save to file
    file_path = briefings_dir / f"{briefing_id}.json"
    with open(file_path, 'w') as f:
        json.dump(briefing_data, f, indent=2)

    return {"briefing_id": briefing_id}


@app.get("/api/briefing/{briefing_id}")
async def get_briefing(briefing_id: str):
    """
    Retrieve a saved briefing.

    Args:
        briefing_id: ID of the briefing to retrieve

    Returns:
        BriefingResponse
    """

    file_path = Path("data/briefings") / f"{briefing_id}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Briefing not found")

    with open(file_path, 'r') as f:
        briefing_data = json.load(f)

    return briefing_data


@app.post("/api/export/pdf")
async def export_briefing_pdf(briefing: BriefingResponse):
    """
    Export briefing as PDF.

    Args:
        briefing: BriefingResponse to export

    Returns:
        PDF file download
    """

    try:
        # Create exports directory
        exports_dir = Path("data/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"briefing_{timestamp}.pdf"
        pdf_path = exports_dir / pdf_filename

        # Generate PDF
        briefing_dict = briefing.dict()
        generate_briefing_pdf(briefing_dict, str(pdf_path))

        # Return PDF as download
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_filename,
            headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@app.post("/api/find-related")
async def find_related_articles(request: Dict[str, Any]):
    """
    Find semantically similar articles to the given article.

    Args:
        request: Dict with 'article_url' and optionally 'article_text'

    Returns:
        List of related article URLs with similarity scores
    """

    article_url = request.get('article_url')
    article_text = request.get('article_text', '')

    if not article_url:
        raise HTTPException(status_code=400, detail="article_url is required")

    try:
        # Get enhanced article discovery service
        discovery = get_enhanced_discovery_service()

        # If no text provided, fetch it
        if not article_text:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(article_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            soup = BeautifulSoup(response.text, 'html.parser')
            article_body = soup.find('article') or soup.find('div', {'class': 'artText'})
            if article_body:
                article_text = article_body.get_text(separator=' ', strip=True)

        # Find related articles
        related = discovery.find_related_articles(
            base_url=article_url,
            base_text=article_text,
            max_articles=5,
            similarity_threshold=0.25  # Higher threshold for genuine relevance
        )

        return {
            "related_articles": related,
            "count": len(related)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find related articles: {str(e)}"
        )


@app.post("/api/qa/ask")
async def ask_question(request: Dict[str, Any]):
    """
    Answer a question about the analyzed articles using RAG.

    Args:
        request: Dict with 'question' and 'session_id'

    Returns:
        Answer with sources and confidence level
    """
    question = request.get('question')
    session_id = request.get('session_id')

    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    try:
        # Get Q&A service
        qa_service = get_qa_service()

        # Answer question
        result = qa_service.answer_question(question, session_id)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(e)}"
        )


@app.post("/api/qa/index")
async def index_articles(request: Dict[str, Any]):
    """
    Index articles for Q&A.

    Args:
        request: Dict with 'articles' (list of {title, text}) and 'session_id'

    Returns:
        Success message
    """
    articles = request.get('articles', [])
    session_id = request.get('session_id')

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    try:
        # Get Q&A service
        qa_service = get_qa_service()

        # Index articles
        qa_service.index_articles(articles, session_id)

        return {"status": "success", "indexed": len(articles)}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to index articles: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "NewsLens AI",
        "version": "1.0.0"
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
