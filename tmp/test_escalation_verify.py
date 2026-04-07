import asyncio
from support_ticket_env.server.ai_service import analyze_ticket_with_ai
import json

async def test_escalation():
    print("Testing Escalation Logic Scenarios...\n")
    
    # We'll use messages that we expect the AI (or fallback) to mark as High or Negative
    # Since we have a fallback if no key, we might need to mock the AI output if we want to test those specific rules
    # BUT, the rules are deterministic based on the 'analysis' dict values.
    
    scenarios = [
        {
            "name": "High Priority Trigger",
            "message": "This is a very important issue, please help high priority.", 
            # Note: The AI might mark this as high.
        },
        {
            "name": "Negative Sentiment Trigger",
            "message": "I am extremely angry and disappointed with your service. This is terrible.",
            # Note: The AI might mark this as negative.
        },
        {
            "name": "Critical Keyword Trigger (Existing)",
            "message": "URGENT! Production is down!",
        }
    ]
    
    for scenario in scenarios:
        print(f"--- Scenario: {scenario['name']} ---")
        result = await analyze_ticket_with_ai(scenario['message'])
        print(f"Priority: {result['priority']} | Sentiment: {result['sentiment']} | Escalated: {result['requires_escalation']}")
        print(f"Reason: {result['escalation_reason']}\n")

if __name__ == "__main__":
    asyncio.run(test_escalation())
