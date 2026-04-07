import asyncio
import os
from support_ticket_env.server.ai_service import analyze_ticket_with_ai

async def test_ai():
    print("Testing AI Service...")
    message = "I have a problem with my billing. I was charged twice for this month."
    
    print(f"Input: {message}")
    result = await analyze_ticket_with_ai(message)
    
    print("\nResult:")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    # Check if API key is set
    key = os.getenv("OPENAI_API_KEY")
    if not key or "dummy" in key:
        print("WARNING: OPENAI_API_KEY is not set or is a dummy key. Falling back to error handling.")
    
    asyncio.run(test_ai())
