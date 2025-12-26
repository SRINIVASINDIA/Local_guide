"""
Food Recommendation Engine for Bangalore Local Guide
Provides time-aware and location-based food recommendations.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
from dataclasses import dataclass


@dataclass
class FoodRecommendation:
    """Data model for food recommendations."""
    name: str
    location: str
    food_type: str
    time_suitable: List[str]  # morning, afternoon, evening
    description: str
    local_rating: str  # sakkath, good, okay


class FoodRecommendationEngine:
    """Engine for generating time-aware and location-based food recommendations."""
    
    def __init__(self, context_content: str):
        """
        Initialize food recommendation engine with context.
        
        Args:
            context_content: Content from product.md containing food information
        """
        self.context_content = context_content
        self.recommendations = self._parse_food_recommendations()
        self.time_mappings = self._setup_time_mappings()
    
    def _parse_food_recommendations(self) -> List[FoodRecommendation]:
        """Parse food recommendations from context content."""
        recommendations = []
        
        # Extract food section
        food_section_match = re.search(
            r'## Popular Breakfast Spots and Street Food Areas(.*?)(?=##|$)', 
            self.context_content, 
            re.DOTALL
        )
        
        if not food_section_match:
            return recommendations
        
        food_section = food_section_match.group(1)
        
        # Parse breakfast places
        breakfast_places = [
            FoodRecommendation(
                name="Janatha Hotel",
                location="Malleshwaram",
                food_type="South Indian breakfast",
                time_suitable=["morning"],
                description="Famous for dosas and traditional breakfast",
                local_rating="sakkath"
            ),
            FoodRecommendation(
                name="Upahara Darshini",
                location="Malleshwaram",
                food_type="South Indian breakfast",
                time_suitable=["morning"],
                description="Quick breakfast spot",
                local_rating="good"
            ),
            FoodRecommendation(
                name="Vidyarthi Bhavan",
                location="Basavanagudi",
                food_type="South Indian breakfast",
                time_suitable=["morning"],
                description="Traditional South Indian breakfast, famous dosas",
                local_rating="sakkath"
            ),
            FoodRecommendation(
                name="VV Puram Food Street",
                location="VV Puram",
                food_type="Street food",
                time_suitable=["evening"],
                description="Evening street food paradise with chaat and snacks",
                local_rating="sakkath"
            ),
            FoodRecommendation(
                name="Shivajinagar Street Food",
                location="Shivajinagar",
                food_type="North Indian snacks",
                time_suitable=["evening"],
                description="Chaat and North Indian snacks",
                local_rating="good"
            ),
            FoodRecommendation(
                name="Koramangala Cafes",
                location="Koramangala",
                food_type="Trendy food",
                time_suitable=["afternoon", "evening"],
                description="Trendy cafes and food joints",
                local_rating="good"
            ),
            FoodRecommendation(
                name="Indiranagar Restaurants",
                location="Indiranagar",
                food_type="Mixed cuisine",
                time_suitable=["evening"],
                description="Hip restaurants and pubs",
                local_rating="good"
            )
        ]
        
        recommendations.extend(breakfast_places)
        return recommendations
    
    def _setup_time_mappings(self) -> Dict[str, List[str]]:
        """Setup time period mappings."""
        return {
            'morning': ['6am', '7am', '8am', '9am', '10am', 'morning', 'breakfast', 'early'],
            'afternoon': ['11am', '12pm', '1pm', '2pm', '3pm', '4pm', 'afternoon', 'lunch', 'noon'],
            'evening': ['5pm', '6pm', '7pm', '8pm', '9pm', '10pm', 'evening', 'dinner', 'night']
        }
    
    def get_recommendations(self, query: str, current_time: Optional[datetime] = None) -> List[FoodRecommendation]:
        """
        Get food recommendations based on query and time.
        
        Args:
            query: User's food query
            current_time: Current time (optional, uses system time if None)
            
        Returns:
            List of relevant food recommendations
        """
        query_lower = query.lower()
        
        # Determine time context
        time_context = self._extract_time_context(query_lower, current_time)
        
        # Determine location context
        location_context = self._extract_location_context(query_lower)
        
        # Filter recommendations
        filtered_recommendations = self._filter_recommendations(
            time_context, location_context, query_lower
        )
        
        return filtered_recommendations
    
    def _extract_time_context(self, query_lower: str, current_time: Optional[datetime]) -> str:
        """Extract time context from query or current time."""
        # First check for explicit PM/AM patterns
        import re
        
        # Check for PM times (evening)
        pm_pattern = r'\b([5-9]|10|11|12)\s*pm\b'
        if re.search(pm_pattern, query_lower):
            return 'evening'
        
        # Check for AM times (morning/afternoon)
        am_pattern = r'\b([6-9]|10)\s*am\b'
        if re.search(am_pattern, query_lower):
            return 'morning'
        
        am_afternoon_pattern = r'\b(11|12|1|2|3|4)\s*am\b'
        if re.search(am_afternoon_pattern, query_lower):
            return 'afternoon'
        
        # Check for explicit time mentions in query
        for time_period, keywords in self.time_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                return time_period
        
        # Use current time if no explicit mention
        if current_time:
            hour = current_time.hour
            if 6 <= hour <= 10:
                return 'morning'
            elif 11 <= hour <= 16:
                return 'afternoon'
            else:
                return 'evening'
        
        # Default to general if no time context
        return 'general'
    
    def _extract_location_context(self, query_lower: str) -> Optional[str]:
        """Extract location context from query."""
        locations = [
            'malleshwaram', 'basavanagudi', 'koramangala', 
            'indiranagar', 'vv puram', 'shivajinagar'
        ]
        
        for location in locations:
            if location in query_lower:
                return location
        
        return None
    
    def _filter_recommendations(self, time_context: str, location_context: Optional[str], query_lower: str) -> List[FoodRecommendation]:
        """Filter recommendations based on context."""
        filtered = []
        
        for rec in self.recommendations:
            # Filter by time
            if time_context != 'general' and time_context not in rec.time_suitable:
                continue
            
            # Filter by location if specified
            if location_context and location_context not in rec.location.lower():
                continue
            
            # Filter by food type if specified
            food_type_match = (
                'breakfast' in query_lower and 'breakfast' in rec.food_type.lower() or
                'street food' in query_lower and 'street' in rec.food_type.lower() or
                'snack' in query_lower and 'snack' in rec.food_type.lower() or
                'lunch' in query_lower and rec.time_suitable == ['afternoon'] or
                'dinner' in query_lower and 'evening' in rec.time_suitable or
                True  # Include all if no specific type mentioned
            )
            
            if food_type_match:
                filtered.append(rec)
        
        return filtered
    
    def generate_food_response(self, query: str, current_time: Optional[datetime] = None) -> str:
        """
        Generate a natural language food recommendation response.
        
        Args:
            query: User's food query
            current_time: Current time for time-aware recommendations
            
        Returns:
            Natural language response with food recommendations
        """
        recommendations = self.get_recommendations(query, current_time)
        query_lower = query.lower()
        
        # Determine time context for response
        time_context = self._extract_time_context(query_lower, current_time)
        location_context = self._extract_location_context(query_lower)
        
        # Generate response based on context
        if time_context == 'morning' or 'breakfast' in query_lower:
            response = "For breakfast, guru, you should try the traditional South Indian spots! "
            
            if location_context == 'malleshwaram' or not location_context:
                response += "In Malleshwaram, hit up Janatha Hotel or any Upahara Darshini for sakkath dosas. "
            
            if not location_context or location_context == 'basavanagudi':
                response += "Basavanagudi's Vidyarthi Bhavan is famous for their traditional dosas too. "
            
            response += "Get some filter coffee with it - that's how we start the day here!"
            
        elif time_context == 'evening' or 'evening' in query_lower or 'snack' in query_lower:
            response = "Evening time, machcha! "
            
            if not location_context or 'vv puram' in query_lower:
                response += "Head to VV Puram Food Street - it's the place for chaat and bajjis. "
            
            if not location_context or 'shivajinagar' in query_lower:
                response += "Or try Shivajinagar for some North Indian snacks. "
            
            response += "Perfect with evening tea!"
            
        elif time_context == 'afternoon' or 'lunch' in query_lower:
            response = "For lunch, guru, you want proper meals! "
            response += "Traditional South Indian meals with rice, sambar, rasam, and vegetables are perfect. "
            response += "Try any local Darshini or traditional restaurant for authentic lunch meals. "
            response += "Rice-based meals are the way to go during lunch time!"
            
        else:
            response = "Bangalore has sakkath food options! "
            
            if location_context == 'malleshwaram':
                response += "Malleshwaram is famous for traditional breakfast spots like Janatha Hotel. "
            elif location_context == 'koramangala':
                response += "Koramangala has trendy cafes and food joints. "
            elif location_context == 'indiranagar':
                response += "Indiranagar has hip restaurants and pubs. "
            else:
                response += "VV Puram Food Street for evening snacks, Malleshwaram for breakfast, "
                response += "and Koramangala for trendy cafes. "
        
        # Add specific recommendations if available
        if recommendations:
            response += "\n\nSpecific recommendations:\n"
            for rec in recommendations[:3]:  # Limit to top 3
                response += f"• {rec.name} in {rec.location} - {rec.description}\n"
        
        # Add slang explanations
        response += "\n\n(Guru = buddy, Sakkath = awesome, Machcha = dude)"
        
        return response
    
    def get_time_appropriate_foods(self, time_period: str) -> List[str]:
        """Get foods appropriate for a specific time period."""
        time_foods = {
            'morning': ['Idli', 'Dosa', 'Vada', 'Filter Coffee', 'Upma'],
            'afternoon': ['Meals (rice with sambar)', 'Rasam', 'Vegetables', 'Curd rice'],
            'evening': ['Chaat', 'Bajji', 'Tea/Coffee', 'Bonda', 'Masala Puri']
        }
        
        return time_foods.get(time_period, [])
    
    def get_location_specialties(self, location: str) -> List[str]:
        """Get food specialties for a specific location."""
        location_specialties = {
            'malleshwaram': ['Traditional dosas', 'Filter coffee', 'South Indian breakfast'],
            'basavanagudi': ['Vidyarthi Bhavan dosas', 'Traditional meals'],
            'vv puram': ['Street chaat', 'Evening snacks', 'Bajjis'],
            'koramangala': ['Trendy cafes', 'International cuisine'],
            'indiranagar': ['Pub food', 'Hip restaurants', 'Nightlife dining']
        }
        
        return location_specialties.get(location.lower(), [])


def get_food_recommendations(query: str, context_content: str, current_time: Optional[datetime] = None) -> str:
    """
    Convenience function to get food recommendations.
    
    Args:
        query: User's food query
        context_content: Content from product.md
        current_time: Current time for time-aware recommendations
        
    Returns:
        Natural language response with food recommendations
    """
    engine = FoodRecommendationEngine(context_content)
    return engine.generate_food_response(query, current_time)


if __name__ == "__main__":
    # Test the food recommendation engine
    sample_context = """
    ## Popular Breakfast Spots and Street Food Areas
    
    ### Traditional Breakfast Places:
    - **Malleshwaram**: Famous for Dosas at Janatha Hotel, Upahara Darshini
    - **Basavanagudi**: Traditional South Indian breakfast at Vidyarthi Bhavan
    
    ### Street Food Areas:
    - **VV Puram Food Street**: Evening street food paradise
    - **Shivajinagar**: Chaat and North Indian snacks
    """
    
    engine = FoodRecommendationEngine(sample_context)
    
    test_queries = [
        "Where should I eat breakfast in Malleshwaram?",
        "What evening snacks are good?",
        "Food recommendations for lunch time"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = engine.generate_food_response(query)
        print(f"Response: {response[:100]}...")
        
        recommendations = engine.get_recommendations(query)
        print(f"Found {len(recommendations)} recommendations")