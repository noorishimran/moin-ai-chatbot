import { useState, type FormEvent } from "react";

import { captureLead } from "../api";
import { ApiError } from "../types";


interface Props {
  sessionToken: string;
  onDone: () => void;
  onCancel: () => void;
}


interface FormState {
  full_name: string;
  email: string;
  contact_number: string;
  service_interest: string;
}


const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


export function LeadForm({
  sessionToken,
  onDone,
  onCancel,
}: Props) {
  const [form, setForm] = useState<FormState>({
    full_name: "",
    email: "",
    contact_number: "",
    service_interest: "",
  });

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);


  function updateField(
    field: keyof FormState,
    value: string
  ) {
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));

    setFieldErrors((prev) => {
      if (!prev[field]) {
        return prev;
      }

      const next = { ...prev };
      delete next[field];

      return next;
    });

    setGeneralError(null);
  }


  function validateClientSide(): Record<string, string> {
    const errors: Record<string, string> = {};

    if (form.full_name.trim().length < 2) {
      errors.full_name = "Please enter your full name.";
    }

    if (!EMAIL_PATTERN.test(form.email.trim())) {
      errors.email = "Please enter a valid email address.";
    }

    if (
      form.contact_number.replace(/\D/g, "").length < 7
    ) {
      errors.contact_number =
        "Please enter a valid phone number.";
    }

    if (form.service_interest.trim().length < 2) {
      errors.service_interest =
        "Please tell us what you're interested in.";
    }

    return errors;
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setGeneralError(null);
    setFieldErrors({});

    const clientErrors = validateClientSide();

    if (Object.keys(clientErrors).length > 0) {
      setFieldErrors(clientErrors);
      return;
    }

    setSubmitting(true);

    try {
      await captureLead({
        session_token: sessionToken,
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        contact_number: form.contact_number.trim(),
        service_interest: form.service_interest.trim(),
      });

      setSubmitted(true);
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.fieldErrors.length > 0
      ) {
        const errors: Record<string, string> = {};

        for (const fieldError of error.fieldErrors) {
          errors[fieldError.field] =
            fieldError.message;
        }

        setFieldErrors(errors);
      } else {
        setGeneralError(
          error instanceof ApiError
            ? error.message
            : "Couldn't submit your details. Please try again."
        );
      }
    } finally {
      setSubmitting(false);
    }
  }


  if (submitted) {
    return (
      <div
        className="maiw-lead-success"
        role="status"
        aria-live="polite"
      >
        <p>
          Thanks! Your details have been submitted successfully.
          The MoinSystems AI team will be in touch shortly.
        </p>

        <button
          type="button"
          className="maiw-btn-primary"
          onClick={onDone}
        >
          Continue chat
        </button>
      </div>
    );
  }


  return (
    <form
      className="maiw-lead-form"
      onSubmit={handleSubmit}
      noValidate
    >
      <p className="maiw-lead-intro">
        Share your details and the team will follow up.
      </p>

      <label htmlFor="maiw-full-name">
        Full name
      </label>

      <input
        id="maiw-full-name"
        value={form.full_name}
        onChange={(event) =>
          updateField(
            "full_name",
            event.target.value
          )
        }
        disabled={submitting}
        aria-invalid={!!fieldErrors.full_name}
        aria-describedby={
          fieldErrors.full_name
            ? "maiw-full-name-err"
            : undefined
        }
      />

      {fieldErrors.full_name && (
        <span
          id="maiw-full-name-err"
          className="maiw-field-error"
          role="alert"
        >
          {fieldErrors.full_name}
        </span>
      )}

      <label htmlFor="maiw-email">
        Email
      </label>

      <input
        id="maiw-email"
        type="email"
        value={form.email}
        onChange={(event) =>
          updateField(
            "email",
            event.target.value
          )
        }
        disabled={submitting}
        aria-invalid={!!fieldErrors.email}
        aria-describedby={
          fieldErrors.email
            ? "maiw-email-err"
            : undefined
        }
      />

      {fieldErrors.email && (
        <span
          id="maiw-email-err"
          className="maiw-field-error"
          role="alert"
        >
          {fieldErrors.email}
        </span>
      )}

      <label htmlFor="maiw-contact-number">
        Phone number
      </label>

      <input
        id="maiw-contact-number"
        type="tel"
        value={form.contact_number}
        onChange={(event) =>
          updateField(
            "contact_number",
            event.target.value
          )
        }
        disabled={submitting}
        aria-invalid={
          !!fieldErrors.contact_number
        }
        aria-describedby={
          fieldErrors.contact_number
            ? "maiw-contact-number-err"
            : undefined
        }
      />

      {fieldErrors.contact_number && (
        <span
          id="maiw-contact-number-err"
          className="maiw-field-error"
          role="alert"
        >
          {fieldErrors.contact_number}
        </span>
      )}

      <label htmlFor="maiw-service-interest">
        What are you interested in?
      </label>

      <input
        id="maiw-service-interest"
        value={form.service_interest}
        onChange={(event) =>
          updateField(
            "service_interest",
            event.target.value
          )
        }
        disabled={submitting}
        aria-invalid={
          !!fieldErrors.service_interest
        }
        aria-describedby={
          fieldErrors.service_interest
            ? "maiw-service-interest-err"
            : undefined
        }
      />

      {fieldErrors.service_interest && (
        <span
          id="maiw-service-interest-err"
          className="maiw-field-error"
          role="alert"
        >
          {fieldErrors.service_interest}
        </span>
      )}

      {generalError && (
        <div
          className="maiw-field-error"
          role="alert"
        >
          {generalError}
        </div>
      )}

      <div className="maiw-lead-actions">
        <button
          type="button"
          onClick={onCancel}
          className="maiw-btn-secondary"
          disabled={submitting}
        >
          Not now
        </button>

        <button
          type="submit"
          disabled={submitting}
          className="maiw-btn-primary"
        >
          {submitting
            ? "Sending..."
            : "Send"}
        </button>
      </div>
    </form>
  );
}