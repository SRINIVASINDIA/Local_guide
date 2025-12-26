"""
Integration Tests for Example Queries - Bangalore Local Guide
Tests all four example query types: itinerary, slang, traffic, food
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


class TestExampleQueriesIntegration:
    """Test integration with the four example query types specified in requirements."""
    
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
            'context': context
        }
    
    def test_itinerary_query_integration(self, system_components):
        """Test itinerary planning query - Requirements 9.1."""
        query_processor = system_components['query_processor']
        
        # Test the example itinerary query
        query = "I have one day in Bangalore. Plan it like a local."
        
        result = query_processor.process_query(query)
        
        # Basic validation
        assert result.success, f"Itinerary query should succeed: {result.error_message}"
        assert result.agent_response is not None, "Should have agent response"
        assert result.processed_query.query_type in [QueryType.ITINERARY, QueryType.GENERAL], \
            f"Should be classified as itinerary or general, got {result.processed_query.query_type}"
        
        response_content = result.agent_response.content.lower()
        
        # Content validation - should contain itinerary elements
        itinerary_indicators = [
            'morning', 'afternoon', 'evening', 'breakfast', 'lunch', 'dinner',
            'visit', 'start', 'plan', 'day'
        ]
        found_indicators = [ind for ind in itinerary_indicators if ind in response_content]
        assert len(found_indicators) >= 3, \
            f"Itinerary should contain time-based planning elements, found: {found_indicators}"
        
        # Should mention specific Bangalore places from knowledge base
        bangalore_places = [
            'lalbagh', 'cubbon park', 'commercial street', 'brigade road',
            'malleshwaram', 'basavanagudi', 'jayanagar', 'vv puram', 'indiranagar'
        ]
        found_places = [place for place in bangalore_places if place in response_content]
        assert len(found_places) >= 2, \
            f"Itinerary should mention specific Bangalore places, found: {found_places}"
        
        # Should be substantial response
        assert len(response_content) > 200, \
            f"Itinerary response should be detailed, got {len(response_content)} characters"
        
        # Should not hallucinate other cities
        other_cities = ['mumbai', 'delhi', 'chennai', 'hyderabad', 'pune']
        found_other_cities = [city for city in other_cities if city in response_content]
        assert len(found_other_cities) == 0, \
            f"Should not mention other cities, found: {found_other_cities}"
        
        print(f"✓ Itinerary query test passed - Response length: {len(result.agent_response.content)}")
    
    def test_slang_explanation_query_integration(self, system_components):
        """Test slang explanation query - Requirements 9.2."""
        query_processor = system_components['query_processor']
        
        # Test the example slang query
        query = "What does 'guru' mean in Bangalore?"
        
        result = query_processor.process_query(query)
        
        # Basic validation
        assert result.success, f"Slang query should succeed: {result.error_message}"
        assert result.agent_response is not None, "Should have agent response"
        assert result.processed_query.query_type in [QueryType.SLANG, QueryType.GENERAL], \
            f"Should be classified as slang or general, got {result.processed_query.query_type}"
        
        response_content = result.agent_response.content.lower()
        
        # Should explain the slang term 'guru'
        guru_explanations = ['buddy', 'friend', 'endearment', 'dude']
        found_explanations = [exp for exp in guru_explanations if exp in response_content]
        assert len(found_explanations) >= 1, \
            f"Should explain 'guru' meaning, found: {found_explanations}"
        
        # Should mention the term being explained
        assert 'guru' in response_content, "Response should mention the term 'guru'"
        
        # Should indicate local context
        local_indicators = ['bangalore', 'local', 'kannada', 'here', 'we']
        found_local = [ind for ind in local_indicators if ind in response_content]
        assert len(found_local) >= 1, \
            f"Should indicate local context, found: {found_local}"
        
        # Should be appropriately sized (not too short, not too long)
        assert 30 < len(response_content) < 500, \
            f"Slang explanation should be appropriately sized, got {len(response_content)} characters"
        
        print(f"✓ Slang query test passed - Response length: {len(result.agent_response.content)}")
    
    def test_traffic_advice_query_integration(self, system_components):
        """Test traffic advice query - Requirements 9.3."""
        query_processor = system_components['query_processor']
        
        # Test the example traffic query
        query = "How's the traffic to Electronic City at 8 PM?"
        
        result = query_processor.process_query(query)
        
        # Basic validation
        assert result.success, f"Traffic query should succeed: {result.error_message}"
        assert result.agent_response is not None, "Should have agent response"
        assert result.processed_query.query_type in [QueryType.TRAFFIC, QueryType.GENERAL], \
            f"Should be classified as traffic or general, got {result.processed_query.query_type}"
        
        response_content = result.agent_response.content.lower()
        
        # Should mention Electronic City specifically
        assert 'electronic city' in response_content, \
            "Traffic response should mention Electronic City"
        
        # Should provide realistic traffic assessment
        traffic_indicators = ['traffic', 'congested', 'heavy', 'slow', 'busy', 'peak', 'bad']
        found_traffic = [ind for ind in traffic_indicators if ind in response_content]
        assert len(found_traffic) >= 1, \
            f"Should mention traffic conditions, found: {found_traffic}"
        
        # Should suggest alternatives (metro, timing, routes)
        alternative_indicators = [
            'metro', 'namma metro', 'alternative', 'avoid', 'earlier', 'later',
            'purple line', 'green line', 'leave', 'wait'
        ]
        found_alternatives = [alt for alt in alternative_indicators if alt in response_content]
        assert len(found_alternatives) >= 1, \
            f"Should suggest alternatives, found: {found_alternatives}"
        
        # Should be practical advice (substantial response)
        assert len(response_content) > 80, \
            f"Traffic advice should be detailed enough, got {len(response_content)} characters"
        
        # Should be time-aware (8 PM is peak evening traffic)
        time_awareness = ['8', 'evening', 'peak', 'pm', 'night']
        found_time = [time for time in time_awareness if time in response_content]
        assert len(found_time) >= 1, \
            f"Should be time-aware for 8 PM query, found: {found_time}"
        
        print(f"✓ Traffic query test passed - Response length: {len(result.agent_response.content)}")
    
    def test_food_recommendation_query_integration(self, system_components):
        """Test food recommendation query - Requirements 9.4."""
        query_processor = system_components['query_processor']
        
        # Test the example food query
        query = "Where can I get good breakfast in Malleshwaram?"
        
        result = query_processor.process_query(query)
        
        # Basic validation
        assert result.success, f"Food query should succeed: {result.error_message}"
        assert result.agent_response is not None, "Should have agent response"
        assert result.processed_query.query_type in [QueryType.FOOD, QueryType.GENERAL], \
            f"Should be classified as food or general, got {result.processed_query.query_type}"
        
        response_content = result.agent_response.content.lower()
        
        # Should mention Malleshwaram specifically
        assert 'malleshwaram' in response_content, \
            "Food response should mention Malleshwaram"
        
        # Should mention breakfast foods from knowledge base
        breakfast_foods = ['dosa', 'idli', 'vada', 'coffee', 'breakfast', 'upahara darshini']
        found_foods = [food for food in breakfast_foods if food in response_content]
        assert len(found_foods) >= 2, \
            f"Should mention breakfast foods, found: {found_foods}"
        
        # Should mention specific places from knowledge base
        places = ['janatha hotel', 'upahara darshini', 'vidyarthi bhavan']
        found_places = [place for place in places if place in response_content]
        assert len(found_places) >= 1, \
            f"Should mention specific places from knowledge base, found: {found_places}"
        
        # Should be time-appropriate (breakfast context)
        time_appropriate = ['morning', 'breakfast', 'start', 'day', 'early']
        found_time = [time for time in time_appropriate if time in response_content]
        assert len(found_time) >= 1, \
            f"Should include breakfast time context, found: {found_time}"
        
        # Should be substantial response
        assert len(response_content) > 80, \
            f"Food recommendation should be detailed enough, got {len(response_content)} characters"
        
        print(f"✓ Food query test passed - Response length: {len(result.agent_response.content)}")
    
    def test_comprehensive_query_handling_integration(self, system_components):
        """Test comprehensive query handling - Requirements 9.5."""
        query_processor = system_components['query_processor']
        
        # Test all four example query types plus a culture query
        test_queries = [
            ("Plan my day in Bangalore", QueryType.ITINERARY, "itinerary"),
            ("What does scene illa maga mean?", QueryType.SLANG, "slang"),
            ("Traffic to Whitefield now?", QueryType.TRAFFIC, "traffic"),
            ("Best dosa place in Basavanagudi?", QueryType.FOOD, "food"),
            ("Cultural norms in temples", QueryType.CULTURE, "culture")
        ]
        
        results = []
        
        for query_text, expected_type, test_name in test_queries:
            result = query_processor.process_query(query_text)
            
            # Each query should succeed
            assert result.success, \
                f"Query '{query_text}' should succeed: {result.error_message}"
            
            # Should have response
            assert result.agent_response is not None, \
                f"Query '{query_text}' should have response"
            assert len(result.agent_response.content) > 30, \
                f"Query '{query_text}' should have substantial response"
            
            # Should be classified appropriately (allow GENERAL as fallback)
            actual_type = result.processed_query.query_type
            assert actual_type in [expected_type, QueryType.GENERAL], \
                f"Query '{query_text}' classified as {actual_type}, expected {expected_type} or GENERAL"
            
            # Should be based on knowledge base (no hallucination)
            response_lower = result.agent_response.content.lower()
            forbidden_cities = ['mumbai', 'chennai', 'delhi', 'hyderabad', 'pune']
            found_forbidden = [city for city in forbidden_cities if city in response_lower]
            assert len(found_forbidden) == 0, \
                f"Query '{query_text}' should not mention other cities: {found_forbidden}"
            
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
        
        # Average processing time should be reasonable (under 10 seconds)
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        assert avg_processing_time < 10000, \
            f"Average processing time should be under 10s, got {avg_processing_time:.2f}ms"
        
        print(f"✓ Comprehensive query handling test passed - {len(successful_queries)}/{len(test_queries)} queries successful")
        print(f"  Average processing time: {avg_processing_time:.2f}ms")
    
    def test_response_quality_standards(self, system_components):
        """Test that responses meet quality and accuracy requirements."""
        query_processor = system_components['query_processor']
        
        quality_test_queries = [
            "Recommend breakfast spots in Basavanagudi",
            "Explain scene illa maga",
            "Traffic situation at Silk Board",
            "Plan a cultural day in Bangalore"
        ]
        
        for query in quality_test_queries:
            result = query_processor.process_query(query)
            
            assert result.success, f"Quality test query should succeed: {query}"
            response = result.agent_response.content
            
            # Quality checks
            assert len(response) >= 50, \
                f"Response should be detailed enough for '{query}', got {len(response)} chars"
            assert len(response) <= 2000, \
                f"Response should not be too verbose for '{query}', got {len(response)} chars"
            
            # Should not contain placeholder text
            placeholders = ['[placeholder]', 'todo', 'tbd', 'xxx', '...']
            response_lower = response.lower()
            found_placeholders = [p for p in placeholders if p in response_lower]
            assert len(found_placeholders) == 0, \
                f"Response should not contain placeholders for '{query}': {found_placeholders}"
            
            # Should be coherent (no excessive repetition)
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            if len(sentences) > 1:
                unique_sentences = set(s.lower() for s in sentences)
                repetition_ratio = len(unique_sentences) / len(sentences)
                assert repetition_ratio > 0.7, \
                    f"Response should not be repetitive for '{query}': ratio {repetition_ratio:.2f}"
            
            # Content-specific validation
            if 'breakfast' in query.lower():
                breakfast_terms = ['dosa', 'idli', 'coffee', 'malleshwaram', 'basavanagudi']
                found_terms = [term for term in breakfast_terms if term in response_lower]
                assert len(found_terms) >= 1, \
                    f"Breakfast query should mention relevant terms for '{query}': {found_terms}"
            
            if 'traffic' in query.lower():
                traffic_terms = ['congested', 'peak', 'metro', 'avoid', 'silk board']
                found_terms = [term for term in traffic_terms if term in response_lower]
                assert len(found_terms) >= 1, \
                    f"Traffic query should mention relevant terms for '{query}': {found_terms}"
            
            if 'scene illa' in query.lower():
                slang_terms = ['not happening', 'not possible', 'dude', 'maga']
                found_terms = [term for term in slang_terms if term in response_lower]
                assert len(found_terms) >= 1, \
                    f"Slang query should explain the term for '{query}': {found_terms}"
        
        print(f"✓ Response quality standards test passed for {len(quality_test_queries)} queries")
    
    def test_knowledge_base_consistency(self, system_components):
        """Test that responses are consistent with knowledge base content."""
        context = system_components['context']
        query_processor = system_components['query_processor']
        
        # Test queries that should reference specific knowledge base content
        knowledge_tests = [
            {
                'query': 'What are the peak traffic hours?',
                'expected_content': ['8:00 am', '10:30 am', '6:00 pm', '9:00 pm', 'peak'],
                'section': 'traffic patterns'
            },
            {
                'query': 'What does sakkath mean?',
                'expected_content': ['awesome', 'excellent'],
                'section': 'slang'
            },
            {
                'query': 'Which metro line goes to Whitefield?',
                'expected_content': ['purple line', 'namma metro'],
                'section': 'metro'
            }
        ]
        
        for test_case in knowledge_tests:
            result = query_processor.process_query(test_case['query'])
            
            assert result.success, f"Knowledge test query should succeed: {test_case['query']}"
            response_lower = result.agent_response.content.lower()
            
            # Check that response contains expected content from knowledge base
            found_content = [content for content in test_case['expected_content'] 
                           if content in response_lower]
            
            assert len(found_content) >= 1, \
                f"Response for '{test_case['query']}' should contain knowledge base content. " \
                f"Expected: {test_case['expected_content']}, Found: {found_content}"
        
        print(f"✓ Knowledge base consistency test passed for {len(knowledge_tests)} queries")


if __name__ == "__main__":
    # Run tests manually if executed directly
    print("Running Example Queries Integration Tests...")
    
    try:
        # Initialize system components
        context_manager = ContextManager("product.md")
        context = context_manager.load_context()
        
        if not context or not context.is_valid():
            print("✗ Failed to load valid context")
            sys.exit(1)
        
        agent_manager = AgentManager(".kiro/config.yaml", "product.md")
        agent = agent_manager.initialize_agent()
        
        if not agent:
            print("✗ Failed to initialize agent")
            sys.exit(1)
        
        query_processor = QueryProcessor(agent_manager)
        
        system_components = {
            'context_manager': context_manager,
            'agent_manager': agent_manager,
            'query_processor': query_processor,
            'context': context
        }
        
        print("✓ System components initialized")
        
        # Create test instance
        test_instance = TestExampleQueriesIntegration()
        
        # Run individual tests
        print("\n1. Testing itinerary query...")
        test_instance.test_itinerary_query_integration(system_components)
        
        print("\n2. Testing slang explanation query...")
        test_instance.test_slang_explanation_query_integration(system_components)
        
        print("\n3. Testing traffic advice query...")
        test_instance.test_traffic_advice_query_integration(system_components)
        
        print("\n4. Testing food recommendation query...")
        test_instance.test_food_recommendation_query_integration(system_components)
        
        print("\n5. Testing comprehensive query handling...")
        test_instance.test_comprehensive_query_handling_integration(system_components)
        
        print("\n6. Testing response quality standards...")
        test_instance.test_response_quality_standards(system_components)
        
        print("\n7. Testing knowledge base consistency...")
        test_instance.test_knowledge_base_consistency(system_components)
        
        print("\n" + "="*60)
        print("✓ All Example Queries Integration Tests Passed!")
        print("\nRequirements validation:")
        print("✓ 9.1 - Itinerary planning query tested and validated")
        print("✓ 9.2 - Slang explanation query tested and validated") 
        print("✓ 9.3 - Traffic advice query tested and validated")
        print("✓ 9.4 - Food recommendation query tested and validated")
        print("✓ 9.5 - Comprehensive query handling tested and validated")
        print("\nAll four example query types meet quality and accuracy requirements!")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)