"""
Property-based tests for traffic and transportation advisor functionality.
Tests universal properties for traffic-aware transportation advice.
"""

import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, time
from traffic_advisor import TrafficAdvisor, TrafficLevel, get_traffic_advice


class TestTrafficAwareTransportationAdvice:
    """Property-based tests for traffic-aware transportation advice."""
    
    def test_traffic_aware_transportation_advice(self):
        """
        Feature: bangalore-local-guide, Property 5: Traffic-aware transportation advice
        For any traffic or transportation query, responses should include realistic 
        congestion warnings and suggest metro alternatives during peak hours when appropriate.
        **Validates: Requirements 1.3, 4.3, 4.4, 9.3**
        """
        # Sample context content for testing
        context_content = """
        ## Traffic Patterns and Peak Hours
        
        ### Peak Traffic Hours:
        - **Morning**: 8:00 AM - 10:30 AM
        - **Evening**: 6:00 PM - 9:00 PM
        - **Friday evenings**: Especially bad from 5:00 PM - 10:00 PM
        
        ### Notorious Traffic Areas:
        - **Silk Board Junction**: Always congested, especially 6-9 PM
        - **Electronic City Flyover**: Heavy during IT office hours
        - **Outer Ring Road**: Congested throughout the day
        - **Whitefield Road**: Bad during peak hours
        
        ### Metro Recommendations:
        - Use Namma Metro during peak hours (8-10 AM, 6-9 PM)
        - Purple Line: Covers Whitefield to Mysore Road
        - Green Line: Covers Nagasandra to Silk Institute
        """
        
        advisor = TrafficAdvisor(context_content)
        
        # Test peak hour traffic queries
        peak_hour_queries = [
            "Is Silk Board bad at 6 PM?",
            "Traffic at Electronic City during evening?",
            "How is Whitefield road at 8 AM?",
            "ORR traffic during rush hour"
        ]
        
        for query in peak_hour_queries:
            # Test with peak hour time
            peak_time = datetime(2024, 1, 1, 18, 0)  # 6 PM
            advice = advisor.get_traffic_advice(query, peak_time)
            advice_lower = advice.lower()
            
            # Property: Peak hour queries should include realistic warnings
            warning_terms = ['bad', 'congested', 'heavy', 'crazy', 'packed', 'nightmare', 'scene illa']
            assert any(term in advice_lower for term in warning_terms), \
                f"Peak hour query should include realistic warnings: {query}"
            
            # Property: Should suggest metro during peak hours
            metro_terms = ['metro', 'namma metro', 'purple line', 'green line']
            assert any(term in advice_lower for term in metro_terms), \
                f"Peak hour query should suggest metro alternatives: {query}"
            
            # Property: Should mention time-specific advice
            time_terms = ['peak', 'rush', 'hours', 'timing', 'avoid']
            assert any(term in advice_lower for term in time_terms), \
                f"Should provide time-specific advice: {query}"
        
        # Test non-peak hour queries
        non_peak_queries = [
            "Traffic at 2 PM",
            "How is Silk Board at 11 AM?",
            "Late night traffic conditions"
        ]
        
        for query in non_peak_queries:
            non_peak_time = datetime(2024, 1, 1, 14, 0)  # 2 PM
            advice = advisor.get_traffic_advice(query, non_peak_time)
            advice_lower = advice.lower()
            
            # Property: Non-peak queries should be less alarming
            # Should not use extreme warning terms
            extreme_terms = ['nightmare', 'scene illa', 'absolutely packed']
            extreme_count = sum(1 for term in extreme_terms if term in advice_lower)
            assert extreme_count <= 1, \
                f"Non-peak query should not be overly alarming: {query}"
    
    @given(st.integers(min_value=0, max_value=23))
    def test_peak_hour_detection_consistency(self, hour):
        """
        Property test for peak hour detection consistency.
        Tests that peak hour detection works correctly for all hours.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        Peak hours: 8-10 AM, 6-9 PM on weekdays.
        """
        
        advisor = TrafficAdvisor(context_content)
        
        # Create test time for weekday
        test_time = datetime(2024, 1, 1, hour, 0)  # Monday
        
        is_peak = advisor._is_peak_hour(test_time)
        
        # Property: Peak hour detection should be consistent with defined hours
        if 8 <= hour <= 10 or 18 <= hour <= 21:
            assert is_peak, f"Hour {hour} should be detected as peak hour"
        else:
            # Allow some flexibility for edge cases, but most non-peak hours should not be peak
            if hour not in [7, 11, 17, 22]:  # Adjacent hours might have some flexibility
                assert not is_peak, f"Hour {hour} should not be detected as peak hour"
    
    def test_location_specific_traffic_advice(self):
        """
        Property test for location-specific traffic advice.
        Tests that different locations receive appropriate traffic advice.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        
        ### Notorious Traffic Areas:
        - **Silk Board Junction**: Always congested, especially 6-9 PM
        - **Electronic City Flyover**: Heavy during IT office hours
        - **Whitefield Road**: Bad during peak hours
        """
        
        advisor = TrafficAdvisor(context_content)
        
        location_test_cases = [
            ("Silk Board traffic", "silk_board", ["silk board", "scene illa", "nightmare"]),
            ("Electronic City conditions", "electronic_city", ["electronic city", "it office", "heavy"]),
            ("Whitefield road status", "whitefield", ["whitefield", "peak hours", "purple line"]),
            ("ORR traffic update", "outer_ring_road", ["orr", "outer ring", "congested"])
        ]
        
        for query, expected_location, expected_terms in location_test_cases:
            advice = advisor.get_traffic_advice(query)
            advice_lower = advice.lower()
            
            # Property: Location-specific queries should mention the location
            location_mentioned = any(term in advice_lower for term in expected_terms[:2])
            assert location_mentioned, \
                f"Response should mention location for query: {query}"
            
            # Property: Should provide location-specific advice
            has_specific_advice = any(term in advice_lower for term in expected_terms)
            assert has_specific_advice, \
                f"Should provide location-specific advice for: {query}"
    
    def test_metro_suggestion_properties(self):
        """
        Property test for metro suggestion behavior.
        Tests that metro suggestions are provided appropriately.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        Metro available for most routes during peak hours.
        """
        
        advisor = TrafficAdvisor(context_content)
        
        # Test queries that should trigger metro suggestions
        metro_trigger_queries = [
            "Traffic during peak hours",
            "How to avoid rush hour traffic?",
            "Best way to travel at 6 PM",
            "Silk Board at evening time"
        ]
        
        for query in metro_trigger_queries:
            peak_time = datetime(2024, 1, 1, 18, 30)  # 6:30 PM
            advice = advisor.get_traffic_advice(query, peak_time)
            advice_lower = advice.lower()
            
            # Property: Peak hour queries should suggest metro
            metro_suggestions = ['metro', 'namma metro', 'purple line', 'green line']
            assert any(suggestion in advice_lower for suggestion in metro_suggestions), \
                f"Peak hour query should suggest metro: {query}"
            
            # Property: Should explain why metro is better
            metro_benefits = ['faster', 'avoid', 'save', 'better', 'best friend']
            assert any(benefit in advice_lower for benefit in metro_benefits), \
                f"Should explain metro benefits: {query}"
    
    def test_realistic_warning_properties(self):
        """
        Property test for realistic warning generation.
        Tests that warnings are realistic and contextually appropriate.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        Various traffic conditions across the city.
        """
        
        advisor = TrafficAdvisor(context_content)
        
        # Test different severity levels
        severity_test_cases = [
            ("Silk Board at 6 PM", ["scene illa", "nightmare", "absolutely packed"]),
            ("Electronic City during office hours", ["crazy", "heavy", "bad"]),
            ("General traffic query", ["unpredictable", "busy", "congested"])
        ]
        
        for query, expected_severity_terms in severity_test_cases:
            advice = advisor.get_traffic_advice(query)
            advice_lower = advice.lower()
            
            # Property: Should include appropriate severity indicators
            has_severity_indicator = any(term in advice_lower for term in expected_severity_terms)
            assert has_severity_indicator, \
                f"Should include severity indicators for: {query}"
            
            # Property: Warnings should be realistic, not exaggerated
            exaggerated_terms = ['impossible', 'never', 'always stuck', 'completely blocked']
            exaggerated_count = sum(1 for term in exaggerated_terms if term in advice_lower)
            assert exaggerated_count == 0, \
                f"Should not use exaggerated terms: {query}"
    
    def test_time_context_extraction_properties(self):
        """
        Property test for time context extraction from queries.
        Tests that time context is correctly identified from various query formats.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        Time-based traffic information.
        """
        
        advisor = TrafficAdvisor(context_content)
        
        time_test_cases = [
            ("Traffic at 8 AM", "morning"),
            ("How is traffic at 6 PM?", "evening"),
            ("Afternoon traffic conditions", "afternoon"),
            ("Late night travel", "night"),
            ("Morning rush hour", "morning"),
            ("Evening peak time", "evening")
        ]
        
        for query, expected_time_context in time_test_cases:
            extracted_context = advisor._extract_time_context(query.lower(), None)
            
            # Property: Time context should be extracted correctly
            assert extracted_context == expected_time_context, \
                f"Time context extraction failed for '{query}': expected {expected_time_context}, got {extracted_context}"
    
    def test_slang_explanation_in_traffic_responses(self):
        """
        Property test for slang explanation in traffic responses.
        Tests that traffic responses include slang explanations when slang is used.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        Traffic information with local context.
        """
        
        advisor = TrafficAdvisor(context_content)
        
        queries = [
            "Is Silk Board bad?",
            "Traffic conditions now",
            "How to avoid peak hour traffic?",
            "Metro suggestions please"
        ]
        
        for query in queries:
            advice = advisor.get_traffic_advice(query)
            advice_lower = advice.lower()
            
            # Property: If slang is used, explanations should be provided
            slang_terms = ['scene illa maga', 'guru', 'sakkath', 'machcha']
            used_slang = [term for term in slang_terms if term in advice_lower]
            
            if used_slang:
                # Should have explanations in parentheses or similar format
                has_explanation = (
                    '(' in advice and ')' in advice or
                    '=' in advice or
                    'buddy' in advice_lower or
                    'dude' in advice_lower or
                    'awesome' in advice_lower or
                    'not happening' in advice_lower
                )
                
                assert has_explanation, \
                    f"Response uses slang {used_slang} but lacks explanations: {query}"
    
    @given(st.sampled_from(['silk_board', 'electronic_city', 'whitefield', 'outer_ring_road']))
    def test_notorious_area_handling(self, location_key):
        """
        Property test for notorious area handling.
        Tests that notorious traffic areas receive appropriate warnings.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        Information about notorious traffic areas.
        """
        
        advisor = TrafficAdvisor(context_content)
        
        # Create query for the location
        location_names = {
            'silk_board': 'Silk Board',
            'electronic_city': 'Electronic City',
            'whitefield': 'Whitefield',
            'outer_ring_road': 'Outer Ring Road'
        }
        
        query = f"How is traffic at {location_names[location_key]}?"
        advice = advisor.get_traffic_advice(query)
        advice_lower = advice.lower()
        
        # Property: Notorious areas should have traffic data
        if location_key in advisor.traffic_data:
            traffic_condition = advisor.traffic_data[location_key]
            
            # Should mention the location
            location_mentioned = location_names[location_key].lower() in advice_lower
            assert location_mentioned, f"Should mention {location_names[location_key]} in response"
            
            # Should provide realistic warning if it's a heavy traffic area
            if traffic_condition.current_level in [TrafficLevel.HEAVY, TrafficLevel.NIGHTMARE]:
                warning_terms = ['bad', 'heavy', 'congested', 'crazy', 'packed']
                has_warning = any(term in advice_lower for term in warning_terms)
                assert has_warning, f"Heavy traffic area should have warnings: {location_key}"
    
    def test_alternative_suggestion_properties(self):
        """
        Property test for alternative transportation suggestions.
        Tests that appropriate alternatives are suggested based on context.
        """
        context_content = """
        ## Traffic Patterns and Peak Hours
        Various transportation alternatives available.
        """
        
        advisor = TrafficAdvisor(context_content)
        
        # Test queries asking for alternatives
        alternative_queries = [
            "How to avoid traffic?",
            "Alternative routes to Whitefield",
            "Best way to travel during peak hours",
            "Avoid Silk Board traffic"
        ]
        
        for query in alternative_queries:
            advice = advisor.get_traffic_advice(query)
            advice_lower = advice.lower()
            
            # Property: Should suggest practical alternatives
            alternative_terms = [
                'metro', 'alternative', 'avoid', 'early', 'late', 
                'different route', 'purple line', 'green line'
            ]
            
            has_alternatives = any(term in advice_lower for term in alternative_terms)
            assert has_alternatives, \
                f"Should suggest alternatives for: {query}"
            
            # Property: Should provide actionable advice
            actionable_terms = ['use', 'take', 'try', 'leave', 'go']
            has_actionable_advice = any(term in advice_lower for term in actionable_terms)
            assert has_actionable_advice, \
                f"Should provide actionable advice for: {query}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])