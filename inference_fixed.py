import os
import json
import sys
import time
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from support_ticket_env.client import SupportTicketEnv
from support_ticket_env.models import SupportTicketAction
from tasks import get_all_tasks

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FallbackAnalyzer:
    """Fallback rule-based analyzer when OpenAI API is unavailable."""
    
    @staticmethod
    def analyze_ticket(message: str) -> Dict[str, Any]:
        """Analyze ticket using rule-based approach."""
        message_lower = message.lower()
        
        # Category detection
        billing_keywords = ["bill", "payment", "charge", "cost", "fee", "subscription", "invoice", "refund", "price", "charged"]
        technical_keywords = ["error", "bug", "broken", "crash", "issue", "down", "upload", "login", "password", "access", "technical"]
        account_keywords = ["account", "profile", "settings", "user", "registration", "signup"]
        
        if any(word in message_lower for word in billing_keywords):
            category = "billing"
        elif any(word in message_lower for word in technical_keywords):
            category = "technical"
        elif any(word in message_lower for word in account_keywords):
            category = "account"
        else:
            category = "general"
        
        # Priority detection
        high_priority_keywords = ["urgent", "emergency", "critical", "immediate", "asap", "broken", "crash", "down", "cannot", "unable", "stuck"]
        medium_priority_keywords = ["please", "help", "assist", "support", "need", "issue", "problem"]
        
        if any(word in message_lower for word in high_priority_keywords):
            priority = "high"
        elif any(word in message_lower for word in medium_priority_keywords):
            priority = "medium"
        else:
            priority = "low"
        
        # Sentiment detection
        negative_keywords = ["angry", "frustrated", "terrible", "awful", "hate", "worst", "unacceptable", "disappointed", "annoyed", "upset", "mad", "furious"]
        positive_keywords = ["happy", "great", "excellent", "love", "thank", "awesome", "perfect", "satisfied", "pleased", "wonderful"]
        
        negative_count = sum(1 for word in negative_keywords if word in message_lower)
        positive_count = sum(1 for word in positive_keywords if word in message_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
        elif positive_count > negative_count:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        
        # Generate response
        responses = {
            "billing": f"Thank you for contacting support regarding your {priority} priority billing concern. Our billing team will review this matter and get back to you shortly.",
            "technical": f"I apologize for the technical difficulties. Your {priority} priority issue has been escalated to our technical support team for immediate attention.",
            "account": f"Your account access issue has been logged. We'll address this {priority} priority concern promptly.",
            "general": f"Thank you for contacting support. We'll address your {priority} priority inquiry promptly."
        }
        
        response = responses.get(category, responses["general"])
        
        return {
            "category": category,
            "priority": priority,
            "sentiment": sentiment,
            "response": response
        }

class SafeInferenceEngine:
    """Safe inference engine with timeout protection and fallback logic."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o", timeout: int = 30):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.client = None
        self.fallback_analyzer = FallbackAnalyzer()
        
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def analyze_with_timeout(self, message: str) -> Dict[str, Any]:
        """Analyze message with timeout protection."""
        if not self.client:
            logger.info("Using fallback analyzer (no OpenAI client)")
            return self.fallback_analyzer.analyze_ticket(message)
        
        try:
            # Start timeout timer
            start_time = time.time()
            
            prompt = f"""
            Analyze this support ticket: "{message}"
            Provide a JSON response with:
            - category: (billing, technical, account, general)
            - priority: (high, medium, low)
            - sentiment: (negative, neutral, positive)
            - response: A professional response.
            """
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert support triage agent."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                timeout=self.timeout
            )
            
            # Check if we exceeded timeout
            if time.time() - start_time > self.timeout:
                logger.warning("OpenAI API call exceeded timeout, using fallback")
                return self.fallback_analyzer.analyze_ticket(message)
            
            analysis = json.loads(completion.choices[0].message.content)
            logger.info("OpenAI analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}, using fallback analyzer")
            return self.fallback_analyzer.analyze_ticket(message)

def main():
    """Main inference function with comprehensive error handling."""
    logger.info("Starting inference process")
    
    # Environment variables with defaults
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    model_name = os.environ.get("MODEL_NAME", "gpt-4o")
    hf_token = os.environ.get("HF_TOKEN")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    logger.info(f"API Base URL: {api_base_url}")
    logger.info(f"Model: {model_name}")
    logger.info(f"OpenAI API Key available: {bool(openai_api_key)}")
    
    # Initialize inference engine
    inference_engine = SafeInferenceEngine(
        api_key=openai_api_key,
        model_name=model_name,
        timeout=30
    )
    
    # Initialize environment with error handling
    env = None
    try:
        env = SupportTicketEnv(base_url=api_base_url)
        logger.info("Environment client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize environment: {e}")
        print(f"[ERROR] Failed to initialize environment: {e}")
        sys.exit(1)
    
    # Get all tasks
    try:
        tasks = get_all_tasks()
        logger.info(f"Loaded {len(tasks)} tasks")
    except Exception as e:
        logger.error(f"Failed to load tasks: {e}")
        print(f"[ERROR] Failed to load tasks: {e}")
        if env:
            env.close()
        sys.exit(1)
    
    total_score = 0.0
    task_results = []
    
    print("[START]")
    print(f"task_count: {len(tasks)}")
    
    try:
        for i, task in enumerate(tasks):
            task_id = task["id"]
            task_name = task["name"]
            message = task["message"]
            grader = task["grader"]
            
            logger.info(f"Processing task {i+1}/{len(tasks)}: {task_id}")
            print(f"[STEP]")
            print(f"task_id: {task_id}")
            print(f"task_name: {task_name}")
            
            try:
                # Reset environment
                reset_result = env.reset()
                logger.debug("Environment reset successful")
            except Exception as e:
                logger.error(f"Environment reset failed for task {task_id}: {e}")
                continue
            
            try:
                # Analyze ticket
                analysis = inference_engine.analyze_with_timeout(message)
                logger.debug(f"Analysis completed for task {task_id}")
            except Exception as e:
                logger.error(f"Analysis failed for task {task_id}: {e}")
                # Use fallback analysis
                analysis = inference_engine.fallback_analyzer.analyze_ticket(message)
            
            try:
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
                
                logger.info(f"Task {task_id} completed with score: {task_score}")
                
            except Exception as e:
                logger.error(f"Task execution failed for {task_id}: {e}")
                print(f"ERROR: Task {task_id} failed: {e}")
                continue
                
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("[INTERRUPTED]")
    except Exception as e:
        logger.error(f"Unexpected error during inference: {e}")
        print(f"ERROR: {e}")
    finally:
        if env:
            try:
                env.close()
                logger.info("Environment closed")
            except Exception as e:
                logger.error(f"Error closing environment: {e}")
    
    print("[END]")
    print(f"total_score: {total_score / len(tasks) if tasks else 0.0}")
    print(f"tasks_completed: {len(task_results)}")
    
    # Detailed results
    for result in task_results:
        print(f"task_{result['task_id']}_score: {result['score']}")
    
    logger.info("Inference process completed")

if __name__ == "__main__":
    main()
