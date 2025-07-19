# 🚀 Heroku Deployment Guide

## Prerequisites

### Option 1: Install Heroku CLI via Homebrew (Recommended)
```bash
# First install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Heroku CLI
brew install heroku/brew/heroku
```

### Option 2: Install Heroku CLI directly
```bash
# Download and install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh
```

### Option 3: Download from Heroku website
Visit: https://devcenter.heroku.com/articles/heroku-cli
Download the installer for macOS and run it.

## Deployment Steps

1. **Login to Heroku:**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app:**
   ```bash
   heroku create your-unique-trading-bot-name
   ```
   Replace `your-unique-trading-bot-name` with a unique name (e.g., `my-awesome-trading-bot-2024`)

3. **Deploy to Heroku:**
   ```bash
   git push heroku main
   ```

4. **Open your deployed app:**
   ```bash
   heroku open
   ```

## Alternative: Deploy via Heroku Dashboard

If you prefer not to use the CLI:

1. **Create a GitHub repository:**
   ```bash
   # Create a new repo on GitHub and push your code
   git remote add origin https://github.com/yourusername/trading-bot.git
   git push -u origin main
   ```

2. **Deploy via Heroku Dashboard:**
   - Go to https://dashboard.heroku.com/
   - Click "New" → "Create new app"
   - Choose a unique app name
   - Select your GitHub repository
   - Click "Deploy Branch"

## Troubleshooting

### If you get a "slug size too large" error:
```bash
# Add this to your .gitignore
*.pyc
__pycache__/
```

### If the app crashes on Heroku:
```bash
# Check the logs
heroku logs --tail
```

### If you need to restart the app:
```bash
heroku restart
```

## Your App URL

Once deployed, your app will be available at:
`https://your-app-name.herokuapp.com`

## Environment Variables

The app is configured to work out of the box, but you can add environment variables in the Heroku dashboard if needed.

## Support

If you encounter any issues:
1. Check the Heroku logs: `heroku logs --tail`
2. Ensure all files are committed: `git status`
3. Verify the Procfile is correct
4. Make sure requirements.txt is up to date

---

🎉 **Your trading bot will be live on the internet!** 🎉 