"""
Integration Tests for Bangalore Local Guide
Tests complete end-to-end functionality with example queries.
Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from context_manager import ContextManager
from agent_manager import AgentManager
from query_processor import QueryProcessor, QueryType


class TestIntegrationExampleQueries:
    """Test integration with the four example query types."""
    
    @pytest.fixture(scope="class")
    def system_components(self):
        """Initialize system components for testing."""
        # Initialize context manager
        context_manager = ContextManager("product.md")
        context = context_manager.load_context()
        
        assert context is not None, "Context should be loaded"
        assert context.is_valid(), "Context should be valid"
        
        # Initialize agent manager
        agent_manager = AgentManager(".kiro/config.yaml", "product.md")
        agent = agent_manager.initialize_agent()
        
        assert agent is not None, "Agent should be initialized"
        
        # Initialize query processor
        query_processor = QueryProcessor(agent_manager)
        
        return {
            'context_manager': context_manager,
            'agent_manager': agent_manager,
            'query_processor': query_processor,
 