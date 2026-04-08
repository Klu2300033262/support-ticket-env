# HF Spaces Deployment Script for Support Ticket Environment

Write-Host "🚀 Deploying Support Ticket Environment to Hugging Face Spaces..." -ForegroundColor Green

# Clone your Space repository
Write-Host "📥 Cloning your Space..." -ForegroundColor Blue
git clone https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env
Set-Location support-ticket-env

# Copy files from your project
Write-Host "📁 Copying project files..." -ForegroundColor Blue
$sourcePath = $PSScriptRoot
Copy-Item "$sourcePath\Dockerfile" . -Force
Copy-Item "$sourcePath\server" . -Recurse -Force
Copy-Item "$sourcePath\models.py" . -Force
Copy-Item "$sourcePath\client.py" . -Force
Copy-Item "$sourcePath\inference.py" . -Force
Copy-Item "$sourcePath\tasks.py" . -Force
Copy-Item "$sourcePath\HF_README.md" README.md -Force

# Git configuration
Write-Host "🔧 Setting up git..." -ForegroundColor Blue
git config user.name "LasyaSrivalli"
git config user.email "lasya@example.com"

# Add and commit files
Write-Host "📦 Adding files to git..." -ForegroundColor Blue
git add .
git commit -m "Deploy OpenEnv Support Ticket Environment"

# Push to HF Spaces
Write-Host "🚀 Pushing to Hugging Face Spaces..." -ForegroundColor Blue
git push origin main

Write-Host "✅ Deployment initiated!" -ForegroundColor Green
Write-Host "📗 Your Space will be available at: https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env" -ForegroundColor Cyan
Write-Host "📖 API docs will be at: https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env/docs" -ForegroundColor Cyan
Write-Host "🧪 Test endpoints at: https://huggingface.co/spaces/LasyaSrivalli/support-ticket-env/health" -ForegroundColor Cyan

Set-Location ..
