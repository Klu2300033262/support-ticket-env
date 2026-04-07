import asyncio
from support_ticket_env.server.support_ticket_env_environment import SupportTicketEnvironment
from support_ticket_env.models import SupportTicketAction

async def test_reward_logic():
    env = SupportTicketEnvironment()
    
    # 1. Test Perfect Score (1.0)
    print("Testing Perfect Score...")
    action_perfect = SupportTicketAction(
        user_id="u1", 
        message="I lost my password and cannot sign in.",
        category="account",
        priority="low",
        sentiment="neutral",
        response="We understand your frustration and will provide immediate assistance to reset your account credentials."
    )
    obs = await env.step(action_perfect)
    print(f"Perfect Reward: {obs.reward}")
    assert obs.reward == 1.0
    
    # 2. Test Partial Score (Category only: 0.4)
    print("Testing Category Only Score...")
    action_partial = SupportTicketAction(
        user_id="u2",
        message="I need help with my billing invoice.",
        category="billing"
    )
    obs = await env.step(action_partial)
    print(f"Partial Reward (Expected 0.4): {obs.reward}")
    assert abs(obs.reward - 0.4) < 1e-9
    
    # 3. Test Penalty (Wrong category: -0.1)
    # Plus priority 0.3 = 0.2 total
    print("Testing Penalty Score...")
    action_penalty = SupportTicketAction(
        user_id="u3",
        message="The app is crashing! This is a big problem.",
        category="billing",  # Incorrect, should be technical
        priority="medium"    # Correct
    )

    obs = await env.step(action_penalty)
    print(f"Penalty Reward (Expected 0.2): {obs.reward}")
    assert abs(obs.reward - 0.2) < 1e-9

    # 4. Test Tone Only (+0.2)
    print("Testing Tone Only Score...")
    action_tone = SupportTicketAction(
        user_id="u4",
        message="Normal query",
        response="We sincerely apologize for any delay and appreciate your continued support while we review this matter."
    )
    obs = await env.step(action_tone)
    # Category = general, priority = low, sentiment = neutral
    # If agent provided none of those, they get 0 for them.
    # But wait, if they didn't provide them, they don't match or mismatch.
    # My logic: "if action.category == analysis['category']: reward += 0.4"
    # If action.category is None, it won't match.
    # So 0.2 for tone.
    print(f"Tone Only Reward (Expected 0.2): {obs.reward}")
    assert abs(obs.reward - 0.2) < 1e-9

    print("\nReward function verification passed!")

if __name__ == "__main__":
    asyncio.run(test_reward_logic())
