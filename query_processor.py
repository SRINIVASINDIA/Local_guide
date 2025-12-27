"""
Query Processing Pipeline for Bangalore Local Guide
Handles query validation, processing, and response generation.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from agent_manager import AgentManager, UserQuery, AgentResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Enumeration of supported query types."""
    FOOD = "food"
    TRAFFIC = "traffic"
    SLANG = "slang"
    ITINERARY = "itinerary"
    CULTURE = "culture"
    GENERAL = "general"
    INVALID = "invalid"


@dataclass
class ProcessedQuery:
    """Data model for processed query information."""
    original_text: str
    cleaned_text: str
    query_type: QueryType
    keywords: List[str]
    time_context: Optional[str]
    location_context: Optional[str]
    confidence: float
    is_valid: bool


@dataclass
class QueryProcessingResult:
    """Result of query processing pipeline."""
    processed_query: ProcessedQuery
    agent_response: Optional[AgentResponse]
    processing_time_ms: float
    success: bool
    error_message: Optional[str]


class QueryValidator:
    """Validates and sanitizes user queries."""
    
    def __init__(self):
        self.min_length = 2
        self.max_length = 500
        self.forbidden_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript URLs
            r'data:',                   # Data URLs
            r'vbscript:',               # VBScript URLs
        ]
    
    def validate_query(self, query_text: str) -> Tuple[bool, str, str]:
        """
        Validate and sanitize a user query.
        
        Args:
            query_text: Raw user input
            
        Returns:
            Tuple of (is_valid, cleaned_text, error_message)
        """
        if not query_text:
            return False, "", "Query cannot be empty"
        
        # Basic length validation
        if len(query_text.strip()) < self.min_length:
            return False, "", f"Query too short (minimum {self.min_length} characters)"
        
        if len(query_text) > self.max_length:
            return False, "", f"Query too long (maximum {self.max_length} characters)"
        
        # Security validation - check for malicious patterns
        query_lower = query_text.lower()
        for pattern in self.forbidden_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False, "", "Query contains invalid content"
        
        # Clean the query
        cleaned = self._clean_query(query_text)
        
        return True, cleaned, ""
    
    def _clean_query(self, query_text: str) -> str:
        """Clean and normalize query text."""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', query_text.strip())
        
        # Remove potentially harmful characters but keep basic punctuation
        cleaned = re.sub(r'[<>{}]', '', cleaned)
        
        return cleaned


class QueryAnalyzer:
    """Analyzes queries to determine type and extract context."""
    
    def __init__(self):
        self.query_patterns = {
            QueryType.FOOD: [
                r'\b(food|eat|breakfast|lunch|dinner|restaurant|cafe|dosa|idli|meal|hungry|taste)\b',
                r'\b(where.*eat|what.*eat|food.*recommend|restaurant.*suggest)\b',
                r'\b(malleshwaram|basavanagudi|vv puram|street food)\b'
            ],
            QueryType.TRAFFIC: [
                r'\b(traffic|road|drive|metro|transport|travel|commute|bus|auto)\b',
                r'\b(silk board|electronic city|outer ring|whitefield|hebbal)\b',
                r'\b(how.*reach|traffic.*bad|metro.*better|avoid.*traffic)\b'
            ],
            QueryType.SLANG: [
                r'\b(slang|mean|meaning|what.*mean|explain|guru|machcha|sakkath|scene illa)\b',
                r'\b(what.*guru|what.*machcha|what.*sakkath|scene illa maga)\b'
            ],
            QueryType.ITINERARY: [
                r'\b(itinerary|plan|day|visit|places|tour|trip|schedule)\b',
                r'\b(one day|full day|places.*visit|what.*see|plan.*day)\b'
            ],
            QueryType.CULTURE: [
                r'\b(culture|custom|tradition|etiquette|behavior|respect|temple)\b',
                r'\b(cultural.*norm|how.*behave|what.*expect|local.*custom)\b'
            ]
        }
        
        self.time_patterns = {
            'morning': r'\b(morning|breakfast|6am|7am|8am|9am|early)\b',
            'afternoon': r'\b(afternoon|lunch|12pm|1pm|2pm|3pm|noon)\b',
            'evening': r'\b(evening|dinner|6pm|7pm|8pm|9pm|night)\b'
        }
        
        self.location_patterns = {
            'malleshwaram': r'\bmalleshwaram\b',
            'basavanagudi': r'\bbasavanagudi\b',
            'koramangala': r'\bkoramangala\b',
            'indiranagar': r'\bindiranagar\b',
            'whitefield': r'\bwhitefield\b',
            'electronic_city': r'\belectronic city\b',
            'silk_board': r'\bsilk board\b'
        }
    
    def analyze_query(self, query_text: str) -> ProcessedQuery:
        """
        Analyze query to determine type and extract context.
        
        Args:
            query_text: Cleaned query text
            
        Returns:
            ProcessedQuery with analysis results
        """
        query_lower = query_text.lower()
        
        # Determine query type
        query_type, confidence = self._determine_query_type(query_lower)
        
        # Extract keywords
        keywords = self._extract_keywords(query_lower)
        
        # Extract time context
        time_context = self._extract_time_context(query_lower)
        
        # Extract location context
        location_context = self._extract_location_context(query_lower)
        
        # Determine if query is valid
        is_valid = query_type != QueryType.INVALID and confidence > 0.3
        
        return ProcessedQuery(
            original_text=query_text,
            cleaned_text=query_text,
            query_type=query_type,
            keywords=keywords,
            time_context=time_context,
            location_context=location_context,
            confidence=confidence,
            is_valid=is_valid
        )
    
    def _determine_query_type(self, query_lower: str) -> Tuple[QueryType, float]:
        """Determine the type of query and confidence score."""
        type_scores = {}
        
        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                type_scores[query_type] = score
        
        if not type_scores:
            return QueryType.GENERAL, 0.5
        
        # Get the type with highest score
        best_type = max(type_scores, key=type_scores.get)
        max_score = type_scores[best_type]
        
        # Normalize confidence (simple heuristic)
        confidence = min(0.9, 0.5 + (max_score * 0.2))
        
        return best_type, confidence
    
    def _extract_keywords(self, query_lower: str) -> List[str]:
        """Extract relevant keywords from query."""
        # Simple keyword extraction - can be enhanced
        words = re.findall(r'\b\w+\b', query_lower)
        
        # Filter out common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _extract_time_context(self, query_lower: str) -> Optional[str]:
        """Extract time context from query."""
        for time_period, pattern in self.time_patterns.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                return time_period
        return None
    
    def _extract_location_context(self, query_lower: str) -> Optional[str]:
        """Extract location context from query."""
        for location, pattern in self.location_patterns.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                return location
        return None


