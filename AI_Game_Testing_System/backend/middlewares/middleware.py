"""
Custom middleware for the AI Game Testing System.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from utils.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        start_time = time.time()
        
        # Log request
        logger.info(
            "Incoming request",
            extra={
                "extra_fields": {
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": str(request.query_params),
                    "client_host": request.client.host if request.client else None,
                }
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": str(request.url.path),
                        "status_code": response.status_code,
                        "process_time_ms": round(process_time * 1000, 2),
                    }
                }
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": str(request.url.path),
                        "error": str(e),
                        "process_time_ms": round(process_time * 1000, 2),
                    }
                },
                exc_info=True
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Only add HSTS in production
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

