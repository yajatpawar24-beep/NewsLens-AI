"""
Q&A Service with RAG (Retrieval-Augmented Generation)
======================================================

Provides question answering over analyzed articles using:
- ChromaDB for vector storage
- Sentence transformers for embeddings
- Claude for answer generation
"""

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_aws import ChatBedrock
from typing import List, Dict, Any
from pathlib import Path


class QAService:
    """Question answering service using RAG"""

    def __init__(self):
        """Initialize Q&A service with ChromaDB and Claude"""
        # Initialize embedding model (same as article discovery for consistency)
        print("📚 Loading embedding model for Q&A...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

        # Initialize ChromaDB
        chroma_dir = Path("data/chroma_qa")
        chroma_dir.mkdir(parents=True, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="article_content",
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize Claude for answer generation
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={"temperature": 0.0}
        )

        print("✅ Q&A service initialized")

    def index_articles(self, articles: List[Dict[str, Any]], session_id: str):
        """
        Index articles for Q&A.

        Args:
            articles: List of articles with 'title' and 'text'
            session_id: Unique session identifier for this briefing
        """
        # Clear previous session data
        try:
            self.collection.delete(where={"session_id": session_id})
        except:
            pass

        documents = []
        metadatas = []
        ids = []

        for idx, article in enumerate(articles):
            text = article.get('text', '')
            title = article.get('title', f'Article {idx+1}')

            if not text or len(text) < 50:
                continue

            # Split into chunks (500 char chunks with 50 char overlap)
            chunk_size = 500
            overlap = 50

            chunks = []
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                if len(chunk) > 50:  # Only add meaningful chunks
                    chunks.append(chunk)
                start += (chunk_size - overlap)

            # Add chunks to collection
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"{session_id}:article_{idx}:chunk_{chunk_idx}"
                documents.append(chunk)
                metadatas.append({
                    "session_id": session_id,
                    "article_idx": idx,
                    "article_title": title,
                    "chunk_idx": chunk_idx
                })
                ids.append(doc_id)

        if documents:
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents, convert_to_numpy=True).tolist()

            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            print(f"✅ Indexed {len(documents)} chunks from {len(articles)} articles")

    def answer_question(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: User's question
            session_id: Session ID to retrieve relevant context

        Returns:
            Dictionary with answer, sources, and confidence
        """
        # Generate question embedding
        question_embedding = self.embedding_model.encode(question, convert_to_numpy=True).tolist()

        # Query ChromaDB for relevant chunks
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=5,
            where={"session_id": session_id}
        )

        if not results['documents'] or len(results['documents'][0]) == 0:
            return {
                "answer": "I don't have enough context from the articles to answer this question. Please ask about topics mentioned in the analyzed articles.",
                "sources": [],
                "confidence": "low"
            }

        # Extract relevant chunks and sources
        relevant_chunks = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        # Build context from relevant chunks
        context = "\n\n".join([
            f"[Source: {meta['article_title']}]\n{doc}"
            for doc, meta in zip(relevant_chunks, metadatas)
        ])

        # Generate answer using Claude
        prompt = f"""Based on the following context from news articles, answer the user's question.

Context from articles:
{context}

User question: {question}

Instructions:
- Answer based ONLY on the information provided in the context
- If the context doesn't contain enough information, say so
- Be concise and factual
- Cite which article(s) you're referencing when appropriate

Answer:"""

        response = self.llm.invoke(prompt)
        answer = response.content.strip()

        # Determine confidence based on relevance scores (lower distance = higher confidence)
        avg_distance = sum(distances) / len(distances)
        if avg_distance < 0.5:
            confidence = "high"
        elif avg_distance < 0.7:
            confidence = "medium"
        else:
            confidence = "low"

        # Extract unique sources
        sources = list(set([meta['article_title'] for meta in metadatas]))

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }


# Global instance
_qa_service_instance = None

def get_qa_service() -> QAService:
    """Get or create QA service instance"""
    global _qa_service_instance
    if _qa_service_instance is None:
        _qa_service_instance = QAService()
    return _qa_service_instance
