#!/usr/bin/env python3
"""
ChromaDB Setup Script for NewsLens AI
Initializes vector database with sentence-transformers embeddings
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class ChromaDBSetup:
    """Initialize and configure ChromaDB vector database"""

    def __init__(self, persist_directory: str = None, collection_name: str = "articles"):
        """
        Initialize ChromaDB setup

        Args:
            persist_directory: Path to ChromaDB storage (default: ./data/chroma_db)
            collection_name: Name of the collection (default: articles)
        """
        # Set default persist directory
        if persist_directory is None:
            base_dir = Path(__file__).parent.parent
            persist_directory = base_dir / "data" / "chroma_db"

        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name

        # Create directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        print(f"📁 Persist directory: {self.persist_directory}")
        print(f"📊 Collection name: {self.collection_name}")

        # Initialize embedding model
        print("\n🔄 Loading embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Embedding model loaded successfully")

        # Initialize ChromaDB client
        print("\n🔄 Initializing ChromaDB client...")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print("✅ ChromaDB client initialized")

        self.collection = None

    def create_collection(self, reset: bool = False):
        """
        Create or get collection with embedding function

        Args:
            reset: If True, delete existing collection and create new one
        """
        print(f"\n🔄 Creating collection '{self.collection_name}'...")

        # Delete existing collection if reset=True
        if reset:
            try:
                self.client.delete_collection(name=self.collection_name)
                print(f"🗑️  Deleted existing collection '{self.collection_name}'")
            except Exception as e:
                print(f"ℹ️  No existing collection to delete: {e}")

        # Create or get collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "NewsLens AI article embeddings"}
            )
            print(f"✅ Collection '{self.collection_name}' created/retrieved")
            print(f"📊 Current collection size: {self.collection.count()} documents")
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            raise

    def load_articles(self, articles_path: str = None):
        """
        Load articles from JSON file

        Args:
            articles_path: Path to articles.json (default: ./data/articles/articles.json)

        Returns:
            List of articles or empty list if file doesn't exist
        """
        if articles_path is None:
            base_dir = Path(__file__).parent.parent
            articles_path = base_dir / "data" / "articles" / "articles.json"

        articles_path = Path(articles_path)

        if not articles_path.exists():
            print(f"⚠️  Articles file not found: {articles_path}")
            print("ℹ️  Creating empty collection for future use")
            return []

        print(f"\n🔄 Loading articles from {articles_path}...")
        try:
            with open(articles_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            print(f"✅ Loaded {len(articles)} articles")
            return articles
        except Exception as e:
            print(f"❌ Error loading articles: {e}")
            return []

    def index_articles(self, articles: list):
        """
        Index articles into ChromaDB with embeddings

        Args:
            articles: List of article dictionaries
        """
        if not articles:
            print("\n⚠️  No articles to index")
            return

        if self.collection is None:
            raise ValueError("Collection not initialized. Call create_collection() first.")

        print(f"\n🔄 Indexing {len(articles)} articles...")

        # Prepare data for indexing
        documents = []
        metadatas = []
        ids = []

        for idx, article in enumerate(articles):
            # Create full text for embedding
            full_text = f"{article.get('title', '')} {article.get('text', '')}"
            documents.append(full_text)

            # Store metadata
            metadata = {
                'url': article.get('url', ''),
                'title': article.get('title', ''),
                'category': article.get('category', 'general'),
                'date': article.get('date', '')
            }
            metadatas.append(metadata)

            # Generate unique ID
            ids.append(f"article_{idx}")

        try:
            # Generate embeddings
            print("🔄 Generating embeddings...")
            start_time = time.time()
            embeddings = self.embedding_model.encode(
                documents,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            embedding_time = time.time() - start_time
            print(f"✅ Generated embeddings in {embedding_time:.2f}s")

            # Add to ChromaDB
            print("🔄 Adding documents to ChromaDB...")
            self.collection.add(
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ Successfully indexed {len(articles)} articles")
            print(f"📊 Total documents in collection: {self.collection.count()}")

        except Exception as e:
            print(f"❌ Error indexing articles: {e}")
            raise

    def get_stats(self):
        """Get collection statistics"""
        if self.collection is None:
            print("⚠️  Collection not initialized")
            return

        count = self.collection.count()
        print(f"\n📊 Collection Statistics:")
        print(f"   - Name: {self.collection_name}")
        print(f"   - Documents: {count}")
        print(f"   - Storage: {self.persist_directory}")

        return {
            'name': self.collection_name,
            'count': count,
            'storage': str(self.persist_directory)
        }


def main():
    """Main setup function"""
    print("=" * 60)
    print("NewsLens AI - ChromaDB Setup")
    print("=" * 60)

    # Initialize setup
    setup = ChromaDBSetup()

    # Create collection (reset=True to start fresh)
    setup.create_collection(reset=True)

    # Load articles
    articles = setup.load_articles()

    # Index articles if available
    if articles:
        setup.index_articles(articles)

    # Display statistics
    setup.get_stats()

    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
