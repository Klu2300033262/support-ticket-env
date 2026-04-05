from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Support Ticket Environment")

# Global state for demonstration
global_state = {
    "episode_id": "demo-123",
    "step_count": 0,
    "conversation_history": [],
    "last_ticket": None
}

# API endpoints
@app.get("/")
def root():
    return {"message": "Support Ticket Environment", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/reset")
def reset():
    global global_state
    global_state = {
        "episode_id": "demo-123",
        "step_count": 0,
        "conversation_history": [],
        "last_ticket": None
    }
    return {"message": "Environment reset", "done": False}

@app.get("/state")
def state():
    return global_state

@app.get("/step")
def step():
    global_state["step_count"] += 1
    return {
        "observation": {
            "message": "Step processed successfully",
            "category": "billing",
            "priority": "medium",
            "sentiment": "neutral"
        },
        "reward": 0.8,
        "done": global_state["step_count"] >= 10
    }

# UI Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Support Ticket Environment Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .stat-card { background: #4CAF50; color: white; padding: 15px; border-radius: 8px; text-align: center; }
            .btn { background: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #1976D2; }
            .btn-reset { background: #f44336; }
            .btn-reset:hover { background: #d32f2f; }
            .response { background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎫 Support Ticket Environment Dashboard</h1>
                <p>OpenEnv Compliant AI Agent Training Environment</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3 id="episode-id">Loading...</h3>
                    <p>Episode ID</p>
                </div>
                <div class="stat-card" style="background: #FF9800;">
                    <h3 id="step-count">0</h3>
                    <p>Step Count</p>
                </div>
                <div class="stat-card" style="background: #9C27B0;">
                    <h3 id="status">Running</h3>
                    <p>System Status</p>
                </div>
                <div class="stat-card" style="background: #607D8B;">
                    <h3 id="reward">0.0</h3>
                    <p>Last Reward</p>
                </div>
            </div>
            
            <div class="card">
                <h2>🎮 Environment Controls</h2>
                <button class="btn" onclick="resetEnvironment()">🔄 Reset Environment</button>
                <button class="btn" onclick="processStep()">⚡ Process Step</button>
                <button class="btn" onclick="checkHealth()">💚 Health Check</button>
                <button class="btn" onclick="getState()">📊 Get State</button>
            </div>
            
            <div class="card">
                <h2>📋 API Responses</h2>
                <div id="responses"></div>
            </div>
            
            <div class="card">
                <h2>🔗 API Endpoints</h2>
                <ul>
                    <li><strong>GET /</strong> - Main endpoint</li>
                    <li><strong>GET /health</strong> - Health check</li>
                    <li><strong>GET /reset</strong> - Reset environment</li>
                    <li><strong>GET /state</strong> - Get current state</li>
                    <li><strong>GET /step</strong> - Process step</li>
                </ul>
            </div>
        </div>
        
        <script>
            async function apiCall(endpoint, method = 'GET') {
                try {
                    const response = await fetch(endpoint, { method });
                    const data = await response.json();
                    return data;
                } catch (error) {
                    return { error: error.message };
                }
            }
            
            async function resetEnvironment() {
                const data = await apiCall('/reset');
                addResponse('Reset Environment', data);
                updateStats();
            }
            
            async function processStep() {
                const data = await apiCall('/step');
                addResponse('Process Step', data);
                updateStats();
            }
            
            async function checkHealth() {
                const data = await apiCall('/health');
                addResponse('Health Check', data);
            }
            
            async function getState() {
                const data = await apiCall('/state');
                addResponse('Get State', data);
                updateStats();
            }
            
            async function updateStats() {
                const state = await apiCall('/state');
                if (state.episode_id) {
                    document.getElementById('episode-id').textContent = state.episode_id;
                    document.getElementById('step-count').textContent = state.step_count;
                }
            }
            
            function addResponse(title, data) {
                const responses = document.getElementById('responses');
                const responseDiv = document.createElement('div');
                responseDiv.className = 'response';
                responseDiv.innerHTML = `
                    <h4>${title}</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
                responses.insertBefore(responseDiv, responses.firstChild);
                
                // Keep only last 5 responses
                while (responses.children.length > 5) {
                    responses.removeChild(responses.lastChild);
                }
            }
            
            // Initialize stats on load
            updateStats();
        </script>
    </body>
    </html>
    """

# Catch all routes
@app.get("/{path:path}")
def catch_all(path: str):
    return {"message": f"Route '{path}' working", "path": path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
