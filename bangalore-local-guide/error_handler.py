"""
Error Handler for Bangalore Local Guide
Provides comprehensive error handling and user feedback mechanisms.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ErrorType(Enum):
    """Types of errors that can occur in the application."""
    CONTEXT_LOADING = "context_loading"
    AGENT_INITIALIZATION = "agent_initialization"
    QUERY_PROCESSING = "query_processing"
    FILE_ACCESS = "file_access"
    NETWORK = "network"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """Information about an error occurrence."""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: str
    timestamp: datetime
    recovery_suggestions: List[str]
    can_retry: bool = False


class ErrorHandler:
    """Centralized error handling for the Bangalore Local Guide application."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error_history = []
    
    def handle_context_loading_error(self, exception: Exception, file_path: str) -> ErrorInfo:
        """Handle errors related to context file loading."""
        error_info = ErrorInfo(
            error_type=ErrorType.CONTEXT_LOADING,
            severity=ErrorSeverity.CRITICAL,
            message=f"Failed to load context from {file_path}",
            user_message="Unable to load Bangalore knowledge base. The application cannot function without this information.",
            technical_details=str(exception),
            timestamp=datetime.now(),
            recovery_suggestions=[
                "Check if product.md exists in the application directory",
                "Verify file permissions are correct",
                "Ensure the file is not corrupted or empty",
                "Try restarting the application"
            ],
            can_retry=True
        )
        
        self._log_error(error_info, exception)
        self._error_history.append(error_info)
        return error_info
    
    def handle_agent_initialization_error(self, exception: Exception, config_path: str) -> ErrorInfo:
        """Handle errors related to agent initialization."""
        error_info = ErrorInfo(
            error_type=ErrorType.AGENT_INITIALIZATION,
            severity=ErrorSeverity.HIGH,
            message=f"Failed to initialize Kiro agent with config {config_path}",
            user_message="Unable to start your local guide. The AI assistant is not available.",
            technical_details=str(exception),
            timestamp=datetime.now(),
            recovery_suggestions=[
                "Check if .kiro/config.yaml exists and is valid",
                "Verify Kiro agent configuration is correct",
                "Ensure all required dependencies are installed",
                "Try restarting the application"
            ],
            can_retry=True
        )
        
        self._log_error(error_info, exception)
        self._error_history.append(error_info)
        return error_info
    
    def handle_query_processing_error(self, exception: Exception, query: str) -> ErrorInfo:
        """Handle errors during query processing."""
        error_info = ErrorInfo(
            error_type=ErrorType.QUERY_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            message=f"Failed to process query: {query[:50]}...",
            user_message="Sorry, I couldn't understand or process your question. Please try rephrasing it.",
            technical_details=str(exception),
            timestamp=datetime.now(),
            recovery_suggestions=[
                "Try rephrasing your question",
                "Use simpler language",
                "Ask about specific topics like food, traffic, or culture",
                "Check if your question is related to Bangalore"
            ],
            can_retry=True
        )
        
        self._log_error(error_info, exception)
        self._error_history.append(error_info)
        return error_info
    
    def handle_file_access_error(self, exception: Exception, file_path: str) -> ErrorInfo:
        """Handle file access errors."""
        error_info = ErrorInfo(
            error_type=ErrorType.FILE_ACCESS,
            severity=ErrorSeverity.HIGH,
            message=f"Cannot access file: {file_path}",
            user_message="Unable to access required files. Some features may not work properly.",
            technical_details=str(exception),
            timestamp=datetime.now(),
            recovery_suggestions=[
                "Check if the file exists",
                "Verify file permissions",
                "Ensure the application has read access",
                "Try running with appropriate permissions"
            ],
            can_retry=True
        )
        
        self._log_error(error_info, exception)
        self._error_history.append(error_info)
        return error_info
    
    def handle_validation_error(self, message: str, details: str) -> ErrorInfo:
        """Handle validation errors."""
        error_info = ErrorInfo(
            error_type=ErrorType.VALIDATION,
            severity=ErrorSeverity.LOW,
            message=message,
            user_message="Please check your input and try again.",
            technical_details=details,
            timestamp=datetime.now(),
            recovery_suggestions=[
                "Verify your input is complete",
                "Check for any special characters",
                "Try a different approach to your question"
            ],
            can_retry=True
        )
        
        self.logger.warning(f"Validation error: {message}")
        self._error_history.append(error_info)
        return error_info
    
    def handle_unknown_error(self, exception: Exception, context: str = "") -> ErrorInfo:
        """Handle unexpected errors."""
        error_info = ErrorInfo(
            error_type=ErrorType.UNKNOWN,
            severity=ErrorSeverity.HIGH,
            message=f"Unexpected error occurred{': ' + context if context else ''}",
            user_message="Something unexpected happened. Please try again or contact support if the problem persists.",
            technical_details=str(exception),
            timestamp=datetime.now(),
            recovery_suggestions=[
                "Try refreshing the page",
                "Restart the application",
                "Check your internet connection",
                "Contact support if the problem persists"
            ],
            can_retry=True
        )
        
        self._log_error(error_info, exception)
        self._error_history.append(error_info)
        return error_info
    
    def _log_error(self, error_info: ErrorInfo, exception: Exception = None):
        """Log error information."""
        log_message = f"[{error_info.error_type.value.upper()}] {error_info.message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        if exception:
            self.logger.debug(f"Technical details: {error_info.technical_details}")
            self.logger.debug(f"Stack trace: {traceback.format_exc()}")
    
    def get_error_history(self) -> List[ErrorInfo]:
        """Get the history of errors."""
        return self._error_history.copy()
    
    def get_recent_errors(self, count: int = 5) -> List[ErrorInfo]:
        """Get the most recent errors."""
        return self._error_history[-count:] if self._error_history else []
    
    def clear_error_history(self):
        """Clear the error history."""
        self._error_history.clear()
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get statistics about errors."""
        if not self._error_history:
            return {"total_errors": 0}
        
        error_counts = {}
        severity_counts = {}
        
        for error in self._error_history:
            error_type = error.error_type.value
            severity = error.severity.value
            
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_errors": len(self._error_history),
            "error_types": error_counts,
            "severity_distribution": severity_counts,
            "most_recent": self._error_history[-1].timestamp if self._error_history else None
        }


# Global error handler instance
error_handler = ErrorHandler()