import os
import json
import sys
from openai import OpenAI
from client import SupportTicketEnv
from models import SupportTicketAction, SupportTicketObservation
from tasks import get_all_tasks

import requests
import time

def main():
    # Required environment variables
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
    MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY is not set. Using fallback logic.")

    # Initialize client and environment
    ai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and OPENAI_API_KEY != "dummy-key" else None
    
    # Get all tasks
    tasks = get_all_tasks()
    total_score = 0.0
    task_results = []

    print("[START]")
    print(f"task_count: {len(tasks)}")
    
    try:
        for task in tasks:
            task_id = task["id"]
            task_name = task["name"]
            message = task["message"]
            grader = task["grader"]
            
            print(f"[STEP]")
            print(f"task_id: {task_id}")
            print(f"task_name: {task_name}")
            
            # Reset environment for each task via HTTP REST POST
            reset_resp = requests.post(f"{API_BASE_URL}/reset")
            if not reset_resp.ok:
                print(f"ERROR: Reset failed {reset_resp.status_code} - {reset_resp.text}")
                continue
            
            # Agent decision making
            analysis = {"category": "general", "priority": "medium", "sentiment": "neutral", "response": "Default response."}
            if ai_client:
                try:
                    prompt = f"""
                    Analyze this support ticket: "{message}"
                    Provide a JSON response with:
                    - category: (billing, technical, account, general)
                    - priority: (high, medium, low)
                    - sentiment: (negative, neutral, positive)
                    - response: A professional response.
                    """

                    completion = ai_client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "system", "content": "You are an expert support triage agent."},
                                  {"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    analysis = json.loads(completion.choices[0].message.content)
                except Exception as e:
                    print(f"OpenAI error (fallback applied): {e}")

            # Create action
            action = SupportTicketAction(
                user_id="hackathon_agent_001",
                message=message,
                category=analysis.get("category"),
                priority=analysis.get("priority"),
                sentiment=analysis.get("sentiment"),
                response=analysis.get("response")
            )

            # Execute step via REST
            step_resp = requests.post(f"{API_BASE_URL}/step", json=action.dict())
            if not step_resp.ok:
                print(f"ERROR: Step failed {step_resp.status_code} - {step_resp.text}")
                continue

            step_result = step_resp.json()
            # Construct observation manually since we got dict from HTTP
            obs_data = step_result.get("state", {})
            observation = SupportTicketObservation(
                category=obs_data.get("category", ""),
                priority=obs_data.get("priority", "Low"),
                sentiment=obs_data.get("sentiment", "Neutral"),
                response=obs_data.get("response", ""),
                requires_escalation=obs_data.get("requires_escalation", False),
                escalation_reason=obs_data.get("escalation_reason", "")
            )
            
            # Grade the task
            task_score = grader.forward(action, observation)
            task_score = max(0.0, min(1.0, float(task_score)))
            
            reward = step_result.get("reward", 0.0)
            done = step_result.get("done", False)

            print(f"reward: {reward}")
            print(f"score: {task_score}")
            print(f"done: {done}")
            
            total_score += task_score
            task_results.append({
                "task_id": task_id,
                "score": task_score,
                "reward": reward
            })
            
    except Exception as e:
        print(f"ERROR: {e}")

    print("[END]")
    print(f"total_score: {total_score / len(tasks) if tasks else 0.0}")
    print(f"tasks_completed: {len(task_results)}")
    
    # Detailed results
    for result in task_results:
        print(f"task_{result['task_id']}_score: {result['score']}")

if __name__ == "__main__":
    main()
