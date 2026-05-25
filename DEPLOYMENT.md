# Deployment Guide for Render

This document provides step-by-step instructions for deploying your Telegram bot to Render.

## Prerequisites

1. A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
2. A Render account
3. Git installed on your machine

## Step 1: Configure Environment Variables

1. Create a `.env` file in the `telegrambot` directory:
   ```
   BOT_TOKEN=your_bot_token_here
   WEBHOOK_URL=https://your-app-name.onrender.com
   PORT=10000
   ```

2. **Important**: Never commit `.env` files to version control. The `.gitignore` file already excludes them.

## Step 2: Set Up on Render

### Method 1: Using Render Dashboard (Recommended)

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** and select **Web Service**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `telegrambot` (or your preferred name)
   - **Region**: Choose your preferred region
   - **Runtime**: Python 3.14
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Root Directory**: `/` (or `telegrambot` if files are in a subdirectory)
5. Add Environment Variables:
   - `BOT_TOKEN`: Your Telegram bot token
   - `PORT`: `10000`
   - `WEBHOOK_URL`: Your Render app URL (will be provided after deployment)
6. Click **Deploy Web Service**

### Method 2: Using .render.yaml (Automatic Deployment)

1. Push your code to GitHub
2. Connect your GitHub repository to Render
3. Render will automatically detect the `.render.yaml` file and configure the service
4. Add the required environment variables in the Render dashboard
5. Click **Deploy Web Service**

## Step 3: Configure Telegram Bot

After your service is deployed:

1. Go to your Render app URL in the browser
2. Copy your app URL (e.g., `https://telegrambot.onrender.com`)
3. Set the `WEBHOOK_URL` environment variable in Render to this URL + `/webhook`
4. If you're using the automatic webhook generation, Render will provide this automatically
5. If you need to manually set it, go to your bot in Telegram and run:
   ```
   /setwebhook https://your-app-name.onrender.com/webhook
   ```

## Troubleshooting

### Common Issues

1. **"BOT_TOKEN not set" error**
   - Ensure the `BOT_TOKEN` environment variable is set correctly in Render

2. **"WEBHOOK_URL not set" error**
   - Set the `WEBHOOK_URL` environment variable in Render

3. **Connection refused errors**
   - Wait a few minutes after deployment for the service to start
   - Check the Render logs for detailed error messages

4. **Port already in use**
   - The service should automatically use the PORT environment variable
   - Ensure your code is configured to read from `os.environ.get('PORT', 10000)`

### Checking Logs

1. Go to your Render service dashboard
2. Click on the service name
3. Scroll down to the "Logs" section
4. View the recent logs to diagnose issues

### Manual Testing

1. Use `curl` to test the webhook endpoint:
   ```bash
   curl -X POST https://your-app-name.onrender.com/webhook
   ```

2. Send a test message to your bot on Telegram

## Environment Variables Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `BOT_TOKEN` | Yes | Your Telegram bot token | - |
| `WEBHOOK_URL` | Yes | Render app URL (includes /webhook) | - |
| `PORT` | No | Port number for the web server | 10000 |

## Manual Deployment

If you need to deploy manually without Render:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export BOT_TOKEN="your_token"
   export WEBHOOK_URL="https://your-domain.com"
   export PORT="10000"
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Updating the Bot

After making changes to the code:

1. Commit and push your changes to GitHub
2. Render will automatically detect changes and start a new deployment
3. Monitor the deployment status in the Render dashboard
4. Wait for the deployment to complete (usually takes 2-3 minutes)

## Scaling

Render will automatically scale your bot based on demand. The service uses:
- **Web Service**: For webhook handling
- **Free tier**: 512MB RAM, 0.5 CPU
- **Pro tier**: Up to 16GB RAM, 16 CPU cores

## Security Best Practices

1. Never share your `BOT_TOKEN` publicly
2. Use Render's built-in SSL certificates for HTTPS
3. Rotate your bot token regularly
4. Monitor your Render dashboard for any security alerts
5. Keep your dependencies updated

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Python Telegram Bot Documentation](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## Support

If you encounter issues:
1. Check the logs in the Render dashboard
2. Review this deployment guide
3. Check the [Telegram Bot documentation](https://docs.python-telegram-bot.org/)
4. Open an issue in your repository