#!/usr/bin/env python3
"""
Simple integration test to verify end-to-end functionality.
"""

from integration_manager import IntegrationManager

def main():
    print("Testing Integration Manager...")
    
    try:
        # Test system creation and initialization
        manager = IntegrationManager()
        
        # Initialize the system
        init_result = manager.initialize_system()
        
        if not init_result.success:
            print(f"System initialization failed: {init_result.message}")
            return False
        
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
            
        return test_result['success']
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✓ Integration test passed!")
    else:
        print("\n✗ Integration test failed!")