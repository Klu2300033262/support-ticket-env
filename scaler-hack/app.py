from fastapi import FastAPI

app = FastAPI(title="Support Ticket Environment")

@app.get("/")
def root():
    return {"message": "Support Ticket Environment", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    return {"message": "Environment reset", "done": False}

@app.get("/state")
def state():
    return {"episode_id": "test-123", "step_count": 0}

@app.post("/step")
def step():
    return {"observation": {"message": "Step processed"}, "reward": 0.5}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
