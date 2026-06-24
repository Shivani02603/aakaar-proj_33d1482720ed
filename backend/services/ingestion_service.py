import os
from typing import List
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from backend.routers.ingestion import ChunkMetadata
from ai.embeddings import embed_text
from database.config import get_db
from pypdf import PdfReader
from docx import Document as DocxDocument

class IngestionService:
    CHUNK_SIZE = 1000
    OVERLAP = 200

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error extracting text from PDF: {str(e)}"
            )

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error extracting text from DOCX: {str(e)}"
            )

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error extracting text from TXT: {str(e)}"
            )

    @staticmethod
    def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    @staticmethod
    def embed_text_chunk(chunk_text: str) -> List[float]:
        try:
            return embed_text(chunk_text)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error embedding text chunk: {str(e)}"
            )

    @staticmethod
    def create_document_chunks(
        session_id: str,
        user_id: str,
        filename: str,
        text: str,
        db: Session
    ) -> List[ChunkMetadata]:
        chunks = IngestionService.chunk_text(text, IngestionService.CHUNK_SIZE, IngestionService.OVERLAP)
        chunk_metadata_list = []

        for index, chunk_text in enumerate(chunks):
            embedding = IngestionService.embed_text_chunk(chunk_text)
            chunk = DocumentChunk(
                session_id=session_id,
                user_id=user_id,
                source_filename=filename,
                chunk_index=index,
                chunk_text=chunk_text,
                embedding=embedding,
                created_at=datetime.utcnow()
            )
            db.add(chunk)
            chunk_metadata_list.append(ChunkMetadata(
                chunk_index=index,
                chunk_text=chunk_text,
                embedding=embedding
            ))

        db.commit()
        return chunk_metadata_list

    @staticmethod
    def ingest_document(file_path: str, session_id: str, user_id: str, db: Session) -> List[ChunkMetadata]:
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".pdf":
            text = IngestionService.extract_text_from_pdf(file_path)
        elif file_extension == ".docx":
            text = IngestionService.extract_text_from_docx(file_path)
        elif file_extension == ".txt":
            text = IngestionService.extract_text_from_txt(file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type"
            )

        return IngestionService.create_document_chunks(session_id, user_id, os.path.basename(file_path), text, db)

    @staticmethod
    def get_document_by_id(document_id: str, db: Session) -> DocumentChunk:
        document_chunk = db.query(DocumentChunk).filter(DocumentChunk.id == document_id).first()
        if not document_chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document chunk not found"
            )
        return document_chunk

    @staticmethod
    def list_all_chunks(session_id: str, user_id: str, db: Session) -> List[DocumentChunk]:
        return db.query(DocumentChunk).filter(
            DocumentChunk.session_id == session_id,
            DocumentChunk.user_id == user_id
        ).all()

    @staticmethod
    def update_chunk(chunk_id: str, updated_chunk_text: str, db: Session) -> DocumentChunk:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chunk not found"
            )

        chunk.chunk_text = updated_chunk_text
        chunk.embedding = IngestionService.embed_text_chunk(updated_chunk_text)
        chunk.updated_at = datetime.utcnow()
        db.commit()
        return chunk

    @staticmethod
    def delete_chunk(chunk_id: str, db: Session) -> None:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chunk not found"
            )

        db.delete(chunk)
        db.commit()