import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { useChatWidget } from "../hooks/useChatWidget";
import { LeadForm } from "./LeadForm";
import "./ChatWidget.css";

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const { sessionToken, messages, isSending, error, leadCaptureNeeded, sendMessage, dismissLeadCapture } =
    useChatWidget();

  const messageListRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messageListRef.current?.scrollTo({ top: messageListRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, leadCaptureNeeded]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  function handleSend() {
    if (!input.trim() || isSending) return;
    sendMessage(input);
    setInput("");
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="maiw-root">
      {!open && (
        <button
          className="maiw-launcher"
          onClick={() => setOpen(true)}
          aria-label="Open chat with MoinSystems AI assistant"
        >
          Chat with us
        </button>
      )}

      {open && (
        <div className="maiw-panel" role="dialog" aria-label="MoinSystems AI chat">
          <header className="maiw-header">
            <span>MoinSystems AI Assistant</span>
            <button
              className="maiw-close-btn"
              onClick={() => setOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </header>

          <div className="maiw-message-list" ref={messageListRef} aria-live="polite">
            {messages.length === 0 && (
              <p className="maiw-empty-state">Hi! Ask me anything about MoinSystems AI's services.</p>
            )}

            {messages.map((m) => (
              <div key={m.id} className={`maiw-message maiw-message-${m.role}`}>
                <span className="maiw-bubble">{m.content}</span>
                {m.failed && <span className="maiw-failed-tag">Not sent</span>}
              </div>
            ))}

            {isSending && (
              <div className="maiw-message maiw-message-assistant" aria-label="Assistant is typing">
                <span className="maiw-bubble maiw-typing">
                  <span></span><span></span><span></span>
                </span>
              </div>
            )}

            {leadCaptureNeeded && sessionToken && (
              <LeadForm sessionToken={sessionToken} onDone={dismissLeadCapture} onCancel={dismissLeadCapture} />
            )}
          </div>

          {error && (
            <div className="maiw-error-banner" role="alert">
              {error}
            </div>
          )}

          <div className="maiw-composer">
            <label htmlFor="maiw-input" className="maiw-sr-only">
              Type a message
            </label>
            <textarea
              id="maiw-input"
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              rows={1}
              disabled={!sessionToken}
            />
            <button
              onClick={handleSend}
              disabled={isSending || !input.trim() || !sessionToken}
              aria-label="Send message"
              className="maiw-send-btn"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}