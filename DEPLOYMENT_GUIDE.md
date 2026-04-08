# Hugging Face Spaces Deployment Guide

## 1. Create a New Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the details:
   - **Space name**: `support-ticket-env` (or your choice)
   - **Owner**: Your username
   - **License**: MIT
   - **Space SDK**: Docker
   - **Hardware**: CPU basic (free tier)
   - **Make it public**: ✅ Check this box
   - **Tags**: `openenv`, `support-ticket`, `customer-service`

### 2. Configure Space Settings

In your Space settings, add these environment variables:

#### Required Environment Variables:
```
API_BASE_URL=http://localhost:8000
MODEL_NAME=gpt-4o
HF_TOKEN=your_hf_token_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional for testing
```

### 3. Upload Your Files

Upload these files to your Space repository:

#### Core Files:
- `Dockerfile` (already created)
- `support_ticket_env/` (entire directory)
- `inference.py` (already created)
- `tasks.py` (already created)
- `README.md` (already created)

#### HF Space Configuration:
Create a new file called `README.md` in the root with HF metadata:

```yaml
---
title: Support Ticket Environment
emoji: 🎫
colorFrom: blue
colorTo: purple
sdk: docker
dockerfile: Dockerfile
app_port: 8000
tags:
- openenv
- support-ticket
- customer-service
- ai-agents
license: mit
---

# Support Ticket Environment

An OpenEnv environment for AI agent training on customer support ticket triage tasks.

## Environment Description

This environment simulates a real-world customer support ticket triage system where AI agents must:

1. **Classify** incoming tickets by category (billing, technical, account, general)
2. **Prioritize** tickets based on urgency (high, medium, low)
3. **Analyze** customer sentiment (negative, neutral, positive)
4. **Generate** professional responses
5. **Determine** escalation requirements

## Tasks

- **Easy**: Billing Classification - Correctly identify billing-related issues
- **Medium**: Urgent Sentiment Detection - Detect urgent/angry sentiment and assign high priority  
- **Hard**: Escalation Logic - Determine when tickets require human escalation

## API Endpoints

- `POST /reset` - Initialize new episode
- `POST /step` - Process agent action
- `GET /state` - Get current environment state
- `GET /docs` - Interactive API documentation

## Usage

The environment follows the OpenEnv specification with typed models for Action, Observation, and State.

Visit `/docs` for the interactive API documentation.
```

### 4. Deploy Process

Once files are uploaded:

1. **Build Process**: HF Spaces will automatically build your Docker image
2. **Deployment**: The app will start on port 8000
3. **Access**: Your Space will be available at `https://huggingface.co/spaces/your-username/support-ticket-env`

### 5. Verify Deployment

Check these endpoints once deployed:

```bash
# Health check
curl https://your-username.hf.space/support-ticket-env/health

# OpenEnv reset
curl -X POST https://your-username.hf.space/support-ticket-env/reset

# API docs
# Visit: https://your-username.hf.space/support-ticket-env/docs
```

### 6. Test with OpenEnv Validator

```bash
# Validate the deployed environment
openenv validate https://your-username.hf.space/support-ticket-env
```

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Ensure proper file paths

2. **Runtime Errors**:
   - Check environment variables
   - Verify port 8000 is exposed
   - Check logs in HF Space interface

3. **OpenEnv Validation Failures**:
   - Ensure `/reset`, `/step`, `/state` endpoints exist
   - Verify proper JSON response formats
   - Check typed models are correctly implemented

### Debug Commands:

```bash
# Check Space logs
# In HF Space interface, go to "Logs" tab

# Test locally before deploying
docker build -t support-ticket-env .
docker run -p 8000:8000 support-ticket-env

# Validate OpenEnv spec locally
cd support_ticket_env
openenv validate
```

## Submission Ready

Once deployed successfully:
1. Copy your Space URL
2. Test all endpoints work
3. Run OpenEnv validation
4. Submit Space URL to hackathon

## Expected URL Format
```
https://huggingface.co/spaces/your-username/support-ticket-env
```

## API Documentation
Once deployed, interactive docs will be at:
```
https://huggingface.co/spaces/your-username/support-ticket-env/docs
```
