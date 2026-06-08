"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

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

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setMessages((prev) => [...prev, {
      role: "assistant",
      content: "",
      citations: [],
      streaming: true,
    }]);

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
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "100%",
      background: "rgba(255,255,255,0.01)",
    }}>

      {/* header */}
      <div style={{
        padding: "14px 20px",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(255,255,255,0.02)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{
            width: "24px", height: "24px",
            background: "linear-gradient(135deg, #6366F1, #00D4FF)",
            borderRadius: "6px",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "12px"
          }}>✦</div>
          <span style={{
            fontSize: "12px",
            fontWeight: 600,
            color: "rgba(255,255,255,0.5)",
            letterSpacing: "1.5px",
            fontFamily: "Inter, sans-serif"
          }}>
            AI CHAT
          </span>
        </div>
        {isReady && (
          <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{
              width: "6px", height: "6px",
              borderRadius: "50%",
              background: "#10B981",
              boxShadow: "0 0 8px #10B981"
            }} />
            <span style={{ fontSize: "11px", color: "#10B981", fontWeight: 500 }}>
              ready
            </span>
          </span>
        )}
      </div>

      {/* messages area */}
      <div style={{
        flex: 1,
        overflowY: "auto",
        padding: "16px",
        display: "flex",
        flexDirection: "column",
        gap: "12px",
      }}>

        {/* not ready state */}
        {!isReady && (
          <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            gap: "12px",
          }}>
            <div style={{
              width: "48px", height: "48px",
              borderRadius: "16px",
              background: "rgba(99,102,241,0.1)",
              border: "1px solid rgba(99,102,241,0.2)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "22px"
            }}>⌗</div>
            <p style={{ fontSize: "13px", color: "rgba(255,255,255,0.3)", textAlign: "center" }}>
              Ingest two videos first<br />to start chatting
            </p>
          </div>
        )}

        {/* suggested questions */}
        {isReady && messages.length === 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <p style={{
              fontSize: "11px",
              color: "rgba(255,255,255,0.3)",
              fontWeight: 600,
              letterSpacing: "1px",
              marginBottom: "4px"
            }}>
              SUGGESTED QUESTIONS
            </p>
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => setInput(q)}
                style={{
                  textAlign: "left",
                  fontSize: "12px",
                  padding: "10px 14px",
                  borderRadius: "10px",
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.07)",
                  color: "rgba(255,255,255,0.5)",
                  cursor: "pointer",
                  transition: "all 0.2s",
                  width: "100%",
                  fontFamily: "Inter, sans-serif",
                  lineHeight: 1.4,
                }}
                onMouseEnter={e => {
                  (e.currentTarget).style.background = "rgba(99,102,241,0.12)";
                  (e.currentTarget).style.borderColor = "rgba(99,102,241,0.3)";
                  (e.currentTarget).style.color = "#fff";
                }}
                onMouseLeave={e => {
                  (e.currentTarget).style.background = "rgba(255,255,255,0.03)";
                  (e.currentTarget).style.borderColor = "rgba(255,255,255,0.07)";
                  (e.currentTarget).style.color = "rgba(255,255,255,0.5)";
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* messages */}
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex",
            flexDirection: "column",
            gap: "4px",
            alignItems: msg.role === "user" ? "flex-end" : "flex-start",
            animation: "fadeUp 0.3s ease forwards",
          }}>

            {/* role label */}
            <span style={{
              fontSize: "10px",
              fontWeight: 600,
              letterSpacing: "1px",
              color: msg.role === "user"
                ? "rgba(99,102,241,0.7)"
                : "rgba(0,212,255,0.7)",
              padding: "0 4px",
              fontFamily: "Inter, sans-serif"
            }}>
              {msg.role === "user" ? "YOU" : "AI"}
            </span>

            {/* bubble */}
            <div style={{
  maxWidth: "100%",
  padding: "10px 14px",
  borderRadius: msg.role === "user"
    ? "14px 4px 14px 14px"
    : "4px 14px 14px 14px",
  fontSize: "13px",
  lineHeight: 1.65,
  fontFamily: "Inter, sans-serif",
  background: msg.role === "user"
    ? "rgba(99,102,241,0.15)"
    : "rgba(255,255,255,0.04)",
  border: msg.role === "user"
    ? "1px solid rgba(99,102,241,0.25)"
    : "1px solid rgba(255,255,255,0.07)",
  color: "#fff",
}}>
  {msg.role === "assistant" && !msg.streaming ? (
    <ReactMarkdown
      components={{
        p: ({children}) => <p style={{ marginBottom: "8px" }}>{children}</p>,
        strong: ({children}) => <strong style={{ color: "#00D4FF", fontWeight: 600 }}>{children}</strong>,
        ul: ({children}) => <ul style={{ paddingLeft: "16px", marginBottom: "8px" }}>{children}</ul>,
        li: ({children}) => <li style={{ marginBottom: "4px" }}>{children}</li>,
        h1: ({children}) => <h1 style={{ fontSize: "15px", fontWeight: 600, marginBottom: "8px", color: "#fff" }}>{children}</h1>,
        h2: ({children}) => <h2 style={{ fontSize: "14px", fontWeight: 600, marginBottom: "6px", color: "#fff" }}>{children}</h2>,
      }}
    >
      {msg.content}
    </ReactMarkdown>
  ) : (
    <span style={{ whiteSpace: "pre-wrap" }}>
      {msg.content}
      {msg.streaming && <span className="cursor" />}
    </span>
  )}
</div>

            {/* citations */}
            {msg.citations && msg.citations.length > 0 && !msg.streaming && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", padding: "0 4px" }}>
                {Array.from(new Set(msg.citations.map(c => c.video_id))).map((vid, j) => (
                  <span key={j} style={{
                    fontSize: "10px",
                    fontWeight: 600,
                    padding: "3px 10px",
                    borderRadius: "20px",
                    fontFamily: "Inter, sans-serif",
                    letterSpacing: "0.5px",
                    background: vid === "A"
                      ? "rgba(0,212,255,0.08)"
                      : "rgba(236,72,153,0.08)",
                    border: `1px solid ${vid === "A"
                      ? "rgba(0,212,255,0.25)"
                      : "rgba(236,72,153,0.25)"}`,
                    color: vid === "A" ? "#00D4FF" : "#EC4899",
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

      {/* input area */}
      <div style={{
        padding: "12px 16px 16px",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
          <input
            type="text"
            placeholder={isReady ? "Ask about the videos..." : "Ingest videos first"}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!isReady || isLoading}
            style={{
              flex: 1,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "12px",
              padding: "10px 14px",
              fontSize: "13px",
              color: "#fff",
              outline: "none",
              opacity: !isReady ? 0.4 : 1,
              fontFamily: "Inter, sans-serif",
              transition: "all 0.2s",
            }}
            onFocus={e => {
              e.target.style.borderColor = "rgba(99,102,241,0.5)";
              e.target.style.boxShadow = "0 0 0 3px rgba(99,102,241,0.1)";
            }}
            onBlur={e => {
              e.target.style.borderColor = "rgba(255,255,255,0.1)";
              e.target.style.boxShadow = "none";
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!isReady || isLoading || !input.trim()}
            className="btn-glow"
            style={{
              padding: "10px 18px",
              fontSize: "15px",
              borderRadius: "12px",
              opacity: !isReady || !input.trim() ? 0.4 : 1,
            }}
          >
            {isLoading ? "⏳" : "→"}
          </button>
        </div>
        <p style={{
          fontSize: "11px",
          color: "rgba(255,255,255,0.2)",
          fontFamily: "Inter, sans-serif",
          textAlign: "center",
        }}>
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}