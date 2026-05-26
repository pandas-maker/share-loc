# Quick Start: Deploy to Render

## Local Development vs Production

The bot now supports **two modes**:

### Local Development (Polling Mode)
- Run without any special configuration
- Uses environment variables from `.env` file
- Bot polls Telegram for updates every 1-5 seconds
- **Use this when testing locally**

### Production (Render) - Webhook Mode
- Requires `WEBHOOK_URL` environment variable
- Better performance and lower latency
- **Use this when deploying to Render**

## Quick Deployment Steps

### 1. Local Development

```bash
# 1. Set your bot token in .env file
echo "BOT_TOKEN=your_token_here" > telegrambot/.env

# 2. Run the bot
cd telegrambot
python main.py
```

You should see:
```
✅ Bot started in POLLING mode (local development)
📝 Set WEBHOOK_URL to switch to webhook mode for production
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
   - `WEBHOOK_URL`: Your Render app URL (e.g., `https://telegrambot.onrender.com`)
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
- **Local Development**: Now supports polling mode for local testing


- `Procfile` - Render process configuration
- `.render.yaml` - Automated deployment config
- `DEPLOYMENT.md` - Complete deployment guide
- `CHANGELOG.md` - Detailed change history
- `src/webhook_handler.py` - Webhook endpoint handler

## Support

Check `DEPLOYMENT.md` for detailed troubleshooting and advanced configuration.
