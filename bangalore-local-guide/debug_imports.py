#!/usr/bin/env python3
"""Debug import issues."""

print("Starting import debug...")

try:
    print("Importing logging...")
    import logging
    print("✓ logging imported")
    
    print("Importing typing...")
    from typing import Dict, Any, Optional, List
    print("✓ typing imported")
    
    print("Importing dataclasses...")
    from dataclasses import dataclass
    print("✓ dataclasses imported")
    
    print("Importing datetime...")
    from datetime import datetime
    print("✓ datetime imported")
    
    print("Importing pathlib...")
    from pathlib import Path
    print("✓ pathlib imported")
    
    print("Importing context_manager...")
    from context_manager import ContextManager, LocalContext
    print("✓ context_manager imported")
    
    print("Importing agent_manager...")
    from agent_manager import AgentManager, BangaloreLocalAgent
    print("✓ agent_manager imported")
    
    print("Importing query_processor...")
    from query_processor import QueryProcessor, QueryProcessingResult
    print("✓ query_processor imported")
    
    print("Importing error_handler...")
    from error_handler import ErrorHandler, ErrorInfo, ErrorType, ErrorSeverity
    print("✓ error_handler imported")
    
    print("All imports successful!")
    
    # Now try to define a simple class
    print("Defining test class...")
    
    @dataclass
    class TestClass:
        name: str
        
    print("✓ Test class defined")
    
    # Try to import the integration_manager module
    print("Importing integration_manager module...")
    import integration_manager
    print(f"✓ integration_manager module imported")
    print(f"Module contents: {dir(integration_manager)}")
    
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()