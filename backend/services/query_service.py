from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import Query, QuerySource, DocumentChunk
from backend.routers.query import QueryCreate, QueryBase
from ai.embeddings import embed_question
from backend.routers.query import build_context_prompt, similarity_search, call_llm


class QueryService:
    @staticmethod
    def create_query(query_data: QueryCreate, user_id: str, session_id: str, db: Session) -> Query:
        """
        Create a new query and store it in the database.
        """
        embedded_question = embed_question(query_data.question)
        top_chunks = similarity_search(db, embedded_question, session_id)

        if not top_chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant chunks found for the query."
            )

        context_prompt = build_context_prompt(top_chunks)
        answer = call_llm(context_prompt)

        query = Query(
            id=query_data.id,
            user_id=user_id,
            session_id=session_id,
            question=query_data.question,
            answer=answer,
            created_at=datetime.utcnow()
        )
        db.add(query)
        db.commit()

        for chunk in top_chunks[:5]:  # Limit to top 5 chunks
            query_source = QuerySource(
                query_id=query.id,
                chunk_id=chunk.id,
                similarity_score=chunk.similarity_score
            )
            db.add(query_source)

        db.commit()
        return query

    @staticmethod
    def get_query_by_id(query_id: str, user_id: str, db: Session) -> Query:
        """
        Retrieve a query by its ID.
        """
        query = db.query(Query).filter(Query.id == query_id, Query.user_id == user_id).first()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found."
            )
        return query

    @staticmethod
    def list_queries(user_id: str, db: Session) -> List[Query]:
        """
        List all queries for a specific user.
        """
        queries = db.query(Query).filter(Query.user_id == user_id).all()
        return queries

    @staticmethod
    def delete_query(query_id: str, user_id: str, db: Session) -> None:
        """
        Delete a query by its ID.
        """
        query = db.query(Query).filter(Query.id == query_id, Query.user_id == user_id).first()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found."
            )
        db.query(QuerySource).filter(QuerySource.query_id == query_id).delete()
        db.delete(query)
        db.commit()

    @staticmethod
    def process_query(query_data: QueryBase, user_id: str, session_id: str, db: Session) -> dict:
        """
        Process a query by embedding the question, performing similarity search, and calling the LLM.
        """
        embedded_question = embed_question(query_data.question)
        top_chunks = similarity_search(db, embedded_question, session_id)

        if not top_chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant chunks found for the query."
            )

        context_prompt = build_context_prompt(top_chunks)
        answer = call_llm(context_prompt)

        sources = [
            {
                "chunk_id": chunk.id,
                "similarity_score": chunk.similarity_score,
                "chunk_text": chunk.chunk_text
            }
            for chunk in top_chunks[:5]  # Limit to top 5 chunks
        ]

        return {
            "answer": answer,
            "sources": sources
        }