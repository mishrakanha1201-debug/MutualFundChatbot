#!/bin/bash

echo "=========================================="
echo "Pushing to GitHub"
echo "=========================================="
echo ""

cd "/Users/kanha.m/Mutual Fund Chatbot"

# Configure git credential helper
git config --global credential.helper osxkeychain

echo "Attempting to push to GitHub..."
echo "You will be prompted for credentials:"
echo "  Username: mishrakanha1201-debug"
echo "  Password: [Your GitHub Personal Access Token]"
echo ""
echo "If you don't have a token, create one at:"
echo "https://github.com/settings/tokens"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
else
    echo ""
    echo "❌ Push failed. Please check your credentials."
    echo ""
    echo "To create a Personal Access Token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token' → 'Generate new token (classic)'"
    echo "3. Name: MutualFundChatbot"
    echo "4. Select scope: ✅ repo"
    echo "5. Generate and copy the token"
    echo "6. Run this script again and use the token as password"
fi
