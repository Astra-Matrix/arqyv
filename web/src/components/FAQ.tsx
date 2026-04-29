"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const FAQS = [
  {
    q: "Is ARQYV really free? No subscription?",
    a: "Completely free, forever. MIT licensed. Open source on GitHub. There is no ARQYV account, no cloud service, no telemetry. You can build it yourself from the source code.",
  },
  {
    q: "Do I need to install VLC or FFmpeg?",
    a: "No. ARQYV ships with Qt Multimedia as the primary playback engine — it uses platform-native codecs (Windows Media Foundation on Windows, AVFoundation on macOS, GStreamer on Linux). If you have VLC installed, ARQYV will detect it automatically and upgrade to VLC's extended codec support (H.265, AV1, AC3, DTS…). Nothing to configure.",
  },
  {
    q: "Does AI analysis send my files to the cloud?",
    a: "Never. Every AI model runs locally on your machine: Whisper for transcription, BLIP for image captioning, sentence-transformers for embeddings, spaCy for NLP tagging. No API keys required. No internet connection needed for any AI feature.",
  },
  {
    q: "How does P2P file sharing work?",
    a: "ARQYV starts a lightweight HTTP server (stdlib-only, no external deps) bound to your local IP. It generates a one-time token and encodes the share URL as a QR code. Scan it from any device on the same network. The server auto-shuts down when the transfer completes or you close the dialog. Nothing ever goes through ARQYV's servers — there are none.",
  },
  {
    q: "What file formats does the media engine support?",
    a: "The format detector recognises 40+ formats via magic bytes (MP4, MKV, AVI, MOV, WebM, MP3, FLAC, WAV, AAC, OGG, OPUS, M4A, WMA, and many more). Actual playback coverage depends on which backend is active: Qt Multimedia covers all common formats; VLC (if installed) covers virtually everything including exotic containers and legacy codecs.",
  },
  {
    q: "Can I use ARQYV with Google Drive / OneDrive / Dropbox?",
    a: "Yes. Cloud providers are integrated via OAuth2. ARQYV never stores your credentials — it uses each provider's official SDK. The cloud sync feature is off by default; enable it in Settings or via ARQYV_ENABLE_CLOUD_SYNC=true.",
  },
  {
    q: "Is there a mobile app?",
    a: "A Flutter mobile scaffold is included in the repo. It connects to the local API server (localhost:8765) that ARQYV starts automatically alongside the desktop app. A full mobile client is on the roadmap.",
  },
  {
    q: "What Python version do I need to run from source?",
    a: "Python 3.11 or newer. ARQYV is tested in CI on Python 3.11, 3.12, and 3.13 across Windows, macOS, and Linux. The pre-built binaries require no Python at all.",
  },
  {
    q: "How do I report a bug or request a feature?",
    a: "Open an issue on GitHub: github.com/ALaustrup/arqyv/issues. PRs are welcome — the codebase is modular and every component has a clear interface.",
  },
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-14">
          <p className="text-sm font-medium text-[#00b4d8] uppercase tracking-widest mb-4">FAQ</p>
          <h2 className="text-4xl md:text-5xl font-bold text-[#e0e0e0] mb-5">Common questions</h2>
        </div>

        <div className="space-y-3">
          {FAQS.map((faq, i) => (
            <div
              key={i}
              className={`rounded-2xl border transition-all ${
                open === i
                  ? "bg-[#16213e] border-[#00b4d8]/30"
                  : "bg-[#16213e]/50 border-[#2a2a4a] hover:border-[#2a2a4a]"
              }`}
            >
              <button
                className="w-full flex items-center justify-between gap-4 px-6 py-5 text-left"
                onClick={() => setOpen(open === i ? null : i)}
              >
                <span className={`text-sm font-medium ${open === i ? "text-[#e0e0e0]" : "text-[#9e9e9e]"}`}>
                  {faq.q}
                </span>
                <ChevronDown
                  size={16}
                  className={`shrink-0 text-[#9e9e9e] transition-transform ${open === i ? "rotate-180 text-[#00b4d8]" : ""}`}
                />
              </button>
              {open === i && (
                <div className="px-6 pb-5 text-sm text-[#9e9e9e] leading-relaxed border-t border-[#2a2a4a] pt-4">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
