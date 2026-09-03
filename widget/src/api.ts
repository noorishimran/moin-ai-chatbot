import {
  ApiError,
  type ChatRequest,
  type ChatResponse,
  type LeadCaptureRequest,
  type LeadCaptureResponse,
  type SessionCreateResponse,
} from "./types";

const API_BASE ="https://moin-ai-chatbot-production-2cf8.up.railway.app/api/v1";

const REQUEST_TIMEOUT_MS = 60000;
const MAX_RETRIES = 2;

async function fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function parseErrorResponse(response: Response): Promise<ApiError> {
  let detail: unknown;
  try {
    detail = await response.json();
  } catch {
    return new ApiError("Something went wrong. Please try again.", response.status);
  }

  if (Array.isArray((detail as { detail?: unknown })?.detail)) {
    const fieldErrors = (detail as { detail: { loc: string[]; msg: string }[] }).detail.map((e) => ({
      field: e.loc[e.loc.length - 1],
      message: e.msg.replace("Value error, ", ""),
    }));
    return new ApiError("Please check the highlighted fields.", response.status, fieldErrors);
  }

  const message =
    typeof (detail as { detail?: unknown })?.detail === "string"
      ? (detail as { detail: string }).detail
      : "Something went wrong. Please try again.";
  return new ApiError(message, response.status);
}

async function requestJson<T>(path: string, options: RequestInit, attempt = 1): Promise<T> {
  let response: Response;
  try {
    response = await fetchWithTimeout(`${API_BASE}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch {
    if (attempt < MAX_RETRIES) {
      await new Promise((r) => setTimeout(r, attempt * 800));
      return requestJson<T>(path, options, attempt + 1);
    }
    throw new ApiError("Network error. Please check your connection and try again.", 0);
  }

  if (!response.ok) {
    if (response.status >= 500 && attempt < MAX_RETRIES) {
      await new Promise((r) => setTimeout(r, attempt * 800));
      return requestJson<T>(path, options, attempt + 1);
    }
    throw await parseErrorResponse(response);
  }

  return (await response.json()) as T;
}

export async function createSession(sourcePage?: string): Promise<SessionCreateResponse> {
  return requestJson<SessionCreateResponse>("/sessions", {
    method: "POST",
    body: JSON.stringify({ source_page: sourcePage ?? null }),
  });
}

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  return requestJson<ChatResponse>("/chat/messages", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function captureLead(payload: LeadCaptureRequest): Promise<LeadCaptureResponse> {
  return requestJson<LeadCaptureResponse>("/lead-capture", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}