"""
6.2 Notification template + 6.10 input protection.
"""

from datetime import datetime, timezone

MAX_FIELD_LENGTH = 500


def _clean(value: str | None, max_len: int = MAX_FIELD_LENGTH) -> str:
    if not value:
        return "-"
    single_line = " ".join(value.split())
    return single_line[:max_len]


def build_lead_notification_email(
    full_name: str,
    email: str,
    contact_number: str,
    service_interest: str,
    company_name: str | None,
    project_summary: str | None,
    timeline: str | None,
    budget_range: str | None,
    source_page: str | None,
    user_question: str | None,
    conversation_summary: str | None,
) -> tuple[str, str]:
    subject = f"New MoinSystems AI Lead — {_clean(full_name, 100)}"

    body = f"""New lead captured from the MoinSystems AI website chatbot.

CONTACT DETAILS
Name: {_clean(full_name, 200)}
Email: {_clean(email, 320)}
Phone: {_clean(contact_number, 64)}
Company: {_clean(company_name, 200)}

PROJECT
Service interest: {_clean(service_interest, 512)}
Project summary: {_clean(project_summary, 2000)}
Timeline: {_clean(timeline, 128)}
Budget range: {_clean(budget_range, 128)}

CONTEXT
Source page: {_clean(source_page, 512)}
Visitor's question: {_clean(user_question, 1000)}
Conversation summary: {_clean(conversation_summary, 1500)}

Submitted: {datetime.now(timezone.utc).isoformat()}

--
This lead was NOT added to a CRM — MoinSystems AI's chatbot does not
use one. Please follow up directly using the contact details above.
"""
    return subject, body