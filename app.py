from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from datetime import datetime
import random

app = FastAPI(title="Support Ticket Environment")

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
        "script.js": "script.js"
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
    # Serve the main frontend
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Support Ticket Environment", "status": "running"}

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
def step():
    global_state["step_count"] += 1
    
    # Simulate ticket processing
    categories = ["billing", "technical", "account", "general"]
    priorities = ["high", "medium", "low"]
    sentiments = ["negative", "neutral", "positive"]
    
    ticket_data = {
        "id": len(global_state["tickets"]) + 1,
        "message": f"Sample ticket #{global_state['step_count']}",
        "category": random.choice(categories),
        "priority": random.choice(priorities),
        "sentiment": random.choice(sentiments),
        "timestamp": datetime.now().isoformat(),
        "status": "processed"
    }
    
    global_state["tickets"].append(ticket_data)
    global_state["last_ticket"] = ticket_data
    
    return {
        "observation": {
            "message": "Step processed successfully",
            "category": ticket_data["category"],
            "priority": ticket_data["priority"],
            "sentiment": ticket_data["sentiment"]
        },
        "reward": round(random.uniform(0.5, 1.0), 2),
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
            "/", "/health", "/reset", "/state", "/step", "/tickets", "/analytics"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
