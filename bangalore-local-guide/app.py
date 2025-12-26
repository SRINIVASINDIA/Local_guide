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

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Import our modules
from query_processor import QueryProcessor, QueryProcessingResult
from agent_manager import AgentManager
from context_manager import ContextManager
from error_handler import error_handler, ErrorType, ErrorSeverity

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
    
    .info-container {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3182ce;
        margin: 1rem 0;
    }
    
    .example-queries {
        background-color: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'processor' not in st.session_state:
        st.session_state.processor = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    
    if 'context_loaded' not in st.session_state:
        st.session_state.context_loaded = False


def load_context():
    """Load and validate the Bangalore knowledge context."""
    try:
        # Get the correct path to product.md
        product_path = current_dir / "product.md"
        
        if not product_path.exists():
            st.error(f"❌ Knowledge base not found at: {product_path}")
            st.info("Please ensure product.md exists in the application directory.")
            return None
        
        context_manager = ContextManager(str(product_path))
        context = context_manager.load_context()
        
        st.session_state.context_loaded = True
        logger.info("Context loaded successfully")
        return context
        
    except Exception as e:
        st.error(f"❌ Failed to load knowledge base: {str(e)}")
        logger.error(f"Context loading error: {e}")
        return None


def initialize_agent():
    """Initialize the Kiro agent and query processor."""
    try:
        if st.session_state.processor is None:
            # Get correct paths
            config_path = current_dir / ".kiro" / "config.yaml"
            product_path = current_dir / "product.md"
            
            # Create agent manager with correct paths
            agent_manager = AgentManager(
                config_path=str(config_path),
                product_path=str(product_path)
            )
            
            # Create query processor
            processor = QueryProcessor(agent_manager)
            
            st.session_state.processor = processor
            st.session_state.agent_initialized = True
            
            logger.info("Agent initialized successfully")
            return True
            
    except Exception as e:
        st.error(f"❌ Failed to initialize agent: {str(e)}")
        logger.error(f"Agent initialization error: {e}")
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


def process_user_query(query: str) -> QueryProcessingResult:
    """Process user query through the agent."""
    if not st.session_state.processor:
        if not initialize_agent():
            return None
    
    try:
        result = st.session_state.processor.process_query(query)
        return result
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return None


def display_response(result: QueryProcessingResult):
    """Display the agent's response with proper formatting."""
    if not result:
        st.markdown('<div class="error-container">', unsafe_allow_html=True)
        st.error("❌ Sorry, I couldn't process your query. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if not result.success:
        st.markdown('<div class="error-container">', unsafe_allow_html=True)
        st.error(f"❌ {result.error_message}")
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
    """Display chat history in sidebar."""
    if st.session_state.chat_history:
        st.sidebar.markdown("### 💬 Chat History")
        
        for i, (query, timestamp) in enumerate(reversed(st.session_state.chat_history[-5:])):
            with st.sidebar.expander(f"Query {len(st.session_state.chat_history) - i}", expanded=False):
                st.write(f"**Time:** {timestamp.strftime('%H:%M:%S')}")
                st.write(f"**Query:** {query[:50]}{'...' if len(query) > 50 else ''}")


def display_system_status():
    """Display system status in sidebar."""
    st.sidebar.markdown("### 🔧 System Status")
    
    # Context status
    context_status = "✅ Loaded" if st.session_state.context_loaded else "❌ Not Loaded"
    st.sidebar.markdown(f"**Knowledge Base:** {context_status}")
    
    # Agent status
    agent_status = "✅ Ready" if st.session_state.agent_initialized else "❌ Not Ready"
    st.sidebar.markdown(f"**AI Agent:** {agent_status}")
    
    # Show agent info if available
    if st.session_state.processor and st.session_state.agent_initialized:
        try:
            agent_info = st.session_state.processor.get_processing_stats()
            if agent_info.get('agent_info'):
                info = agent_info['agent_info']
                st.sidebar.markdown(f"**Session:** {info.get('session_id', 'Unknown')[:8]}...")
        except:
            pass


def main():
    """Main Streamlit application."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🏙️ Bangalore Local Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your friendly AI guide to Bengaluru, powered by local knowledge</div>', unsafe_allow_html=True)
    
    # Load context on first run
    if not st.session_state.context_loaded:
        with st.spinner("Loading Bangalore knowledge base..."):
            context = load_context()
            if not context:
                st.stop()
    
    # Initialize agent
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing your local guide..."):
            if not initialize_agent():
                st.stop()
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Query input
    user_query = st.text_input(
        "Ask like a local:",
        placeholder="What would you like to know about Bangalore?",
        help="Ask me about food, traffic, culture, places to visit, or local slang!"
    )
    
    # Process query button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ask_button = st.button("🗣️ Ask Your Local Guide", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process query when button is clicked or Enter is pressed
    if ask_button and user_query.strip():
        # Add to chat history
        st.session_state.chat_history.append((user_query, datetime.now()))
        
        # Process query
        with st.spinner("Thinking like a local..."):
            result = process_user_query(user_query)
        
        # Display response
        display_response(result)
    
    elif ask_button and not user_query.strip():
        st.warning("Please enter a question first!")
    
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
        
        # Display chat history
        display_chat_history()
        
        # Clear history button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("""
    **Bangalore Local Guide** • Powered by Kiro AI • Built with ❤️ for Bengaluru  
    *All recommendations based on local knowledge and experience*
    """)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()