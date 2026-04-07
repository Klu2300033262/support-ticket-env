#!/usr/bin/env python3
"""
Test script to verify OpenEnv environment functionality without requiring API keys.
"""

import requests
import json

def test_openenv_endpoints():
    """Test all required OpenEnv endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing OpenEnv Environment...")
    print(f"Base URL: {base_url}")
    
    # Test 1: Health Check
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Health Failed: {e}")
        return False
    
    # Test 2: Reset Endpoint
    print("\n2. Testing Reset Endpoint...")
    try:
        response = requests.post(f"{base_url}/reset")
        data = response.json()
        print(f"   Reset: {response.status_code}")
        print(f"   Initial Reward: {data.get('reward', 0.0)}")
        print(f"   Episode ID: {data.get('info', {}).get('episode_id', 'N/A')}")
    except Exception as e:
        print(f"   Reset Failed: {e}")
        return False
    
    # Test 3: State Endpoint
    print("\n3. Testing State Endpoint...")
    try:
        response = requests.get(f"{base_url}/state")
        data = response.json()
        print(f"   State: {response.status_code}")
        print(f"   Step Count: {data.get('step_count', 0)}")
        print(f"   Conversation History: {len(data.get('conversation_history', []))} messages")
    except Exception as e:
        print(f"   State Failed: {e}")
        return False
    
    # Test 4: Step Endpoint
    print("\n4. Testing Step Endpoint...")
    try:
        action_data = {
            "user_id": "test_user",
            "message": "I was charged twice for my subscription last night. This is unacceptable, I need a refund immediately!",
            "category": "billing",
            "priority": "high",
            "sentiment": "negative",
            "response": "I sincerely apologize for the duplicate charge. I understand your frustration and will immediately review your account to process a refund."
        }
        
        response = requests.post(f"{base_url}/step", json=action_data)
        data = response.json()
        print(f"   Step: {response.status_code}")
        print(f"   Reward: {data.get('reward', 0.0)}")
        print(f"   Done: {data.get('done', False)}")
        print(f"   Category: {data.get('observation', {}).get('category', 'N/A')}")
    except Exception as e:
        print(f"   Step Failed: {e}")
        return False
    
    # Test 5: Tasks and Graders
    print("\n5. Testing Tasks and Graders...")
    try:
        from tasks import get_all_tasks
        from support_ticket_env.models import SupportTicketAction, SupportTicketObservation
        
        tasks = get_all_tasks()
        print(f"   Found {len(tasks)} tasks")
        
        for task in tasks:
            grader = task['grader']
            action = SupportTicketAction(
                user_id='test',
                message=task['message'],
                category='billing',
                priority='high',
                sentiment='negative',
                response='Test response'
            )
            
            obs = SupportTicketObservation(
                category='billing',
                priority='high', 
                sentiment='negative',
                response='Test response',
                requires_escalation=True,
                escalation_reason='Test reason'
            )
            
            score = grader.forward(action, obs)
            valid_score = 0.0 <= score <= 1.0
            print(f"   Task {task['id']}: {score:.2f} (valid: {valid_score})")
            
            if not valid_score:
                return False
                
    except Exception as e:
        print(f"   Tasks Failed: {e}")
        return False
    
    print("\nAll tests passed! Environment is ready for submission.")
    return True

if __name__ == "__main__":
    success = test_openenv_endpoints()
    exit(0 if success else 1)
