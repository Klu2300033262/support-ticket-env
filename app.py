from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
from datetime import datetime
import random

app = FastAPI(title="Support Ticket Environment")

# Pydantic model for analysis requests
class AnalysisRequest(BaseModel):
    message: str
    user_id: str = "saas_user_1"

# Global state for demonstration
global_state = {
    "episode_id": "demo-123",
    "step_count": 0,
    "conversation_history": [],
    "last_ticket": None,
    "tickets": []
}

# Create static directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

# Copy frontend files to static directory
def setup_static_files():
    import shutil
    frontend_files = {
        "index.html": "index.html",
        "style.css": "style.css", 
        "script.js": "script.js",
        "landing.html": "landing.html",
        "landing.css": "landing.css"
    }
    
    for dest_file, src_file in frontend_files.items():
        if os.path.exists(src_file) and not os.path.exists(f"static/{dest_file}"):
            shutil.copy2(src_file, f"static/{dest_file}")

# Setup static files on startup
setup_static_files()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API endpoints
@app.get("/")
def root():
    # Serve the landing page first
    if os.path.exists("static/landing.html"):
        return FileResponse("static/landing.html")
    return {"message": "Support Ticket Environment", "status": "running"}

@app.get("/ui")
def dashboard():
    # Serve the main dashboard
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Dashboard not found"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/reset")
def reset():
    global global_state
    global_state = {
        "episode_id": f"episode-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "step_count": 0,
        "conversation_history": [],
        "last_ticket": None,
        "tickets": []
    }
    return {"message": "Environment reset", "done": False, "episode_id": global_state["episode_id"]}

@app.get("/state")
def state():
    return global_state

