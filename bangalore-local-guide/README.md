# Bangalore Local Guide

🏙️ **Your friendly AI guide to Bengaluru, powered by local knowledge**

A Streamlit web application that demonstrates context-driven AI using Kiro agents. This application acts as a knowledgeable Bangalore local, providing authentic advice about the city based on comprehensive local knowledge stored in a single context file.

## Problem Statement

Visitors to Bangalore often struggle with:
- Finding authentic local food recommendations beyond tourist spots
- Understanding local slang and cultural nuances
- Navigating the city's notorious traffic patterns
- Getting practical, time-sensitive advice (like what to eat for breakfast vs dinner)
- Accessing insider knowledge that only locals would know

Traditional travel apps provide generic information, but lack the contextual awareness and local authenticity that makes advice truly valuable.

## Solution Approach

The Bangalore Local Guide solves this by:

1. **Context-Driven Intelligence**: All knowledge comes from a single, comprehensive context file (`product.md`) that contains authentic local information
2. **AI Agent Integration**: Uses Kiro AI agents configured with a local persona to process queries intelligently
3. **Time-Aware Responses**: Provides recommendations based on time of day, traffic conditions, and local patterns
4. **Cultural Awareness**: Explains local slang and cultural norms to help visitors understand the city better
5. **No Hallucination**: Responses are strictly based on the provided context, ensuring accuracy and authenticity

## How Kiro Integration Accelerates Development

### Traditional Approach vs. Kiro-Powered Development

**Without Kiro:**
- Hardcode city knowledge in application logic
- Build complex query parsing and response generation
- Manually handle different query types and contexts
- Implement natural language processing from scratch
- Maintain knowledge scattered across multiple files

**With Kiro:**
- Store all knowledge in a single `product.md` file
- Configure agent behavior through simple YAML configuration
- Let Kiro handle natural language understanding and response generation
- Focus on application logic rather than AI implementation
- Update knowledge by simply editing the context file

### How `product.md` Teaches Kiro

The `product.md` file serves as the "brain" of our local guide:

```markdown
# Bangalore Local Guide Knowledge Base

## City Overview
Bangalore (officially Bengaluru) is the Silicon Valley of India...

## Local Slang Dictionary
- "Scene illa maga" - Nothing happening, dude
- "Guru" - Friend/buddy (used commonly)
- "Macha" - Friend (Tamil influence)

## Traffic Patterns
- Peak hours: 8-10 AM, 6-9 PM
- Silk Board: Always congested, especially evenings
- Electronic City: Heavy traffic during IT hours

## Food Recommendations
### Breakfast (6 AM - 11 AM)
- Malleshwaram: CTR for dosas
- Basavanagudi: Vidyarthi Bhavan for masala dosa
```

When a user asks "What does 'scene illa maga' mean?", Kiro:
1. Searches the context for relevant information
2. Finds the slang definition in the Local Slang Dictionary section
3. Responds with the explanation in a friendly, local tone
4. Maintains consistency with the configured persona

This approach means:
- **Rapid Knowledge Updates**: Edit `product.md` to add new restaurants, update traffic patterns, or include new slang
- **Consistent Responses**: All answers come from the same authoritative source
- **Easy Maintenance**: No code changes needed for knowledge updates
- **Scalable**: Can easily extend to other cities by creating new context files

## Features

- 🍽️ **Food Recommendations**: Time-aware suggestions for breakfast, lunch, dinner, and street food
- 🚗 **Traffic Advice**: Real-time insights about congestion patterns and alternative routes
- 🗣️ **Slang Translation**: Explanations of local Kannada, Tamil, and English slang
- 📍 **Local Insights**: Cultural norms, etiquette, and insider tips
- 🎯 **Itinerary Planning**: One-day plans crafted like a local would suggest
- 💬 **Natural Conversation**: Chat interface that feels like talking to a friend

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd bangalore-local-guide
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

That's it! Your Bangalore Local Guide is ready to help.

## Usage Examples

### Ask About Food
```
"Where should I eat breakfast in Malleshwaram?"
"Best street food areas in Bangalore?"
"What's good for dinner near Koramangala?"
```

### Get Traffic Advice
```
"Is Silk Board bad at 6 PM?"
"How's the traffic to Electronic City in the morning?"
"Should I take metro or cab to MG Road?"
```

