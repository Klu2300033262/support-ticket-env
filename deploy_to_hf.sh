#!/bin/bash
# HF Spaces Deployment Script for LasyaSrivalli/support-ticket-env

echo "🚀 Deploying Support Ticket Environment to Hugging Face Spaces..."

# Clone your Space repository
echo "📥 Cloning your Space..."
git clone https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env
cd support-ticket-env

# Copy files from your project
echo "📁 Copying project files..."
cp ../Dockerfile .
cp -r ../server/ .
cp ../models.py .
cp ../client.py .
cp ../inference.py .
cp ../tasks.py .
cp ../HF_README.md README.md

# Git configuration
echo "🔧 Setting up git..."
git config user.name "LasyaSrivalli"
git config user.email "your-email@example.com"  # Update this

# Add and commit files
echo "📦 Adding files to git..."
git add .
git commit -m "Deploy OpenEnv Support Ticket Environment"

# Push to HF Spaces
echo "🚀 Pushing to Hugging Face Spaces..."
git push origin main

echo "✅ Deployment initiated!"
echo "📗 Your Space will be available at: https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env"
echo "📖 API docs will be at: https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env/docs"
echo "🧪 Test endpoints at: https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env/health"

cd ..
