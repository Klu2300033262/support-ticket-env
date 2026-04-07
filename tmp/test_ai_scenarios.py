import asyncio
import os
import json
from support_ticket_env.server.ai_service import analyze_ticket_with_ai

async def test_ai_scenarios():
    print("Testing AI Service Scenarios...\n")
    
    scenarios = [
        {
            "name": "Standard Billing Issue",
            "message": "I have a problem with my billing. I was charged twice for this month."
        },
        {
            "name": "Urgent Technical Issue (Override)",
            "message": "URGENT! Production is down and my system is completely broken!"
        },
        {
            "name": "Neutral Account Query",
            "message": "Hello, I just wanted to ask how I can update my profile picture."
        }
    ]
    
    for scenario in scenarios:
        print(f"--- Scenario: {scenario['name']} ---")
        print(f"Input: {scenario['message']}")
        result = await analyze_ticket_with_ai(scenario['message'])
        print(f"Result: {json.dumps(result, indent=2)}\n")

if __name__ == "__main__":
    # Ensure .env is loaded (ai_service handles this)
    asyncio.run(test_ai_scenarios())
