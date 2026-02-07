"""
PocketBuzz - FastAPI Main Application
The AI Marketing Agent that lives in a restaurant owner's pocket.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import webhook, campaigns, auth, mock_sendgrid, whatsapp_webhook

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered retention marketing for Indian SMB restaurants",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.app_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://named-allied-herb-fifteen.trycloudflare.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(mock_sendgrid.router, prefix="/mock", tags=["Mock/Testing"])
app.include_router(whatsapp_webhook.router, prefix="/webhook", tags=["WhatsApp"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "ok",
        "services": {
            "api": "running",
            "database": "connected" if settings.supabase_url else "not configured"
        }
    }
