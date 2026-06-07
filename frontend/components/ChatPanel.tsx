"use client";

import { useState, useRef, useEffect } from "react";

interface Citation {
  video_id: string;
  chunk_index: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  streaming?: boolean;
}

interface ChatPanelProps {
  isReady: boolean;
}

export default function ChatPanel({ isReady }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef<string>("");
  useEffect(() => {
    sessionId.current = `session_${Date.now()}`;
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput("");
    setIsLoading(true);

    // add user message
    setMessages((prev) => [...prev, { role: "user", content: question }]);

    // add empty assistant message for streaming
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: "",
        citations: [],
        streaming: true,
      },
    ]);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          session_id: sessionId.current,
        }),
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let citations: Citation[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.replace("data: ", "").trim();
          if (!raw) continue;

          try {
            const parsed = JSON.parse(raw);

            if (parsed.done) {
              citations = parsed.citations || [];
              // final update with citations
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    content: fullContent,
                    citations,
                    streaming: false,
                  };
                }
                return updated;
              });
            } else if (parsed.token) {
              fullContent += parsed.token;
              // stream tokens into last message
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    content: fullContent,
                    streaming: true,
                  };
                }
                return updated;
              });
            }
          } catch {
            // skip malformed chunks
          }
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Something went wrong. Make sure the backend is running.",
          streaming: false,
        };
        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestedQuestions = [
    "Compare the hooks in the first 5 seconds",
    "What is the engagement rate of each video?",
    "Which video has better content quality?",
    "Who are the creators of each video?",
    "Suggest 3 improvements for Video B",
  ];

  return (
    <div
      className="flex flex-col h-full"
      style={{ background: "var(--bg-secondary)" }}
    >
      {/* header */}
      <div
        className="px-4 py-3 flex items-center justify-between"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <span
          className="mono text-xs font-medium tracking-widest uppercase"
          style={{ color: "var(--text-secondary)" }}
        >
          Chat
        </span>
        {isReady && (
          <span className="flex items-center gap-1.5">
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: "var(--accent-green)" }}
            />
            <span
              className="mono text-xs"
              style={{ color: "var(--accent-green)" }}
            >
              ready
            </span>
          </span>
        )}
      </div>

      {/* messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4">
        {!isReady && (
          <div
            className="flex flex-col items-center justify-center h-full gap-2"
            style={{ color: "var(--text-muted)" }}
          >
            <span className="text-2xl">⌗</span>
            <span className="text-sm">Ingest videos first</span>
          </div>
        )}

        {isReady && messages.length === 0 && (
          <div className="flex flex-col gap-2 fade-in">
            <p className="text-xs mb-2" style={{ color: "var(--text-muted)" }}>
              Suggested questions
            </p>
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => setInput(q)}
                className="text-left text-xs px-3 py-2 rounded transition-all"
                style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  color: "var(--text-secondary)",
                }}
                onMouseEnter={(e) => {
                  (e.target as HTMLElement).style.borderColor =
                    "var(--border-hover)";
                  (e.target as HTMLElement).style.color = "var(--text-primary)";
                }}
                onMouseLeave={(e) => {
                  (e.target as HTMLElement).style.borderColor = "var(--border)";
                  (e.target as HTMLElement).style.color =
                    "var(--text-secondary)";
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex flex-col gap-1 fade-in ${
              msg.role === "user" ? "items-end" : "items-start"
            }`}
          >
            {/* role label */}
            <span
              className="mono text-xs px-1"
              style={{ color: "var(--text-muted)" }}
            >
              {msg.role === "user" ? "you" : "ai"}
            </span>

            {/* bubble */}
            <div
              className="max-w-full px-3 py-2 rounded-lg text-sm leading-relaxed whitespace-pre-wrap"
              style={{
                background:
                  msg.role === "user" ? "var(--bg-hover)" : "var(--bg-card)",
                border: "1px solid var(--border)",
                color: "var(--text-primary)",
              }}
            >
              {msg.content}
              {msg.streaming && <span className="cursor" />}
            </div>

            {/* citations */}
            
            {msg.citations && msg.citations.length > 0 && !msg.streaming && (
  <div className="flex flex-wrap gap-1 px-1">
    {/* deduplicate by video_id only */}
    {Array.from(new Set(msg.citations.map(c => c.video_id))).map((vid, j) => (
      <span key={j}
        className="mono text-xs px-2 py-0.5 rounded-full"
        style={{
          background: vid === "A"
            ? "rgba(34,197,94,0.1)"
            : "rgba(245,158,11,0.1)",
          border: `1px solid ${vid === "A"
            ? "rgba(34,197,94,0.3)"
            : "rgba(245,158,11,0.3)"}`,
          color: vid === "A"
            ? "var(--accent-green)"
            : "var(--accent-amber)",
        }}>
        Video {vid}
      </span>
    ))}
  </div>
)}
          </div>
        ))}

        <div ref={bottomRef} />
      </div>

      {/* input */}
      <div
        className="px-4 py-3"
        style={{ borderTop: "1px solid var(--border)" }}
      >
        <div className="flex gap-2">
          <input
            type="text"
            placeholder={
              isReady
                ? "Ask anything about the videos..."
                : "Ingest videos first"
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!isReady || isLoading}
            className="flex-1 px-3 py-2 rounded-lg text-sm outline-none transition-all"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              color: "var(--text-primary)",
              opacity: !isReady ? 0.5 : 1,
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!isReady || isLoading || !input.trim()}
            className="px-4 py-2 rounded-lg text-sm font-medium mono transition-all"
            style={{
              background:
                isReady && input.trim() && !isLoading
                  ? "var(--accent-green)"
                  : "var(--bg-hover)",
              color:
                isReady && input.trim() && !isLoading
                  ? "#000"
                  : "var(--text-muted)",
              cursor:
                !isReady || isLoading || !input.trim()
                  ? "not-allowed"
                  : "pointer",
            }}
          >
            {isLoading ? "..." : "→"}
          </button>
        </div>
        <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
