from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from database.config import get_db
from backend.services.auth_service import get_current_user
from backend.services.ingestion_service import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    chunk_text,
    embed_text,
)
from ai.embeddings import embed_batch

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

# Pydantic schemas
class ChunkMetadata(BaseModel):
    session_id: UUID
    user_id: UUID
    source_filename: str
    chunk_text: str

class ChunkResponse(BaseModel):
    id: UUID
    session_id: UUID
    user_id: UUID
    source_filename: str
    chunk_text: str
    embedding: List[float]

# Routes
@router.post("/extract", response_model=List[ChunkResponse])
async def extract_and_chunk_file(
    file: UploadFile = File(...),
    session_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Extract text from a file, chunk it, embed the chunks, and store metadata in the database.
    """
    try:
        # Determine file type and extract text
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file.file)
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extracted_text = extract_text_from_docx(file.file)
        elif file.content_type == "text/plain":
            extracted_text = extract_text_from_txt(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Chunk the extracted text
        chunks = chunk_text(extracted_text, chunk_size=1000, overlap=200)

        # Embed the chunks
        embeddings = embed_batch(chunks)

        # Store chunks and embeddings in the database
        chunk_responses = []
        for chunk_text, embedding in zip(chunks, embeddings):
            chunk = DocumentChunk(
                session_id=session_id,
                user_id=current_user["id"],
                source_filename=file.filename,
                chunk_text=chunk_text,
                embedding=embedding,
            )
            db.add(chunk)
            db.commit()
            db.refresh(chunk)

            chunk_responses.append(
                ChunkResponse(
                    id=chunk.id,
                    session_id=chunk.session_id,
                    user_id=chunk.user_id,
                    source_filename=chunk.source_filename,
                    chunk_text=chunk.chunk_text,
                    embedding=chunk.embedding,
                )
            )

        return chunk_responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chunks", response_model=List[ChunkResponse])
async def list_chunks(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all chunks for a given session.
    """
    try:
        chunks = db.query(DocumentChunk).filter_by(session_id=session_id, user_id=current_user["id"]).all()
        return [
            ChunkResponse(
                id=chunk.id,
                session_id=chunk.session_id,
                user_id=chunk.user_id,
                source_filename=chunk.source_filename,
                chunk_text=chunk.chunk_text,
                embedding=chunk.embedding,
            )
            for chunk in chunks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chunks/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve a specific chunk by ID.
    """
    try:
        chunk = db.query(DocumentChunk).filter_by(id=chunk_id, user_id=current_user["id"]).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")

        return ChunkResponse(
            id=chunk.id,
            session_id=chunk.session_id,
            user_id=chunk.user_id,
            source_filename=chunk.source_filename,
            chunk_text=chunk.chunk_text,
            embedding=chunk.embedding,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chunks/{chunk_id}", response_model=dict)
async def delete_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a specific chunk by ID.
    """
    try:
        chunk = db.query(DocumentChunk).filter_by(id=chunk_id, user_id=current_user["id"]).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")

        db.delete(chunk)
        db.commit()
        return {"detail": "Chunk deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))