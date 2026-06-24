from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import User, Document, Query, QuerySource, DocumentChunk
from backend.routers.ui import UserResponse, DocumentResponse, QueryResponse, QuerySourceResponse
from backend.routers.auth import UserCreate, UserUpdate
from backend.routers.document_management import DocumentCreate, DocumentUpdate
from backend.routers.query import QueryCreate
from database.config import get_db


class UIService:
    def create_user(self, user_data: UserCreate, db: Session) -> UserResponse:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
        new_user = User(
            id=user_data.id,
            email=user_data.email,
            hashed_password=user_data.hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return UserResponse.from_orm(new_user)

    def get_user_by_id(self, user_id: str, db: Session) -> UserResponse:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return UserResponse.from_orm(user)

    def list_all_users(self, db: Session) -> List[UserResponse]:
        users = db.query(User).all()
        return [UserResponse.from_orm(user) for user in users]

    def update_user(self, user_id: str, user_data: UserUpdate, db: Session) -> UserResponse:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        user.email = user_data.email or user.email
        user.hashed_password = user_data.hashed_password or user.hashed_password
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return UserResponse.from_orm(user)

    def delete_user(self, user_id: str, db: Session) -> None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        db.delete(user)
        db.commit()

    def create_document(self, document_data: DocumentCreate, db: Session) -> DocumentResponse:
        new_document = Document(
            id=document_data.id,
            user_id=document_data.user_id,
            session_id=document_data.session_id,
            filename=document_data.filename,
            original_filename=document_data.original_filename,
            file_size=document_data.file_size,
            mime_type=document_data.mime_type,
            status=document_data.status,
            uploaded_at=datetime.utcnow(),
            processed_at=document_data.processed_at,
            error_message=document_data.error_message
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        return DocumentResponse.from_orm(new_document)

    def get_document_by_id(self, document_id: str, db: Session) -> DocumentResponse:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found."
            )
        return DocumentResponse.from_orm(document)

    def list_all_documents(self, db: Session) -> List[DocumentResponse]:
        documents = db.query(Document).all()
        return [DocumentResponse.from_orm(document) for document in documents]

    def update_document(self, document_id: str, document_data: DocumentUpdate, db: Session) -> DocumentResponse:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found."
            )
        document.filename = document_data.filename or document.filename
        document.status = document_data.status or document.status
        document.processed_at = document_data.processed_at or document.processed_at
        document.error_message = document_data.error_message or document.error_message
        db.commit()
        db.refresh(document)
        return DocumentResponse.from_orm(document)

    def delete_document(self, document_id: str, db: Session) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found."
            )
        db.delete(document)
        db.commit()

    def create_query(self, query_data: QueryCreate, db: Session) -> QueryResponse:
        new_query = Query(
            id=query_data.id,
            user_id=query_data.user_id,
            session_id=query_data.session_id,
            question=query_data.question,
            answer=query_data.answer,
            created_at=datetime.utcnow()
        )
        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        return QueryResponse.from_orm(new_query)

    def get_query_by_id(self, query_id: str, db: Session) -> QueryResponse:
        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found."
            )
        return QueryResponse.from_orm(query)

    def list_all_queries(self, db: Session) -> List[QueryResponse]:
        queries = db.query(Query).all()
        return [QueryResponse.from_orm(query) for query in queries]

    def delete_query(self, query_id: str, db: Session) -> None:
        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found."
            )
        db.delete(query)
        db.commit()

    def get_query_sources(self, query_id: str, db: Session) -> List[QuerySourceResponse]:
        sources = db.query(QuerySource).filter(QuerySource.query_id == query_id).all()
        if not sources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query sources not found."
            )
        return [QuerySourceResponse.from_orm(source) for source in sources]