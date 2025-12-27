"""
Integration Tests for Bangalore Local Guide
Tests complete end-to-end functionality with example queries.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from integration_manager import IntegrationManager, IntegrationResult
from query_processor import QueryProcessingResult, QueryType
from agent_manager import AgentResponse


class TestIntegrationEndToEnd:
    """Test complete end-to-end integration functionality."""
    
    @pytest.fixture
    def integration_manager(self):
        """Create integration manager for testing."""
        manager = IntegrationManager(
            config_path=".kiro/config.yaml",
            product_path="product.md"
        )
        
        # Initialize the system
        result = manager.initialize_system()
        assert result.success, f"System initialization failed: {result.message}"
        
        return manager
    
    def test_system_initialization(self, integration_manager):
        """Test that the complete system initializes successfully."""
        # Check system health
        health = integration_manager.get_system_health()
        
        assert health['overall_status'] == 'healthy', "System should be healthy after initialization"
        assert health['components']['context']['status'] == 'loaded', "Context should be loaded"
        assert health['components']['agent']['status'] == 'initialized', "Agent should be initialized"
        assert health['components']['processor']['status'] == 'ready', "Processor should be ready"
        
        # Check session ID is set
        assert health['session_id'], "Session ID should be set"
        
        # Check no critical errors
        critical_errors = [e for e in health['errors'] if e['severity'] == 'critical']
        assert len(critical_errors) == 0, f"No critical errors expected, found: {critical_errors}"
    
    def test_itinerary_query(self, integration_manager):
        """Test itinerary planning query - Requirements 9.1."""
        query = "I have one day in Bangalore. Plan it like a local."
        
        result = integration_manager.process_user_query(query)
        
        # Basic result validation
        assert result.success, f"Query processing should succeed: {result.error_message}"
        assert result.processed_query.query_type == QueryType.ITINERARY, "Should be classified as itinerary query"
        assert result.agent_response is not None, "Should have agent response"
        
        # Response content validation
        response_content = result.agent_response.content.lower()
        
        # Should contain itinerary-related content
        itinerary_indicators = [
            'morning', 'afternoon', 'evening', 'visit', 'start', 'plan',
            'lalbagh', 'cubbon park', 'bangalore palace', 'commercial street',
            'malleshwaram', 'basavanagudi', 'breakfast', 'lunch', 'dinner'
        ]
        
        found_indicators = [indicator for indicator in itinerary_indicators 
                          if indicator in response_content]
        
        assert len(found_indicators) >= 3, f"Response should contain itinerary elements, found: {found_indicators}"
        
        # Should be substantial response (not just a short answer)
        assert len(response_content) > 200, "Itinerary response should be detailed"
        
        # Should not contain hallucinated information
        assert 'mumbai' not in response_content, "Should not mention other cities"
        assert 'delhi' not in response_content, "Should not mention other cities"
    
    def test_slang_explanation_query(self, integration_manager):
        """Test slang explanation query - Requirements 9.2."""
        query = "What does 'guru' mean in Bangalore?"
        
        result = integration_manager.process_user_query(query)
        
        # Basic result validation
        assert result.success, f"Query processing should succeed: {result.error_message}"
        assert result.processed_query.query_type == QueryType.SLANG, "Should be classified as slang query"
        assert result.agent_response is not None, "Should have agent response"
        
        # Response content validation
        response_content = result.agent_response.content.lower()
        
        # Should explain the slang term
        slang_explanations = ['buddy', 'friend', 'endearment', 'dude']
        found_explanations = [exp for exp in slang_explanations if exp in response_content]
        
        assert len(found_explanations) >= 1, f"Should explain 'guru' meaning, found: {found_explanations}"
        
        # Should mention it's local slang
        local_indicators = ['bangalore', 'local', 'slang', 'kannada']
        found_local = [ind for ind in local_indicators if ind in response_content]
        
        assert len(found_local) >= 1, f"Should indicate local context, found: {found_local}"
        
        # Should be informative but concise
        assert 50 < len(response_content) < 500, "Slang explanation should be appropriately sized"
    
    def test_traffic_advice_query(self, integration_manager):
        """Test traffic advice query - Requirements 9.3."""
        query = "How's the traffic to Electronic City at 8 PM?"
        
        result = integration_manager.process_user_query(query)
        
        # Basic result validation
        assert result.success, f"Query processing should succeed: {result.error_message}"
        assert result.processed_query.query_type == QueryType.TRAFFIC, "Should be classified as traffic query"
        assert result.agent_response is not None, "Should have agent response"
        
        # Response content validation
        response_content = result.agent_response.content.lower()
        
        # Should mention Electronic City specifically
        assert 'electronic city' in response_content, "Should mention Electronic City"
        
        # Should provide realistic traffic assessment
        traffic_indicators = ['traffic', 'congested', 'heavy', 'slow', 'busy', 'peak']
        found_traffic = [ind for ind in traffic_indicators if ind in response_content]
        
        assert len(found_traffic) >= 1, f"Should mention traffic conditions, found: {found_traffic}"
        
        # Should suggest alternatives (metro, timing, routes)
        alternative_indicators = ['metro', 'namma metro', 'alternative', 'avoid', 'earlier', 'later']
        found_alternatives = [alt for alt in alternative_indicators if alt in response_content]
        
        assert len(found_alternatives) >= 1, f"Should suggest alternatives, found: {found_alternatives}"
        
        # Should be practical advice
        assert len(response_content) > 100, "Traffic advice should be detailed enough"
    
    def test_food_recommendation_query(self, integration_manager):
        """Test food recommendation query - Requirements 9.4."""
        query = "Where can I get good breakfast in Malleshwaram?"
        
        result = integration_manager.process_user_query(query)
        
        # Basic result validation
        assert result.success, f"Query processing should succeed: {result.error_message}"
        assert result.processed_query.query_type == QueryType.FOOD, "Should be classified as food query"
        assert result.agent_response is not None, "Should have agent response"
        
        # Response content validation
        response_content = result.agent_response.content.lower()
        
        # Should mention Malleshwaram specifically
        assert 'malleshwaram' in response_content, "Should mention Malleshwaram"
        
        # Should mention breakfast foods
        breakfast_foods = ['dosa', 'idli', 'vada', 'coffee', 'breakfast']
        found_foods = [food for food in breakfast_foods if food in response_content]
        
        assert len(found_foods) >= 2, f"Should mention breakfast foods, found: {found_foods}"
        
        # Should mention specific places from knowledge base
        places = ['janatha hotel', 'upahara darshini', 'vidyarthi bhavan']
        found_places = [place for place in places if place in response_content]
        
        # At least one specific place should be mentioned
        assert len(found_places) >= 1, f"Should mention specific places, found: {found_places}"
        
        # Should be time-appropriate (morning food)
        time_appropriate = ['morning', '6', '7', '8', '9', 'early']
        found_time = [time for time in time_appropriate if time in response_content]
        
        # Time context should be present for breakfast query
        assert len(found_time) >= 1, f"Should include time context, found: {found_time}"
    
    def test_comprehensive_query_handling(self, integration_manager):
        """Test that system handles various query types comprehensively - Requirements 9.5."""
        test_queries = [
            ("Plan my day in Bangalore", QueryType.ITINERARY),
            ("What does machcha mean?", QueryType.SLANG),
            ("Traffic to Whitefield now?", QueryType.TRAFFIC),
            ("Best dosa place?", QueryType.FOOD),
            ("Cultural norms in temples", QueryType.CULTURE)
        ]
        
        results = []
        
        for query_text, expected_type in test_queries:
            result = integration_manager.process_user_query(query_text)
            
            # Each query should succeed
            assert result.success, f"Query '{query_text}' should succeed: {result.error_message}"
            
            # Should be classified correctly (or as general if close)
            actual_type = result.processed_query.query_type
            assert actual_type in [expected_type, QueryType.GENERAL], \
                f"Query '{query_text}' classified as {actual_type}, expected {expected_type} or GENERAL"
            
            # Should have response
            assert result.agent_response is not None, f"Query '{query_text}' should have response"
            assert len(result.agent_response.content) > 50, f"Query '{query_text}' should have substantial response"
            
            # Should be based on knowledge base (no hallucination)
            response_lower = result.agent_response.content.lower()
            assert 'mumbai' not in response_lower, f"Query '{query_text}' should not mention other cities"
            assert 'chennai' not in response_lower, f"Query '{query_text}' should not mention other cities"
            
            results.append({
                'query': query_text,
                'expected_type': expected_type,
                'actual_type': actual_type,
                'success': result.success,
                'response_length': len(result.agent_response.content),
                'processing_time': result.processing_time_ms
            })
        
        # All queries should have been processed successfully
        successful_queries = [r for r in results if r['success']]
        assert len(successful_queries) == len(test_queries), \
            f"All {len(test_queries)} queries should succeed, got {len(successful_queries)}"
        
        # Average processing time should be reasonable (under 5 seconds)
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        assert avg_processing_time < 5000, f"Average processing time should be under 5s, got {avg_processing_time:.2f}ms"
    
    def test_response_quality_standards(self, integration_manager):
        """Test that responses meet quality and accuracy requirements."""
        quality_test_queries = [
            "Recommend breakfast spots in Basavanagudi",
            "Explain scene illa maga",
            "Traffic situation at Silk Board",
            "Plan a cultural day in Bangalore"
        ]
        
        for query in quality_test_queries:
            result = integration_manager.process_user_query(query)
            
            assert result.success, f"Quality test query should succeed: {query}"
            response = result.agent_response.content
            
            # Quality checks
            assert len(response) >= 100, f"Response should be detailed enough: {query}"
            assert len(response) <= 2000, f"Response should not be too verbose: {query}"
            
            # Should not contain placeholder text
            placeholders = ['[placeholder]', 'todo', 'tbd', 'xxx', '...']
            response_lower = response.lower()
            found_placeholders = [p for p in placeholders if p in response_lower]
            assert len(found_placeholders) == 0, f"Response should not contain placeholders: {found_placeholders}"
            
            # Should be coherent (no repeated phrases)
            sentences = response.split('.')
            unique_sentences = set(s.strip().lower() for s in sentences if s.strip())
            repetition_ratio = len(unique_sentences) / max(len(sentences), 1)
            assert repetition_ratio > 0.8, f"Response should not be repetitive: {query}"
            
            # Should contain relevant keywords from knowledge base
            if 'breakfast' in query.lower():
                breakfast_terms = ['dosa', 'idli', 'coffee', 'malleshwaram', 'basavanagudi']
                found_terms = [term for term in breakfast_terms if term in response_lower]
                assert len(found_terms) >= 2, f"Breakfast query should mention relevant terms: {found_terms}"
            
            if 'traffic' in query.lower():
                traffic_terms = ['congested', 'peak', 'metro', 'avoid', 'silk board']
                found_terms = [term for term in traffic_terms if term in response_lower]
                assert len(found_terms) >= 2, f"Traffic query should mention relevant terms: {found_terms}"