### Learn Local Slang
```
"What does 'scene illa maga' mean?"
"Explain Bangalore slang to me"
"What do locals call each other?"
```

### Plan Your Day
```
"I have one day in Bangalore. Plan it like a local."
"What should I do on a weekend in Bangalore?"
"Cultural places to visit with local insights?"
```

## Project Structure

```
bangalore-local-guide/
├── .kiro/                          # Kiro configuration
│   └── config.yaml                 # Agent configuration and persona
├── screenshots/                    # Documentation screenshots
├── app.py                         # Main Streamlit application
├── product.md                     # Complete Bangalore knowledge base
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── context_manager.py             # Context loading and management
├── agent_manager.py               # Kiro agent initialization
├── query_processor.py             # Query processing pipeline
├── integration_manager.py         # System integration
├── error_handler.py               # Error handling utilities
├── food_recommender.py            # Food recommendation logic
├── traffic_advisor.py             # Traffic advice functionality
└── test_*.py                      # Property-based and unit tests
```

## Configuration

### Agent Configuration (`.kiro/config.yaml`)

```yaml
name: bangalore-local-guide
description: Friendly Bangalore local guide
persona:
  identity: Bangalore local resident
  tone: helpful, practical, culturally aware
  style: concise but informative
behavior_rules:
  - explain_slang_when_used
  - recommend_food_by_time
  - warn_about_traffic_realistically
  - suggest_metro_during_peaks
  - no_hallucination_policy
context_sources:
  - product.md
```

### Knowledge Base (`product.md`)

The knowledge base contains:
- **City Overview**: Basic information about Bangalore
- **Languages**: Kannada, English, Tamil usage patterns
- **Local Slang Dictionary**: Common terms with explanations
- **Traffic Patterns**: Peak hours, problem areas, alternatives
- **Food Spots**: Area-wise recommendations by meal time
- **Cultural Norms**: Etiquette and local customs
- **Practical Tips**: Local insights and advice

## How It Works

1. **Context Loading**: Application loads `product.md` as the knowledge base
2. **Agent Initialization**: Kiro agent is configured with local persona and behavior rules
3. **Query Processing**: User questions are processed with full context awareness
4. **Intelligent Response**: Agent generates responses using only the provided knowledge
5. **Local Authenticity**: All advice comes from the curated local knowledge base

## Development and Testing

### Running Tests

The project includes comprehensive testing:

```bash
# Run all tests
pytest

# Run property-based tests
pytest test_*_properties.py

# Run integration tests
pytest test_integration*.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Types

- **Property-Based Tests**: Validate universal correctness properties using Hypothesis
- **Unit Tests**: Test specific functionality and edge cases
- **Integration Tests**: End-to-end testing of complete user journeys

### Adding New Knowledge

To add new information to the guide:

1. Edit `product.md` with new content
2. Follow the existing format and structure
3. Test with sample queries
4. No code changes required!

## Architecture Highlights

### Context-Driven Design
- Single source of truth for all local knowledge
- No hardcoded information in application code
- Easy knowledge updates without deployment

### Modular Components
- Separate managers for context, agents, queries, and integration
- Clean separation of concerns
- Comprehensive error handling

### User Experience Focus
- Intuitive chat interface
- Loading indicators and error messages
- System health monitoring
- Chat history and example queries

## Troubleshooting

### Common Issues

**"Context loading failed"**
- Ensure `product.md` exists in the project directory
- Check file permissions and encoding (should be UTF-8)

**"Agent initialization failed"**
- Verify `.kiro/config.yaml` exists and is valid YAML
- Check that all required dependencies are installed

**"Application won't start"**
- Run `pip install -r requirements.txt` to ensure dependencies
- Try `streamlit run app.py --server.port 8502` if port 8501 is busy

### Getting Help

1. Check the system health indicator in the sidebar
2. View error details in the expandable sections
3. Use the "Refresh System" button to reset the application
4. Check the console output for detailed error messages

## Contributing

This project demonstrates Kiro's capabilities for context-driven AI applications. To contribute:

1. Fork the repository
2. Add new knowledge to `product.md`
3. Test your changes with relevant queries
4. Submit a pull request

## License

This project is created for demonstration purposes to showcase Kiro's context-driven AI capabilities.

---

**Built with ❤️ for Bengaluru** • Powered by [Kiro AI](https://kiro.ai) • Made with [Streamlit](https://streamlit.io)

*Experience the difference when AI truly understands local context*