"""
Integration Manager for Bangalore Local Guide
Coordinates all components and ensures proper data flow between layers.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from context_manager import ContextManager, LocalContext
from agent_manager import AgentManager, BangaloreLocalAgent
from query_processor import QueryProcessor, QueryProcessingResult
from error_handler import ErrorHandler, ErrorInfo, ErrorType, ErrorSeverity

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SystemStatus:
    """System health and status information."""
    context_loaded: bool
    agent_initialized: bool
    processor_ready: bool
    last_health_check: datetime
    errors: List[ErrorInfo]
    session_id: str


@dataclass
class IntegrationResult:
    """Result of integration operations."""
    success: bool
    message: str
    system_status: SystemStatus
    error_info: Optional[ErrorInfo] = None


class IntegrationManager:
    """
    Manages integration between all system components.
    Ensures proper initialization order and data flow.
    """
    
    def __init__(self, 
                 config_path: str = ".kiro/config.yaml",
                 product_path: str = "product.md"):
        """
        Initialize integration manager.
        
        Args:
            config_path: Path to agent configuration
            product_path: Path to product knowledge file
        """
        self.config_path = config_path
        self.product_path = product_path
        
        # Component managers
        self.context_manager: Optional[ContextManager] = None
        self.agent_manager: Optional[AgentManager] = None
        self.query_processor: Optional[QueryProcessor] = None
        self.error_handler = ErrorHandler()
        
        # System state
        self.context: Optional[LocalContext] = None
        self.agent: Optional[BangaloreLocalAgent] = None
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.initialization_errors: List[ErrorInfo] = []
        self.system_initialized = False
        
        logger.info(f"Integration manager initialized for session: {self.session_id}")
    
    def initialize_system(self) -> IntegrationResult:
        """
        Initialize all system components in proper order.
        
        Returns:
            IntegrationResult with initialization status
        """
        logger.info("Starting system initialization...")
        
        try:
            # Step 1: Initialize context manager and load context
            context_result = self._initialize_context()
            if not context_result.success:
                return context_result
            
            # Step 2: Initialize agent manager with loaded context
            agent_result = self._initialize_agent()
            if not agent_result.success:
                return agent_result
            
            # Step 3: Initialize query processor with agent
            processor_result = self._initialize_processor()
            if not processor_result.success:
                return processor_result
            
            # Mark system as initialized
            self.system_initialized = True
            
            # Create success result
            system_status = self._get_system_status()
            
            logger.info("System initialization completed successfully")
            return IntegrationResult(
                success=True,
                message="All components initialized successfully",
                system_status=system_status
            )
            
        except Exception as e:
            error_info = self.error_handler.handle_unknown_error(e, "system initialization")
            self.initialization_errors.append(error_info)
            
            system_status = self._get_system_status()
            
            logger.error(f"System initialization failed: {e}")
            return IntegrationResult(
                success=False,
                message=f"System initialization failed: {str(e)}",
                system_status=system_status,
                error_info=error_info
            )
    
    def _initialize_context(self) -> IntegrationResult:
        """Initialize context manager and load context."""
        try:
            logger.info("Initializing context manager...")
            
            self.context_manager = ContextManager(self.product_path)
            self.context = self.context_manager.load_context()
            
            if not self.context or not self.context.is_valid():
                error_info = self.error_handler.handle_validation_error(
                    "Invalid context loaded",
                    f"Context from {self.product_path} is empty or invalid"
                )
                self.initialization_errors.append(error_info)
                
                return IntegrationResult(
                    success=False,
                    message="Context loading failed",
                    system_status=self._get_system_status(),
                    error_info=error_info
                )
            
            logger.info("Context initialized successfully")
            return IntegrationResult(
                success=True,
                message="Context loaded successfully",
                system_status=self._get_system_status()
            )
            
        except Exception as e:
            error_info = self.error_handler.handle_context_loading_error(e, self.product_path)
            self.initialization_errors.append(error_info)
            
            return IntegrationResult(
                success=False,
                message=f"Context initialization failed: {str(e)}",
                system_status=self._get_system_status(),
                error_info=error_info
            )
    
    def _initialize_agent(self) -> IntegrationResult:
        """Initialize agent manager with loaded context."""
        try:
            logger.info("Initializing agent manager...")
            
            if not self.context:
                error_info = self.error_handler.handle_validation_error(
                    "Cannot initialize agent without context",
                    "Context must be loaded before agent initialization"
                )
                self.initialization_errors.append(error_info)
                
                return IntegrationResult(
                    success=False,
                    message="Agent initialization failed - no context",
                    system_status=self._get_system_status(),
                    error_info=error_info
                )
            
            self.agent_manager = AgentManager(self.config_path, self.product_path)
            self.agent = self.agent_manager.initialize_agent()
            
            if not self.agent:
                error_info = self.error_handler.handle_agent_initialization_error(
                    Exception("Agent initialization returned None"),
                    self.config_path
                )
                self.initialization_errors.append(error_info)
                
                return IntegrationResult(
                    success=False,
                    message="Agent initialization failed",
                    system_status=self._get_system_status(),
                    error_info=error_info
                )
            
            logger.info("Agent initialized successfully")
            return IntegrationResult(
                success=True,
                message="Agent initialized successfully",
                system_status=self._get_system_status()
            )
            
        except Exception as e:
            error_info = self.error_handler.handle_agent_initialization_error(e, self.config_path)
            self.initialization_errors.append(error_info)
            
            return IntegrationResult(
                success=False,
                message=f"Agent initialization failed: {str(e)}",
                system_status=self._get_system_status(),
                error_info=error_info
            )
    
    def _initialize_processor(self) -> IntegrationResult:
        """Initialize query processor with agent."""
        try:
            logger.info("Initializing query processor...")
            
            if not self.agent_manager:
                error_info = self.error_handler.handle_validation_error(
                    "Cannot initialize processor without agent",
                    "Agent must be initialized before processor"
                )
                self.initialization_errors.append(error_info)
                
                return IntegrationResult(
                    success=False,
                    message="Processor initialization failed - no agent",
                    system_status=self._get_system_status(),
                    error_info=error_info
                )
            
            self.query_processor = QueryProcessor(self.agent_manager)
            
            logger.info("Query processor initialized successfully")
            return IntegrationResult(
                success=True,
                message="Query processor initialized successfully",
                system_status=self._get_system_status()
            )
            
        except Exception as e:
            error_info = self.error_handler.handle_unknown_error(e, "processor initialization")
            self.initialization_errors.append(error_info)
            
            return IntegrationResult(
                success=False,
                message=f"Processor initialization failed: {str(e)}",
                system_status=self._get_system_status(),
                error_info=error_info
            )
    
    def process_user_query(self, query_text: str) -> QueryProcessingResult:
        """
        Process user query through the complete pipeline.
        
        Args:
            query_text: User's question
            
        Returns:
            QueryProcessingResult with response
        """
        if not self.system_initialized:
            # Try to initialize system first
            init_result = self.initialize_system()
            if not init_result.success:
                # Return error result
                from query_processor import ProcessedQuery, QueryType
                return QueryProcessingResult(
                    processed_query=ProcessedQuery(
                        original_text=query_text,
                        cleaned_text="",
                        query_type=QueryType.INVALID,
                        keywords=[],
                        time_context=None,
                        location_context=None,
                        confidence=0.0,
                        is_valid=False
                    ),
                    agent_response=None,
                    processing_time_ms=0.0,
                    success=False,
                    error_message=init_result.message
                )
        
        if not self.query_processor:
            from query_processor import ProcessedQuery, QueryType
            return QueryProcessingResult(
                processed_query=ProcessedQuery(
                    original_text=query_text,
                    cleaned_text="",
                    query_type=QueryType.INVALID,
                    keywords=[],
                    time_context=None,
                    location_context=None,
                    confidence=0.0,
                    is_valid=False
                ),
                agent_response=None,
                processing_time_ms=0.0,
                success=False,
                error_message="Query processor not available"
            )
        
        return self.query_processor.process_query(query_text)
    
    def _get_system_status(self) -> SystemStatus:
        """Get current system status."""
        return SystemStatus(
            context_loaded=self.context is not None and self.context.is_valid(),
            agent_initialized=self.agent is not None,
            processor_ready=self.query_processor is not None,
            last_health_check=datetime.now(),
            errors=self.initialization_errors.copy(),
            session_id=self.session_id
        )
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health information.
        
        Returns:
            Dictionary with system health details
        """
        status = self._get_system_status()
        
        health_info = {
            "overall_status": "healthy" if self.system_initialized else "error",
            "session_id": status.session_id,
            "last_check": status.last_health_check.isoformat(),
            "components": {
                "context": {
                    "status": "loaded" if status.context_loaded else "error",
                    "details": self.context_manager.get_context_summary() if self.context_manager else None
                },
                "agent": {
                    "status": "initialized" if status.agent_initialized else "error",
                    "details": self.agent_manager.get_agent_info() if self.agent_manager else None
                },
                "processor": {
                    "status": "ready" if status.processor_ready else "error",
                    "details": self.query_processor.get_processing_stats() if self.query_processor else None
                }
            },
            "errors": [
                {
                    "type": error.error_type.value,
                    "severity": error.severity.value,
                    "message": error.user_message,
                    "timestamp": error.timestamp.isoformat()
                }
                for error in status.errors
            ]
        }
        
        return health_info
    
    def reload_system_context(self) -> IntegrationResult:
        """
        Reload system context from product.md file.
        
        Returns:
            IntegrationResult with reload status
        """
        try:
            logger.info("Reloading system context...")
            
            if not self.context_manager:
                return IntegrationResult(
                    success=False,
                    message="Context manager not initialized",
                    system_status=self._get_system_status()
                )
            
            # Reload context
            self.context = self.context_manager.reload_context()
            
            # Update agent with new context if available
            if self.agent_manager:
                self.agent_manager.reload_context()
            
            # Update processor if available
            if self.query_processor:
                self.query_processor.reload_agent_context()
            
            logger.info("System context reloaded successfully")
            return IntegrationResult(
                success=True,
                message="Context reloaded successfully",
                system_status=self._get_system_status()
            )
            
        except Exception as e:
            error_info = self.error_handler.handle_unknown_error(e, "context reload")
            self.initialization_errors.append(error_info)
            
            return IntegrationResult(
                success=False,
                message=f"Context reload failed: {str(e)}",
                system_status=self._get_system_status(),
                error_info=error_info
            )
    
    def test_end_to_end_flow(self, test_query: str = "What does guru mean?") -> Dict[str, Any]:
        """
        Test complete end-to-end flow from query to response.
        
        Args:
            test_query: Query to test with
            
        Returns:
            Dictionary with test results
        """
        logger.info(f"Testing end-to-end flow with query: {test_query}")
        
        start_time = datetime.now()
        
        try:
            # Test system initialization
            if not self.system_initialized:
                init_result = self.initialize_system()
                if not init_result.success:
                    return {
                        "success": False,
                        "stage": "initialization",
                        "error": init_result.message,
                        "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
                    }
            
            # Test query processing
            result = self.process_user_query(test_query)
            
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds() * 1000
            
            return {
                "success": result.success,
                "stage": "complete" if result.success else "query_processing",
                "query": test_query,
                "query_type": result.processed_query.query_type.value if result.processed_query else "unknown",
                "response_preview": result.agent_response.content[:100] + "..." if result.agent_response else None,
                "processing_time_ms": result.processing_time_ms,
                "total_duration_ms": total_duration,
                "error": result.error_message if not result.success else None,
                "system_health": self.get_system_health()
            }
            
        except Exception as e:
            return {
                "success": False,
                "stage": "test_execution",
                "error": str(e),
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
            }


