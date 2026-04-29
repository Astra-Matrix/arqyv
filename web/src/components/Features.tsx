import {
  Play,
  Search,
  Brain,
  Share2,
  Cloud,
  Mic,
  FileText,
  Zap,
  Shield,
  Layers,
  RefreshCw,
  MonitorSpeaker,
} from "lucide-react";

const FEATURES = [
  {
    icon: Play,
    title: "Custom Media Engine",
    desc: "ARQYVMediaEngine: zero external installs. Magic-byte format detection for 40+ formats. Qt Multimedia primary with auto-detected VLC upgrade.",
    accent: true,
  },
  {
    icon: Brain,
    title: "On-Device AI",
    desc: "BLIP image captioning, Whisper transcription, sentence-transformers embeddings — all local. No API keys. No data leaves your machine.",
    accent: true,
  },
  {
    icon: Share2,
    title: "Instant P2P Sharing",
    desc: "One click generates a QR code. Scan it on any device and the download starts. mDNS discovery finds ARQYV peers on your LAN automatically.",
    accent: true,
  },
  {
    icon: Search,
    title: "Semantic Search",
    desc: "ChromaDB vector store + sentence-transformers. Search by meaning, not keywords. Combine with filter tokens like type:video or date:>2024.",
  },
  {
    icon: Mic,
    title: "Voice Search",
    desc: "Speak your query. Whisper transcribes locally in real-time, submits to the search engine, and returns results — no internet required.",
  },
  {
    icon: Cloud,
    title: "Cloud Sync",
    desc: "Google Drive, OneDrive, and Dropbox providers wired in. OAuth2 auth, no data ever sent to ARQYV — only you and your cloud provider.",
  },
  {
    icon: FileText,
    title: "Smart Metadata",
    desc: "mutagen, EXIF, MediaInfo, PyMuPDF, and spaCy NLP auto-extract technical + semantic metadata from every file format in your library.",
  },
  {
    icon: Layers,
    title: "Subtitle Engine",
    desc: "Pure-Python SRT / WebVTT / ASS parser with Qt overlay renderer. Auto-detects and loads subtitle files next to video. No codec needed.",
  },
  {
    icon: RefreshCw,
    title: "Smart Resume",
    desc: "Remembers exactly where you were in every file. Reopen any video or audio track and it resumes from the last position automatically.",
  },
  {
    icon: Zap,
    title: "Batch Rename",
    desc: "Template engine with {name}, {date}, {counter}, {ai_tag}, {ext} tokens. Live preview in the dialog. Undo-safe, never destructive.",
  },
  {
    icon: MonitorSpeaker,
    title: "Audio DSP",
    desc: "Built-in EQ presets (Bass Boost, Cinema, Night Mode, Flat) with peak metering. No external audio plugins or codecs required.",
  },
  {
    icon: Shield,
    title: "Local-First, Always",
    desc: "No accounts. No telemetry. No cloud dependency. Every byte stays on your machine. The API server only binds to localhost.",
  },
];

export default function Features() {
  return (
    <section id="features" className="py-32 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-20">
          <p className="text-sm font-medium text-[#00b4d8] uppercase tracking-widest mb-4">
            Built different
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-[#e0e0e0] mb-5">
            Everything. In one application.
          </h2>
          <p className="text-[#9e9e9e] text-lg max-w-2xl mx-auto">
            ARQYV is not a media player wrapper. Every component — the media
            engine, the search stack, the sharing system — is built from the
            ground up to work offline, forever.
          </p>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <div
                key={f.title}
                className={`group relative rounded-2xl p-6 border transition-all duration-300 hover:border-[#00b4d8]/40 hover:-translate-y-1 ${
                  f.accent
                    ? "bg-gradient-to-br from-[#16213e] to-[#0f3460] border-[#00b4d8]/20"
                    : "bg-[#16213e] border-[#2a2a4a]"
                }`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                {f.accent && (
                  <div className="absolute inset-0 rounded-2xl bg-[#00b4d8]/3 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${
                    f.accent
                      ? "bg-[#00b4d8]/20 text-[#00b4d8]"
                      : "bg-[#0f3460] text-[#9e9e9e] group-hover:text-[#00b4d8] group-hover:bg-[#00b4d8]/15 transition-colors"
                  }`}
                >
                  <Icon size={20} />
                </div>
                <h3 className="font-semibold text-[#e0e0e0] mb-2 text-base">{f.title}</h3>
                <p className="text-[#9e9e9e] text-sm leading-relaxed">{f.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
