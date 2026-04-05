# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Support Ticket Env Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
"""

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from support_ticket_env.models import SupportTicketAction, SupportTicketObservation, SupportTicketState
    from support_ticket_env.server.ai_service import analyze_ticket_with_ai
except ImportError:
    try:
        from ..models import SupportTicketAction, SupportTicketObservation, SupportTicketState
        from .ai_service import analyze_ticket_with_ai
    except ImportError:
        from models import SupportTicketAction, SupportTicketObservation, SupportTicketState
        from ai_service import analyze_ticket_with_ai



class SupportTicketEnvironment(Environment):
    """
    A simple echo environment that echoes back messages.

    This environment is designed for testing the HTTP server infrastructure.
    It maintains minimal state and simply echoes back whatever message it receives.

    Example:
        >>> env = SupportTicketEnvironment()
        >>> obs = env.reset()
        >>> print(obs.echoed_message)  # "Support Ticket Env environment ready!"
        >>>
        >>> obs = env.step(SupportTicketAction(message="Hello"))
        >>> print(obs.echoed_message)  # "Hello"
        >>> print(obs.message_length)  # 5
    """

    # Enable concurrent WebSocket sessions.
    # Set to True if your environment isolates state between instances.
    # When True, multiple WebSocket clients can connect simultaneously, each
    # getting their own environment instance (when using factory mode in app.py).
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the support_ticket_env environment."""
        self._state = SupportTicketState(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0

    def reset(self) -> SupportTicketObservation:
        """
        Reset the environment.

        Returns:
            SupportTicketObservation with a ready message
        """
        self._state = SupportTicketState(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1

        return SupportTicketObservation(
            echoed_message="Support Ticket Env environment ready!",
            message_length=0,
            done=False,
            reward=0.0,
        )

    async def step(self, action: SupportTicketAction) -> SupportTicketObservation:  # type: ignore[override]
        """
        Execute a step in the environment by processing the support ticket.

        Args:
            action: SupportTicketAction containing the ticket message

        Returns:
            SupportTicketObservation with the analyzed ticket data
        """
        self._state.step_count += 1
        self._state.steps_taken += 1

        message = action.message
        
        # Use our deterministic AI simulation logic
        analysis = await analyze_ticket_with_ai(message)
        
        # Calculate Reward based on partial progress rules
        reward = 0.0
        
        # 1. Correct Category (+0.4)
        if action.category == analysis["category"]:
            reward += 0.4
        elif action.category is not None:
            # Penalty for wrong classification
            reward -= 0.1
            
        # 2. Correct Priority (+0.3)
        if action.priority == analysis["priority"]:
            reward += 0.3
            
        # 3. Correct Sentiment (+0.1)
        if action.sentiment == analysis["sentiment"]:
            reward += 0.1
            
        # 4. Professional Response Tone (+0.2)
        if action.response:
            prof_keywords = ["sincerely", "apologize", "understand", "urgency", "assistance", "immediately", "review", "support"]
            response_lower = action.response.lower()
            if any(word in response_lower for word in prof_keywords) and len(action.response) > 20:
                reward += 0.2

        # Final Clamp
        reward = max(0.0, min(1.0, float(reward)))

        # Update State Tracking
        self._state.last_ticket_category = analysis["category"]
        self._state.last_priority = analysis["priority"]
        self._state.conversation_history.append({
            "user": message,
            "assistant": analysis["response"]
        })

        return SupportTicketObservation(
            **analysis,
            done=False,
            reward=reward,
            metadata={"original_message": message, "step": self._state.step_count},
        )


    @property
    def state(self) -> SupportTicketState:
        """
        Get the current environment state.

        Returns:
            SupportTicketState with episode_id, step_count, and history
        """
        return self._state
