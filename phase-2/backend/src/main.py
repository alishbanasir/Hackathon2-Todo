"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="Phase II Todo Full-Stack Web Application - Backend API",
    version="0.1.0",
)

# Add CORS middleware - Allow ALL origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Basic health routes
@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"


@app.get("/")
def root():
    return {"message": "Todo API - Phase II", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "todo-api"}


# Import and register API routers
from src.api import auth, todos

app.include_router(auth.router, prefix="/api/v1")
app.include_router(todos.router, prefix="/api/v1")