@app.post("/step")
def step(request: AnalysisRequest):
    global_state["step_count"] += 1
    
    # Simulate AI analysis with improved logic
    categories = ["billing", "technical", "account", "general"]
    priorities = ["high", "medium", "low"]
    sentiments = ["negative", "neutral", "positive"]
    
    # Enhanced keyword-based analysis
    message_lower = request.message.lower()
    
    # Determine category based on keywords (more comprehensive)
    billing_keywords = ["bill", "payment", "charge", "cost", "fee", "subscription", "invoice", "refund", "price", "charged"]
    technical_keywords = ["error", "bug", "broken", "crash", "issue", "down", "upload", "login", "password", "access", "technical"]
    account_keywords = ["account", "profile", "settings", "user", "registration", "signup"]
    
    if any(word in message_lower for word in billing_keywords):
        category = "billing"
    elif any(word in message_lower for word in technical_keywords):
        category = "technical"
    elif any(word in message_lower for word in account_keywords):
        category = "account"
    else:
        category = "general"
    
    # Enhanced priority detection
    high_priority_keywords = ["urgent", "emergency", "critical", "immediate", "asap", "broken", "crash", "down", "cannot", "unable", "stuck"]
    medium_priority_keywords = ["please", "help", "assist", "support", "need", "issue", "problem"]
    
    if any(word in message_lower for word in high_priority_keywords):
        priority = "high"
    elif any(word in message_lower for word in medium_priority_keywords):
        priority = "medium"
    else:
        priority = "low"
    
    # Enhanced sentiment analysis
    negative_keywords = ["angry", "frustrated", "terrible", "awful", "hate", "worst", "unacceptable", "disappointed", "annoyed", "upset", "mad", "furious"]
    positive_keywords = ["happy", "great", "excellent", "love", "thank", "awesome", "perfect", "satisfied", "pleased", "wonderful"]
    
    negative_count = sum(1 for word in negative_keywords if word in message_lower)
    positive_count = sum(1 for word in positive_keywords if word in message_lower)
    
    if negative_count > positive_count:
        sentiment = "negative"
    elif positive_count > negative_count:
        sentiment = "positive"
    else:
        sentiment = "neutral"
    
    # Enhanced escalation logic
    requires_escalation = False
    escalation_reason = None
    
    # Escalate for high priority + negative sentiment
    if priority == "high" and sentiment == "negative":
        requires_escalation = True
        escalation_reason = "High priority negative sentiment requires immediate attention"
    # Escalate for critical technical issues
    elif category == "technical" and priority == "high":
        requires_escalation = True
        escalation_reason = "Critical technical issue requires escalation"
    # Escalate for billing disputes
    elif category == "billing" and any(word in message_lower for word in ["dispute", "wrong", "double", "overcharge", "refund"]):
        requires_escalation = True
        escalation_reason = "Billing dispute requires review"
    
    # Generate contextual responses
    responses = {
        "billing": [
            f"Thank you for contacting support regarding your {priority} priority billing concern. I've escalated this to our billing team for immediate review.",
            f"I understand your billing issue. Our team will investigate this {priority} priority matter and get back to you shortly.",
            f"Your billing concern has been logged. We'll address this {priority} priority issue with the urgency it requires."
        ],
        "technical": [
            f"I apologize for the technical difficulties. Your {priority} priority issue has been escalated to our technical support team.",
            f"Our technical team is aware of this {priority} priority issue and is working to resolve it as quickly as possible.",
            f"I understand the frustration with this technical problem. We're treating this as a {priority} priority issue."
        ],
        "account": [
            f"Your account access issue has been logged. We'll address this {priority} priority concern promptly.",
            f"I understand the account access problem. Our team will help resolve this {priority} priority issue.",
            f"Thank you for reporting the account issue. We're treating this as a {priority} priority matter."
        ],
        "general": [
            f"Thank you for contacting support. We'll address your {priority} priority inquiry promptly.",
            f"I've received your message and will ensure this {priority} priority concern gets proper attention.",
            f"Your support request has been logged. We'll handle this {priority} priority issue accordingly."
        ]
    }
    
    response_text = random.choice(responses.get(category, responses["general"]))
    
    ticket_data = {
        "ticket_id": len(global_state["tickets"]) + 1,
        "message": request.message,
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "response": response_text,
        "requires_escalation": requires_escalation,
        "escalation_reason": escalation_reason,
        "timestamp": datetime.now().isoformat(),
        "status": "processed",
        "user_id": request.user_id
    }
    
    global_state["tickets"].append(ticket_data)
    global_state["last_ticket"] = ticket_data
    
    # Calculate reward based on analysis quality
    reward = 0.9 if category != "general" else 0.7
    if requires_escalation:
        reward += 0.1  # Bonus for proper escalation detection
    
    return {
        "observation": ticket_data,
        "reward": reward,
        "done": global_state["step_count"] >= 10,
        "ticket": ticket_data
    }

@app.get("/tickets")
def get_tickets():
    return {"tickets": global_state["tickets"]}

@app.get("/analytics")
def get_analytics():
    if not global_state["tickets"]:
        return {
            "total_tickets": 0,
            "category_distribution": {},
            "priority_distribution": {},
            "sentiment_distribution": {},
            "timeline": []
        }
    
    # Calculate distributions
    categories = {}
    priorities = {}
    sentiments = {}
    
    for ticket in global_state["tickets"]:
        cat = ticket["category"]
        pri = ticket["priority"] 
        sen = ticket["sentiment"]
        
        categories[cat] = categories.get(cat, 0) + 1
        priorities[pri] = priorities.get(pri, 0) + 1
        sentiments[sen] = sentiments.get(sen, 0) + 1
    
    return {
        "total_tickets": len(global_state["tickets"]),
        "category_distribution": categories,
        "priority_distribution": priorities,
        "sentiment_distribution": sentiments,
        "timeline": [
            {"date": ticket["timestamp"], "count": 1} 
            for ticket in global_state["tickets"][-10:]
        ]
    }

# Catch all routes
@app.get("/{path:path}")
def catch_all(path: str):
    # Try to serve static files first
    if os.path.exists(f"static/{path}"):
        return FileResponse(f"static/{path}")
    
    # Return API info for unknown routes
    return {
        "message": f"Route '{path}' not found",
        "available_endpoints": [
            "/", "/ui", "/health", "/reset", "/state", "/step", "/tickets", "/analytics"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
