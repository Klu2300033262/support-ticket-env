import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_tickets():
    # 1. Post a new ticket
    ticket_payload = {
        "message": "I cannot access my account. The password reset link is not working.",
        "user_id": "user_123"
    }
    
    print(f"Posting ticket: {ticket_payload}")
    response = requests.post(f"{BASE_URL}/analyze-ticket", json=ticket_payload)
    
    if response.status_code == 200:
        print("Successfully posted ticket.")
        print(f"AI Analysis: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Failed to post ticket. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return

    # 2. Verify tickets list
    print("\nFetching tickets list...")
    response = requests.get(f"{BASE_URL}/tickets")
    
    if response.status_code == 200:
        tickets = response.json().get("tickets", [])
        print(f"Found {len(tickets)} tickets.")
        for t in tickets:
            print(f"- ID: {t['ticket_id']}, Message: {t['message']}, Category: {t['category']}")
    else:
        print(f"Failed to fetch tickets. Status code: {response.status_code}")

if __name__ == "__main__":
    test_tickets()
