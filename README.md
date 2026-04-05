---
title: Support Ticket Environment
emoji: 🎫
colorFrom: blue
colorTo: purple
sdk: docker
dockerfile: Dockerfile
app_port: 7860
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

## 🌐 **Live Demo**

**https://lasyasrivalli-ticket-env.hf.space**

## 🚀 **Hugging Face Space**

**https://huggingface.co/spaces/Lasyasrivalli/ticket-env**

## API Endpoints

- `POST /reset` - Initialize new episode
- `POST /step` - Process agent action
- `GET /state` - Get current environment state
- `GET /docs` - Interactive API documentation

## Usage

The environment follows the OpenEnv specification with typed models for Action, Observation, and State.

Visit `/docs` for the interactive API documentation.

## Environment Variables

Set these in your Space settings:
- `API_BASE_URL=http://localhost:8000`
- `MODEL_NAME=gpt-4o`
- `HF_TOKEN=your_hf_token`
- `OPENAI_API_KEY=your_openai_api_key` (optional for testing)
