"""
Error Handling
==============
Centralized error definitions and exception handlers.
"""

from typing import Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)
    
    def to_response(self) -> ErrorResponse:
        """Convert to error response."""
        return ErrorResponse(
            error_code=self.error_code,
            message=self.message,
            details=self.details,
        )


class ValidationError(AppException):
    """Validation error for bad input."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(AppException):
    """Resource not found error."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type} if resource_type else None,
        )


class BusinessRuleViolation(AppException):
    """Business rule violation error."""
    
    def __init__(self, message: str, rule: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_VIOLATION",
            status_code=400,
            details={"rule": rule} if rule else None,
        )


class AuthenticationError(AppException):
    """Authentication failure."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
        )


class AuthorizationError(AppException):
    """Authorization failure."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
        )


class RateLimitError(AppException):
    """Rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class DatabaseError(AppException):
    """Database operation error."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
        )


class ExternalServiceError(AppException):
    """External service error."""
    
    def __init__(self, message: str, service_name: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service_name} if service_name else None,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI app."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Handle application exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_response().model_dump(),
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request,
        exc: ValueError,
    ) -> JSONResponse:
        """Handle value errors as validation errors."""
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_code="VALIDATION_ERROR",
                message=str(exc),
            ).model_dump(),
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        # Log the error (don't expose details to client)
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred",
            ).model_dump(),
        )
