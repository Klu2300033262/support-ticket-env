import os
import json
import sys
from openai import OpenAI
from support_ticket_env.client import SupportTicketEnv
from support_ticket_env.models import SupportTicketAction
from tasks import get_all_tasks

def main():
    # Required environment variables
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
    MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")
    HF_TOKEN = os.environ.get("HF_TOKEN")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY is not set.")
        sys.exit(1)

    # Initialize client and environment
    env = SupportTicketEnv(base_url=API_BASE_URL)
    ai_client = OpenAI(api_key=OPENAI_API_KEY)
    
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
            
            # Reset environment for each task
            reset_result = env.reset()
            
            # Agent decision making
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

            # Create action
            action = SupportTicketAction(
                user_id="hackathon_agent_001",
                message=message,
                category=analysis.get("category"),
                priority=analysis.get("priority"),
                sentiment=analysis.get("sentiment"),
                response=analysis.get("response")
            )

            # Execute step
            step_result = env.step(action)
            observation = step_result.observation
            
            # Grade the task
            task_score = grader.forward(action, observation)
            task_score = max(0.0, min(1.0, float(task_score)))
            
            print(f"reward: {step_result.reward}")
            print(f"score: {task_score}")
            print(f"done: {step_result.done}")
            
            total_score += task_score
            task_results.append({
                "task_id": task_id,
                "score": task_score,
                "reward": step_result.reward
            })
            
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        env.close()

    print("[END]")
    print(f"total_score: {total_score / len(tasks) if tasks else 0.0}")
    print(f"tasks_completed: {len(task_results)}")
    
    # Detailed results
    for result in task_results:
        print(f"task_{result['task_id']}_score: {result['score']}")

if __name__ == "__main__":
    main()
