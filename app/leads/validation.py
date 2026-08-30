"""
5.9 Server-side validation for lead capture.
"""

import re

PLACEHOLDER_PATTERNS = [
    r"^n/?a$",
    r"^test$",
    r"^asdf+$",
    r"^x+$",
    r"^none$",
    r"^-+$",
    r"^\.+$",
    r"^unknown$",
]

PLACEHOLDER_EMAIL_LOCAL_PARTS = {"test", "asdf", "example", "fake", "none", "na"}

PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")


def is_placeholder_text(value: str) -> bool:
    normalized = value.strip().lower()
    return any(re.fullmatch(pattern, normalized) for pattern in PLACEHOLDER_PATTERNS)


def validate_full_name(name: str) -> str:
    name = name.strip()
    if len(name) < 2:
        raise ValueError("full_name must be at least 2 characters.")
    if is_placeholder_text(name):
        raise ValueError("full_name looks like a placeholder, not a real name.")
    return name


def validate_email_address(email: str) -> str:
    email = email.strip().lower()
    local_part = email.split("@")[0] if "@" in email else email
    if local_part in PLACEHOLDER_EMAIL_LOCAL_PARTS:
        raise ValueError("email looks like a placeholder address.")
    return email


def validate_contact_number(number: str) -> str:
    number = number.strip()
    if not PHONE_REGEX.match(number):
        raise ValueError("contact_number is not a valid phone number format.")
    digits_only = re.sub(r"\D", "", number)
    if len(digits_only) < 7:
        raise ValueError("contact_number does not have enough digits.")
    return number