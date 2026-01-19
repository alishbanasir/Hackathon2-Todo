"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

# Create FastAPI app
app = FastAPI(
    title="Todo AI API",
    description="Phase II Todo App with Phase III AI Integration",
    version="0.1.0",
)

# Add CORS middleware - Updated for production safety
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, # Credentials true karein auth ke liye
    allow_methods=["*"],
    allow_headers=["*"],
)


# Basic health routes
@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"


@app.get("/")
def root():
    return {"message": "Todo AI API - Unified Backend", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "todo-ai-api"}


# Import and register API routers
# Note: Ensure these paths exist in your project structure
from src.api import auth, todos, chat 

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(todos.router, prefix="/api/v1", tags=["Todos"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chatbot"]) # AI Router added here