// Matches app/schemas/chat.py and app/schemas/lead.py exactly.

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  session_id: string | null;
  history: ConversationMessage[];
}

export interface ChatResponse {
  answer: string;
  session_id: string | null;
  intent: string;
  next_state: string;
  used_rag: boolean;
}

export interface SessionCreateResponse {
  session_token: string;
}

export interface LeadCaptureRequest {
  session_token: string;
  full_name: string;
  email: string;
  contact_number: string;
  service_interest: string;
  company_name?: string | null;
  project_summary?: string | null;
  timeline?: string | null;
  budget_range?: string | null;
  source_page?: string | null;
}

export interface LeadCaptureResponse {
  lead_id: string;
  status: string;
  email_status: "sent" | "failed";
  message: string;
}

export interface ApiFieldError {
  field: string;
  message: string;
}

export class ApiError extends Error {
  status: number;
  fieldErrors: ApiFieldError[];

  constructor(message: string, status: number, fieldErrors: ApiFieldError[] = []) {
    super(message);
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}