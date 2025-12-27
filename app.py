"""
Bangalore Local Guide - Streamlit Application
Main web interface for the Bangalore Local Guide using Kiro AI agent.
"""

import streamlit as st
import os
import sys
from datetime import datetime
from pathlib import Path
import logging
import time
import traceback
from typing import Optional

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Import our modules
from query_processor import QueryProcessor, QueryProcessingResult
from agent_manager import AgentManager
from context_manager import ContextManager
from integration_manager import IntegrationManager, IntegrationResult
from error_handler import ErrorHandler, ErrorType, ErrorSeverity, ErrorInfo, error_handler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Bangalore Local Guide",
    page_icon="🏙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .response-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .error-container {
        background-color: #fff5f5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #e53e3e;
        margin: 1rem 0;
    }
    
    .warning-container {
        background-color: #fffbf0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f6ad55;
        margin: 1rem 0;
    }
    
    .info-container {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3182ce;
        margin: 1rem 0;
    }
    
    .success-container {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #38a169;
        margin: 1rem 0;
    }
    
    .example-queries {
        background-color: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .loading-container {
        text-align: center;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #38a169;
    }
    
    .status-offline {
        background-color: #e53e3e;
    }
    
    .status-warning {
        background-color: #f6ad55;
    }
    
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #eee;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'integration_manager' not in st.session_state:
        st.session_state.integration_manager = None
    
    if 'processor' not in st.session_state:
        st.session_state.processor = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    
    if 'context_loaded' not in st.session_state:
        st.session_state.context_loaded = False
    
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
    
    if 'initialization_errors' not in st.session_state:
        st.session_state.initialization_errors = []
    
    if 'show_error_details' not in st.session_state:
        st.session_state.show_error_details = False
    
    if 'system_status' not in st.session_state:
        st.session_state.system_status = {
            'context': 'unknown',
            'agent': 'unknown',
            'last_check': None
        }
    
    if 'retry_count' not in st.session_state:
        st.session_state.retry_count = {}


def display_loading_indicator(message: str, show_spinner: bool = True):
    """Display a loading indicator with message."""
    st.markdown('<div class="loading-container">', unsafe_allow_html=True)
    
    if show_spinner:
        with st.spinner(message):
            time.sleep(0.1)  # Brief pause for visual feedback
    else:
        st.markdown(f"⏳ {message}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_error_info(error_info: ErrorInfo, show_details: bool = False):
    """Display error information with user-friendly formatting."""
    # Choose appropriate icon and color based on severity
    if error_info.severity == ErrorSeverity.CRITICAL:
        icon = "🚨"
        container_class = "error-container"
    elif error_info.severity == ErrorSeverity.HIGH:
        icon = "⚠️"
        container_class = "error-container"
    elif error_info.severity == ErrorSeverity.MEDIUM:
        icon = "⚡"
        container_class = "warning-container"
    else:
        icon = "ℹ️"
        container_class = "info-container"
    
    st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
    
    # Main error message
    st.markdown(f"**{icon} {error_info.user_message}**")
    
    # Recovery suggestions
    if error_info.recovery_suggestions:
        st.markdown("**What you can try:**")
        for suggestion in error_info.recovery_suggestions:
            st.markdown(f"• {suggestion}")
    
    # Show retry button if applicable
    if error_info.can_retry:
        retry_key = f"retry_{error_info.error_type.value}_{error_info.timestamp.timestamp()}"
        
        # Track retry attempts
        if retry_key not in st.session_state.retry_count:
            st.session_state.retry_count[retry_key] = 0
        
        # Limit retry attempts
        max_retries = 3
        if st.session_state.retry_count[retry_key] < max_retries:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"🔄 Try Again ({max_retries - st.session_state.retry_count[retry_key]} attempts left)", 
                           key=retry_key):
                    st.session_state.retry_count[retry_key] += 1
                    # Reset relevant session state based on error type
                    if error_info.error_type == ErrorType.CONTEXT_LOADING:
                        st.session_state.context_loaded = False
                    elif error_info.error_type == ErrorType.AGENT_INITIALIZATION:
                        st.session_state.agent_initialized = False
                        st.session_state.processor = None
                    
                    st.rerun()
        else:
            st.markdown("*Maximum retry attempts reached. Please restart the application.*")
    
    # Technical details in expander
    if show_details:
        with st.expander("🔧 Technical Details", expanded=False):
            st.code(f"Error Type: {error_info.error_type.value}")
            st.code(f"Severity: {error_info.severity.value}")
            st.code(f"Timestamp: {error_info.timestamp}")
            st.code(f"Technical Message: {error_info.message}")
            if error_info.technical_details:
                st.code(f"Details: {error_info.technical_details}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_system_health():
    """Display system health status."""
    st.markdown("### 🏥 System Health")
    
    # Context status
    context_status = st.session_state.system_status['context']
    if context_status == 'healthy':
        st.markdown('<span class="status-indicator status-online"></span>**Knowledge Base:** ✅ Loaded and Ready', 
                   unsafe_allow_html=True)
    elif context_status == 'error':
        st.markdown('<span class="status-indicator status-offline"></span>**Knowledge Base:** ❌ Failed to Load', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-indicator status-warning"></span>**Knowledge Base:** ⏳ Loading...', 
                   unsafe_allow_html=True)
    
    # Agent status
    agent_status = st.session_state.system_status['agent']
    if agent_status == 'healthy':
        st.markdown('<span class="status-indicator status-online"></span>**AI Agent:** ✅ Ready to Help', 
                   unsafe_allow_html=True)
    elif agent_status == 'error':
        st.markdown('<span class="status-indicator status-offline"></span>**AI Agent:** ❌ Not Available', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-indicator status-warning"></span>**AI Agent:** ⏳ Initializing...', 
                   unsafe_allow_html=True)
    
    # Last health check
    if st.session_state.system_status['last_check']:
        st.caption(f"Last checked: {st.session_state.system_status['last_check'].strftime('%H:%M:%S')}")


def initialize_integrated_system() -> bool:
    """Initialize the complete integrated system using IntegrationManager."""
    try:
        display_loading_indicator("Initializing your Bangalore guide system...", show_spinner=False)
        
        # Create integration manager
        if not st.session_state.integration_manager:
            st.session_state.integration_manager = IntegrationManager(
                config_path=".kiro/config.yaml",
                product_path="product.md"
            )
        
        # Initialize the complete system
        result = st.session_state.integration_manager.initialize_system()
        
        if result.success:
            # Update session state based on system status
            status = result.system_status
            st.session_state.context_loaded = status.context_loaded
            st.session_state.agent_initialized = status.agent_initialized
            st.session_state.system_initialized = True
            
            # Update system status for UI
            st.session_state.system_status = {
                'context': 'healthy' if status.context_loaded else 'error',
                'agent': 'healthy' if status.agent_initialized else 'error',
                'last_check': status.last_health_check
            }
            
            # Set up processor reference for compatibility
            st.session_state.processor = st.session_state.integration_manager.query_processor
            
            # Show success message
            st.markdown('<div class="success-container">', unsafe_allow_html=True)
            st.markdown("✅ **Your Bangalore Local Guide is ready!** All systems initialized successfully.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            logger.info("Integrated system initialized successfully")
            return True
        else:
            # Handle initialization failure
            if result.error_info:
                st.session_state.initialization_errors.append(result.error_info)
                display_error_info(result.error_info, show_details=True)
            
            # Update system status
            status = result.system_status
            st.session_state.system_status = {
                'context': 'healthy' if status.context_loaded else 'error',
                'agent': 'healthy' if status.agent_initialized else 'error',
                'last_check': status.last_health_check
            }
            
            st.error(f"❌ **System initialization failed:** {result.message}")
            return False
            
    except Exception as e:
        error_info = error_handler.handle_unknown_error(e, "system initialization")
        st.session_state.initialization_errors.append(error_info)
        display_error_info(error_info, show_details=True)
        
        st.session_state.system_status = {
            'context': 'error',
            'agent': 'error',
            'last_check': datetime.now()
        }
        
        logger.error(f"Failed to initialize integrated system: {e}")
        return False


def display_example_queries():
    """Display example queries for user guidance."""
    st.markdown('<div class="example-queries">', unsafe_allow_html=True)
    st.markdown("**💡 Try asking me about:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        • *"I have one day in Bangalore. Plan it like a local."*
        • *"What does 'scene illa maga' mean?"*
        • *"Where should I eat breakfast in Malleshwaram?"*
        """)
    
    with col2:
        st.markdown("""
        • *"Is Silk Board bad at 6 PM?"*
        • *"What are the cultural norms here?"*
        • *"Best street food areas?"*
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)


def process_user_query(query: str) -> Optional[QueryProcessingResult]:
    """Process user query through the integrated system with comprehensive error handling."""
    if not st.session_state.integration_manager:
        if not initialize_integrated_system():
            return None
    
    try:
        # Show processing indicator
        with st.spinner("Thinking like a local..."):
            result = st.session_state.integration_manager.process_user_query(query)
        
        if not result:
            error_info = error_handler.handle_query_processing_error(
                Exception("Query processing returned None"), 
                query
            )
            display_error_info(error_info)
            return None
        
        return result
        
    except ValueError as e:
        error_info = error_handler.handle_validation_error(
            f"Invalid query format: {str(e)}", 
            f"Query: {query[:100]}..."
        )
        display_error_info(error_info)
        return None
        
    except Exception as e:
        error_info = error_handler.handle_query_processing_error(e, query)
        display_error_info(error_info, show_details=True)
        return None


def display_response(result: Optional[QueryProcessingResult]):
    """Display the agent's response with proper formatting and error handling."""
    if not result:
        st.markdown('<div class="error-container">', unsafe_allow_html=True)
        st.markdown("**❌ Unable to Process Query**")
        st.markdown("I couldn't process your question. Please try rephrasing it or ask about something else.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if not result.success:
        st.markdown('<div class="error-container">', unsafe_allow_html=True)
        st.markdown(f"**❌ Query Processing Failed**")
        st.markdown(f"{result.error_message}")
        st.markdown("Please try asking your question differently.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Display successful response
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    
    # Main response content
    st.markdown("**🏙️ Local Guide Says:**")
    st.markdown(result.agent_response.content)
    
    # Show slang explanations if any
    if result.agent_response.slang_explained:
        st.markdown("---")
        st.markdown("**📚 Slang Explanations:**")
        for slang, explanation in result.agent_response.slang_explained.items():
            st.markdown(f"• **{slang}**: {explanation}")
    
    # Show processing info in expander
    with st.expander("ℹ️ Query Details", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Query Type", result.processed_query.query_type.value.title())
            st.metric("Processing Time", f"{result.processing_time_ms:.1f}ms")
        
        with col2:
            st.metric("Confidence", f"{result.processed_query.confidence:.2f}")
            if result.processed_query.keywords:
                st.write("**Keywords:**", ", ".join(result.processed_query.keywords[:5]))
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_chat_history():
    """Display chat history in sidebar with error handling."""
    try:
        if st.session_state.chat_history:
            st.sidebar.markdown("### 💬 Chat History")
            
            # Show only last 5 queries to avoid clutter
            recent_history = st.session_state.chat_history[-5:]
            
            for i, (query, timestamp) in enumerate(reversed(recent_history)):
                query_preview = query[:50] + "..." if len(query) > 50 else query
                
                with st.sidebar.expander(f"Query {len(recent_history) - i}", expanded=False):
                    st.write(f"**Time:** {timestamp.strftime('%H:%M:%S')}")
                    st.write(f"**Query:** {query_preview}")
                    
                    # Option to ask again
                    if st.button(f"Ask Again", key=f"reask_{i}_{timestamp.timestamp()}"):
                        st.session_state.current_query = query
                        st.rerun()
    
    except Exception as e:
        logger.error(f"Error displaying chat history: {e}")
        st.sidebar.error("Unable to load chat history")


def display_system_status():
    """Display system status in sidebar with comprehensive information."""
    try:
        st.sidebar.markdown("### 🔧 System Status")
        
        # Context status
        if st.session_state.system_status['context'] == 'healthy':
            st.sidebar.markdown("**Knowledge Base:** ✅ Loaded")
        elif st.session_state.system_status['context'] == 'error':
            st.sidebar.markdown("**Knowledge Base:** ❌ Error")
        else:
            st.sidebar.markdown("**Knowledge Base:** ⏳ Loading")
        
        # Agent status
        if st.session_state.system_status['agent'] == 'healthy':
            st.sidebar.markdown("**AI Agent:** ✅ Ready")
        elif st.session_state.system_status['agent'] == 'error':
            st.sidebar.markdown("**AI Agent:** ❌ Error")
        else:
            st.sidebar.markdown("**AI Agent:** ⏳ Initializing")
        
        # Show agent info if available
        if st.session_state.integration_manager and st.session_state.system_initialized:
            try:
                health_info = st.session_state.integration_manager.get_system_health()
                if health_info.get('session_id'):
                    session_id = health_info['session_id'][-8:]  # Last 8 characters
                    st.sidebar.markdown(f"**Session:** {session_id}")
                    
                    # Show query count
                    query_count = len(st.session_state.chat_history)
                    st.sidebar.markdown(f"**Queries:** {query_count}")
                    
            except Exception as e:
                logger.debug(f"Could not get system health info: {e}")
        
        # Error summary
        if st.session_state.initialization_errors:
            error_count = len(st.session_state.initialization_errors)
            st.sidebar.markdown(f"**Errors:** ⚠️ {error_count}")
            
            if st.sidebar.button("View Error Details"):
                st.session_state.show_error_details = True
                st.rerun()
        
        # Last health check
        if st.session_state.system_status.get('last_check'):
            last_check = st.session_state.system_status['last_check']
            st.sidebar.caption(f"Last check: {last_check.strftime('%H:%M:%S')}")
    
    except Exception as e:
        logger.error(f"Error displaying system status: {e}")
        st.sidebar.error("Status unavailable")


def display_error_summary():
    """Display error summary if requested."""
    if st.session_state.show_error_details and st.session_state.initialization_errors:
        st.markdown("### 🚨 Error Summary")
        
        for i, error_info in enumerate(st.session_state.initialization_errors):
            with st.expander(f"Error {i+1}: {error_info.error_type.value.title()}", expanded=False):
                display_error_info(error_info, show_details=True)
        
        # Close button
        if st.button("Close Error Details"):
            st.session_state.show_error_details = False
            st.rerun()


def validate_user_input(query: str) -> tuple[bool, Optional[str]]:
    """Validate user input and return validation result."""
    if not query or not query.strip():
        return False, "Please enter a question first!"
    
    if len(query.strip()) < 3:
        return False, "Please enter a more detailed question."
    
    if len(query) > 1000:
        return False, "Your question is too long. Please keep it under 1000 characters."
    
    # Check for potentially harmful content (basic check)
    harmful_patterns = ['<script', 'javascript:', 'eval(', 'exec(']
    query_lower = query.lower()
    
    for pattern in harmful_patterns:
        if pattern in query_lower:
            return False, "Please avoid using special characters or code in your question."
    
    return True, None


def handle_user_query(query: str):
    """Handle user query with comprehensive validation and error handling."""
    # Validate input
    is_valid, error_message = validate_user_input(query)
    
    if not is_valid:
        st.markdown('<div class="warning-container">', unsafe_allow_html=True)
        st.markdown(f"**⚠️ Input Validation**")
        st.markdown(error_message)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Add to chat history
    st.session_state.chat_history.append((query, datetime.now()))
    
    # Process query
    result = process_user_query(query)
    
    # Display response
    display_response(result)


def main():
    """Main Streamlit application with comprehensive error handling."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Header
        st.markdown('<div class="main-header">🏙️ Bangalore Local Guide</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Your friendly AI guide to Bengaluru, powered by local knowledge</div>', unsafe_allow_html=True)
        
        # Show error summary if requested
        display_error_summary()
        
        # Load context on first run
        if not st.session_state.system_initialized:
            if not initialize_integrated_system():
                st.error("❌ **Application cannot start without the integrated system.**")
                st.info("Please check the error details above and try the suggested solutions.")
                
                # Show system health for debugging
                if st.session_state.integration_manager:
                    with st.expander("🔧 System Health Details", expanded=False):
                        health = st.session_state.integration_manager.get_system_health()
                        st.json(health)
                
                st.stop()
        
        # Main chat interface
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Query input with better UX
        user_query = st.text_input(
            "Ask like a local:",
            placeholder="What would you like to know about Bangalore?",
            help="Ask me about food, traffic, culture, places to visit, or local slang!",
            key="main_query_input"
        )
        
        # Process query button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            ask_button = st.button("🗣️ Ask Your Local Guide", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle query submission
        if ask_button and user_query.strip():
            handle_user_query(user_query)
        elif ask_button and not user_query.strip():
            st.warning("Please enter a question first!")
        
        # Handle query from chat history
        if hasattr(st.session_state, 'current_query') and st.session_state.current_query:
            handle_user_query(st.session_state.current_query)
            st.session_state.current_query = None
        
        # Show example queries if no interaction yet
        if not st.session_state.chat_history:
            display_example_queries()
        
        # Sidebar content
        with st.sidebar:
            st.markdown("### 🎯 About This Guide")
            st.markdown("""
            I'm your friendly Bangalore local guide! I know the city inside out and can help you with:
            
            🍽️ **Food & Restaurants**  
            🚗 **Traffic & Transportation**  
            🗣️ **Local Slang & Culture**  
            📍 **Places to Visit**  
            🎯 **Local Tips & Tricks**
            
            All my knowledge comes from local expertise, so you get authentic Bangalore advice!
            """)
            
            # Display system status
            display_system_status()
            
            # Display system health
            display_system_health()
            
            # Display chat history
            display_chat_history()
            
            # Clear history button
            if st.session_state.chat_history:
                if st.button("🗑️ Clear History"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Refresh system button
            if st.button("🔄 Refresh System"):
                # Reset system state
                st.session_state.integration_manager = None
                st.session_state.context_loaded = False
                st.session_state.agent_initialized = False
                st.session_state.system_initialized = False
                st.session_state.processor = None
                st.session_state.initialization_errors = []
                st.session_state.system_status = {
                    'context': 'unknown',
                    'agent': 'unknown',
                    'last_check': None
                }
                st.rerun()
        
        # Footer
        st.markdown('<div class="footer">', unsafe_allow_html=True)
        st.markdown("""
        **Bangalore Local Guide** • Powered by Kiro AI • Built with ❤️ for Bengaluru  
        *All recommendations based on local knowledge and experience*
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        # Catch-all error handler for the main application
        logger.critical(f"Critical application error: {e}")
        logger.critical(f"Stack trace: {traceback.format_exc()}")
        
        st.error("🚨 **Critical Application Error**")
        st.error("The application encountered an unexpected error and cannot continue.")
        
        with st.expander("Error Details", expanded=False):
            st.code(f"Error: {str(e)}")
            st.code(f"Type: {type(e).__name__}")
            st.code(f"Time: {datetime.now()}")
        
        st.info("Please refresh the page or restart the application.")


if __name__ == "__main__":
    main()