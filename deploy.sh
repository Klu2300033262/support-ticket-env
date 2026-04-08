#!/bin/bash
# HF Spaces Deployment Script

echo "🚀 Deploying Support Ticket Environment to Hugging Face Spaces..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: OpenEnv Support Ticket Environment"
fi

# Add HF remote (replace with your username)
echo "🔗 Adding Hugging Face remote..."
HF_USERNAME="your-username"  # CHANGE THIS
SPACE_NAME="support-ticket-env"
HF_REPO="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

git remote add hf $HF_REPO
git push hf main

echo "✅ Deployment initiated! Check your Hugging Face Space for build status."
echo "📖 API docs will be available at: https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME/docs"
echo "🧪 Test endpoints at: https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME/health"
