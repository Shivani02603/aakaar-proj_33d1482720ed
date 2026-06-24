from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import Document
from database.config import get_db
from backend.services.auth_service import get_current_user
from backend.services.document_service import validate_file_type, upload_document, delete_document_by_id, update_document_details, list_all_documents, get_document_by_id
from datetime import datetime

router = APIRouter(prefix="/document-management", tags=["Document Management"])

# Pydantic Schemas
class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class DocumentCreate(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str

class DocumentUpdate(BaseModel):
    status: Optional[str] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID
    session_id: UUID

# Routes
@router.post("/", response_model=DocumentResponse)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    session_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    """
    Upload a document in PDF, DOCX, or TXT format.
    """
    validate_file_type(file)
    document = await upload_document(file, session_id, current_user, db)
    return document

@router.get("/", response_model=List[DocumentResponse])
async def list_documents_endpoint(
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    """
    List all documents for the current user.
    """
    documents = await list_all_documents(db, current_user)
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_endpoint(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    """
    Retrieve a document by its ID.
    """
    document = await get_document_by_id(document_id, db, current_user)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document_endpoint(
    document_id: UUID,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    """
    Update details of a document.
    """
    updated_document = await update_document_details(document_id, document_update, db, current_user)
    if not updated_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated_document

@router.delete("/{document_id}")
async def delete_document_endpoint(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    """
    Delete a document by its ID.
    """
    success = await delete_document_by_id(document_id, db, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"detail": "Document deleted successfully"}