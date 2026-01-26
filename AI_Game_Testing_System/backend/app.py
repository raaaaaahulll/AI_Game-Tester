"""
Main application entry point for the AI Game Testing System.

Sets up FastAPI application with production-grade middleware, error handling,
and configuration.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from routes.api import router
from routes.history import history_router
from routes.windows import windows_router
from config.settings import settings
from utils.logging import setup_logging, get_logger
from middlewares.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from utils.exceptions import GameTestingException

# Setup logging first
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting AI Game Testing System",
        extra={
            "extra_fields": {
                "environment": settings.ENVIRONMENT,
                "host": settings.API_HOST,
                "port": settings.API_PORT,
                "log_level": settings.LOG_LEVEL,
            }
        }
    )
    
    # Initialize metrics and reset status if no test is running
    from services.metrics_service import metrics_collector
    from controllers.rl_controller import rl_controller
    
    # Reset status to Idle on startup if no test is running
    if not rl_controller.is_running():
        metrics_collector.update("status", "Idle")
        logger.info("Reset metrics status to Idle on startup")
    
    logger.info("Application startup complete, ready to accept connections")
    
    yield
    # Shutdown
    logger.info("Shutting down AI Game Testing System")


# Create FastAPI app
app = FastAPI(
    title="AI Game Testing System",
    version="1.0.0",
    description="RESTful API for autonomous game testing using Reinforcement Learning",
    lifespan=lifespan,
    docs_url="/docs" if not settings.IS_PRODUCTION else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.IS_PRODUCTION else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# Custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Include API routers
app.include_router(router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(windows_router, prefix="/api")


# Global exception handlers
@app.exception_handler(GameTestingException)
async def game_testing_exception_handler(request: Request, exc: GameTestingException):
    """Handle custom game testing exceptions."""
    logger.warning(
        f"Game testing exception: {exc.message}",
        extra={
            "extra_fields": {
                "path": str(request.url.path),
                "details": exc.details,
            }
        }
    )
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "extra_fields": {
                "path": str(request.url.path),
                "status_code": exc.status_code,
            }
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(
        "Request validation error",
        extra={
            "extra_fields": {
                "path": str(request.url.path),
                "errors": exc.errors(),
            }
        }
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "Unhandled exception",
        extra={
            "extra_fields": {
                "path": str(request.url.path),
                "error_type": type(exc).__name__,
            }
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def read_root():
    """Root endpoint - health check."""
    return {
        "message": "AI Game Testing System Backend is Running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    from services.metrics_service import metrics_collector
    
    try:
        metrics = metrics_collector.get_all()
        return {
            "status": "healthy",
            "metrics_available": True,
            "current_status": metrics.get("status", "Unknown")
        }
    except Exception as e:
        logger.error("Health check failed", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import sys
    
    logger.info(f"Starting Uvicorn server on {settings.API_HOST}:{settings.API_PORT}")
    print(f"\n{'='*60}")
    print(f"Starting AI Game Testing System Backend")
    print(f"Server will be available at: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"API Documentation: http://localhost:{settings.API_PORT}/docs")
    print(f"{'='*60}\n")
    
    # Create a simple log config that shows uvicorn messages
    import logging
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    try:
        print("🚀 Starting server... (this may take a few seconds)")
        print("   Once you see 'Application startup complete', the server is ready!\n")
        
        uvicorn.run(
            app,  # Pass app directly instead of string to avoid import issues
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.API_RELOAD and settings.IS_DEVELOPMENT,
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(levelname)s:     %(message)s",
                    },
                },
                "handlers": {
                    "default": {
                        "formatter": "default",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    },
                },
                "loggers": {
                    "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
                    "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
                    "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
                },
            },
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n\n✅ Server stopped by user.")
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        print(f"\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

