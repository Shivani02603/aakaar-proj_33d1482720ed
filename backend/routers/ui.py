from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import User, Document, Query, QuerySource, DocumentChunk
from database.config import get_db
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/ui", tags=["UI"])

# Pydantic Schemas
class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: str
    updated_at: str

class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_id: UUID
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    uploaded_at: str
    processed_at: Optional[str]
    error_message: Optional[str]

class QueryResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_id: UUID
    question: str
    answer: str
    created_at: str

class QuerySourceResponse(BaseModel):
    id: UUID
    query_id: UUID
    chunk_id: UUID
    similarity_score: float

class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    user_id: UUID
    session_id: UUID
    chunk_index: int
    chunk_text: str
    embedding: List[float]
    created_at: str

# Routes
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat(),
    )

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return [
        DocumentResponse(
            id=doc.id,
            user_id=doc.user_id,
            session_id=doc.session_id,
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_size=doc.file_size,
            mime_type=doc.mime_type,
            status=doc.status,
            uploaded_at=doc.uploaded_at.isoformat(),
            processed_at=doc.processed_at.isoformat() if doc.processed_at else None,
            error_message=doc.error_message,
        )
        for doc in documents
    ]

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID = Path(..., description="The ID of the document to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.query(Document).filter(
        Document.id == document_id, Document.user_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        session_id=document.session_id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_size=document.file_size,
        mime_type=document.mime_type,
        status=document.status,
        uploaded_at=document.uploaded_at.isoformat(),
        processed_at=document.processed_at.isoformat() if document.processed_at else None,
        error_message=document.error_message,
    )

@router.get("/queries", response_model=List[QueryResponse])
def list_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    queries = db.query(Query).filter(Query.user_id == current_user.id).all()
    return [
        QueryResponse(
            id=query.id,
            user_id=query.user_id,
            session_id=query.session_id,
            question=query.question,
            answer=query.answer,
            created_at=query.created_at.isoformat(),
        )
        for query in queries
    ]

@router.get("/queries/{query_id}", response_model=QueryResponse)
def get_query(
    query_id: UUID = Path(..., description="The ID of the query to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Query).filter(
        Query.id == query_id, Query.user_id == current_user.id
    ).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return QueryResponse(
        id=query.id,
        user_id=query.user_id,
        session_id=query.session_id,
        question=query.question,
        answer=query.answer,
        created_at=query.created_at.isoformat(),
    )

@router.get("/queries/{query_id}/sources", response_model=List[QuerySourceResponse])
def get_query_sources(
    query_id: UUID = Path(..., description="The ID of the query to retrieve sources for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sources = db.query(QuerySource).filter(
        QuerySource.query_id == query_id
    ).all()
    return [
        QuerySourceResponse(
            id=source.id,
            query_id=source.query_id,
            chunk_id=source.chunk_id,
            similarity_score=source.similarity_score,
        )
        for source in sources
    ]

@router.get("/documents/{document_id}/chunks", response_model=List[DocumentChunkResponse])
def get_document_chunks(
    document_id: UUID = Path(..., description="The ID of the document to retrieve chunks for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id, DocumentChunk.user_id == current_user.id
    ).all()
    return [
        DocumentChunkResponse(
            id=chunk.id,
            document_id=chunk.document_id,
            user_id=chunk.user_id,
            session_id=chunk.session_id,
            chunk_index=chunk.chunk_index,
            chunk_text=chunk.chunk_text,
            embedding=chunk.embedding,
            created_at=chunk.created_at.isoformat(),
        )
        for chunk in chunks
    ]