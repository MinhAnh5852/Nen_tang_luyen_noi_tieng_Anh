from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from database import engine, Base
from config import settings
from controllers import chat_controller, session_controller, audio_controller

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/chat_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Tạo tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Chat Service...")
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Chat Service...")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI English Speaking Practice Chat Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Security middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com"]
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)

# Include routers
app.include_router(chat_controller.router)
app.include_router(session_controller.router)
app.include_router(audio_controller.router)

@app.get("/")
async def root():
    return {
        "service": "Chat Service",
        "status": "running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "sessions": "/api/chat/sessions",
            "messages": "/api/chat/sessions/{id}/messages",
            "audio": "/api/chat/audio",
            "websocket": "/api/chat/ws/{session_id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    from database import redis_client
    
    # Check database connection
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis connection
    redis_status = "healthy"
    try:
        redis_client.ping()
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        }
    }

@app.get("/config")
async def get_config():
    """Lấy thông tin cấu hình (chỉ trong development)"""
    if settings.ENVIRONMENT != "development":
        return {"message": "Not available in production"}
    
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_url": "***" if "password" in settings.DATABASE_URL else settings.DATABASE_URL,
        "websocket_port": settings.WEBSOCKET_PORT,
        "max_audio_size_mb": settings.MAX_AUDIO_SIZE_MB
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )