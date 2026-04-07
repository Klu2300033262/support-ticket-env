from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from typing import List, Dict, Any
from support_ticket_env.models import SupportTicketAction, SupportTicketObservation
from support_ticket_env.server.ai_service import analyze_ticket_with_ai
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import Depends
from support_ticket_env.server.database import init_db, get_db, Ticket

# Configure global application logging format suitable for production deployment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize application with robust Swagger API Documentation metadata
app = FastAPI(
    title="AI Support Ticket System",
    description="An intelligent backend mapping OpenEnv structures to instantly classify and process customer support queries dynamically leveraging GPT-4.",
    version="1.0.0",
    docs_url="/docs"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global path for frontend assets (assuming CWD is project root)
FRONTEND_DIR = os.path.join(os.getcwd(), "frontend")

# Mount static files (CSS, JS) only if directory exists
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# Scalability Note: 
# Using SQLite with SQLAlchemy for persistent storage.
# tickets_db is kept for backward compatibility/internal tracking if needed, 
# but primary storage is now the database.
tickets_db: List[Dict[str, Any]] = []

@app.on_event("startup")
async def on_startup():
    await init_db()
    logger.info("Database initialized successfully.")

# Internal environment state tracking
global_state = {
    "conversation_history": [],
    "last_category": None,
    "last_priority": None,
    "step_count": 0
}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Override default validation error to provide clear production-styled HTTP responses globally.
    Ensures safe serialization of failed input blocks for frontends evaluating endpoint drops.
    """
    logger.error(f"Malformed input request trapped: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid Request Constraints", "errors": exc.errors()}
    )


@app.post("/reset", tags=["OpenEnv"])
async def reset_environment():
    """
    OpenEnv reset endpoint - initializes a new episode.
    """
    global_state["conversation_history"] = []
    global_state["last_category"] = None
    global_state["last_priority"] = None
    global_state["step_count"] = 0
    
    # Return initial observation
    initial_obs = SupportTicketObservation(
        category="",
        priority="medium",
        sentiment="neutral",
        response="",
        requires_escalation=False,
        escalation_reason="",
        done=False,
        reward=0.0,
        metadata={"episode_id": str(uuid.uuid4()), "step": 0}
    )
    
    return {
        "state": initial_obs.dict(),
        "reward": 0.0,
        "done": False
    }

@app.post("/step", response_model=dict, tags=["OpenEnv"])
async def step_environment(action: SupportTicketAction, db: AsyncSession = Depends(get_db)):
    """
    OpenEnv step endpoint - processes agent action and returns observation/reward.
    """
    analysis = await analyze_ticket_with_ai(action.message)
    
    # Calculate Reward based on partial progress rules
    reward = 0.0
    
    # 1. Correct Category (+0.4)
    if action.category == analysis["category"]:
        reward += 0.4
    elif action.category is not None:
        reward -= 0.1
        
    # 2. Correct Priority (+0.3)
    if action.priority == analysis["priority"]:
        reward += 0.3
        
    # 3. Correct Sentiment (+0.1)
    if action.sentiment == analysis["sentiment"]:
        reward += 0.1
        
    # 4. Professional Response Tone (+0.2)
    if action.response:
        prof_keywords = ["sincerely", "apologize", "understand", "urgency", "assistance", "immediately", "review", "support"]
        if any(word in action.response.lower() for word in prof_keywords) and len(action.response) > 20:
            reward += 0.2

    # Final Clamp
    reward = max(0.0, min(1.0, float(reward)))
    
    observation = SupportTicketObservation(**analysis, reward=reward)
    
    # Save to database
    db_ticket = Ticket(
        message=action.message,
        category=observation.category,
        priority=observation.priority,
        sentiment=observation.sentiment,
        response=observation.response,
        requires_escalation=observation.requires_escalation,
        escalation_reason=observation.escalation_reason,
    )
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)

    # Update global state
    global_state["conversation_history"].append({"user": action.message, "bot": observation.response})
    global_state["last_category"] = observation.category
    global_state["last_priority"] = observation.priority
    global_state["step_count"] += 1
    
    return {
        "state": observation.dict(),
        "reward": float(reward),
        "done": global_state["step_count"] >= 10
    }

@app.get("/state", tags=["OpenEnv"])
def get_environment_state():
    """
    OpenEnv state endpoint - returns current environment state.
    """
    return {
        "state": {
            "episode_id": str(uuid.uuid4()),
            "step_count": global_state["step_count"],
            "conversation_history": global_state["conversation_history"],
            "last_ticket_category": global_state["last_category"],
            "last_priority": global_state["last_priority"],
            "steps_taken": global_state["step_count"]
        },
        "reward": 0.0,
        "done": global_state["step_count"] >= 10
    }

@app.post("/analyze-ticket", response_model=SupportTicketObservation, tags=["AI Analysis"])
async def analyze_ticket(ticket: SupportTicketAction, db: AsyncSession = Depends(get_db)):
    """
    Evaluate an incoming support ticket schema using OpenAI logic.
    
    This accepts an OpenEnv action natively, calculates severity traits (latency tolerant internally), 
    returns a fully formatted Observation compliant schema, and manages the state layer cache globally.
    """
    analysis = await analyze_ticket_with_ai(ticket.message)
    
    # Calculate Reward based on partial progress rules (for OpenEnv compliance)
    reward = 0.0
    
    # 1. Correct Category (+0.4)
    if ticket.category == analysis["category"]:
        reward += 0.4
    elif ticket.category is not None:
        reward -= 0.1 # Penalty
        
    # 2. Correct Priority (+0.3)
    if ticket.priority == analysis["priority"]:
        reward += 0.3
        
    # 3. Correct Sentiment (+0.1)
    if ticket.sentiment == analysis["sentiment"]:
        reward += 0.1
        
    # 4. Professional Response Tone (+0.2)
    if ticket.response:
        prof_keywords = ["sincerely", "apologize", "understand", "urgency", "assistance", "immediately", "review", "support"]
        if any(word in ticket.response.lower() for word in prof_keywords) and len(ticket.response) > 20:
            reward += 0.2

    # Final Clamp
    reward = max(0.0, min(1.0, float(reward)))
    
    observation = SupportTicketObservation(**analysis, reward=reward)
    
    # Save to database
    db_ticket = Ticket(
        message=ticket.message,
        category=observation.category,
        priority=observation.priority,
        sentiment=observation.sentiment,
        response=observation.response,
        requires_escalation=observation.requires_escalation,
        escalation_reason=observation.escalation_reason,
    )
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)

    # Safely commit to our hackathon datastore with UUID and Timestamp (legacy support)
    ticket_entry = {
        "ticket_id": db_ticket.id,
        "message": db_ticket.message,
        "category": db_ticket.category,
        "priority": db_ticket.priority,
        "sentiment": db_ticket.sentiment,
        "response": db_ticket.response,
        "timestamp": db_ticket.timestamp.isoformat()
    }
    tickets_db.append(ticket_entry)

    # Update internal environment state tracking
    global_state["conversation_history"].append({"user": ticket.message, "bot": observation.response})
    global_state["last_category"] = observation.category
    global_state["last_priority"] = observation.priority
    global_state["step_count"] += 1
    
    logger.info(f"Ticket from user {ticket.user_id} effectively analyzed and persisted.")
    return observation

@app.get("/tickets", tags=["Analytics"])
async def get_tickets(db: AsyncSession = Depends(get_db)):
    """
    Extract the globally executed ticket queue stored within the database.
    """
    result = await db.execute(select(Ticket).order_by(Ticket.timestamp.desc()))
    tickets = result.scalars().all()
    
    formatted_tickets = [
        {
            "ticket_id": t.id,
            "message": t.message,
            "category": t.category,
            "priority": t.priority,
            "sentiment": t.sentiment,
            "response": t.response,
            "requires_escalation": t.requires_escalation,
            "escalation_reason": t.escalation_reason,
            "timestamp": t.timestamp.isoformat()
        }
        for t in tickets
    ]
    
    return {"tickets": formatted_tickets}

@app.get("/analytics-state", tags=["Analytics"])
def get_state():
    """
    Return the synthesized current environment state including history and last metrics.
    """
    return global_state

@app.get("/analytics", tags=["Analytics"])
async def get_analytics(db: AsyncSession = Depends(get_db)):
    """
    Compute distribution metrics for categories, priorities, and sentiments from the ticket history in the DB.
    """
    # Fetch all records to calculate distribution
    # For large datasets, this should be done with SQL aggregations (func.count)
    result = await db.execute(select(Ticket))
    db_tickets = result.scalars().all()
    
    total = len(db_tickets)
    
    category_dist = {}
    priority_dist = {}
    sentiment_dist = {}
    
    for ticket in db_tickets:
        cat = ticket.category or "general"
        prio = ticket.priority or "medium"
        sent = ticket.sentiment or "neutral"
        
        category_dist[cat] = category_dist.get(cat, 0) + 1
        priority_dist[prio] = priority_dist.get(prio, 0) + 1
        sentiment_dist[sent] = sentiment_dist.get(sent, 0) + 1
        
    return {
        "total_tickets": total,
        "category_distribution": category_dist,
        "priority_distribution": priority_dist,
        "sentiment_distribution": sentiment_dist
    }

@app.get("/", tags=["Landing"])
def read_root():
    """
    Serve the modern AI Support Ticket Landing Page.
    """
    if os.path.exists(os.path.join(FRONTEND_DIR, "landing.html")):
        return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))
    else:
        return {"message": "Support Ticket Environment API", "status": "running", "docs": "/docs"}

@app.get("/test", tags=["Test"])
def test_endpoint():
    """
    Simple test endpoint to verify API is working.
    """
    return {"message": "API is working", "status": "success"}

@app.get("/health", tags=["Health"])
def health_check():
    """
    Service health check endpoint for monitoring and load balancing.
    """
    return {"status": "healthy", "service": "AI Support Ticket System"}

@app.get("/ui", tags=["Frontend"])
def serve_ui():
    """
    Serve the modern AI Support Ticket Dashboard directly from the FastAPI server.
    """
    if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    else:
        return {"message": "Frontend not available", "docs": "/docs"}

def main():
    import uvicorn
    uvicorn.run(
        "support_ticket_env.server.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()