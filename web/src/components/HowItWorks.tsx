"use client";

const STEPS = [
  { n: "01", title: "Open a folder",       desc: "Point ARQYV at any folder — local drive, external disk, or mounted cloud. Background indexer starts immediately, UI stays responsive." },
  { n: "02", title: "AI reads everything", desc: "Videos → Whisper transcription. Images → BLIP captioning. Documents → text extraction. spaCy extracts keywords and entities." },
  { n: "03", title: "Vectors stored locally", desc: "sentence-transformers embeds into 384-dim vectors. ChromaDB stores them. All semantic search runs offline in under 100ms." },
  { n: "04", title: "Search by meaning",   desc: "Type 'beach vacation type:video' and get results ranked by semantic relevance, not just filename. Natural language meets precise filters." },
  { n: "05", title: "Play anything",       desc: "Click a file. Magic-byte format detection, codec tier selection, subtitle auto-load, and position resume — all automatic." },
  { n: "06", title: "Share instantly",     desc: "Select a file, click Share. QR code appears. Scan from any device on the same network — download starts. No upload, no cloud." },
];

export default function HowItWorks() {
  return (
    <section className="section-sm relative">
      {/* Gradient divider */}
      <div className="absolute inset-x-0 top-0 h-px"
           style={{ background: "linear-gradient(to right, transparent, rgba(0,210,255,0.15), transparent)" }} />

      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">

          {/* Left: heading */}
          <div className="lg:sticky lg:top-32">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-6"
                 style={{ background: "rgba(0,210,255,0.06)", border: "1px solid rgba(0,210,255,0.12)" }}>
              The pipeline
            </div>
            <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white leading-tight mb-6">
              How ARQYV<br />
              <span className="text-white/25">works.</span>
            </h2>
            <p className="text-white/40 text-lg leading-relaxed">
              Every step happens locally, automatically, without you thinking about it.
            </p>
          </div>

          {/* Right: steps */}
          <div className="space-y-3">
            {STEPS.map((step) => (
              <div
                key={step.n}
                className="group flex gap-5 p-5 rounded-2xl transition-all hover:bg-white/[0.02] cursor-default"
                style={{ border: "1px solid transparent" }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor = "rgba(0,210,255,0.1)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor = "transparent";
                }}
              >
                <div
                  className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center font-mono text-xs font-bold text-[#00d2ff] mt-0.5 transition-all group-hover:scale-110"
                  style={{ background: "rgba(0,210,255,0.06)", border: "1px solid rgba(0,210,255,0.12)" }}
                >
                  {step.n}
                </div>
                <div>
                  <h3 className="font-semibold text-white/90 mb-1.5">{step.title}</h3>
                  <p className="text-white/35 text-sm leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Gradient divider */}
      <div className="absolute inset-x-0 bottom-0 h-px"
           style={{ background: "linear-gradient(to right, transparent, rgba(255,255,255,0.04), transparent)" }} />
    </section>
  );
}
