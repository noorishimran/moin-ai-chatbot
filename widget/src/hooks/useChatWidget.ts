import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  createSession,
  sendChatMessage,
} from "../api";

import {
  ApiError,
  type ConversationMessage,
} from "../types";


export interface DisplayMessage
  extends ConversationMessage {
  id: string;
  pending?: boolean;
  failed?: boolean;
}


const MAX_HISTORY_SENT = 20;


export function useChatWidget() {
  const [sessionToken, setSessionToken] =
    useState<string | null>(null);

  const [messages, setMessages] =
    useState<DisplayMessage[]>([]);

  const [isSending, setIsSending] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [
    leadCaptureNeeded,
    setLeadCaptureNeeded,
  ] = useState(false);


  /*
   * Create a NEW backend session whenever
   * the page/widget application loads.
   *
   * We intentionally do not reuse an old
   * sessionStorage token here.
   */
  useEffect(() => {
    let cancelled = false;

    async function startSession() {
      setError(null);
      setSessionToken(null);

      try {
        const response = await createSession(
          window.location.href
        );

        if (cancelled) {
          return;
        }

        setSessionToken(
          response.session_token
        );
      } catch {
        if (cancelled) {
          return;
        }

        setError(
          "Couldn't start a chat session. Please refresh the page."
        );
      }
    }

    startSession();

    return () => {
      cancelled = true;
    };
  }, []);


  const sendMessage = useCallback(
    async (text: string) => {
      const cleanText = text.trim();

      if (!cleanText || isSending) {
        return;
      }

      if (!sessionToken) {
        setError(
          "Chat session is not ready yet. Please wait a moment and try again."
        );
        return;
      }

      setError(null);

      const userMsgId =
        crypto.randomUUID();

      const userMessage: DisplayMessage = {
        id: userMsgId,
        role: "user",
        content: cleanText,
      };

      setMessages((previous) => [
        ...previous,
        userMessage,
      ]);

      setIsSending(true);

      const historyToSend = [
        ...messages,
        userMessage,
      ]
        .slice(-MAX_HISTORY_SENT)
        .map(({ role, content }) => ({
          role,
          content,
        }));

      try {
        const response =
          await sendChatMessage({
            message: cleanText,
            session_id: sessionToken,
            history: historyToSend,
          });

        setMessages((previous) => [
          ...previous,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: response.answer,
          },
        ]);

        setLeadCaptureNeeded(
          response.next_state ===
            "lead_capture_pending"
        );
      } catch (error) {
        const errorMessage =
          error instanceof ApiError
            ? error.message
            : "Something went wrong. Please try again.";

        setError(errorMessage);

        setMessages((previous) =>
          previous.map((message) =>
            message.id === userMsgId
              ? {
                  ...message,
                  failed: true,
                }
              : message
          )
        );
      } finally {
        setIsSending(false);
      }
    },
    [
      messages,
      sessionToken,
      isSending,
    ]
  );


  function dismissLeadCapture() {
    setLeadCaptureNeeded(false);
  }


  return {
    sessionToken,
    messages,
    isSending,
    error,
    leadCaptureNeeded,
    sendMessage,
    dismissLeadCapture,
  };
}