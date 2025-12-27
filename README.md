# Bangalore Local Guide

A comprehensive local guide for Bangalore with AI-powered recommendations for food, traffic, and local insights.

## Features

- 🍽️ **Food Recommendations**: Discover authentic local cuisine and popular restaurants
- 🚗 **Traffic Advice**: Real-time traffic insights and route suggestions
- 🏛️ **Local Insights**: Cultural spots, events, and local knowledge
- 🤖 **AI-Powered**: Intelligent responses using advanced language models

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Deployment

This app is ready for deployment on:
- **Streamlit Community Cloud**: Connect your GitHub repo at [share.streamlit.io](https://share.streamlit.io)
- **Heroku**: Uses the included Procfile for automatic deployment
- **Other platforms**: Standard Streamlit app structure

## Project Structure

```
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── product.md            # Bangalore knowledge base
├── .streamlit/           # Streamlit configuration
├── .kiro/               # AI agent configuration
└── *.py                 # Core modules (context, agents, etc.)
```

## Live Demo

🚀 **Deploy Instructions**: See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment guide

**Streamlit Community Cloud**: 
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect this GitHub repository
3. Set main file: `app.py`
4. Deploy!

Your app will be available at: `https://[username]-[repo-name].streamlit.app`

## Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Kiro AI agents
- **Testing**: Pytest with Hypothesis
- **Deployment**: Streamlit Community Cloud / Heroku ready

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details