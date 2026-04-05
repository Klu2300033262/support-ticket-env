#!/usr/bin/env python3
import os
import sys
import time

# Set environment variables for testing
os.environ['API_BASE_URL'] = 'https://lasyasrivalli-ticket-env.hf.space'
os.environ['MODEL_NAME'] = 'gpt-4o'
os.environ['OPENAI_API_KEY'] = 'test'

print("Starting inference test...")
start_time = time.time()

try:
    # Import and run inference
    from inference import main
    main()
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

end_time = time.time()
duration = end_time - start_time
print(f"Duration: {duration:.2f} seconds")
print(f"Under 20 minutes: {duration < 1200}")  # 20 minutes = 1200 seconds
