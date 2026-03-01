# 🚀 Deploy to Streamlit Cloud - Step by Step

## ✅ What You Need

1. GitHub account (free)
2. Streamlit Cloud account (free)
3. These files (already created):
   - `dashboard_cloud.py` ✓
   - `graph_data_export.json` ✓
   - `requirements.txt` ✓

## 📋 Deployment Steps

### Step 1: Create GitHub Repository

```bash
# Navigate to your project folder
cd "c:\Users\patel\SEM 2\transformer"

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Global News Intelligence Dashboard"

# Create repository on GitHub:
# Go to: https://github.com/new
# Repository name: global-news-intelligence
# Make it PUBLIC (required for Streamlit Cloud free tier)
# Don't add README/gitignore (we already have them)
# Click "Create repository"

# Link your local repo to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/global-news-intelligence.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to:** https://streamlit.io/cloud
2. **Sign in** with GitHub
3. **Click:** "New app"
4. **Fill in:**
   - Repository: `YOUR_USERNAME/global-news-intelligence`
   - Branch: `main`
   - Main file path: `dashboard_cloud.py`
5. **Click:** "Deploy!"

### Step 3: Share With Friends

After deployment (takes 2-3 minutes), you'll get a URL like:
```
https://your-username-global-news-intelligence-dashboard-cloud-abc123.streamlit.app
```

**Share this URL with anyone!** They can access it from anywhere in the world 🌍

## 🔄 Updating Your Dashboard

When you collect more data and want to update the live dashboard:

```bash
# Export fresh data
python export_for_cloud.py

# Commit and push
git add graph_data_export.json
git commit -m "Update data"
git push

# Streamlit Cloud auto-redeploys in ~1 minute!
```

## ⚠️ Important Notes

- **Free tier limits**: 1GB resources, public apps only
- **Auto-updates**: Every git push triggers redeployment
- **Data refresh**: Run `export_for_cloud.py` whenever you want latest data
- **Always online**: No need to keep your computer running!

## 🎉 You're Done!

Your dashboard is now accessible 24/7 from anywhere in the world!
