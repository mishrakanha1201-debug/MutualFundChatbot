# GitHub CLI Installation & Authentication Guide

## Option 1: Install via Homebrew (Recommended)

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Follow the prompts and enter your password when asked.

2. **Install GitHub CLI**:
   ```bash
   brew install gh
   ```

3. **Authenticate with GitHub**:
   ```bash
   gh auth login
   ```
   - Select: GitHub.com
   - Select: HTTPS
   - Authenticate Git with your GitHub credentials? Yes
   - How would you like to authenticate? Login with a web browser
   - Press Enter to open github.com in your browser
   - Complete authentication in browser
   - Return to terminal

4. **Push your code**:
   ```bash
   cd "/Users/kanha.m/Mutual Fund Chatbot"
   git push -u origin main
   ```

## Option 2: Use HTTPS with Personal Access Token (No CLI needed)

1. **Create a Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: "MutualFundChatbot"
   - Expiration: 90 days (or your preference)
   - Select scope: ✅ **repo** (Full control of private repositories)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Push using the token**:
   ```bash
   cd "/Users/kanha.m/Mutual Fund Chatbot"
   git push -u origin main
   ```
   - Username: `mishrakanha1201-debug`
   - Password: `[paste your token here]`

## Option 3: Manual GitHub CLI Download

1. Download from: https://github.com/cli/cli/releases/latest
2. Download: `gh_*_macOS_amd64.tar.gz`
3. Extract and move to `/usr/local/bin/`:
   ```bash
   tar -xzf gh_*_macOS_amd64.tar.gz
   sudo mv gh_*_macOS_amd64/bin/gh /usr/local/bin/gh
   ```
4. Then follow authentication steps from Option 1
