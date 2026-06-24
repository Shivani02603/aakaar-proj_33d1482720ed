from fastapi import APIRouter, Depends, HTTPException, Query as FastAPIQuery
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import Query, QuerySource, DocumentChunk
from database.config import get_db
from backend.services.auth_service import get_current_user
from backend.routers.ui import list_queries, get_query, delete_query
from backend.routers.query import embed_question, similarity_search, build_context_prompt, call_llm

router = APIRouter(prefix="/query", tags=["Query"])

# Pydantic Schemas
class QueryBase(BaseModel):
    question: str = Field(..., description="The natural-language question asked by the user.")

class QueryCreate(QueryBase):
    session_id: UUID = Field(..., description="The session ID associated with the query.")

class QueryResponse(BaseModel):
    id: UUID
    question: str
    answer: str
    sources: List[dict] = Field(..., description="List of source chunks used to generate the answer.")
    created_at: str

class QuerySourceResponse(BaseModel):
    chunk_id: UUID
    similarity_score: float

# Routes
@router.get("/", response_model=List[QueryResponse])
def list_user_queries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all queries for the current user."""
    return list_queries(current_user, db)

@router.get("/{query_id}", response_model=QueryResponse)
def get_user_query(
    query_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve a specific query by ID."""
    return get_query(query_id, current_user, db)

@router.post("/", response_model=QueryResponse)
async def create_query(
    query_data: QueryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new query and return the answer with sources."""
    # Embed the user's question
    question_embedding = embed_question(query_data.question)

    # Perform similarity search
    chunks = similarity_search(db, question_embedding, query_data.session_id)

    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")

    # Take the top 5 chunks
    top_chunks = sorted(chunks, key=lambda x: x.similarity_score, reverse=True)[:5]

    # Build context prompt
    context_prompt = build_context_prompt([chunk.chunk_text for chunk in top_chunks])

    # Call the LLM
    answer = call_llm(context_prompt)

    # Save the query and sources in the database
    new_query = Query(
        user_id=current_user["id"],
        session_id=query_data.session_id,
        question=query_data.question,
        answer=answer,
    )
    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    for chunk in top_chunks:
        query_source = QuerySource(
            query_id=new_query.id,
            chunk_id=chunk.id,
            similarity_score=chunk.similarity_score,
        )
        db.add(query_source)

    db.commit()

    # Prepare response
    sources_response = [
        {"chunk_id": chunk.id, "similarity_score": chunk.similarity_score}
        for chunk in top_chunks
    ]
    return QueryResponse(
        id=new_query.id,
        question=new_query.question,
        answer=new_query.answer,
        sources=sources_response,
        created_at=new_query.created_at.isoformat(),
    )

@router.delete("/{query_id}")
def delete_user_query(
    query_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a specific query by ID."""
    return delete_query(query_id, db, current_user)