# Convenience functions for easy integration
def create_integrated_system(config_path: str = ".kiro/config.yaml", 
                           product_path: str = "product.md") -> IntegrationManager:
    """
    Create and initialize a complete integrated system.
    
    Args:
        config_path: Path to agent configuration
        product_path: Path to product knowledge file
        
    Returns:
        Initialized IntegrationManager
    """
    manager = IntegrationManager(config_path, product_path)
    init_result = manager.initialize_system()
    
    if not init_result.success:
        logger.warning(f"System initialization had issues: {init_result.message}")
    
    return manager


def test_system_integration(config_path: str = ".kiro/config.yaml", 
                          product_path: str = "product.md") -> Dict[str, Any]:
    """
    Test complete system integration.
    
    Args:
        config_path: Path to agent configuration
        product_path: Path to product knowledge file
        
    Returns:
        Test results dictionary
    """
    manager = IntegrationManager(config_path, product_path)
    return manager.test_end_to_end_flow()


if __name__ == "__main__":
    # Test integration manager
    print("Testing Integration Manager...")
    
    try:
        # Test system creation and initialization
        manager = create_integrated_system()
        
        print("System Health:")
        health = manager.get_system_health()
        print(f"  Overall Status: {health['overall_status']}")
        print(f"  Session ID: {health['session_id']}")
        
        for component, details in health['components'].items():
            print(f"  {component.title()}: {details['status']}")
        
        if health['errors']:
            print(f"  Errors: {len(health['errors'])}")
        
        # Test end-to-end flow
        print("\nTesting End-to-End Flow...")
        test_result = manager.test_end_to_end_flow()
        
        print(f"  Success: {test_result['success']}")
        print(f"  Stage: {test_result['stage']}")
        print(f"  Duration: {test_result.get('total_duration_ms', 0):.2f}ms")
        
        if test_result['success']:
            print(f"  Query Type: {test_result['query_type']}")
            print(f"  Response Preview: {test_result['response_preview']}")
        else:
            print(f"  Error: {test_result['error']}")
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()