from fastapi import FastAPI

app = FastAPI(title="Support Ticket Environment")

@app.get("/")
def root():
    return {"message": "Support Ticket Environment", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/reset")
def reset():
    return {"message": "Environment reset", "done": False}

@app.get("/state")
def state():
    return {"episode_id": "test-123", "step_count": 0}

@app.get("/step")
def step():
    return {"observation": {"message": "Step processed"}, "reward": 0.5}

# Catch all routes for debugging
@app.get("/{path:path}")
def catch_all(path: str):
    return {"message": f"Route '{path}' working", "path": path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
