import logging
import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# --- ANTI-GRAVITY FIX START ---
# Initialize AsyncOpenAI client with a robust fallback for startup robustness
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "missing_key":
    logger.warning("OPENAI_API_KEY not found or invalid. AI features will be gracefully disabled.")
    api_key = None

# Only initialize client if key is available to avoid 401 errors during validation
client = AsyncOpenAI(api_key=api_key) if api_key else None

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

    # Skip API call if client is not initialized (missing key)
    if not client:
        logger.info("Skipping AI analysis due to missing API key. Using safe defaults.")
        return await apply_safety_overrides(message, analysis)

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
        # If API call fails, we return the default analysis gracefully
        analysis["requires_escalation"] = False
        analysis["escalation_reason"] = "AI Service Connectivity: Fallback mode active."

    return await apply_safety_overrides(message, analysis)

async def apply_safety_overrides(message: str, analysis: dict) -> dict:
    """Apply rule-based overrides and escalation logic safely."""
    msg_lower = message.lower()
    critical_keywords = ["immediately", "urgent", "broken", "critical", "blocking", "production down", "emergency"]
    
    # 1. Keyword-based Priority Override
    if any(word in msg_lower for word in critical_keywords):
        logger.info(f"Priority override triggered by keywords. Previous: {analysis['priority']} -> New: critical")
        analysis["priority"] = "critical"
        analysis["requires_escalation"] = True
        if "AI Service" not in analysis["escalation_reason"]:
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
# --- ANTI-GRAVITY FIX END ---
