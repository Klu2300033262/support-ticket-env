import json
from fastapi.testclient import TestClient
from support_ticket_env.server.app import app

client = TestClient(app)

def test_process_ticket():
    # Because OPENAI_API_KEY is not set (most likely), it should fallback
    payload = {
        "user_id": "Alice123",
        "message": "My computer won't turn on!"
    }
    response = client.post("/analyze-ticket", json=payload)
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert "priority" in data
    assert "category" in data
    assert "sentiment" in data
    assert "response" in data
    assert "requires_escalation" in data
    assert "escalation_reason" in data

    # Test the GET endpoint
    get_response = client.get("/tickets")
    assert get_response.status_code == 200
    db_data = get_response.json()
    assert "tickets" in db_data
    assert len(db_data["tickets"]) == 1
    assert db_data["tickets"][0]["input"]["user_id"] == "Alice123"

    # Test the GET /state endpoint
    state_response = client.get("/state")
    assert state_response.status_code == 200
    state_data = state_response.json()
    assert state_data["step_count"] == 1
    assert state_data["last_category"] == "general"
    assert len(state_data["conversation_history"]) == 1
    assert state_data["conversation_history"][0]["user"] == "My computer won't turn on!"


if __name__ == "__main__":
    test_process_ticket()
    print("Test passed successfully!")
