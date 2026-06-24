import os
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import Document
from backend.routers.document_management import DocumentCreate, DocumentUpdate
from backend.routers.ui import DocumentResponse
from backend.routers.ingestion import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from backend.routers.document_management import validate_file_type
from env import get_url


class DocumentManagementService:
    def upload_document(self, file, session_id: str, current_user, db: Session) -> DocumentResponse:
        """
        Upload a document and save its metadata in the database.
        """
        # Validate file type
        validate_file_type(file)

        # Extract file metadata
        original_filename = file.filename
        mime_type = file.content_type
        file_size = len(file.file.read())
        file.file.seek(0)  # Reset file pointer after reading

        # Generate a unique filename and save the file
        filename = f"{datetime.utcnow().timestamp()}_{original_filename}"
        upload_path = os.path.join(get_url(), "uploads", filename)
        with open(upload_path, "wb") as f:
            f.write(file.file.read())

        # Create document record
        document = Document(
            user_id=current_user.id,
            session_id=session_id,
            filename=filename,
            original_filename=original_filename,
            file_size=file_size,
            mime_type=mime_type,
            status="uploaded",
            uploaded_at=datetime.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return DocumentResponse.from_orm(document)

    def get_document_by_id(self, document_id: str, db: Session, current_user) -> DocumentResponse:
        """
        Retrieve a document by its ID.
        """
        document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return DocumentResponse.from_orm(document)

    def list_documents(self, db: Session, current_user) -> List[DocumentResponse]:
        """
        List all documents for the current user.
        """
        documents = db.query(Document).filter(Document.user_id == current_user.id).all()
        return [DocumentResponse.from_orm(doc) for doc in documents]

    def update_document(self, document_id: str, document_update: DocumentUpdate, db: Session, current_user) -> DocumentResponse:
        """
        Update document details.
        """
        document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        for key, value in document_update.dict(exclude_unset=True).items():
            setattr(document, key, value)

        document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(document)

        return DocumentResponse.from_orm(document)

    def delete_document(self, document_id: str, db: Session, current_user) -> None:
        """
        Delete a document by its ID.
        """
        document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Delete the file from the filesystem
        file_path = os.path.join(get_url(), "uploads", document.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the document record
        db.delete(document)
        db.commit()