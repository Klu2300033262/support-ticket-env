import asyncio
from support_ticket_env.server.support_ticket_env_environment import SupportTicketEnvironment
from support_ticket_env.models import SupportTicketAction

async def test_env_state():
    env = SupportTicketEnvironment()
    
    # 1. Check initial state
    state = env.state
    assert state.step_count == 0
    assert state.steps_taken == 0
    assert state.conversation_history == []
    assert state.last_ticket_category is None
    
    # 2. Perform a step
    action = SupportTicketAction(user_id="user1", message="I cannot login to my account, password reset fails.")
    obs = await env.step(action)
    
    # 3. Check updated state
    state = env.state
    print(f"State after 1 step: {state}")
    assert state.step_count == 1
    assert state.steps_taken == 1
    assert state.last_ticket_category == "account"
    assert len(state.conversation_history) == 1
    assert state.conversation_history[0]["user"] == action.message
    
    # 4. Perform another step
    action2 = SupportTicketAction(user_id="user1", message="Also, I was charged twice for my subscription!")
    obs2 = await env.step(action2)
    
    # 5. Check final state
    state = env.state
    print(f"State after 2 steps: {state}")
    assert state.step_count == 2
    assert state.steps_taken == 2
    assert state.last_ticket_category == "billing"
    assert state.last_priority == "high"
    assert len(state.conversation_history) == 2
    
    print("Environment state tracking tests passed!")

if __name__ == "__main__":
    asyncio.run(test_env_state())
