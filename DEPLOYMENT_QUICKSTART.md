# Quick Start: Deploy to Render

## Quick Deployment Steps

### 1. Prepare Your Code

```bash
cd telegrambot
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `telegrambot`
   - **Region**: Choose any
   - **Runtime**: Python 3.14
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. Add Environment Variables:
   - `BOT_TOKEN`: Your bot token from BotFather
   - `PORT`: `10000`
6. Click **Deploy Web Service**

### 3. Set Webhook

After deployment (wait 2-3 minutes):

1. Copy your Render URL: `https://telegrambot.onrender.com`
2. Set `WEBHOOK_URL` in Render environment variables to: `https://telegrambot.onrender.com`
3. Or manually in Telegram:
   ```
   /setwebhook https://telegrambot.onrender.com/webhook
   ```

### 4. Test Your Bot

Send `/start` to your bot on Telegram and test the features!

## What Was Fixed

- **AttributeError**: Updated `python-telegram-bot` from 20.7 to 21.9
- **Webhook Support**: Added proper webhook server configuration
- **Environment Variables**: Fixed config.py to handle Render variables
- **Async Setup**: Converted main function to async for proper webhook handling

## Files Created

- `Procfile` - Render process configuration
- `.render.yaml` - Automated deployment config
- `DEPLOYMENT.md` - Complete deployment guide
- `CHANGELOG.md` - Detailed change history
- `src/webhook_handler.py` - Webhook endpoint handler

## Support

Check `DEPLOYMENT.md` for detailed troubleshooting and advanced configuration.