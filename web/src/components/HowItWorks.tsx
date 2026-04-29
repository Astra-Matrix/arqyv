const STEPS = [
  {
    n: "01",
    title: "Open a Folder",
    desc: "Point ARQYV at any folder — local drive, external disk, or mounted cloud storage. The indexer scans in the background without blocking the UI.",
  },
  {
    n: "02",
    title: "AI Analyzes Every File",
    desc: "Videos → Whisper transcription. Images → BLIP captioning. Documents → text extraction. Audio → tag parsing. spaCy extracts keywords and entities.",
  },
  {
    n: "03",
    title: "Vectors Stored Locally",
    desc: "sentence-transformers embeds everything into 384-dimensional vectors. ChromaDB stores them locally. All semantic search runs offline, in milliseconds.",
  },
  {
    n: "04",
    title: "Search by Meaning",
    desc: "Type 'beach vacation type:video' and get results ranked by semantic relevance, not just filename. Combine natural language with filter tokens.",
  },
  {
    n: "05",
    title: "Play Anything",
    desc: "Click a file. ARQYVMediaEngine detects the format via magic bytes, loads the right codec tier, auto-loads subtitles, and resumes from last position.",
  },
  {
    n: "06",
    title: "Share in Seconds",
    desc: "Select a file, click Share. A QR code appears. Scan it on your phone — the download starts. No upload, no cloud, no account. Pure LAN.",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-24 px-6 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#16213e]/30 to-transparent pointer-events-none" />

      <div className="relative max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-sm font-medium text-[#00b4d8] uppercase tracking-widest mb-4">
            The pipeline
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-[#e0e0e0] mb-5">
            How ARQYV works
          </h2>
          <p className="text-[#9e9e9e] text-lg max-w-xl mx-auto">
            Every step happens locally, automatically, without you thinking about it.
          </p>
        </div>

        <div className="relative">
          {/* Connector line */}
          <div className="absolute left-[27px] top-10 bottom-10 w-px bg-gradient-to-b from-[#00b4d8]/60 via-[#00b4d8]/20 to-transparent hidden md:block" />

          <div className="space-y-6">
            {STEPS.map((step, i) => (
              <div key={step.n} className="flex gap-6 group">
                {/* Number badge */}
                <div className="relative shrink-0">
                  <div className="w-14 h-14 rounded-2xl bg-[#0f3460] border border-[#2a2a4a] group-hover:border-[#00b4d8]/50 flex items-center justify-center font-mono text-sm font-bold text-[#00b4d8] transition-colors group-hover:bg-[#00b4d8]/10 z-10 relative">
                    {step.n}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 bg-[#16213e] border border-[#2a2a4a] group-hover:border-[#00b4d8]/20 rounded-2xl p-5 transition-all">
                  <h3 className="font-semibold text-[#e0e0e0] mb-2">{step.title}</h3>
                  <p className="text-[#9e9e9e] text-sm leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
