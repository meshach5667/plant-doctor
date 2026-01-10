"""
Global exception handlers for the Plant Doctor API.
Provides consistent error responses across the application.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from core.exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        logger.warning(
            f"AppException: {exc.error_code} - {exc.message}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "path": request.url.path,
                "details": exc.details
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
            headers={"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else {}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors with detailed messages."""
        errors = []
        for error in exc.errors():
            # Build field path, filtering out 'body' prefix for cleaner messages
            field_parts = [str(loc) for loc in error["loc"] if loc != "body"]
            field = ".".join(field_parts) if field_parts else "request"
            
            # Clean up the error message
            msg = error["msg"]
            # Remove "Value error, " prefix if present
            if msg.startswith("Value error, "):
                msg = msg[13:]
            
            errors.append({
                "field": field,
                "message": msg,
                "type": error["type"]
            })
        
        # Log with details for debugging
        logger.warning(
            f"Validation error on {request.url.path}: {errors}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "errors": errors
            }
        )
        
        # Build user-friendly error message
        if len(errors) == 1:
            detail_msg = f"Validation failed: {errors[0]['message']}"
        else:
            detail_msg = f"Validation failed with {len(errors)} errors"
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": detail_msg,
                    "details": {"errors": errors}
                }
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(
        request: Request, 
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle database errors."""
        logger.error(
            f"Database error: {str(exc)}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "path": request.url.path
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "A database error occurred",
                    "details": {}
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """Handle all unhandled exceptions."""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "path": request.url.path,
                "exception_type": type(exc).__name__
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred",
                    "details": {}
                }
            }
        )
