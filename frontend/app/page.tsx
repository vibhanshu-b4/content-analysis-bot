"use client";

import { useState } from "react";
import ChatPanel from "@/components/ChatPanel";

interface VideoData {
  title: string;
  creator: string;
  platform: string;
  likes: number;
  comments: number;
  views: number;
  engagement_rate: number;
  daily_interactions: number;
  upload_date_formatted: string;
  days_since_upload: number;
  duration: number;
  followers: string | null;
  source_url: string;
  transcript: string;
  chunks: number;
}

interface StatProps {
  label: string;
  value: string;
  color?: string;
  sub?: string;
}

function fmt(n: number): string {
  if (!n) return "N/A";
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}

function Stat({ label, value, color, sub }: StatProps) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.04)",
      borderRadius: "12px",
      padding: "12px",
      border: "1px solid rgba(255,255,255,0.06)",
      textAlign: "center"
    }}>
      <div style={{
        fontSize: "18px",
        fontWeight: 700,
        color: color || "#fff",
        fontFamily: "Poppins, sans-serif",
        lineHeight: 1.2
      }}>{value}</div>
      <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.45)", marginTop: "4px" }}>{label}</div>
      {sub && <div style={{ fontSize: "10px", color: "#10B981", marginTop: "2px" }}>{sub}</div>}
    </div>
  );
}