class QueryProcessor:
    """Main query processing pipeline."""
    
    def __init__(self, agent_manager: Optional[AgentManager] = None):
        """
        Initialize query processor.
        
        Args:
            agent_manager: Optional pre-initialized agent manager
        """
        self.validator = QueryValidator()
        self.analyzer = QueryAnalyzer()
        self.agent_manager = agent_manager or AgentManager()
        self._agent_initialized = False
    
    def process_query(self, query_text: str) -> QueryProcessingResult:
        """
        Process a user query through the complete pipeline.
        
        Args:
            query_text: Raw user input
            
        Returns:
            QueryProcessingResult with processing outcome
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Validate and sanitize query
            is_valid, cleaned_text, error_msg = self.validator.validate_query(query_text)
            
            if not is_valid:
                return QueryProcessingResult(
                    processed_query=ProcessedQuery(
                        original_text=query_text,
                        cleaned_text="",
                        query_type=QueryType.INVALID,
                        keywords=[],
                        time_context=None,
                        location_context=None,
                        confidence=0.0,
                        is_valid=False
                    ),
                    agent_response=None,
                    processing_time_ms=self._get_elapsed_ms(start_time),
                    success=False,
                    error_message=error_msg
                )
            
            # Step 2: Analyze query
            processed_query = self.analyzer.analyze_query(cleaned_text)
            
            if not processed_query.is_valid:
                return QueryProcessingResult(
                    processed_query=processed_query,
                    agent_response=None,
                    processing_time_ms=self._get_elapsed_ms(start_time),
                    success=False,
                    error_message="Query could not be understood"
                )
            
            # Step 3: Initialize agent if needed
            if not self._agent_initialized:
                self.agent_manager.initialize_agent()
                self._agent_initialized = True
            
            # Step 4: Process through agent
            agent_response = self.agent_manager.process_user_query(cleaned_text)
            
            # Step 5: Return successful result
            return QueryProcessingResult(
                processed_query=processed_query,
                agent_response=agent_response,
                processing_time_ms=self._get_elapsed_ms(start_time),
                success=True,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryProcessingResult(
                processed_query=ProcessedQuery(
                    original_text=query_text,
                    cleaned_text=cleaned_text if 'cleaned_text' in locals() else "",
                    query_type=QueryType.INVALID,
                    keywords=[],
                    time_context=None,
                    location_context=None,
                    confidence=0.0,
                    is_valid=False
                ),
                agent_response=None,
                processing_time_ms=self._get_elapsed_ms(start_time),
                success=False,
                error_message=f"Processing error: {str(e)}"
            )
    
    def _get_elapsed_ms(self, start_time: datetime) -> float:
        """Calculate elapsed time in milliseconds."""
        return (datetime.now() - start_time).total_seconds() * 1000
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about query processing."""
        return {
            "agent_initialized": self._agent_initialized,
            "agent_info": self.agent_manager.get_agent_info() if self._agent_initialized else None,
            "validator_config": {
                "min_length": self.validator.min_length,
                "max_length": self.validator.max_length
            }
        }
    
    def reload_agent_context(self) -> None:
        """Reload agent context (useful when product.md is updated)."""
        if self._agent_initialized:
            self.agent_manager.reload_context()
            logger.info("Agent context reloaded")


# Convenience functions for easy usage
def process_user_query(query_text: str) -> QueryProcessingResult:
    """
    Convenience function to process a single query.
    
    Args:
        query_text: User's question
        
    Returns:
        QueryProcessingResult with response
    """
    processor = QueryProcessor()
    return processor.process_query(query_text)


def get_simple_response(query_text: str) -> str:
    """
    Get a simple string response for a query.
    
    Args:
        query_text: User's question
        
    Returns:
        Response text or error message
    """
    result = process_user_query(query_text)
    
    if result.success and result.agent_response:
        return result.agent_response.content
    else:
        return result.error_message or "Sorry, I couldn't process your query."


if __name__ == "__main__":
    # Test the query processor
    processor = QueryProcessor()
    
    test_queries = [
        "What does scene illa maga mean?",
        "Where should I eat breakfast in Malleshwaram?",
        "Is Silk Board bad at 6 PM?",
        "I have one day in Bangalore. Plan it like a local."
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = processor.process_query(query)
        
        if result.success:
            print(f"Type: {result.processed_query.query_type.value}")
            print(f"Response: {result.agent_response.content[:100]}...")
            print(f"Processing time: {result.processing_time_ms:.2f}ms")
        else:
            print(f"Error: {result.error_message}")
    
    print(f"\nProcessing stats: {processor.get_processing_stats()}")