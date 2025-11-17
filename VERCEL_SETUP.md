# Vercel Deployment Setup Guide

## Setting up Gemini API Key in Vercel

The chatbot requires a Gemini API key to function. Follow these steps to configure it in Vercel:

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or use an existing key
4. Copy the API key (it will look like: `AIzaSy...`)

### Step 2: Add Environment Variable in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Click **Add New**
4. Enter:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: Your Gemini API key (paste the key you copied)
   - **Environment**: Select all environments (Production, Preview, Development)
5. Click **Save**

### Step 3: Redeploy

After adding the environment variable:

1. Go to **Deployments** tab in Vercel
2. Click the three dots (⋯) on the latest deployment
3. Select **Redeploy**
4. Or push a new commit to trigger automatic redeployment

### Step 4: Verify

After redeployment, test the chatbot. If you see an error message about the API key, check:

- The environment variable name is exactly `GEMINI_API_KEY` (case-sensitive)
- The API key is valid and not expired
- The deployment has completed successfully

### Troubleshooting

**Error: "Gemini API key is missing or invalid"**

- Verify the environment variable is set in Vercel
- Check that the variable name is exactly `GEMINI_API_KEY`
- Ensure you've redeployed after adding the variable
- Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)

**Error: "The system is still initializing"**

- This usually means the API key is missing
- Check Vercel deployment logs for more details
- Ensure the environment variable is set for all environments

### Additional Notes

- Environment variables are encrypted and secure in Vercel
- You can set different API keys for different environments if needed
- Changes to environment variables require a redeploy to take effect

