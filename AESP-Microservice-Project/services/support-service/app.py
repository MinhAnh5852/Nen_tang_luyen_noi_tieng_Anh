from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base
from config import settings
from controllers import ticket_controller, report_controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Support Service...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("Shutting down Support Service...")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ticket_controller.router)
app.include_router(report_controller.router)

@app.get("/")
def root():
    return {
        "service": "Support Service",
        "status": "running",
        "endpoints": {
            "tickets": "/api/support/tickets",
            "feedback": "/api/support/feedback",
            "reports": "/api/reports",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)