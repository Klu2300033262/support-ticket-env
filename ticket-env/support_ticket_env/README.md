# AI Support Ticket Triage Environment (OpenEnv)

## 🚀 Environment Motivation
In the era of automated customer service, evaluating the reliability and "professionalism" of AI agents is paramount. The **Support Ticket Triage Environment** provides a deterministic, high-fidelity simulation for testing an AI's ability to process real-world customer grievances. It bridges the gap between raw text processing and structured business logic, ensuring agents can accurately classify, prioritize, and respond to urgent customer needs without human intervention.

## 💼 Real-World Use Case
Imagine a high-traffic SaaS platform receiving thousands of tickets daily. This environment replicates the core triage engine:
1. **Billing** issues are instantly flagged for refunds.
2. **Technical** crashes are prioritized for engineering.
3. **Account** lockouts are routed for security verification.
4. **Sentimental** analysis ensures frustrated customers receive immediate escalation.

## 🛠️ Environment Specifications

### Action Space (`SupportTicketAction`)
Agents submit a processed ticket with the following parameters:
- `message`: (Required) The original ticket content.
- `category`: (billing, technical, account, general)
- `priority`: (high, medium, low)
- `sentiment`: (negative, neutral, positive)
- `response`: A professional response generated for the customer.

### Observation Space (`SupportTicketObservation`)
The environment evaluates the action against ground-truth heuristics and returns:
- `category`: System-validated category.
- `priority`: System-validated priority.
- `sentiment`: System-validated sentiment.
- `response`: Reference professional response.
- `requires_escalation`: Boolean indicating if the ticket needs human touch.
- `escalation_reason`: Automated explanation for escalation.

## 🏆 Reward Design
The environment employs a **partial progress reward system** (clamped 0.0–1.0) to provide granular feedback during training:
- **+0.4**: Correct Category classification.
- **+0.3**: Correct Priority assignment.
- **+0.1**: Correct Sentiment detection.
- **+0.2**: Professional response tone (detected via keyword alignment).
- **-0.1**: Penalty for providing an incorrect category.

## 📋 Task Suite
The environment includes three built-in deterministic tasks (defined in `tasks.py`):
1. **Easy Task**: Accurate category classification for routine requests.
2. **Medium Task**: Correct classification and priority assignment for technical issues.
3. **Hard Task**: Managing high-severity billing complaints with correct sentiment, priority, and professional response tone.

## 🚦 Setup Instructions

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the environment server
uvicorn support_ticket_env.server.app:app --host 0.0.0.0 --port 8000
```

### 2. Docker Deployment
```bash
# Build the image
docker build -t support-ticket-env .

# Run the container
docker run -p 8000:8000 support-ticket-env
```

### 3. Running Inference
```bash
export OPENAI_API_KEY="your-key"
export API_BASE_URL="http://localhost:8000"
python inference.py
```

## 📊 Baseline Scores
| Agent Type | Average Reward | Description |
| :--- | :--- | :--- |
| **Random** | 0.08 | Uniformly random category/priority selection. |
| **Heuristic** | 0.65 | Regex-based keyword matching. |
| **GPT-4o** | 0.98+ | Modern LLM with zero-shot triage capabilities. |

---
*Built for the OpenEnv Hackathon 2026.*
