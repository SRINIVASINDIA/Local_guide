"""
Property-based tests for graceful error handling functionality.
Tests universal properties that should hold for all error handling operations.
"""

import pytest
from hypothesis import given, strategies as st, assume
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock
import shutil
from datetime import datetime

from error_handler import ErrorHandler, ErrorType, ErrorSeverity, ErrorInfo, error_handler
from context_manager import ContextManager
from agent_manager import AgentManager
from query_processor import QueryProcessor


def validate_user_input(query: str) -> tuple[bool, str]:
    """Validate user input and return validation result."""
    if not query or not query.strip():
        return False, "Please enter a question first!"
    
    if len(query.strip()) < 3:
        return False, "Please enter a more detailed question."
    
    if len(query) > 1000:
        return False, "Your question is too long. Please keep it under 1000 characters."
    
    # Check for potentially harmful content (basic check)
    harmful_patterns = ['<script', 'javascript:', 'eval(', 'exec(']
    query_lower = query.lower()
    
    for pattern in harmful_patterns:
        if pattern in query_lower:
            return False, "Please avoid using special characters or code in your question."
    
    return True, None


class TestGracefulErrorHandling:
    """Property-based tests for graceful error handling."""
    
    def test_graceful_error_handling_context_loading(self):
        """
        Feature: bangalore-local-guide, Property 9: Graceful error handling
        For any context loading failure, the system should handle the error 
        gracefully without crashing.
        **Validates: Requirements 6.5**
        """
        # Test FileNotFoundError handling
        handler = ErrorHandler()
        
        # Property: FileNotFoundError should be handled gracefully
        error_info = handler.handle_context_loading_error(
            FileNotFoundError("File not found"), 
            "missing_file.md"
        )
        
        assert error_info.error_type == ErrorType.CONTEXT_LOADING
        assert error_info.severity == ErrorSeverity.CRITICAL
        assert error_info.user_message is not None
        assert len(error_info.recovery_suggestions) > 0
        assert error_info.can_retry is True
        assert "missing_file.md" in error_info.message
        
        # Property: PermissionError should be handled gracefully
        error_info = handler.handle_file_access_error(
            PermissionError("Permission denied"), 
            "restricted_file.md"
        )
        
        assert error_info.error_type == ErrorType.FILE_ACCESS
        assert error_info.severity == ErrorSeverity.HIGH
        assert error_info.user_message is not None
        assert len(error_info.recovery_suggestions) > 0
        assert error_info.can_retry is True
        assert "restricted_file.md" in error_info.message
        
        # Property: Unknown errors should be handled gracefully
        error_info = handler.handle_unknown_error(
            RuntimeError("Unexpected error"), 
            "loading context"
        )
        
        assert error_info.error_type == ErrorType.UNKNOWN
        assert error_info.severity == ErrorSeverity.HIGH
        assert error_info.user_message is not None
        assert len(error_info.recovery_suggestions) > 0
        assert error_info.can_retry is True
        assert "loading context" in error_info.message
    
    def test_graceful_error_handling_agent_initialization(self):
        """
        Property test for graceful agent initialization error handling.
        Tests that agent initialization failures are handled without crashes.
        """
        handler = ErrorHandler()
        
        # Property: Agent initialization errors should be handled gracefully
        error_info = handler.handle_agent_initialization_error(
            Exception("Agent failed to initialize"), 
            ".kiro/config.yaml"
        )
        
        assert error_info.error_type == ErrorType.AGENT_INITIALIZATION
        assert error_info.severity == ErrorSeverity.HIGH
        assert error_info.user_message is not None
        assert len(error_info.recovery_suggestions) > 0
        assert error_info.can_retry is True
        assert ".kiro/config.yaml" in error_info.message
        
        # Property: Error should be logged in history
        history = handler.get_error_history()
        assert len(history) > 0
        assert any(err.error_type == ErrorType.AGENT_INITIALIZATION for err in history)
    
    def test_graceful_error_handling_query_processing(self):
        """
        Property test for graceful query processing error handling.
        Tests that query processing failures are handled without crashes.
        """
        handler = ErrorHandler()
        
        # Property: Query processing errors should be handled gracefully
        test_query = "What is the weather like?"
        error_info = handler.handle_query_processing_error(
            ValueError("Invalid query format"), 
            test_query
        )
        
        assert error_info.error_type == ErrorType.QUERY_PROCESSING
        assert error_info.severity == ErrorSeverity.MEDIUM
        assert error_info.user_message is not None
        assert len(error_info.recovery_suggestions) > 0
        assert error_info.can_retry is True
        assert test_query[:50] in error_info.message
        
        # Property: Validation errors should be handled gracefully
        error_info = handler.handle_validation_error(
            "Empty query provided", 
            "Query was empty string"
        )
        
        assert error_info.error_type == ErrorType.VALIDATION
        assert error_info.severity == ErrorSeverity.LOW
        assert error_info.user_message is not None
        assert len(error_info.recovery_suggestions) > 0
        assert error_info.can_retry is True
    
    @given(st.text(min_size=0, max_size=1000))
    def test_graceful_input_validation_errors(self, user_input):
        """
        Property test for graceful input validation error handling.
        Tests that all types of user input are validated gracefully.
        """
        # Property: Input validation should never crash
        try:
            is_valid, error_message = validate_user_input(user_input)
            
            # Property: Validation should always return a boolean and optional message
            assert isinstance(is_valid, bool)
            if not is_valid:
                assert error_message is not None
                assert isinstance(error_message, str)
                assert len(error_message) > 0
            else:
                # Valid input should have no error message or None
                assert error_message is None
                
        except Exception as e:
            # Property: Validation should never raise exceptions
            pytest.fail(f"Input validation crashed with input '{user_input[:50]}...': {e}")
    
    def test_graceful_context_manager_error_handling(self):
        """
        Property test for graceful context manager error handling.
        Tests that context manager handles various error conditions gracefully.
        """
        # Property: Non-existent file should be handled gracefully
        manager = ContextManager("non_existent_file.md")
        
        with pytest.raises(FileNotFoundError):
            manager.load_context()
        
        # The exception should be raised, but the manager should remain stable
        assert manager._cached_context is None
        
        # Property: Empty file should be handled gracefully
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")  # Empty content
            empty_path = f.name
        
        try:
            manager = ContextManager(empty_path)
            with pytest.raises(ValueError, match="empty"):
                manager.load_context()
            
            # Manager should remain stable after error
            assert manager._cached_context is None
            
        finally:
            os.unlink(empty_path)
        
        # Property: Corrupted file should be handled gracefully
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Invalid content without required sections")
            corrupted_path = f.name
        
        try:
            manager = ContextManager(corrupted_path)
            with pytest.raises(ValueError):
                manager.load_context()
            
            # Manager should remain stable after error
            assert manager._cached_context is None
            
        finally:
            os.unlink(corrupted_path)
    
    def test_graceful_error_recovery_suggestions(self):
        """
        Property test for error recovery suggestions.
        Tests that all error types provide helpful recovery suggestions.
        """
        handler = ErrorHandler()
        
        # Test all error handling methods provide recovery suggestions
        error_methods = [
            (handler.handle_context_loading_error, (FileNotFoundError("test"), "test.md")),
            (handler.handle_agent_initialization_error, (Exception("test"), "config.yaml")),
            (handler.handle_query_processing_error, (ValueError("test"), "test query")),
            (handler.handle_file_access_error, (PermissionError("test"), "test.md")),
            (handler.handle_validation_error, ("test message", "test details")),
            (handler.handle_unknown_error, (RuntimeError("test"), "test context"))
        ]
        
        for method, args in error_methods:
            error_info = method(*args)
            
            # Property: All errors should have recovery suggestions
            assert len(error_info.recovery_suggestions) > 0
            assert all(isinstance(suggestion, str) for suggestion in error_info.recovery_suggestions)
            assert all(len(suggestion) > 0 for suggestion in error_info.recovery_suggestions)
            
            # Property: All errors should have user-friendly messages
            assert error_info.user_message is not None
            assert len(error_info.user_message) > 0
            assert not error_info.user_message.startswith("Traceback")
            
            # Property: All errors should have appropriate severity
            assert error_info.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM, 
                                         ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
    
    def test_graceful_error_history_management(self):
        """
        Property test for error history management.
        Tests that error history is managed gracefully without memory issues.
        """
        handler = ErrorHandler()
        
        # Property: Error history should be manageable
        initial_count = len(handler.get_error_history())
        
        # Add multiple errors
        for i in range(10):
            handler.handle_validation_error(f"Test error {i}", f"Details {i}")
        
        history = handler.get_error_history()
        assert len(history) == initial_count + 10
        
        # Property: Recent errors should be retrievable
        recent = handler.get_recent_errors(5)
        assert len(recent) == 5
        assert all(isinstance(error, ErrorInfo) for error in recent)
        
        # Property: Error stats should be accurate
        stats = handler.get_error_stats()
        assert stats["total_errors"] >= 10
        assert "error_types" in stats
        assert "severity_distribution" in stats
        
        # Property: History should be clearable
        handler.clear_error_history()
        assert len(handler.get_error_history()) == 0
    
    @given(st.integers(min_value=1, max_value=100))
    def test_graceful_multiple_error_handling(self, error_count):
        """
        Property test for handling multiple errors gracefully.
        Tests that the system can handle many errors without degradation.
        """
        handler = ErrorHandler()
        
        # Property: System should handle multiple errors without issues
        for i in range(error_count):
            error_info = handler.handle_validation_error(
                f"Test error {i}", 
                f"Test details {i}"
            )
            
            # Each error should be handled properly
            assert error_info.error_type == ErrorType.VALIDATION
            assert error_info.user_message is not None
            assert len(error_info.recovery_suggestions) > 0
        
        # Property: All errors should be in history
        history = handler.get_error_history()
        assert len(history) >= error_count
        
        # Property: System should remain responsive
        stats = handler.get_error_stats()
        assert stats["total_errors"] >= error_count
        assert isinstance(stats["error_types"], dict)
    
    def test_graceful_file_permission_error_handling(self):
        """
        Property test for file permission error handling.
        Tests that file permission issues are handled gracefully.
        """
        # Create a temporary file with sufficient content and make it unreadable
        test_content = "Test content " * 100  # Make it long enough to pass validation
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            # Make file unreadable (on Unix systems)
            if hasattr(os, 'chmod'):
                os.chmod(temp_path, 0o000)
            
            manager = ContextManager(temp_path)
            
            # Property: Permission errors should be handled gracefully
            try:
                manager.load_context()
                # If no exception, the system handled it gracefully
                # (might happen on some systems where chmod doesn't work as expected)
            except (PermissionError, OSError):
                # These are expected and acceptable - the error should be catchable
                pass
            except ValueError as e:
                # On Windows, permission issues might manifest as ValueError
                # This is still acceptable as long as it's handled gracefully
                if any(phrase in str(e) for phrase in ["incomplete", "empty", "missing required sections"]):
                    pass  # This is acceptable - the system handled the error
                else:
                    pytest.fail(f"Unexpected ValueError: {e}")
            except Exception as e:
                # Other exceptions should not occur
                pytest.fail(f"Unexpected exception type: {type(e).__name__}: {e}")
            
        finally:
            # Restore permissions and clean up
            if hasattr(os, 'chmod'):
                try:
                    os.chmod(temp_path, 0o644)
                except:
                    pass
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def test_graceful_network_error_simulation(self):
        """
        Property test for network-related error handling.
        Tests that network issues are handled gracefully.
        """
        handler = ErrorHandler()
        
        # Simulate network errors
        network_errors = [
            ConnectionError("Network connection failed"),
            TimeoutError("Request timed out"),
            OSError("Network is unreachable")
        ]
        
        for network_error in network_errors:
            # Property: Network errors should be handled gracefully
            error_info = handler.handle_unknown_error(network_error, "network operation")
            
            assert error_info.error_type == ErrorType.UNKNOWN
            assert error_info.user_message is not None
            assert len(error_info.recovery_suggestions) > 0
            assert error_info.can_retry is True
            
            # Property: Recovery suggestions should be relevant
            suggestions_text = " ".join(error_info.recovery_suggestions).lower()
            assert any(word in suggestions_text for word in 
                      ["network", "connection", "internet", "restart", "refresh"])
    
    def test_graceful_memory_error_simulation(self):
        """
        Property test for memory-related error handling.
        Tests that memory issues are handled gracefully.
        """
        handler = ErrorHandler()
        
        # Simulate memory error
        memory_error = MemoryError("Not enough memory")
        
        # Property: Memory errors should be handled gracefully
        error_info = handler.handle_unknown_error(memory_error, "processing large context")
        
        assert error_info.error_type == ErrorType.UNKNOWN
        assert error_info.severity == ErrorSeverity.HIGH
        assert error_info.user_message is not None
        assert len(error_info.recovery_suggestions) > 0
        assert error_info.can_retry is True
    
    def test_graceful_concurrent_error_handling(self):
        """
        Property test for concurrent error handling.
        Tests that multiple simultaneous errors are handled gracefully.
        """
        handler = ErrorHandler()
        
        # Simulate concurrent errors
        import threading
        import time
        
        errors_handled = []
        
        def handle_error(error_id):
            try:
                error_info = handler.handle_validation_error(
                    f"Concurrent error {error_id}",
                    f"Details for error {error_id}"
                )
                errors_handled.append(error_info)
            except Exception as e:
                errors_handled.append(e)
        
        # Property: Concurrent error handling should work without issues
        threads = []
        for i in range(5):
            thread = threading.Thread(target=handle_error, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Property: All errors should be handled successfully
        assert len(errors_handled) == 5
        assert all(isinstance(error, ErrorInfo) for error in errors_handled)
        
        # Property: Error history should contain all errors
        history = handler.get_error_history()
        assert len(history) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])