from typing import Any, List
from support_ticket_env.server.graders import BillingGrader, UrgencyGrader, EscalationGrader

# Task Descriptions for OpenEnv Hackathon Submission

tasks = [
    {
        "id": "task_1_easy",
        "name": "Billing Classification",
        "description": "The agent must correctly identify billing/refund related queries.",
        "message": "I was charged twice for my subscription. I need a refund immediately.",
        "grader": BillingGrader()
    },
    {
        "id": "task_2_medium",
        "name": "Urgent Sentiment Detection",
        "description": "Detect urgent/angry sentiment and assign high priority.",
        "message": "ASAP! The app is totally broken and I'm losing money! HELP!",
        "grader": UrgencyGrader()
    },
    {
        "id": "task_3_hard",
        "name": "Escalation Logic",
        "description": "Determine if a ticket requires human escalation based on anger or billing requests.",
        "message": "I hate this software, it never works. I want my money back now!",
        "grader": EscalationGrader()
    }
]

def get_all_tasks() -> List[dict]:
    return tasks
