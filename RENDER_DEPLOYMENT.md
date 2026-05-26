# Render Deployment Guide

## Issue Fixed: Button Clicks Not Working

The issue was that your webhook configuration was missing:
1. A **secret token** - Required to authenticate webhook callbacks
2. **`drop_pending_updates=False`** - Required to preserve incoming callback queries

## Changes Made

### 1. Updated `main.py`
- Added `secret_token` parameter to webhook configuration
- Changed `drop_pending_updates=True` to `drop_pending_updates=False`
- Added automatic token generation if not provided (for development)

### 2. Updated `.env`
- Added `WEBHOOK_SECRET_TOKEN` placeholder

## How to Deploy to Render

### Step 1: Generate a Secure Secret Token
Create a random secure token for production:

```bash
# On your local machine
python -c "import secrets; print(secrets.token_hex(16))"
```

Or use any random string generator. For example:
- `a1b2c3d4e5f67890abcdef1234567890`

### Step 2: Update Render Environment Variables

1. Go to your Render dashboard: https://dashboard.render.com
2. Select your service
3. Navigate to **Environment** section
4. Add the following environment variables:

| Variable Name | Value | Required |
|---------------|-------|----------|
| `WEBHOOK_SECRET_TOKEN` | [Your secure token from Step 1] | ✅ Required |
| `WEBHOOK_URL` | [Your Render URL] | ✅ Required |
| `PORT` | 10000 | ✅ Required |

**Important:** 
- If you're using a custom domain, use that URL
- The token must be at least 32 characters for production security

### Step 3: Commit and Push Changes

```bash
cd telegrambot
git add .
git commit -m "Fix: Add secret token to webhook configuration"
git push origin main
```

### Step 4: Redeploy on Render

1. Go to your Render service
2. Click **Rebuild** → **Manual**
3. Wait for deployment to complete (usually 1-2 minutes)
4. Check the logs to verify the bot started successfully

### Step 5: Verify It Works

After deployment, test the bot:
1. Click your bot link
2. Try clicking buttons
3. They should now work correctly

## Local Testing

When running locally with the current `.env` file, the bot will automatically generate a random secret token and log it in the console. However, for production (Render), you MUST provide a token via environment variables.

## Troubleshooting

### Buttons still not working?
1. Check Render logs for the secret token warning
2. Ensure `WEBHOOK_SECRET_TOKEN` is set in Render environment variables
3. Verify the webhook URL is correct in Render settings
4. Check that `drop_pending_updates=False` is being used

### Bot shows "400 Bad Request" errors?
This means the secret token doesn't match. Make sure:
- The token in Render environment variables matches exactly
- No extra spaces in the token value
- Restart the bot after changing environment variables

## Security Best Practices

1. **Never commit your real secret token** - It's in .gitignore
2. **Use a unique token** - Generate a new one for each environment
3. **Rotate tokens periodically** - Change your secret token every 3-6 months
4. **Use environment variables** - Never hardcode tokens in code

## Example Render Environment Variables

```
BOT_TOKEN = 8990367974:AAFaljXnls6NkT19T1kYpk1J-J3DJfxPtlQ
WEBHOOK_URL = https://your-app-name.onrender.com
PORT = 10000
WEBHOOK_SECRET_TOKEN = a1b2c3d4e5f67890abcdef1234567890