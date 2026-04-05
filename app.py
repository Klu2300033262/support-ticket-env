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
    
    # Simulate AI analysis
    categories = ["billing", "technical", "account", "general"]
    priorities = ["high", "medium", "low"]
    sentiments = ["negative", "neutral", "positive"]
    
    # Simple keyword-based analysis
    message_lower = request.message.lower()
    
    # Determine category based on keywords
    if any(word in message_lower for word in ["bill", "payment", "charge", "cost", "fee"]):
        category = "billing"
    elif any(word in message_lower for word in ["error", "bug", "broken", "crash", "issue"]):
        category = "technical"
    elif any(word in message_lower for word in ["account", "login", "password", "profile"]):
        category = "account"
    else:
        category = "general"
    
    # Determine priority based on urgency
    if any(word in message_lower for word in ["urgent", "emergency", "critical", "immediate"]):
        priority = "high"
    elif any(word in message_lower for word in ["please", "help", "assist"]):
        priority = "medium"
    else:
        priority = "low"
    
    # Determine sentiment
    if any(word in message_lower for word in ["angry", "frustrated", "terrible", "awful", "hate"]):
        sentiment = "negative"
    elif any(word in message_lower for word in ["happy", "great", "excellent", "love", "thank"]):
        sentiment = "positive"
    else:
        sentiment = "neutral"
    
    # Generate response
    responses = [
        f"Thank you for contacting support. I've analyzed your {category} issue and will help resolve it.",
        f"I understand your concern about the {category} matter. Let me assist you with this {priority} priority issue.",
        f"Your {category} ticket has been processed. Our team will address this {sentiment} feedback accordingly."
    ]
    
    ticket_data = {
        "ticket_id": len(global_state["tickets"]) + 1,
        "message": request.message,
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "response": random.choice(responses),
        "requires_escalation": priority == "high" and sentiment == "negative",
        "escalation_reason": "High priority negative sentiment" if priority == "high" and sentiment == "negative" else None,
        "timestamp": datetime.now().isoformat(),
        "status": "processed",
        "user_id": request.user_id
    }
    
    global_state["tickets"].append(ticket_data)
    global_state["last_ticket"] = ticket_data
    
    # Calculate reward based on analysis quality
    reward = 0.8 if category != "general" else 0.6
    
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
    uvicorn.run(app, host="0.0.0.0", port=7860)
