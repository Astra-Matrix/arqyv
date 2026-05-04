"use client";

import { useState } from "react";
import { useInView } from "@/hooks/useInView";
import { ChevronDown } from "lucide-react";

const ITEMS = [
  {
    q: "Does ARQYV send any data to the internet?",
    a: "No. ARQYV is entirely local. AI models run on your machine. No telemetry, no analytics, no cloud dependency of any kind. The only network traffic is LAN-based file sharing — and that's initiated by you.",
  },
  {
    q: "Do I need a GPU for AI features?",
    a: "No. ARQYV's AI pipeline runs on CPU by default and is fully usable that way. A GPU (CUDA or Apple MPS) makes AI analysis 5–20× faster but is entirely optional. Set ARQYV_AI_DEVICE=cuda or mps to enable it.",
  },
  {
    q: "What happens if I don't install the AI packages?",
    a: "ARQYV continues working perfectly as a media organizer, player, and LAN sharing tool. Live search still works (SQLite full-text fallback). Only semantic search and AI tagging are disabled. Install them anytime to unlock these features.",
  },
  {
    q: "How does P2P sharing work?",
    a: "When you share a file, ARQYV starts a temporary HTTP server on a random port. mDNS/Zeroconf broadcasts it to other ARQYV instances on the same LAN. Non-ARQYV devices can download via the QR-encoded URL. The server closes when you dismiss the share dialog.",
  },
  {
    q: "Can I use ARQYV with a NAS or external drive?",
    a: "Yes. Add any mounted path as a watched folder — including network shares (SMB/NFS), external drives, or cloud-sync folders. ARQYV monitors them for changes automatically.",
  },
  {
    q: "Is there a mobile app?",
    a: "A Flutter mobile companion app is planned for Phase 3. In the meantime, the local FastAPI server on port 8765 allows any device on your network to browse and stream your library via browser.",
  },
  {
    q: "How do I extend ARQYV with custom functionality?",
    a: "ARQYV has a plugin system based on Python entry-points. Create a package that subclasses MetadataPlugin, TaggerPlugin, or PostProcessPlugin, register it, and pip install it. ARQYV discovers it automatically at launch.",
  },
  {
    q: "Is ARQYV free? Will it stay free?",
    a: "ARQYV is MIT-licensed and completely free. There is no paid tier, no freemium model, and no plans to change that. It's a personal project open to community contributions.",
  },
];

export default function FAQ() {
  const { ref, inView } = useInView<HTMLDivElement>({ threshold: 0.05 });
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section id="faq" className="section relative" ref={ref}>
      <div className="max-w-3xl mx-auto">

        <div className={`text-center mb-16 reveal ${inView ? "in-view" : ""}`}>
          <div className="label-pill inline-flex">FAQ</div>
          <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-5">
            Common questions.
          </h2>
        </div>

        <div className="space-y-2">
          {ITEMS.map((item, i) => (
            <div
              key={i}
              className={`reveal ${inView ? "in-view" : ""} rounded-2xl overflow-hidden transition-colors`}
              style={{
                transitionDelay: `${i * 0.04}s`,
                background: open === i ? "rgba(0,210,255,0.03)" : "rgba(255,255,255,0.018)",
                border: `1px solid ${open === i ? "rgba(0,210,255,0.15)" : "rgba(255,255,255,0.055)"}`,
              }}
            >
              <button
                className="w-full flex items-center justify-between text-left px-6 py-5 gap-4"
                onClick={() => setOpen(open === i ? null : i)}
              >
                <span className={`font-semibold text-sm md:text-base leading-snug transition-colors ${
                  open === i ? "text-white" : "text-white/70"
                }`}>
                  {item.q}
                </span>
                <ChevronDown
                  size={16}
                  className={`shrink-0 text-white/30 transition-transform duration-300 ${
                    open === i ? "rotate-180 text-[#00d2ff]" : ""
                  }`}
                />
              </button>
              <div
                className="overflow-hidden transition-all duration-300 ease-in-out"
                style={{ maxHeight: open === i ? "400px" : "0" }}
              >
                <div className="px-6 pb-6 text-sm text-white/40 leading-relaxed">
                  {item.a}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
