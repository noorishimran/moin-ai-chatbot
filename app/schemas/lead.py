"""
Schemas for POST /api/v1/sessions and POST /api/v1/lead-capture.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.leads.validation import (
    validate_contact_number,
    validate_email_address,
    validate_full_name,
    is_placeholder_text,
)


class SessionCreateRequest(BaseModel):
    source_page: str | None = Field(default=None, max_length=512)


class SessionCreateResponse(BaseModel):
    session_token: str


class LeadCaptureRequest(BaseModel):
    session_token: str

    # Required
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    contact_number: str = Field(..., min_length=7, max_length=64)
    service_interest: str = Field(..., min_length=2, max_length=512)

    # Optional
    company_name: str | None = Field(default=None, max_length=200)
    project_summary: str | None = Field(default=None, max_length=2000)
    timeline: str | None = Field(default=None, max_length=128)
    budget_range: str | None = Field(default=None, max_length=128)
    source_page: str | None = Field(default=None, max_length=512)

    @field_validator("full_name")
    @classmethod
    def _check_name(cls, v: str) -> str:
        return validate_full_name(v)

    @field_validator("email")
    @classmethod
    def _check_email(cls, v: str) -> str:
        return validate_email_address(str(v))

    @field_validator("contact_number")
    @classmethod
    def _check_number(cls, v: str) -> str:
        return validate_contact_number(v)

    @field_validator("service_interest")
    @classmethod
    def _check_service_interest(cls, v: str) -> str:
        v = v.strip()
        if is_placeholder_text(v):
            raise ValueError("service_interest looks like a placeholder, not a real answer.")
        return v


class LeadCaptureResponse(BaseModel):
    lead_id: str
    status: str = "saved"
    message: str = "Thanks! The MoinSystems AI team has received your details and will follow up soon."