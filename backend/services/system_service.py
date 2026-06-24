from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from database.models import User, Session as SessionModel
from backend.routers.auth import UserCreate, UserUpdate
from backend.routers.sessions import SessionCreate
from database.config import get_db


class SystemService:
    @staticmethod
    def create_user(user_data: UserCreate, db: Session) -> User:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
        
        new_user = User(
            id=UUID(),
            email=user_data.email,
            hashed_password=user_data.hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get_user_by_id(user_id: UUID, db: Session) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return user

    @staticmethod
    def list_all_users(db: Session) -> List[User]:
        users = db.query(User).all()
        return users

    @staticmethod
    def update_user(user_id: UUID, user_data: UserUpdate, db: Session) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        if user_data.email:
            user.email = user_data.email
        if user_data.hashed_password:
            user.hashed_password = user_data.hashed_password
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(user_id: UUID, db: Session) -> None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        db.delete(user)
        db.commit()

    @staticmethod
    def create_session(session_data: SessionCreate, db: Session) -> SessionModel:
        user = db.query(User).filter(User.id == session_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        new_session = SessionModel(
            id=UUID(),
            user_id=session_data.user_id,
            created_at=datetime.utcnow(),
            expires_at=session_data.expires_at
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    @staticmethod
    def get_session_by_id(session_id: UUID, db: Session) -> SessionModel:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found."
            )
        return session

    @staticmethod
    def list_all_sessions(db: Session) -> List[SessionModel]:
        sessions = db.query(SessionModel).all()
        return sessions

    @staticmethod
    def delete_session(session_id: UUID, db: Session) -> None:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found."
            )
        
        db.delete(session)
        db.commit()