from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import analyze, policy, upload, settings
from app.services.llm_service import LLMService
from app.middleware.rate_limiter import rate_limiter
import time
import asyncio

app = FastAPI(
    title="SecureData AI Platform API",
    version="1.0.0",
    description="Security analysis and data intelligence API"
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Apply rate limiting to API endpoints only
    if request.url.path.startswith("/api/"):
        try:
            await rate_limiter.check_rate_limit(
                request,
                max_requests=30,  # 30 requests
                window_seconds=60  # per minute
            )
        except Exception as e:
            # If rate limit check raises HTTPException, it will be caught here
            if hasattr(e, 'status_code') and e.status_code == 429:
                raise e

    response = await call_next(request)
    return response

# Register routes
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
# Also support document-specified /analyze (without /api prefix)
app.include_router(analyze.router, prefix="", tags=["analyze-compat"])
app.include_router(policy.router, prefix="/api", tags=["policy"])
# File upload endpoint
app.include_router(upload.router, prefix="/api", tags=["upload"])
# Settings endpoint
app.include_router(settings.router, prefix="/api", tags=["settings"])

@app.on_event("startup")
async def startup_event():
    """
    Start background tasks on application startup
    """
    # Start rate limiter cleanup task
    asyncio.create_task(rate_limiter.cleanup_old_entries())

@app.get("/")
async def root():
    return {
        "service": "SecureData AI Platform API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/info")
async def api_info():
    """
    API information and capabilities endpoint
    """
    llm_service = LLMService()
    provider_info = llm_service.get_provider_info()

    return {
        "api_version": "1.0.0",
        "service": "SecureData AI Platform",
        "capabilities": {
            "input_types": ["text", "log", "file", "sql", "chat"],
            "file_formats": ["txt", "log", "pdf", "docx"],
            "detection_types": ["regex", "heuristic"],
            "ai_provider": provider_info['provider'],
            "llm_enabled": provider_info['llm_enabled'],
            "features": {
                "masking": True,
                "risk_scoring": True,
                "policy_engine": True,
                "sql_analysis": True,
                "chat_analysis": True,
                "log_correlation": True,
                "cross_log_analysis": True,
                "chunking_large_files": True,
                "async_processing": True
            }
        },
        "endpoints": {
            "analyze": "/api/analyze",
            "upload": "/api/upload",
            "policy": "/api/policy",
            "settings": "/api/settings",
            "analyses": "/api/analyses",
            "health": "/health",
            "info": "/api/info"
        },
        "status": "operational"
    }
