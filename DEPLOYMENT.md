# Deployment Guide

## Streamlit Community Cloud (Recommended)

### Step 1: Prepare Repository
Your repository is now ready with all required files:
- ✅ `app.py` (main application)
- ✅ `requirements.txt` (dependencies)
- ✅ `.streamlit/config.toml` (configuration)
- ✅ All Python modules in root directory

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy!"

### Step 3: Verify Deployment
- App should be available at: `https://your-username-repo-name.streamlit.app`
- Check logs for any import errors
- Test all functionality

## Alternative: Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Git repository

### Steps
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## Troubleshooting Common Issues

### 404 Error on GitHub
- **Cause**: GitHub Pages doesn't support Python/Streamlit apps
- **Solution**: Use Streamlit Community Cloud instead

### Import Errors
- **Cause**: Missing dependencies or incorrect file paths
- **Solution**: Check `requirements.txt` and ensure all files are in root

### Configuration Issues
- **Cause**: Invalid TOML configuration
- **Solution**: Validate `.streamlit/config.toml` syntax

### Port Issues
- **Cause**: Hardcoded port numbers
- **Solution**: Use environment variables in production

## Environment Variables (Optional)

For production deployment, you can set:
```bash
# Streamlit specific
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true

# Application specific
KIRO_CONFIG_PATH=.kiro/config.yaml
```

## File Structure Verification

Your deployment-ready structure:
```
├── app.py                    # ✅ Main application
├── requirements.txt          # ✅ Dependencies
├── .streamlit/config.toml   # ✅ Streamlit config
├── .kiro/config.yaml        # ✅ AI agent config
├── product.md               # ✅ Knowledge base
├── *.py                     # ✅ All modules
├── Procfile                 # ✅ Heroku config
└── README.md                # ✅ Documentation
```

## Success Checklist

- [ ] Repository is public (for Streamlit Community Cloud)
- [ ] All files are committed and pushed to GitHub
- [ ] `app.py` runs locally without errors
- [ ] Dependencies are correctly listed in `requirements.txt`
- [ ] No hardcoded file paths or environment-specific code

## Support

If deployment fails:
1. Check the deployment logs
2. Verify all files are in the repository
3. Test locally first: `streamlit run app.py`
4. Check Streamlit Community Cloud documentation