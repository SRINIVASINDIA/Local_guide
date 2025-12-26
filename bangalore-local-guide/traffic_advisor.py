"""
Traffic and Transportation Advisor for Bangalore Local Guide
Provides realistic traffic warnings and metro suggestions.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
from dataclasses import dataclass
from enum import Enum


class TrafficLevel(Enum):
    """Traffic congestion levels."""
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    NIGHTMARE = "nightmare"


class TransportMode(Enum):
    """Transportation modes."""
    CAR = "car"
    METRO = "metro"
    BUS = "bus"
    AUTO = "auto"
    WALK = "walk"


@dataclass
class TrafficCondition:
    """Data model for traffic conditions."""
    location: str
    current_level: TrafficLevel
    peak_hours: List[str]
    alternative_routes: List[str]
    metro_available: bool
    metro_suggestion: str
    realistic_warning: str


@dataclass
class TransportAdvice:
    """Data model for transportation advice."""
    recommended_mode: TransportMode
    estimated_time: str
    cost_estimate: str
    pros: List[str]
    cons: List[str]
    local_tips: List[str]


class TrafficAdvisor:
    """Advisor for traffic conditions and transportation recommendations."""
    
    def __init__(self, context_content: str):
        """
        Initialize traffic advisor with context.
        
        Args:
            context_content: Content from product.md containing traffic information
        """
        self.context_content = context_content
        self.traffic_data = self._parse_traffic_data()
        self.peak_hours = self._setup_peak_hours()
        self.notorious_areas = self._setup_notorious_areas()
    
    def _parse_traffic_data(self) -> Dict[str, TrafficCondition]:
        """Parse traffic data from context content."""
        traffic_data = {}
        
        # Extract traffic section
        traffic_section_match = re.search(
            r'## Traffic Patterns and Peak Hours(.*?)(?=##|$)', 
            self.context_content, 
            re.DOTALL
        )
        
        if not traffic_section_match:
            return traffic_data
        
        # Define known traffic conditions based on context
        notorious_locations = {
            "silk_board": TrafficCondition(
                location="Silk Board Junction",
                current_level=TrafficLevel.NIGHTMARE,
                peak_hours=["6:00 PM - 9:00 PM", "8:00 AM - 10:00 AM"],
                alternative_routes=["Namma Metro Purple Line"],
                metro_available=True,
                metro_suggestion="Take Purple Line metro to avoid the chaos",
                realistic_warning="Arre, Silk Board? Scene illa maga! It's absolutely packed during peak hours."
            ),
            "electronic_city": TrafficCondition(
                location="Electronic City Flyover",
                current_level=TrafficLevel.HEAVY,
                peak_hours=["8:00 AM - 10:30 AM", "6:00 PM - 8:30 PM"],
                alternative_routes=["Hosur Road alternate routes", "Metro when available"],
                metro_available=False,
                metro_suggestion="Metro not directly available, plan extra time",
                realistic_warning="Electronic City gets crazy during IT office hours"
            ),
            "outer_ring_road": TrafficCondition(
                location="Outer Ring Road (ORR)",
                current_level=TrafficLevel.HEAVY,
                peak_hours=["All day", "Especially 8-10 AM, 6-9 PM"],
                alternative_routes=["Inner roads", "Metro where possible"],
                metro_available=True,
                metro_suggestion="Use metro stations along the route when possible",
                realistic_warning="Outer Ring Road (ORR) is congested throughout the day, guru"
            ),
            "whitefield": TrafficCondition(
                location="Whitefield Road",
                current_level=TrafficLevel.HEAVY,
                peak_hours=["8:00 AM - 10:00 AM", "6:00 PM - 9:00 PM"],
                alternative_routes=["Namma Metro Purple Line"],
                metro_available=True,
                metro_suggestion="Purple Line metro is your savior for Whitefield",
                realistic_warning="Whitefield road is sakkath bad during peak hours"
            ),
            "bannerghatta_road": TrafficCondition(
                location="Bannerghatta Road",
                current_level=TrafficLevel.MODERATE,
                peak_hours=["8:00 AM - 10:00 AM", "6:00 PM - 8:00 PM"],
                alternative_routes=["Parallel roads", "Metro to nearby stations"],
                metro_available=True,
                metro_suggestion="Use Green Line metro to nearby stations",
                realistic_warning="Bannerghatta Road moves slow most times"
            ),
            "hebbal": TrafficCondition(
                location="Hebbal Flyover",
                current_level=TrafficLevel.HEAVY,
                peak_hours=["7:30 AM - 10:00 AM", "6:00 PM - 8:30 PM"],
                alternative_routes=["Service roads", "Metro to nearby areas"],
                metro_available=True,
                metro_suggestion="Metro can help reach nearby areas",
                realistic_warning="Hebbal flyover is a major bottleneck during rush hours"
            )
        }
        
        traffic_data.update(notorious_locations)
        return traffic_data
    
    def _setup_peak_hours(self) -> Dict[str, List[Tuple[int, int]]]:
        """Setup peak hour definitions."""
        return {
            'morning': [(8, 10), (9, 11)],  # 8-10 AM, 9-11 AM variations
            'evening': [(18, 21), (17, 20)],  # 6-9 PM, 5-8 PM variations
            'friday_evening': [(17, 22)]  # Friday evenings are worse
        }
    
    def _setup_notorious_areas(self) -> List[str]:
        """Setup list of notorious traffic areas."""
        return [
            "silk board", "electronic city", "outer ring road", "whitefield",
            "bannerghatta road", "hosur road", "hebbal flyover"
        ]
    
    def get_traffic_advice(self, query: str, current_time: Optional[datetime] = None) -> str:
        """
        Get traffic advice based on query and current time.
        
        Args:
            query: User's traffic query
            current_time: Current time for time-aware advice
            
        Returns:
            Natural language traffic advice
        """
        query_lower = query.lower()
        
        # Identify location mentioned in query
        location = self._extract_location(query_lower)
        
        # Determine time context
        time_context = self._extract_time_context(query_lower, current_time)
        
        # Check if it's peak hours
        is_peak_hour = self._is_peak_hour(current_time) if current_time else self._mentions_peak_time(query_lower)
        
        # Generate advice
        return self._generate_traffic_advice(location, time_context, is_peak_hour, query_lower)
    
    def _extract_location(self, query_lower: str) -> Optional[str]:
        """Extract traffic location from query."""
        location_mappings = {
            'silk board': 'silk_board',
            'silkboard': 'silk_board',
            'electronic city': 'electronic_city',
            'outer ring road': 'outer_ring_road',
            'orr': 'outer_ring_road',
            'whitefield': 'whitefield',
            'bannerghatta': 'bannerghatta_road',
            'hebbal': 'hebbal'
        }
        
        for location_phrase, location_key in location_mappings.items():
            if location_phrase in query_lower:
                return location_key
        
        return None
    
    def _extract_time_context(self, query_lower: str, current_time: Optional[datetime]) -> str:
        """Extract time context from query or current time."""
        # Check for explicit time mentions with more specific patterns
        time_patterns = {
            'morning': r'\b(morning|8\s*am|9\s*am|10\s*am|8:00|9:00|10:00|breakfast)\b',
            'evening': r'\b(evening|6\s*pm|7\s*pm|8\s*pm|9\s*pm|18:00|19:00|20:00|21:00|dinner)\b',
            'afternoon': r'\b(afternoon|12\s*pm|1\s*pm|2\s*pm|3\s*pm|4\s*pm|lunch|noon)\b',
            'night': r'\b(night|10\s*pm|11\s*pm|22:00|23:00|late)\b'
        }
        
        for time_period, pattern in time_patterns.items():
            if re.search(pattern, query_lower):
                return time_period
        
        # Use current time if available
        if current_time:
            hour = current_time.hour
            if 6 <= hour <= 11:
                return 'morning'
            elif 12 <= hour <= 17:
                return 'afternoon'
            elif 18 <= hour <= 22:
                return 'evening'
            else:
                return 'night'
        
        return 'general'
    
    def _is_peak_hour(self, current_time: datetime) -> bool:
        """Check if current time is peak hour."""
        hour = current_time.hour
        weekday = current_time.weekday()  # 0 = Monday, 6 = Sunday
        
        # Morning peak: 8-10 AM on weekdays
        if weekday < 5 and 8 <= hour <= 10:
            return True
        
        # Evening peak: 6-9 PM on weekdays
        if weekday < 5 and 18 <= hour <= 21:
            return True
        
        # Friday evening extended: 5-10 PM
        if weekday == 4 and 17 <= hour <= 22:
            return True
        
        return False
    
    def _mentions_peak_time(self, query_lower: str) -> bool:
        """Check if query mentions peak time."""
        peak_indicators = [
            'peak', 'rush hour', 'busy', 'crowded', 'traffic jam',
            '6pm', '7pm', '8pm', '9pm', '8am', '9am', '10am',
            'office hours', 'during office', 'work hours', 'working hours'
        ]
        
        return any(indicator in query_lower for indicator in peak_indicators)
    
    def _generate_traffic_advice(self, location: Optional[str], time_context: str, is_peak_hour: bool, query_lower: str) -> str:
        """Generate traffic advice based on context."""
        
        # Check for alternative/avoid queries first (higher priority)
        if 'avoid' in query_lower or 'alternative' in query_lower:
            response = "To avoid traffic madness: Use Namma Metro whenever possible, "
            response += "take alternative routes like inner roads, "
            response += "try leaving early morning or late evening. "
            response += "Go for metro lines where available for faster travel."
            
            # If specific location mentioned, add location-specific advice
            if location and location in self.traffic_data:
                traffic_condition = self.traffic_data[location]
                if traffic_condition.metro_available:
                    response += f" For {traffic_condition.location}, {traffic_condition.metro_suggestion.lower()}."
        
        # Handle specific location queries
        elif location and location in self.traffic_data:
            traffic_condition = self.traffic_data[location]
            
            # For peak hours or explicit peak mentions, provide full warnings
            if (is_peak_hour or 'peak' in query_lower or any(time in query_lower for time in ['6pm', '7pm', '8pm', '9pm'])):
                
                response = f"{traffic_condition.realistic_warning} "
                
                # Add severity indicators based on traffic level
                if traffic_condition.current_level == TrafficLevel.NIGHTMARE:
                    response += "It's absolutely packed and crazy during these hours. "
                elif traffic_condition.current_level == TrafficLevel.HEAVY:
                    response += "Traffic is heavy and bad during office hours. "
                elif traffic_condition.current_level == TrafficLevel.MODERATE:
                    response += "Traffic is busy but manageable. "
                
                if traffic_condition.metro_available:
                    response += f"{traffic_condition.metro_suggestion}. "
                
                if location == 'silk_board':
                    response += "If you must drive, leave by 5 PM or wait till after 9 PM. "
                
                response += "Metro is definitely your best friend during these hours!"
                
            # For notorious areas during non-peak times, give moderate warnings
            elif traffic_condition.current_level in [TrafficLevel.HEAVY, TrafficLevel.NIGHTMARE]:
                response = f"{traffic_condition.location} can get busy even during off-peak hours. "
                response += "Traffic is generally heavy here, so "
                if traffic_condition.metro_available:
                    response += f"{traffic_condition.metro_suggestion.lower()} for convenience. "
                response += "It's generally better outside peak times though."
                
            else:
                response = f"{traffic_condition.location} can get busy, but it's manageable outside peak hours. "
                if traffic_condition.metro_available:
                    response += f"Still, {traffic_condition.metro_suggestion.lower()} for convenience. "
        
        # Handle general traffic queries
        elif 'metro' in query_lower:
            response = "Namma Metro is sakkath for avoiding traffic! "
            response += "Purple Line covers Whitefield to Mysore Road, Green Line covers Nagasandra to Silk Institute. "
            response += "Metro operates 5:00 AM to 11:00 PM. During peak hours (8-10 AM, 6-9 PM), it's much faster than roads."
        
        elif is_peak_hour or 'peak' in query_lower:
            response = "Peak hours in Bangalore are crazy, guru! Morning 8-10 AM and evening 6-9 PM are the worst. "
            response += "Major bottlenecks: Silk Board, Electronic City Flyover, ORR, Hebbal. "
            response += "Definitely use Namma Metro during these times - it'll save you hours!"
        
        else:
            response = "Bangalore traffic can be unpredictable, machcha! "
            response += "Peak hours (8-10 AM, 6-9 PM) are definitely the worst. "
            response += "Metro is your best bet during busy times. "
            response += "Which specific area or time are you asking about?"
        
        # Add slang explanations
        response += "\n\n(Scene illa maga = not happening/not possible, Guru = buddy, Sakkath = awesome, Machcha = dude)"
        
        return response
    
    def get_metro_suggestions(self, source: str, destination: str) -> TransportAdvice:
        """Get metro-specific transportation advice."""
        return TransportAdvice(
            recommended_mode=TransportMode.METRO,
            estimated_time="30-45 minutes",
            cost_estimate="₹15-40 depending on distance",
            pros=[
                "Avoids traffic completely",
                "Predictable timing",
                "Air conditioned",
                "Economical"
            ],
            cons=[
                "Limited coverage areas",
                "Crowded during peak hours",
                "Last mile connectivity needed"
            ],
            local_tips=[
                "Download Namma Metro app for routes",
                "Avoid 8-10 AM and 6-9 PM for comfort",
                "Keep exact change or use smart card",
                "Purple and Green lines are main routes"
            ]
        )
    
    def get_peak_hour_alternatives(self, location: str) -> List[str]:
        """Get alternatives for peak hour travel."""
        alternatives = [
            "Use Namma Metro if available",
            "Leave before 8 AM or after 10 AM for morning",
            "Leave before 6 PM or after 9 PM for evening",
            "Work from home if possible",
            "Use ride-sharing with carpool options"
        ]
        
        if location in self.traffic_data:
            condition = self.traffic_data[location]
            alternatives.extend(condition.alternative_routes)
        
        return alternatives
    
    def is_notorious_area(self, location: str) -> bool:
        """Check if location is a notorious traffic area."""
        location_lower = location.lower()
        return any(area in location_lower for area in self.notorious_areas)
    
    def get_realistic_travel_time(self, distance_km: float, time_context: str, is_peak: bool) -> str:
        """Get realistic travel time estimate."""
        base_speed = 15 if is_peak else 25  # km/h during peak vs normal
        
        if time_context in ['morning', 'evening'] and is_peak:
            base_speed = 10  # Even slower during peak
        
        estimated_time = (distance_km / base_speed) * 60  # Convert to minutes
        
        if estimated_time < 30:
            return f"{int(estimated_time)}-{int(estimated_time * 1.5)} minutes"
        else:
            hours = estimated_time / 60
            return f"{hours:.1f}-{hours * 1.5:.1f} hours"


def get_traffic_advice(query: str, context_content: str, current_time: Optional[datetime] = None) -> str:
    """
    Convenience function to get traffic advice.
    
    Args:
        query: User's traffic query
        context_content: Content from product.md
        current_time: Current time for time-aware advice
        
    Returns:
        Natural language traffic advice
    """
    advisor = TrafficAdvisor(context_content)
    return advisor.get_traffic_advice(query, current_time)


if __name__ == "__main__":
    # Test the traffic advisor
    sample_context = """
    ## Traffic Patterns and Peak Hours
    
    ### Peak Traffic Hours:
    - **Morning**: 8:00 AM - 10:30 AM
    - **Evening**: 6:00 PM - 9:00 PM
    
    ### Notorious Traffic Areas:
    - **Silk Board Junction**: Always congested, especially 6-9 PM
    - **Electronic City Flyover**: Heavy during IT office hours
    - **Outer Ring Road**: Congested throughout the day
    """
    
    advisor = TrafficAdvisor(sample_context)
    
    test_queries = [
        "Is Silk Board bad at 6 PM?",
        "How to avoid traffic during peak hours?",
        "Metro suggestions for Whitefield",
        "Traffic conditions now"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        advice = advisor.get_traffic_advice(query)
        print(f"Advice: {advice[:100]}...")
        
        # Test location extraction
        location = advisor._extract_location(query.lower())
        if location:
            print(f"Detected location: {location}")
            if location in advisor.traffic_data:
                condition = advisor.traffic_data[location]
                print(f"Traffic level: {condition.current_level.value}")
                print(f"Metro available: {condition.metro_available}")