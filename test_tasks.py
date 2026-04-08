import asyncio
from support_ticket_env.server.graders import BillingGrader, UrgencyGrader, EscalationGrader
from support_ticket_env.models import SupportTicketAction, SupportTicketObservation

async def test_graders():
    # 1. Test BillingGrader
    billing_grader = BillingGrader()
    obs_billing = SupportTicketObservation(category="billing")
    obs_general = SupportTicketObservation(category="general")
    obs_other = SupportTicketObservation(category="technical")
    
    assert billing_grader.forward(None, obs_billing) == 1.0
    assert billing_grader.forward(None, obs_general) == 0.5
    assert billing_grader.forward(None, obs_other) == 0.0
    print("BillingGrader passed!")

    # 2. Test UrgencyGrader
    urgency_grader = UrgencyGrader()
    obs_urgent = SupportTicketObservation(priority="high", sentiment="negative")
    obs_semi = SupportTicketObservation(priority="medium", sentiment="negative")
    obs_none = SupportTicketObservation(priority="low", sentiment="positive")
    
    assert urgency_grader.forward(None, obs_urgent) == 1.0
    assert urgency_grader.forward(None, obs_semi) == 0.5
    assert urgency_grader.forward(None, obs_none) == 0.0
    print("UrgencyGrader passed!")

    # 3. Test EscalationGrader
    escalation_grader = EscalationGrader()
    obs_esc = SupportTicketObservation(requires_escalation=True)
    obs_no_esc = SupportTicketObservation(requires_escalation=False)
    
    assert escalation_grader.forward(None, obs_esc) == 1.0
    assert escalation_grader.forward(None, obs_no_esc) == 0.0
    print("EscalationGrader passed!")

if __name__ == "__main__":
    asyncio.run(test_graders())
