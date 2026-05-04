"use client";

import { useInView } from "@/hooks/useInView";

const STEPS = [
  {
    n: "01",
    title: "Add a folder",
    desc: "Point ARQYV at any directory — your Downloads, a NAS, an external drive. The watcher stays active and picks up new files in real time.",
    accent: "#00d2ff",
    detail: "Supports recursive scanning of unlimited depth. Filters to 40+ supported extensions automatically.",
  },
  {
    n: "02",
    title: "ARQYV indexes & understands",
    desc: "Every file is analyzed: metadata extracted, thumbnails generated, AI tags and summaries computed. All off the main thread, never blocking the UI.",
    accent: "#7c3aed",
    detail: "Whisper transcripts audio/video. BLIP captions images. Sentence-transformers embeds text into ChromaDB.",
  },
  {
    n: "03",
    title: "Search anything, instantly",
    desc: "Type a word — or a sentence — and results appear before you finish. Semantic understanding, BM25 precision, and full-text search run in parallel.",
    accent: "#00d2ff",
    detail: "Filter with type:video, date:>2024, ext:.flac, size:>500mb. Combine freely.",
  },
  {
    n: "04",
    title: "Play, share, or organize",
    desc: "Play any file directly in the built-in engine. Share via QR code over LAN. Auto-collections group your files intelligently — no manual tagging.",
    accent: "#f97316",
    detail: "P2P share uses mDNS discovery. No servers. Files stream directly between devices.",
  },
];

export default function HowItWorks() {
  const { ref, inView } = useInView<HTMLDivElement>({ threshold: 0.05 });

  return (
    <section id="how" className="section relative" ref={ref}>
      <div className="max-w-5xl mx-auto">

        <div className={`text-center mb-20 reveal ${inView ? "in-view" : ""}`}>
          <div className="label-pill inline-flex">How it works</div>
          <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-5">
            Up and running<br />
            <span className="text-white/22">in four steps.</span>
          </h2>
        </div>

        <div className="relative">
          {/* Vertical connector line */}
          <div
            className="absolute left-[27px] top-12 bottom-12 w-px hidden md:block"
            style={{ background: "linear-gradient(to bottom, rgba(0,210,255,0.15), rgba(124,58,237,0.15), rgba(249,115,22,0.1))" }}
          />

          <div className="space-y-12">
            {STEPS.map((step, i) => {
              const delay = `${i * 0.1}s`;
              return (
                <div
                  key={step.n}
                  className={`reveal ${inView ? "in-view" : ""} flex gap-8 md:gap-12`}
                  style={{ transitionDelay: delay }}
                >
                  {/* Number circle */}
                  <div className="shrink-0 flex flex-col items-center gap-3 mt-1">
                    <div
                      className="w-14 h-14 rounded-full flex items-center justify-center text-sm font-black z-10"
                      style={{
                        background: `${step.accent}12`,
                        border: `1px solid ${step.accent}28`,
                        color: step.accent,
                      }}
                    >
                      {step.n}
                    </div>
                  </div>

                  {/* Content */}
                  <div
                    className="flex-1 rounded-2xl p-6 md:p-8 group hover:border-white/[0.1] transition-colors"
                    style={{ background: "rgba(255,255,255,0.018)", border: "1px solid rgba(255,255,255,0.055)" }}
                  >
                    <h3 className="text-xl md:text-2xl font-bold text-white mb-3">{step.title}</h3>
                    <p className="text-white/45 text-base leading-relaxed mb-4">{step.desc}</p>
                    <div
                      className="text-sm text-white/30 px-4 py-3 rounded-xl leading-relaxed"
                      style={{
                        background: `${step.accent}06`,
                        border: `1px solid ${step.accent}12`,
                        borderLeft: `3px solid ${step.accent}40`,
                      }}
                    >
                      {step.detail}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
