import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_analytics():
    print("Testing Analytics Endpoint...\n")
    
    # 1. Post a few tickets to populate data
    # (Using keywords that trigger the priority override for variety)
    test_tickets = [
        {"message": "I need help with my billing immediately!", "user_id": "user_1"},
        {"message": "The system is broken and critical for my work.", "user_id": "user_2"},
        {"message": "Just a general question about my account settings.", "user_id": "user_3"}
    ]
    
    for t in test_tickets:
        print(f"Submitting ticket: {t['message']}")
        requests.post(f"{BASE_URL}/analyze-ticket", json=t)
        time.sleep(0.5) # Small delay for server updates

    # 2. Call /analytics
    print("\nFetching Analytics...")
    response = requests.get(f"{BASE_URL}/analytics")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Basic validation
        assert data["total_tickets"] >= 3
        assert "category_distribution" in data
        assert "priority_distribution" in data
        assert "sentiment_distribution" in data
        print("\nVerification Successful!")
    else:
        print(f"Failed to fetch analytics. Status code: {response.status_code}")

if __name__ == "__main__":
    test_analytics()
