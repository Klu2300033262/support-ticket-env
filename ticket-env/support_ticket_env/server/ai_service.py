import logging
import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize AsyncOpenAI client with a fallback for startup robustness
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY not found in environment. AI features will be unavailable.")
    api_key = "missing_key"

client = AsyncOpenAI(api_key=api_key)

async def analyze_ticket_with_ai(message: str) -> dict:
    """
    Process a support ticket using OpenAI GPT to categorize, detect priority, and generate a response.
    Returns a dictionary matching the observation schema.
    """
    analysis = {
        "category": "general",
        "priority": "medium",
        "sentiment": "neutral",
        "response": "Thank you for contacting us. We have received your request.",
        "requires_escalation": False,
        "escalation_reason": ""
    }

    try:
        # Define the system prompt for structured analysis
        system_prompt = """
        You are an AI Support Triage Agent. Analyze the incoming customer message and return a JSON object with the following fields:
        - "category": One of [technical, billing, account, general]
        - "priority": One of [low, medium, high, critical]
        - "sentiment": One of [positive, neutral, negative]
        - "response": A professional, empathetic 1-2 sentence response to the customer.
        - "requires_escalation": Boolean.
        - "escalation_reason": String.

        Return ONLY the raw JSON object.
        """

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=500
        )

        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        analysis.update(result)

    except Exception as e:
        logger.error(f"AI Analysis failed: {str(e)}")
        analysis["requires_escalation"] = True
        analysis["escalation_reason"] = f"AI Service Error: {str(e)}"

    # --- Rule-based Overrides & Escalation (Safety Layer) ---
    msg_lower = message.lower()
    critical_keywords = ["immediately", "urgent", "broken", "critical", "blocking", "production down", "emergency"]
    
    # 1. Keyword-based Priority Override
    if any(word in msg_lower for word in critical_keywords):
        logger.info(f"Priority override triggered by keywords. Previous: {analysis['priority']} -> New: critical")
        analysis["priority"] = "critical"
        analysis["requires_escalation"] = True
        if "AI Service Error" not in analysis["escalation_reason"]:
            analysis["escalation_reason"] = "Forced escalation due to critical priority override."

    # 2. Forced Escalation based on Priority or Sentiment
    forced_reasons = []
    if analysis["priority"].lower() == "high":
        forced_reasons.append("High Priority")
    if analysis["sentiment"].lower() == "negative":
        forced_reasons.append("Negative Sentiment")
    
    if forced_reasons:
        logger.info(f"Forced escalation triggered: {', '.join(forced_reasons)}")
        analysis["requires_escalation"] = True
        
        # Append to existing reason if it exists
        new_reason = f"Automated escalation due to: {', '.join(forced_reasons)}."
        if analysis["escalation_reason"]:
            if new_reason not in analysis["escalation_reason"]:
                analysis["escalation_reason"] = f"{analysis['escalation_reason']} | {new_reason}"
        else:
            analysis["escalation_reason"] = new_reason

    logger.info(f"AI Analysis complete: {analysis['category']} | {analysis['priority']} | Escalated: {analysis['requires_escalation']}")
    return analysis
