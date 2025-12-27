#!/usr/bin/env python3
"""
Direct integration test to verify end-to-end functionality.
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from context_manager import ContextManager
from agent_manager import AgentManager
from query_processor import QueryProcessor

def test_complete_integration():
    """Test complete integration from context loading to query processing."""
    print("Testing Complete Integration...")
    
    try:
        # Step 1: Initialize context manager and load context
        print("1. Loading context...")
        context_manager = ContextManager("product.md")
        context = context_manager.load_context()
        
        if not context or not context.is_valid():
            print("✗ Context loading failed")
            return False
        
        print(f"✓ Context loaded: {len(context.content)} characters")
        
        # Step 2: Initialize agent manager
        print("2. Initializing agent...")
        agent_manager = AgentManager(".kiro/config.yaml", "product.md")
        agent = agent_manager.initialize_agent()
        
        if not agent:
            print("✗ Agent initialization failed")
            return False
        
        print("✓ Agent initialized successfully")
        
        # Step 3: Initialize query processor
        print("3. Initializing query processor...")
        query_processor = QueryProcessor(agent_manager)
        print("✓ Query processor initialized")
        
        # Step 4: Test end-to-end query processing
        print("4. Testing end-to-end query processing...")
        
        test_queries = [
            "What does guru mean?",
            "Plan my day in Bangalore",
            "Traffic to Electronic City at 8 PM",
            "Best breakfast in Malleshwaram"
        ]
        
        all_successful = True
        
        for i, query in enumerate(test_queries, 1):
            print(f"   4.{i} Testing: {query}")
            
            result = query_processor.process_query(query)
            
            if not result.success:
                print(f"   ✗ Query failed: {result.error_message}")
                all_successful = False
                continue
            
            if not result.agent_response:
                print("   ✗ No agent response")
                all_successful = False
                continue
            
            response_length = len(result.agent_response.content)
            if response_length < 20:
                print(f"   ✗ Response too short: {response_length} chars")
                all_successful = False
                continue
            
            print(f"   ✓ Query successful: {response_length} chars, {result.processing_time_ms:.2f}ms")
        
        if all_successful:
            print("✓ All end-to-end tests passed!")
            return True
        else:
            print("✗ Some end-to-end tests failed")
            return False
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_flow():
    """Test proper data flow between all layers."""
    print("\nTesting Data Flow...")
    
    try:
        # Initialize components
        context_manager = ContextManager("product.md")
        agent_manager = AgentManager(".kiro/config.yaml", "product.md")
        query_processor = QueryProcessor(agent_manager)
        
        # Test context loading
        context = context_manager.load_context()
        assert context is not None, "Context should be loaded"
        assert context.is_valid(), "Context should be valid"
        print("✓ Context layer working")
        
        # Test agent initialization
        agent = agent_manager.initialize_agent()
        assert agent is not None, "Agent should be initialized"
        print("✓ Agent layer working")
        
        # Test query processing
        result = query_processor.process_query("Test query")
        assert result is not None, "Query result should exist"
        print("✓ Query processing layer working")
        
        # Test complete pipeline
        test_query = "What does machcha mean?"
        result = query_processor.process_query(test_query)
        
        assert result.success, f"Query should succeed: {result.error_message}"
        assert result.agent_response is not None, "Should have agent response"
        assert len(result.agent_response.content) > 10, "Response should be substantial"
        
        print("✓ Complete data flow working")
        return True
        
    except Exception as e:
        print(f"✗ Data flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("BANGALORE LOCAL GUIDE - INTEGRATION TESTS")
    print("=" * 60)
    
    # Test 1: Complete integration
    success1 = test_complete_integration()
    
    # Test 2: Data flow
    success2 = test_data_flow()
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    if success1 and success2:
        print("✓ ALL INTEGRATION TESTS PASSED!")
        print("\nRequirements validation:")
        print("✓ 5.4 - System handles user input and generates responses")
        print("✓ 6.3 - Agent processes queries with loaded context")
        print("✓ Complete user journey from query to response works")
        print("✓ Proper data flow between all layers confirmed")
        return True
    else:
        print("✗ SOME INTEGRATION TESTS FAILED")
        print(f"Complete integration: {'✓' if success1 else '✗'}")
        print(f"Data flow: {'✓' if success2 else '✗'}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)