function VideoCard({ label, data }: { label: string; data: VideoData }) {
  const color = label === "A" ? "#00D4FF" : "#EC4899";
  const glow = label === "A"
    ? "rgba(0,212,255,0.15)"
    : "rgba(236,72,153,0.15)";

  return (
    <div className="glass fade-up" style={{
      padding: "20px",
      boxShadow: `0 0 30px ${glow}`,
    }}>
      {/* label badge */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
        <div style={{
          background: `linear-gradient(135deg, ${color}22, ${color}44)`,
          border: `1px solid ${color}44`,
          borderRadius: "20px",
          padding: "4px 12px",
          fontSize: "11px",
          fontWeight: 600,
          color: color,
          letterSpacing: "1px",
          textTransform: "uppercase" as const
        }}>
          Video {label}
        </div>
        <div style={{
          fontSize: "10px",
          color: "rgba(255,255,255,0.3)",
          background: "rgba(255,255,255,0.05)",
          borderRadius: "20px",
          padding: "3px 10px",
        }}>
          {data.platform?.toUpperCase()}
        </div>
      </div>

      {/* creator */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
        <div style={{
          width: "36px", height: "36px",
          borderRadius: "50%",
          background: `linear-gradient(135deg, ${color}44, ${color}22)`,
          border: `1px solid ${color}44`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "13px", fontWeight: 700, color: color,
          boxShadow: `0 0 12px ${glow}`
        }}>
          {data.creator?.[0]?.toUpperCase() || "?"}
        </div>
        <div>
          <div style={{ fontSize: "14px", fontWeight: 600 }}>{data.creator}</div>
          <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.4)" }}>
            {data.upload_date_formatted} · {data.days_since_upload}d ago
          </div>
        </div>
      </div>

      {/* stats grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px", marginBottom: "14px" }}>
        <Stat label="Likes" value={fmt(data.likes)} color={color} />
        <Stat label="Comments" value={fmt(data.comments)} />
        <Stat label="Daily" value={`${data.daily_interactions}/d`} color="#10B981" sub="rate" />
      </div>

      {/* duration + progress bar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
        <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.4)" }}>Duration</span>
        <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.7)", fontWeight: 500 }}>
          {Math.round(data.duration || 0)}s
        </span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${Math.min((data.duration / 90) * 100, 100)}%` }} />
      </div>
    </div>
  );
}

function IngestForm({ onIngest, isLoading }: {
  onIngest: (a: string, b: string) => void;
  isLoading: boolean;
}) {
  const [urlA, setUrlA] = useState("");
  const [urlB, setUrlB] = useState("");

  return (
    <div style={{ width: "100%", maxWidth: "520px" }}>
      {/* hero text */}
      <div style={{ marginBottom: "32px" }}>
        <div style={{
          fontSize: "11px", fontWeight: 600,
          color: "rgba(99,102,241,0.8)",
          letterSpacing: "2px",
          textTransform: "uppercase" as const,
          marginBottom: "10px"
        }}>
          AI Video Intelligence
        </div>
        <h1 style={{
          fontSize: "38px",
          fontWeight: 700,
          fontFamily: "Poppins, sans-serif",
          lineHeight: 1.15,
          marginBottom: "12px"
        }}>
          Compare <span className="grad-text">any two</span><br />social videos
        </h1>
        <p style={{ fontSize: "15px", color: "rgba(255,255,255,0.5)", lineHeight: 1.6 }}>
          Paste YouTube or Instagram URLs. AI analyzes transcripts,
          engagement metrics, hooks, and storytelling in minutes.
        </p>
      </div>

      {/* inputs */}
      <div style={{ display: "flex", flexDirection: "column" as const, gap: "12px", marginBottom: "16px" }}>
        {[
          { val: urlA, set: setUrlA, label: "Video A", color: "#00D4FF", placeholder: "YouTube or Instagram URL" },
          { val: urlB, set: setUrlB, label: "Video B", color: "#EC4899", placeholder: "YouTube or Instagram URL" },
        ].map(({ val, set, label, color, placeholder }) => (
          <div key={label} style={{ position: "relative" as const }}>
            <div style={{
              position: "absolute" as const,
              left: "14px", top: "50%", transform: "translateY(-50%)",
              fontSize: "11px", fontWeight: 700,
              color: color,
              background: `${color}22`,
              border: `1px solid ${color}44`,
              borderRadius: "6px",
              padding: "2px 7px",
              pointerEvents: "none" as const
            }}>
              {label}
            </div>
            <input
              type="text"
              value={val}
              onChange={e => set(e.target.value)}
              placeholder={placeholder}
              style={{
                width: "100%",
                background: "rgba(255,255,255,0.05)",
                border: `1px solid rgba(255,255,255,0.1)`,
                borderRadius: "14px",
                padding: "14px 16px 14px 72px",
                fontSize: "13px",
                color: "#fff",
                outline: "none",
                fontFamily: "Inter, sans-serif",
                transition: "all 0.2s",
              }}
              onFocus={e => {
                e.target.style.borderColor = `${color}66`;
                e.target.style.boxShadow = `0 0 0 3px ${color}15`;
              }}
              onBlur={e => {
                e.target.style.borderColor = "rgba(255,255,255,0.1)";
                e.target.style.boxShadow = "none";
              }}
            />
          </div>
        ))}
      </div>

      <button
        className="btn-glow"
        onClick={() => onIngest(urlA, urlB)}
        disabled={isLoading || !urlA || !urlB}
        style={{ width: "100%", padding: "15px", fontSize: "15px" }}
      >
        {isLoading
          ? "⏳  Analyzing... (2–3 min)"
          : "✦  Analyze Videos"}
      </button>

      {isLoading && (
        <div style={{
          marginTop: "16px",
          padding: "12px 16px",
          background: "rgba(99,102,241,0.08)",
          border: "1px solid rgba(99,102,241,0.2)",
          borderRadius: "12px",
          fontSize: "12px",
          color: "rgba(255,255,255,0.5)",
          lineHeight: 1.6
        }}>
          🔄 Downloading transcripts → Whisper transcription → BGE-M3 embeddings → ChromaDB indexing
        </div>
      )}
    </div>
  );
}

export default function Home() {
  const [videoA, setVideoA] = useState<VideoData | null>(null);
  const [videoB, setVideoB] = useState<VideoData | null>(null);
  const [isIngested, setIsIngested] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  const handleIngest = async (urlA: string, urlB: string) => {
    setIsIngesting(true);
    try {
      const res = await fetch("http://localhost:8000/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_url_a: urlA, video_url_b: urlB }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ingest failed");
      setVideoA(data.video_a);
      setVideoB(data.video_b);
      setIsIngested(true);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Ingest failed");
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", position: "relative", zIndex: 1 }}>

      {/* top navbar */}
      <nav style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 24px",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(5,8,22,0.8)",
        backdropFilter: "blur(20px)",
        flexShrink: 0,
        zIndex: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{
            width: "28px", height: "28px",
            background: "linear-gradient(135deg, #6366F1, #00D4FF)",
            borderRadius: "8px",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "14px"
          }}>⚡</div>
          <span style={{ fontFamily: "Poppins, sans-serif", fontWeight: 700, fontSize: "15px" }}>
            VideoRAG
          </span>
        </div>

        <div style={{ display: "flex", gap: "4px" }}>
          {["Dashboard", "Analytics", "Compare", "Settings"].map((item, i) => (
            <div key={item} className={`nav-pill ${i === 0 ? "active" : ""}`}>
              {item}
            </div>
          ))}
        </div>

        <div style={{
          fontSize: "12px",
          color: "rgba(255,255,255,0.3)",
          fontFamily: "monospace",
          background: "rgba(255,255,255,0.04)",
          padding: "6px 12px",
          borderRadius: "8px",
          border: "1px solid rgba(255,255,255,0.06)"
        }}>
          llama3.2 · bge-m3
        </div>
      </nav>

      {/* main content */}
      <div style={{ flex: 1, overflow: "hidden", display: "flex" }}>

        {/* landing — before ingest */}
        {!isIngested && (
          <div style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "40px",
          }}>
            <IngestForm onIngest={handleIngest} isLoading={isIngesting} />
          </div>
        )}

        {/* dashboard — after ingest */}
        {isIngested && videoA && videoB && (
          <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>

            {/* left panel — video cards */}
            <div style={{
              flex: 1,
              overflowY: "auto",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              gap: "16px",
            }}>
              {/* header row */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <h2 style={{
                    fontFamily: "Poppins, sans-serif",
                    fontSize: "20px",
                    fontWeight: 700,
                    marginBottom: "2px"
                  }}>
                    Analysis <span className="grad-text">Complete</span>
                  </h2>
                  <p style={{ fontSize: "12px", color: "rgba(255,255,255,0.35)" }}>
                    {new Date().toLocaleString()} · 2 videos indexed
                  </p>
                </div>
                <button
                  onClick={() => { setIsIngested(false); setVideoA(null); setVideoB(null); }}
                  style={{
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "10px",
                    color: "rgba(255,255,255,0.5)",
                    padding: "8px 16px",
                    fontSize: "12px",
                    cursor: "pointer",
                  }}
                >
                  ↩ New Analysis
                </button>
              </div>

              {/* video cards */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <VideoCard label="A" data={videoA} />
                <VideoCard label="B" data={videoB} />
              </div>

              {/* comparison summary card */}
              <div className="glass" style={{ padding: "20px" }}>
                <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)", marginBottom: "12px", fontWeight: 500 }}>
                  QUICK COMPARISON
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "12px" }}>
                  <Stat
                    label="A — Total Interactions"
                    value={fmt(videoA.likes + videoA.comments)}
                    color="#00D4FF"
                  />
                  <Stat
                    label="B — Total Interactions"
                    value={fmt(videoB.likes + videoB.comments)}
                    color="#EC4899"
                  />
                  <Stat
                    label="A — Daily Rate"
                    value={`${videoA.daily_interactions}/d`}
                    color="#00D4FF"
                    sub={videoA.daily_interactions > videoB.daily_interactions ? "↑ faster" : ""}
                  />
                  <Stat
                    label="B — Daily Rate"
                    value={`${videoB.daily_interactions}/d`}
                    color="#EC4899"
                    sub={videoB.daily_interactions > videoA.daily_interactions ? "↑ faster" : ""}
                  />
                </div>
              </div>
            </div>

            {/* right panel — chat */}
            <div style={{
              width: "400px",
              flexShrink: 0,
              borderLeft: "1px solid rgba(255,255,255,0.06)",
              display: "flex",
              flexDirection: "column",
            }}>
              <ChatPanel isReady={isIngested} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}