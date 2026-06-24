from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime
from database.models import User, Session as DBSession
from database.config import get_db
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/system", tags=["System"])

# Pydantic Schemas
class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    updated_at: datetime

class UserCreate(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="securepassword")

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, example="newemail@example.com")
    password: Optional[str] = Field(None, example="newsecurepassword")

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    expires_at: datetime

class SessionCreate(BaseModel):
    user_id: UUID
    expires_at: datetime

# Endpoints
@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID = Path(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = user_data.password  # Replace with actual hashing logic
    new_user = User(email=user_data.email, hashed_password=hashed_password, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID = Path(...), user_data: UserUpdate = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.hashed_password = user_data.password  # Replace with actual hashing logic
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: UUID = Path(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return

@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(DBSession).filter(DBSession.user_id == current_user.id).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID = Path(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(DBSession).filter(DBSession.id == session_id, DBSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_session = DBSession(user_id=session_data.user_id, created_at=datetime.utcnow(), expires_at=session_data.expires_at)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: UUID = Path(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(DBSession).filter(DBSession.id == session_id, DBSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return