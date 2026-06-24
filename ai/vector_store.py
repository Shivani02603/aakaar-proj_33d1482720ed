import os
from typing import List, Dict
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from database.config import SessionLocal

class VectorStore:
    def __init__(self):
        pass

    def _get_db_session(self) -> Session:
        """
        Lazily initialize and return a database session.
        """
        return SessionLocal()

    def upsert(self, id: int, vector: List[float], doc_metadata: Dict) -> None:
        """
        Add or update a DocumentChunk row in the database.
        """
        if len(vector) != 1536:  # Ensure vector dimensionality matches the spec
            raise ValueError(f"Vector dimensionality must be {1536}, got {len(vector)}.")
        
        session = self._get_db_session()
        try:
            chunk = session.query(DocumentChunk).filter_by(id=id).first()
            if chunk:
                # Update existing row
                chunk.embedding = vector
                chunk.doc_metadata = doc_metadata
            else:
                # Insert new row
                chunk = DocumentChunk(id=id, embedding=vector, doc_metadata=doc_metadata)
                session.add(chunk)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def search(self, query_embedding: List[float], top_k: int) -> List[Dict]:
        """
        Search for the top_k most similar document chunks based on cosine distance.
        """
        if len(query_embedding) != 1536:  # Ensure query embedding dimensionality matches the spec
            raise ValueError(f"Query embedding dimensionality must be {1536}, got {len(query_embedding)}.")
        
        session = self._get_db_session()
        try:
            results = (
                session.query(DocumentChunk)
                .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
                .all()
            )
            return [
                {"id": chunk.id, "content": chunk.content, "doc_metadata": chunk.doc_metadata}
                for chunk in results
            ]
        finally:
            session.close()

# Singleton instance of VectorStore
vector_store = VectorStore()