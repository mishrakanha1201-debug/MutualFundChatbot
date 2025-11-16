#!/bin/bash

echo "=========================================="
echo "GitHub CLI Installation & Push Script"
echo "=========================================="
echo ""

# Step 1: Install Homebrew
echo "Step 1: Installing Homebrew..."
if command -v brew &> /dev/null; then
    echo "✅ Homebrew is already installed!"
else
    echo "Installing Homebrew (this will ask for your password)..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH (for Apple Silicon Macs)
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f /usr/local/bin/brew ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

echo ""
echo "Step 2: Installing GitHub CLI..."
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI is already installed!"
else
    brew install gh
fi

echo ""
echo "Step 3: Authenticating with GitHub..."
if gh auth status &>/dev/null; then
    echo "✅ Already authenticated!"
else
    echo "Starting authentication (this will open your browser)..."
    gh auth login --web
fi

echo ""
echo "Step 4: Pushing to GitHub..."
cd "/Users/kanha.m/Mutual Fund Chatbot"
git push -u origin main

echo ""
echo "=========================================="
echo "Done! Check the output above for any errors."
echo "=========================================="
