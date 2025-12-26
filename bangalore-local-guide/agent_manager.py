"""
Agent Manager for Bangalore Local Guide
Handles Kiro agent initialization, configuration, and session management.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from context_manager import ContextManager, LocalContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserQuery:
    """Data model for user queries."""
    text: str
    timestamp: datetime
    session_id: str


@dataclass
class AgentResponse:
    """Data model for agent responses."""
    content: str
    confidence: float
    sources_used: list
    slang_explained: Dict[str, str]


class BangaloreLocalAgent:
    """
    Bangalore Local Guide Agent
    Simulates Kiro agent behavior for local guide responses.
    """
    
    def __init__(self, config: Dict[str, Any], context: LocalContext):
        """
        Initialize the agent with configuration and context.
        
        Args:
            config: Agent configuration from config.yaml
            context: Loaded Bangalore knowledge context
        """
        self.config = config
        self.context = context
        self.name = config.get('name', 'bangalore-local-guide')
        self.description = config.get('description', '')
        self.persona = config.get('persona', {})
        self.behavior_rules = config.get('behavior_rules', [])
        
        logger.info(f"Initialized agent: {self.name}")
    
    def process_query(self, query: UserQuery) -> AgentResponse:
        """
        Process a user query and generate a response.
        
        Args:
            query: User query object
            
        Returns:
            AgentResponse with generated content
        """
        logger.info(f"Processing query: {query.text[:50]}...")
        
        # Analyze query type
        query_type = self._analyze_query_type(query.text.lower())
        
        # Generate response based on query type and context
        response_content = self._generate_response(query.text, query_type)
        
        # Extract any slang explanations
        slang_explained = self._extract_slang_explanations(response_content)
        
        # Create response object
        response = AgentResponse(
            content=response_content,
            confidence=0.9,  # High confidence since we use curated content
            sources_used=["product.md"],
            slang_explained=slang_explained
        )
        
        logger.info("Query processed successfully")
        return response
    
    def _analyze_query_type(self, query_lower: str) -> str:
        """Analyze the type of query to provide appropriate response."""
        if any(word in query_lower for word in ['food', 'eat', 'breakfast', 'lunch', 'dinner', 'restaurant']):
            return 'food'
        elif any(word in query_lower for word in ['traffic', 'travel', 'metro', 'transport', 'road']):
            return 'traffic'
        elif any(word in query_lower for word in ['slang', 'mean', 'meaning', 'scene illa', 'guru', 'machcha']):
            return 'slang'
        elif any(word in query_lower for word in ['itinerary', 'plan', 'day', 'visit', 'places']):
            return 'itinerary'
        elif any(word in query_lower for word in ['culture', 'etiquette', 'custom', 'tradition']):
            return 'culture'
        else:
            return 'general'
    
    def _generate_response(self, query: str, query_type: str) -> str:
        """Generate response based on query type and context."""
        sections = self.context.get_sections()
        
        if query_type == 'food':
            return self._generate_food_response(query, sections)
        elif query_type == 'traffic':
            return self._generate_traffic_response(query, sections)
        elif query_type == 'slang':
            return self._generate_slang_response(query, sections)
        elif query_type == 'itinerary':
            return self._generate_itinerary_response(query, sections)
        elif query_type == 'culture':
            return self._generate_culture_response(query, sections)
        else:
            return self._generate_general_response(query, sections)
    
    def _generate_food_response(self, query: str, sections: Dict[str, str]) -> str:
        """Generate food-related response."""
        food_section = sections.get("Popular Breakfast Spots and Street Food Areas", "")
        
        # Check for time-based recommendations
        query_lower = query.lower()
        if any(time in query_lower for time in ['morning', 'breakfast', '6', '7', '8', '9']):
            response = "For breakfast, guru, you should try the traditional South Indian spots! "
            response += "In Malleshwaram, hit up Janatha Hotel or any Upahara Darshini for amazing dosas. "
            response += "Basavanagudi's Vidyarthi Bhavan is sakkath for their famous dosas too. "
            response += "Get some filter coffee with it - that's how we start the day here!"
        elif any(time in query_lower for time in ['evening', 'snack', '4', '5', '6']):
            response = "Evening time, machcha! Head to VV Puram Food Street - it's the place for chaat and bajjis. "
            response += "Or try Shivajinagar for some North Indian snacks. Perfect with evening tea!"
        else:
            response = "Bangalore has sakkath food options! "
            if "malleshwaram" in query_lower:
                response += "Malleshwaram is famous for traditional breakfast spots like Janatha Hotel. "
            else:
                response += "VV Puram Food Street for evening snacks, Malleshwaram for breakfast, "
                response += "and Koramangala for trendy cafes. "
        
        # Add slang explanations
        response += "\n\n(Guru = buddy, Sakkath = awesome, Machcha = dude)"
        return response
    
    def _generate_traffic_response(self, query: str, sections: Dict[str, str]) -> str:
        """Generate traffic-related response."""
        traffic_section = sections.get("Traffic Patterns and Peak Hours", "")
        
        query_lower = query.lower()
        if "silk board" in query_lower:
            if any(time in query_lower for time in ['6', '7', '8', '9', 'evening', 'pm']):
                response = "Arre, Silk Board at 6 PM? Scene illa maga! It's absolutely packed. "
                response += "Take the metro if possible - Purple Line will save you hours. "
                response += "If you must drive, leave by 5 PM or wait till after 9 PM."
            else:
                response = "Silk Board is always busy, but evenings (6-9 PM) are the worst. "
                response += "Metro is your best friend during peak hours!"
        else:
            response = "Traffic in Bangalore can be crazy, especially 8-10 AM and 6-9 PM. "
            response += "Outer Ring Road, Electronic City Flyover, and Hebbal are major bottlenecks. "
            response += "During peak hours, definitely use Namma Metro - it's much faster!"
        
        response += "\n\n(Scene illa maga = not happening/not possible, dude)"
        return response
    
    def _generate_slang_response(self, query: str, sections: Dict[str, str]) -> str:
        """Generate slang explanation response."""
        slang_section = sections.get("Local Slang and Meanings", "")
        
        query_lower = query.lower()
        if "scene illa" in query_lower:
            return "'Scene illa maga' means 'not happening, dude' or 'not possible'. We use it when something won't work out or isn't going to happen. Like if someone asks to meet during Silk Board traffic - scene illa!"
        elif "guru" in query_lower:
            return "'Guru' is how we address friends here - like 'buddy' or 'dude'. Very common in Bangalore. 'Yen guru?' means 'What's up, buddy?'"
        elif "sakkath" in query_lower:
            return "'Sakkath' means awesome or excellent! When the dosa is really good, we say 'sakkath dosa'. It's pure Bangalore slang, guru!"
        elif "machcha" in query_lower:
            return "'Machcha' literally means 'fish' in Kannada, but we use it like 'dude' or 'buddy'. It's a friendly way to address someone."
        else:
            return "Here are some common Bangalore slang terms:\n" + \
                   "• Scene illa maga = Not happening, dude\n" + \
                   "• Guru = Buddy/friend\n" + \
                   "• Sakkath = Awesome\n" + \
                   "• Machcha = Dude (literally 'fish')\n" + \
                   "• Yen guru = What's up, buddy?"
    
    def _generate_itinerary_response(self, query: str, sections: Dict[str, str]) -> str:
        """Generate itinerary response."""
        response = "Here's a perfect one-day Bangalore plan, guru!\n\n"
        response += "**Morning (8-11 AM):** Start with breakfast in Malleshwaram - try Janatha Hotel for sakkath dosas and filter coffee.\n\n"
        response += "**Late Morning (11 AM-1 PM):** Visit Lalbagh Botanical Garden or Cubbon Park. Take the metro to avoid traffic!\n\n"
        response += "**Lunch (1-3 PM):** Head to Jayanagar 4th Block for a traditional South Indian meals.\n\n"
        response += "**Afternoon (3-6 PM):** Explore Commercial Street for shopping or Brigade Road for cafes.\n\n"
        response += "**Evening (6-8 PM):** VV Puram Food Street for street food - the chaat is amazing!\n\n"
        response += "**Night (8-10 PM):** If you're into pubs, Indiranagar has great options. Otherwise, a nice dinner in Koramangala.\n\n"
        response += "Pro tip: Use Namma Metro during peak hours (6-9 PM) to avoid the traffic madness!"
        response += "\n\n(Guru = buddy, Sakkath = awesome)"
        return response
    
    def _generate_culture_response(self, query: str, sections: Dict[str, str]) -> str:
        """Generate culture/etiquette response."""
        culture_section = sections.get("Cultural Norms and Etiquette", "")
        
        response = "Bangalore culture is pretty chill, but here are some tips:\n\n"
        response += "• Greet with 'Namaste' or 'Namaskara' (Kannada)\n"
        response += "• Remove shoes when entering homes and temples\n"
        response += "• Respect for elders is important - touch their feet as a sign of respect\n"
        response += "• Many people are vegetarian, especially on Tuesdays and Fridays\n"
        response += "• IT culture is casual, but traditional businesses are more formal\n"
        response += "• Sharing food is a sign of friendship\n"
        response += "• Traffic can be chaotic - be patient, it's just how we roll here!"
        
        return response
    
    def _generate_general_response(self, query: str, sections: Dict[str, str]) -> str:
        """Generate general response."""
        return "I'm your friendly Bangalore local guide! Ask me about food, traffic, slang, places to visit, or local culture. I know this city like the back of my hand, guru!"
    
    def _extract_slang_explanations(self, response: str) -> Dict[str, str]:
        """Extract slang explanations from response."""
        explanations = {}
        
        # Look for explanation patterns in parentheses
        import re
        
        # Pattern 1: (term = explanation)
        pattern1 = r'\(([^=]+)=([^)]+)\)'
        matches1 = re.findall(pattern1, response)
        
        for match in matches1:
            slang_term = match[0].strip()
            explanation = match[1].strip()
            explanations[slang_term] = explanation
        
        # Pattern 2: Look for common slang terms and their explanations in the response
        slang_terms = {
            'scene illa': 'not happening/not possible',
            'guru': 'buddy/friend', 
            'sakkath': 'awesome',
            'machcha': 'dude'
        }
        
        response_lower = response.lower()
        for term, meaning in slang_terms.items():
            if term in response_lower:
                # Look for explanation patterns around the term
                if any(word in response_lower for word in ['means', 'meaning', 'like', 'buddy', 'dude', 'awesome']):
                    explanations[term] = meaning
        
        return explanations


class AgentManager:
    """Manages Kiro agent initialization and session handling."""
    
    def __init__(self, config_path: str = ".kiro/config.yaml", product_path: str = "product.md"):
        """
        Initialize agent manager.
        
        Args:
            config_path: Path to agent configuration file
            product_path: Path to product knowledge file
        """
        self.config_path = Path(config_path)
        self.product_path = product_path
        self.context_manager = ContextManager(product_path)
        self.agent: Optional[BangaloreLocalAgent] = None
        self.session_context: Optional[LocalContext] = None
        self.session_id: Optional[str] = None
    
    def initialize_agent(self) -> BangaloreLocalAgent:
        """
        Initialize the Kiro agent with configuration and context.
        
        Returns:
            Initialized BangaloreLocalAgent
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        try:
            # Load agent configuration
            config = self._load_agent_config()
            
            # Load context
            context = self.context_manager.load_context()
            
            # Create agent
            self.agent = BangaloreLocalAgent(config, context)
            self.session_context = context
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"Agent initialized successfully for session: {self.session_id}")
            return self.agent
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    def _load_agent_config(self) -> Dict[str, Any]:
        """Load agent configuration from YAML file."""
        if not self.config_path.exists():
            # Return default configuration if file doesn't exist
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required config field: {field}")
            
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default agent configuration."""
        return {
            'name': 'bangalore-local-guide',
            'description': 'Friendly Bangalore local guide',
            'persona': {
                'identity': 'Bangalore local resident',
                'tone': 'helpful, practical, culturally aware',
                'style': 'concise but informative'
            },
            'behavior_rules': [
                'explain_slang_when_used',
                'recommend_food_by_time',
                'warn_about_traffic_realistically',
                'suggest_metro_during_peaks',
                'no_hallucination_policy'
            ],
            'context_sources': ['product.md']
        }
    
    def process_user_query(self, query_text: str) -> AgentResponse:
        """
        Process a user query through the agent.
        
        Args:
            query_text: User's question or request
            
        Returns:
            AgentResponse with generated content
            
        Raises:
            RuntimeError: If agent is not initialized
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize_agent() first.")
        
        # Create query object
        query = UserQuery(
            text=query_text,
            timestamp=datetime.now(),
            session_id=self.session_id or "default"
        )
        
        # Process through agent
        return self.agent.process_query(query)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the current agent."""
        if not self.agent:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "name": self.agent.name,
            "description": self.agent.description,
            "session_id": self.session_id,
            "context_loaded": self.session_context is not None,
            "context_summary": self.context_manager.get_context_summary()
        }
    
    def reload_context(self) -> None:
        """Reload context and update agent."""
        if self.agent:
            new_context = self.context_manager.reload_context()
            self.agent.context = new_context
            self.session_context = new_context
            logger.info("Context reloaded successfully")


if __name__ == "__main__":
    # Test the agent manager
    try:
        manager = AgentManager()
        agent = manager.initialize_agent()
        
        print("Agent initialized successfully!")
        print(f"Agent info: {manager.get_agent_info()}")
        
        # Test a query
        response = manager.process_user_query("What does 'scene illa maga' mean?")
        print(f"\nTest query response: {response.content}")
        
    except Exception as e:
        print(f"Error: {e}")