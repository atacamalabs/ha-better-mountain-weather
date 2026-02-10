#!/bin/bash
# Script to push A Better Mountain Weather to GitHub

echo "🚀 Pushing to GitHub..."
echo ""

# Add remote
git remote add origin https://github.com/atacamalabs/ha-better-mountain-weather.git

# Push main branch
echo "📤 Pushing main branch..."
git push -u origin main

# Push tag
echo "🏷️  Pushing tag v0.1.0b1..."
git push origin v0.1.0b1

echo ""
echo "✅ Done! Your code is now on GitHub:"
echo "   https://github.com/atacamalabs/ha-better-mountain-weather"
echo ""
echo "Next step: Create the release on GitHub"
echo "   Go to: https://github.com/atacamalabs/ha-better-mountain-weather/releases/new"
