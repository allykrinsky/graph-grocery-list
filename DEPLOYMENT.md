# Deployment Guide

This guide explains how to deploy your grocery app to Streamlit Cloud while keeping your Notion API credentials secure.

## Security Features

The app supports two ways to manage secrets:
- **Local development**: Uses `.env` file (already in .gitignore)
- **Streamlit Cloud**: Uses Streamlit's secrets management (secure and private)

## Local Development Setup

1. Create a `.env` file in the project root with your Notion credentials:
```
RECIPE_SOURCE=your-recipe-database-id
RECIPE_TOKEN=your-recipe-notion-token
INGREDIENT_SOURCE=your-ingredient-database-id
INGREDIENT_TOKEN=your-ingredient-notion-token
```

2. Run the app locally:
```bash
streamlit run app.py
```

## Deploying to Streamlit Cloud

### Step 1: Prepare Your Repository

1. Make sure all changes are committed to git
2. Push your code to GitHub (your secrets are protected by .gitignore)

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch (usually `main`)
5. Set the main file path to `app.py`

### Step 3: Configure Secrets in Streamlit Cloud

1. After creating the app, go to the app's settings (click the three dots menu)
2. Click on "Secrets" in the sidebar
3. Add your secrets in TOML format:

```toml
RECIPE_SOURCE = "your-recipe-database-id"
RECIPE_TOKEN = "your-recipe-notion-token"
INGREDIENT_SOURCE = "your-ingredient-database-id"
INGREDIENT_TOKEN = "your-ingredient-notion-token"
```

4. Click "Save"
5. Your app will automatically redeploy with the secrets

### Step 4: Access Your App

Once deployed, Streamlit Cloud will provide you with a URL like:
`https://your-username-grocery-app-randomid.streamlit.app`

## Privacy Settings

By default, Streamlit Cloud apps are public. To make your app private:

1. Go to your app settings on Streamlit Cloud
2. Navigate to "Sharing" settings
3. Change the app visibility to "Private"
4. Only people you explicitly share the link with can access your app

**Important**: Your Notion API tokens are NEVER exposed to users - they're securely stored on Streamlit's servers and only accessible to your app.

## Troubleshooting

### App shows "Connection Error"
- Check that your secrets are properly configured in Streamlit Cloud
- Verify your Notion API tokens are still valid
- Make sure the database IDs are correct

### Need to update secrets
1. Go to app settings → Secrets
2. Update the values
3. Save (app will auto-redeploy)

## Additional Notes

- The `.streamlit/secrets.toml` file is in .gitignore - never commit it!
- Use `.streamlit/secrets.toml.example` as a template for local secrets setup
- Your secrets are encrypted and only accessible by your deployed app
