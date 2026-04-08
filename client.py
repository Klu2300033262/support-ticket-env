# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Support Ticket Env Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from models import SupportTicketAction, SupportTicketObservation, SupportTicketState


class SupportTicketEnv(
    EnvClient[SupportTicketAction, SupportTicketObservation, SupportTicketState]
):
    """
    Client for the Support Ticket Env Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Example:
        >>> # Connect to a running server
        >>> with SupportTicketEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     print(result.observation.echoed_message)
        ...
        ...     result = client.step(SupportTicketAction(message="Hello!"))
        ...     print(result.observation.echoed_message)

    Example with Docker:
        >>> # Automatically start container and connect
        >>> client = SupportTicketEnv.from_docker_image("support_ticket_env-env:latest")
        >>> try:
        ...     result = client.reset()
        ...     result = client.step(SupportTicketAction(message="Test"))
        ... finally:
        ...     client.close()
    """

    def _step_payload(self, action: SupportTicketAction) -> Dict:
        """
        Convert SupportTicketAction to JSON payload for step message.

        Args:
            action: SupportTicketAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "ticket_id": action.ticket_id,
            "message": action.message,
            "user_id": action.user_id,
        }

    def _parse_result(self, payload: Dict) -> StepResult[SupportTicketObservation]:
        """
        Parse server response into StepResult[SupportTicketObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with SupportTicketObservation
        """
        obs_data = payload.get("state", {})
        observation = SupportTicketObservation(
            category=obs_data.get("category", ""),
            priority=obs_data.get("priority", "Low"),
            sentiment=obs_data.get("sentiment", "Neutral"),
            response=obs_data.get("response", ""),
            requires_escalation=obs_data.get("requires_escalation", False),
            escalation_reason=obs_data.get("escalation_reason", ""),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> SupportTicketState:
        """
        Parse server response into SupportTicketState object.

        Args:
            payload: JSON response from state request

        Returns:
            SupportTicketState object with episode_id, steps, and history
        """
        return SupportTicketState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            conversation_history=payload.get("conversation_history", []),
            last_ticket_category=payload.get("last_ticket_category"),
            last_priority=payload.get("last_priority"),
            steps_taken=payload.get("steps_taken", 0),
        )
