"use client";
import ChatPanel from "../components/ChatPanel";
import { useState } from "react";
// types
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

interface IngestFormProps {
  onIngest: (urlA: string, urlB: string) => void;
  isLoading: boolean;
}

interface VideoCardProps {
  label: string;
  data: VideoData;
}

interface StatProps {
  label: string;
  value: string;
  color?: string;
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
    <main className="h-screen flex flex-col overflow-hidden">
      {/* top bar */}
      <header
        className="border-b flex items-center justify-between px-6 py-3"
        style={{
          borderColor: "var(--border)",
          background: "var(--bg-secondary)",
        }}
      >
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
          <span
            className="mono text-sm font-medium tracking-widest uppercase"
            style={{ color: "var(--text-primary)" }}
          >
            Video RAG Analyzer
          </span>
        </div>
        <span className="mono text-xs" style={{ color: "var(--text-muted)" }}>
          powered by llama3.2 + bge-m3
        </span>
      </header>

      {/* url input form */}
      {!isIngested && (
        <section className="flex flex-col items-center justify-center flex-1 px-6 py-16 fade-in">
          <div className="w-full max-w-2xl">
            <h1
              className="text-3xl font-semibold mb-2"
              style={{ color: "var(--text-primary)" }}
            >
              Compare two videos
            </h1>
            <p
              className="text-sm mb-8"
              style={{ color: "var(--text-secondary)" }}
            >
              Paste any YouTube or Instagram Reel URL. The AI will analyze
              transcripts, metadata, and engagement to answer your questions.
            </p>
            <IngestForm onIngest={handleIngest} isLoading={isIngesting} />
          </div>
        </section>
      )}

      {/* main content after ingest */}
      {isIngested && videoA && videoB && (
  <section className="flex flex-1 overflow-hidden">
    {/* left — video cards */}
    <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
      <div className="text-xs mono mb-2" style={{ color: "var(--text-muted)" }}>
        ANALYSIS READY — {new Date().toLocaleTimeString()}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <VideoCard label="A" data={videoA} />
        <VideoCard label="B" data={videoB} />
      </div>
    </div>

    {/* right — chat */}
    <div className="w-96 flex-shrink-0 flex flex-col"
      style={{ borderLeft: "1px solid var(--border)" }}>
      <ChatPanel isReady={isIngested} />
    </div>
  </section>
)}
    </main>
  );
}

// placeholder components until we build them
function IngestForm({ onIngest, isLoading }: IngestFormProps) {
  const [urlA, setUrlA] = useState("");
  const [urlB, setUrlB] = useState("");
  return (
    <div className="flex flex-col gap-3">
      <input
        type="text"
        placeholder="Video A URL (YouTube or Instagram)"
        value={urlA}
        onChange={(e) => setUrlA(e.target.value)}
        className="w-full px-4 py-3 rounded-lg text-sm mono outline-none"
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          color: "var(--text-primary)",
        }}
      />
      <input
        type="text"
        placeholder="Video B URL (YouTube or Instagram)"
        value={urlB}
        onChange={(e) => setUrlB(e.target.value)}
        className="w-full px-4 py-3 rounded-lg text-sm mono outline-none"
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          color: "var(--text-primary)",
        }}
      />
      <button
        onClick={() => onIngest(urlA, urlB)}
        disabled={isLoading || !urlA || !urlB}
        className="w-full py-3 rounded-lg text-sm font-medium transition-all"
        style={{
          background: isLoading ? "var(--bg-hover)" : "var(--accent-green)",
          color: isLoading ? "var(--text-muted)" : "#000",
          cursor: isLoading ? "not-allowed" : "pointer",
        }}
      >
        {isLoading ? "Analyzing videos... (2-3 min)" : "Analyze Videos"}
      </button>
    </div>
  );
}

function VideoCard({ label, data }: VideoCardProps) {
  return (
    <div
      className="rounded-lg p-4 fade-in"
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
      }}
    >
      <div
        className="mono text-xs mb-2"
        style={{ color: "var(--accent-green)" }}
      >
        VIDEO {label}
      </div>
      <div className="text-sm font-medium mb-1">{data.creator}</div>
      <div className="text-xs mb-3" style={{ color: "var(--text-secondary)" }}>
        {data.platform?.toUpperCase()} · {data.upload_date_formatted}
      </div>
      <div className="grid grid-cols-3 gap-2">
        <Stat label="Likes" value={fmt(data.likes)} />
        <Stat label="Comments" value={fmt(data.comments)} />
        <Stat
          label="Daily"
          value={`${data.daily_interactions}/d`}
          color="var(--accent-amber)"
        />
      </div>
    </div>
  );
}

function Stat({ label, value, color }: StatProps) {
  return (
    <div
      className="rounded p-2 text-center"
      style={{ background: "var(--bg-secondary)" }}
    >
      <div
        className="mono text-sm font-semibold"
        style={{ color: color || "var(--text-primary)" }}
      >
        {value}
      </div>
      <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
        {label}
      </div>
    </div>
  );
}


function fmt(n: number): string {
  if (!n) return "N/A";
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}
