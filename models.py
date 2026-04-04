# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Support Ticket Env Environment.

The support_ticket_env environment is a simple test environment that echoes back messages.
"""

from openenv.core.env_server.types import Action, Observation, State
from pydantic import Field
from typing import Optional


# Scalability Note:
# In a production environment, inheriting from `Action` keeps the system fully modular and decoupled,
# enabling integration into broader agentic architectures, event-driven pipelines, or OpenEnv deployments.

class SupportTicketAction(Action):
    """
    Action for the Support Ticket Env environment - incoming support ticket.
    
    This model defines the strict schema required to submit a support ticket for analysis.
    It inherently conforms to the OpenEnv framework structure, ensuring full compatibility if deployed as a space.
    """

    ticket_id: Optional[str] = Field(default=None, description="Optional ticket ID")
    message: str = Field(..., min_length=10, description="The content of the support ticket")
    user_id: str = Field(..., min_length=1, description="ID of the user submitting the ticket")
    category: Optional[str] = Field(default=None, description="Agent's classified category")
    priority: Optional[str] = Field(default=None, description="Agent's assigned priority")
    sentiment: Optional[str] = Field(default=None, description="Agent's detected sentiment")
    response: Optional[str] = Field(default=None, description="Agent's generated response")



# Scalability Note:
# By inheriting from `Observation`, we unify the return structure. Future modifications can safely append metadata,
# confidence scores, or routing tags without breaking client-side logic expecting the base Observation signature.

class SupportTicketObservation(Observation):
    """
    Observation from the Support Ticket Env environment - AI categorization and response.
    
    This payload captures the structured output synthesized by the AI,
    mapping the category, emotional sentiment, priority, and the dynamically generated response.
    """

    category: str = Field(default="", description="Categorized issue type")
    priority: str = Field(default="Low", description="Priority level: Low, Medium, High, Critical")
    sentiment: str = Field(default="Neutral", description="Sentiment of the message")
    response: str = Field(default="", description="Generated response to the customer")
    requires_escalation: bool = Field(default=False, description="Flag indicating if the ticket requires human escalation")
    escalation_reason: str = Field(default="", description="Reason for escalation if applicable")
    reward: float = Field(default=0.0, description="The reward calculated for this specific step")



class SupportTicketState(State):
    """
    Extends the base OpenEnv State to track historical ticket metrics and conversation logs.
    """

    conversation_history: list[dict[str, str]] = Field(
        default_factory=list, description="Ordered history of ticket messages and responses"
    )
    last_ticket_category: Optional[str] = Field(
        default=None, description="Category of the most recent processed ticket"
    )
    last_priority: Optional[str] = Field(
        default=None, description="Priority of the most recent processed ticket"
    )
    steps_taken: int = Field(
        default=0, description="Total number of tickets processed in this session"
    )

