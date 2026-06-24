import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from database.config import init_db
from backend.routes.auth import router as auth_router
from backend.routes.sessions import router as sessions_router
from backend.routes.documents import router as documents_router

app = FastAPI(
    title="Aakaar Project",
    description="Backend API for Aakaar Project",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(sessions_router, prefix="/api/sessions")
app.include_router(documents_router, prefix="/api/documents")

# Lifespan context manager
@app.on_event("startup")
async def startup_event():
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    pass

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return {"detail": exc.detail, "status_code": exc.status_code}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return {"detail": exc.errors(), "status_code": 422}

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return {"detail": str(exc), "status_code": 500}

# AI_ROUTER_INJECTION_POINT — do not remove this line