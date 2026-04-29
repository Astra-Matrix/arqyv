"use client";

import { useState } from "react";
import { Plus, Minus } from "lucide-react";

const FAQS = [
  {
    q: "Is ARQYV really free? No subscription?",
    a: "Completely free, forever. MIT licensed and open source. No ARQYV account, no cloud service, no telemetry. Build it yourself from source anytime.",
  },
  {
    q: "Do I need VLC or FFmpeg installed?",
    a: "No. ARQYV uses Qt Multimedia as the primary engine — platform-native codecs (Windows Media Foundation, AVFoundation, GStreamer). If you have VLC installed, ARQYV auto-detects it and upgrades to VLC's extended codec support (H.265, AV1, AC3, DTS…). Nothing to configure.",
  },
  {
    q: "Does AI analysis send my files to the cloud?",
    a: "Never. Every AI model runs locally: Whisper for transcription, BLIP for captioning, sentence-transformers for embeddings, spaCy for NLP. No API keys required. No internet needed for any AI feature.",
  },
  {
    q: "How does P2P sharing work?",
    a: "ARQYV starts a lightweight HTTP server bound to your local IP with a one-time token. The share URL is encoded as a QR code. Scan it on any device on the same network — download starts. The server auto-shuts down after transfer or when you close the dialog. Nothing goes through ARQYV servers — there are none.",
  },
  {
    q: "What file formats are supported?",
    a: "The format detector recognises 40+ formats via magic bytes. Actual playback depends on the active backend: Qt Multimedia covers all common formats; VLC (if installed) covers virtually everything including exotic containers and legacy codecs.",
  },
  {
    q: "Can I use ARQYV with cloud storage?",
    a: "Yes — Google Drive, OneDrive, and Dropbox via OAuth2. ARQYV never stores your credentials. Cloud sync is off by default; enable in Settings or set ARQYV_ENABLE_CLOUD_SYNC=true.",
  },
  {
    q: "Is there a mobile app?",
    a: "A Flutter mobile scaffold is included. It connects to the local API server (localhost:8765) that ARQYV starts automatically. A full mobile client is on the roadmap.",
  },
  {
    q: "How do I report a bug?",
    a: "Open an issue at github.com/ALaustrup/arqyv/issues. PRs are welcome — the codebase is modular with clear interfaces.",
  },
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section id="faq" className="section-sm">
      <div className="max-w-3xl mx-auto">

        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-6"
               style={{ background: "rgba(0,210,255,0.06)", border: "1px solid rgba(0,210,255,0.12)" }}>
            FAQ
          </div>
          <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white">
            Questions.
          </h2>
        </div>

        <div className="space-y-2">
          {FAQS.map((faq, i) => (
            <div
              key={i}
              className="rounded-2xl overflow-hidden transition-all"
              style={{
                background: open === i ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0.015)",
                border: open === i ? "1px solid rgba(0,210,255,0.15)" : "1px solid rgba(255,255,255,0.05)",
              }}
            >
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full flex items-center justify-between gap-4 px-6 py-5 text-left group"
              >
                <span className={`text-sm font-medium transition-colors ${open === i ? "text-white" : "text-white/50 group-hover:text-white/70"}`}>
                  {faq.q}
                </span>
                <div className={`shrink-0 w-5 h-5 rounded-full flex items-center justify-center transition-all ${
                  open === i ? "bg-[#00d2ff] text-black" : "bg-white/[0.06] text-white/30"
                }`}>
                  {open === i ? <Minus size={10} /> : <Plus size={10} />}
                </div>
              </button>
              {open === i && (
                <div className="px-6 pb-5 text-sm text-white/40 leading-relaxed"
                     style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
                  <div className="pt-4">{faq.a}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
