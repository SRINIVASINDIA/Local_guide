"""
Property-based tests for food recommendation functionality.
Tests universal properties for time-aware food recommendations.
"""

import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, time
from food_recommender import FoodRecommendationEngine, get_food_recommendations


class TestTimeAwareFoodRecommendations:
    """Property-based tests for time-aware food recommendations."""
    
    def test_time_aware_food_recommendations(self):
        """
        Feature: bangalore-local-guide, Property 4: Time-aware food recommendations
        For any food-related query with time context, recommendations should be 
        appropriate for the specified time of day.
        **Validates: Requirements 1.1, 4.2, 9.4**
        """
        # Sample context content for testing
        context_content = """
        ## Popular Breakfast Spots and Street Food Areas
        
        ### Traditional Breakfast Places:
        - **Malleshwaram**: Famous for Dosas at Janatha Hotel, Upahara Darshini
        - **Basavanagudi**: Traditional South Indian breakfast at Vidyarthi Bhavan
        
        ### Street Food Areas:
        - **VV Puram Food Street**: Evening street food paradise
        - **Shivajinagar**: Chaat and North Indian snacks
        
        ### Time-Based Food Recommendations:
        **Morning (6-10 AM)**: Idli, Dosa, Vada, Filter Coffee
        **Lunch (12-2 PM)**: Meals (rice with sambar, rasam, vegetables)
        **Evening (4-7 PM)**: Chaat, Bajji, Tea/Coffee
        """
        
        engine = FoodRecommendationEngine(context_content)
        
        # Test morning time recommendations
        morning_queries = [
            "What should I eat for breakfast?",
            "Food recommendations for 8 AM",
            "Where to eat in the morning?",
            "Breakfast spots in Malleshwaram"
        ]
        
        for query in morning_queries:
            morning_time = datetime(2024, 1, 1, 8, 0)  # 8 AM
            response = engine.generate_food_response(query, morning_time)
            response_lower = response.lower()
            
            # Property: Morning recommendations should include breakfast items
            breakfast_terms = ['breakfast', 'dosa', 'idli', 'coffee', 'morning']
            assert any(term in response_lower for term in breakfast_terms), \
                f"Morning query should mention breakfast items: {query}"
            
            # Property: Should not recommend evening-specific items in morning
            evening_terms = ['chaat', 'bajji', 'evening snacks']
            assert not any(term in response_lower for term in evening_terms), \
                f"Morning query should not suggest evening items: {query}"
        
        # Test evening time recommendations
        evening_queries = [
            "What snacks are good in the evening?",
            "Food recommendations for 6 PM",
            "Evening food options",
            "Street food for tonight"
        ]
        
        for query in evening_queries:
            evening_time = datetime(2024, 1, 1, 18, 0)  # 6 PM
            response = engine.generate_food_response(query, evening_time)
            response_lower = response.lower()
            
            # Property: Evening recommendations should include snack items
            evening_terms = ['evening', 'snack', 'chaat', 'street food', 'vv puram']
            assert any(term in response_lower for term in evening_terms), \
                f"Evening query should mention evening items: {query}"
            
            # Property: Should not recommend breakfast-specific items in evening
            breakfast_terms = ['breakfast', 'morning']
            assert not any(term in response_lower for term in breakfast_terms), \
                f"Evening query should not suggest breakfast items: {query}"
    
    @given(st.integers(min_value=0, max_value=23))
    def test_time_based_recommendation_consistency(self, hour):
        """
        Property test for time-based recommendation consistency.
        Tests that recommendations are consistent for the same time periods.
        """
        context_content = """
        ## Popular Breakfast Spots and Street Food Areas
        Traditional breakfast and street food information.
        """
        
        engine = FoodRecommendationEngine(context_content)
        test_time = datetime(2024, 1, 1, hour, 0)
        
        # Test multiple queries at the same time
        queries = [
            "What should I eat?",
            "Food recommendations please",
            "Where to eat now?"
        ]
        
        responses = []
        for query in queries:
            response = engine.generate_food_response(query, test_time)
            responses.append(response)
        
        # Property: Time context should be consistent across queries at same time
        time_contexts = []
        for response in responses:
            response_lower = response.lower()
            if any(term in response_lower for term in ['breakfast', 'morning', 'dosa', 'idli']):
                time_contexts.append('morning')
            elif any(term in response_lower for term in ['evening', 'snack', 'chaat']):
                time_contexts.append('evening')
            else:
                time_contexts.append('general')
        
        # All responses should have similar time context for same hour
        if len(set(time_contexts)) > 1:
            # Allow some variation, but morning/evening shouldn't mix
            assert not ('morning' in time_contexts and 'evening' in time_contexts), \
                f"Inconsistent time contexts for hour {hour}: {time_contexts}"
    
    def test_location_specific_recommendations(self):
        """
        Property test for location-specific food recommendations.
        Tests that location mentions in queries affect recommendations appropriately.
        """
        context_content = """
        ## Popular Breakfast Spots and Street Food Areas
        
        ### Traditional Breakfast Places:
        - **Malleshwaram**: Famous for Dosas at Janatha Hotel, Upahara Darshini
        - **Basavanagudi**: Traditional South Indian breakfast at Vidyarthi Bhavan
        
        ### Street Food Areas:
        - **VV Puram Food Street**: Evening street food paradise
        - **Koramangala**: Trendy cafes and food joints
        """
        
        engine = FoodRecommendationEngine(context_content)
        
        location_test_cases = [
            ("Where to eat in Malleshwaram?", "malleshwaram", ["janatha hotel", "upahara darshini"]),
            ("Food in Basavanagudi", "basavanagudi", ["vidyarthi bhavan"]),
            ("VV Puram street food", "vv puram", ["street food", "chaat"]),
            ("Koramangala restaurants", "koramangala", ["trendy", "cafes"])
        ]
        
        for query, location, expected_terms in location_test_cases:
            response = engine.generate_food_response(query)
            response_lower = response.lower()
            
            # Property: Location-specific queries should mention the location
            assert location in response_lower, \
                f"Response should mention {location} for query: {query}"
            
            # Property: Should include location-specific recommendations
            assert any(term in response_lower for term in expected_terms), \
                f"Response should include location-specific terms {expected_terms} for: {query}"
    
    def test_food_type_filtering(self):
        """
        Property test for food type filtering in recommendations.
        Tests that specific food type queries return appropriate recommendations.
        """
        context_content = """
        ## Popular Breakfast Spots and Street Food Areas
        Various food options available.
        """
        
        engine = FoodRecommendationEngine(context_content)
        
        food_type_queries = [
            ("breakfast recommendations", ["breakfast", "morning", "dosa", "idli"]),
            ("street food options", ["street", "snack", "chaat", "evening"]),
            ("lunch suggestions", ["lunch", "meals", "rice"]),
            ("dinner places", ["dinner", "evening", "restaurant"])
        ]
        
        for query, expected_terms in food_type_queries:
            response = engine.generate_food_response(query)
            response_lower = response.lower()
            
            # Property: Food type queries should include relevant terms
            assert any(term in response_lower for term in expected_terms), \
                f"Food type query should include relevant terms {expected_terms}: {query}"
    
    def test_slang_explanation_in_food_responses(self):
        """
        Property test for slang explanation in food responses.
        Tests that food responses include slang explanations when slang is used.
        """
        context_content = """
        ## Popular Breakfast Spots and Street Food Areas
        Food information with local context.
        """
        
        engine = FoodRecommendationEngine(context_content)
        
        queries = [
            "What's good food here?",
            "Recommend some breakfast",
            "Evening snacks please",
            "Where to eat lunch?"
        ]
        
        for query in queries:
            response = engine.generate_food_response(query)
            response_lower = response.lower()
            
            # Property: If slang is used, explanations should be provided
            slang_terms = ['guru', 'machcha', 'sakkath']
            used_slang = [term for term in slang_terms if term in response_lower]
            
            if used_slang:
                # Should have explanations in parentheses or similar format
                has_explanation = (
                    '(' in response and ')' in response or
                    '=' in response or
                    'buddy' in response_lower or
                    'dude' in response_lower or
                    'awesome' in response_lower
                )
                
                assert has_explanation, \
                    f"Response uses slang {used_slang} but lacks explanations: {query}"
    
    @given(st.sampled_from(['morning', 'afternoon', 'evening']))
    def test_time_period_food_appropriateness(self, time_period):
        """
        Property test for time period food appropriateness.
        Tests that foods recommended for specific time periods are appropriate.
        """
        context_content = """
        ## Popular Breakfast Spots and Street Food Areas
        Time-based food recommendations available.
        """
        
        engine = FoodRecommendationEngine(context_content)
        
        # Get time-appropriate foods
        appropriate_foods = engine.get_time_appropriate_foods(time_period)
        
        # Property: Each time period should have appropriate foods
        if time_period == 'morning':
            expected_categories = ['breakfast', 'coffee', 'traditional']
            food_text = ' '.join(appropriate_foods).lower()
            assert any(cat in food_text for cat in ['idli', 'dosa', 'coffee']), \
                f"Morning foods should include breakfast items: {appropriate_foods}"
        
        elif time_period == 'evening':
            food_text = ' '.join(appropriate_foods).lower()
            assert any(cat in food_text for cat in ['chaat', 'snack', 'tea']), \
                f"Evening foods should include snack items: {appropriate_foods}"
        
        # Property: Foods should be non-empty for valid time periods
        assert len(appropriate_foods) > 0, \
            f"Time period {time_period} should have food recommendations"
    
    def test_recommendation_filtering_properties(self):
        """
        Property test for recommendation filtering behavior.
        Tests that filtering works correctly for various contexts.
        """
        context_content = """
        ## Popular Breakfast Spots and Street Food Areas
        Comprehensive food information.
        """
        
        engine = FoodRecommendationEngine(context_content)
        
        # Test that recommendations are filtered appropriately
        morning_recs = engine.get_recommendations("breakfast food", datetime(2024, 1, 1, 8, 0))
        evening_recs = engine.get_recommendations("evening snacks", datetime(2024, 1, 1, 18, 0))
        
        # Property: Morning and evening recommendations should be different
        morning_names = [rec.name for rec in morning_recs]
        evening_names = [rec.name for rec in evening_recs]
        
        # Should have some different recommendations for different times
        if morning_names and evening_names:
            assert morning_names != evening_names or len(morning_names) != len(evening_names), \
                "Morning and evening recommendations should differ"
        
        # Property: Recommendations should be relevant to query context
        for rec in morning_recs:
            assert 'morning' in rec.time_suitable or 'breakfast' in rec.food_type.lower(), \
                f"Morning recommendation should be time-appropriate: {rec.name}"
        
        for rec in evening_recs:
            assert 'evening' in rec.time_suitable or 'snack' in rec.food_type.lower(), \
                f"Evening recommendation should be time-appropriate: {rec.name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])