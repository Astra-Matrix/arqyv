"use client";

const TOKENS = [
  { token: "type:",  example: "type:video",    desc: "Filter by media type",   values: "video · audio · image · document" },
  { token: "ext:",   example: "ext:.flac",     desc: "Exact file extension",   values: ".mp4 · .mkv · .flac · .pdf …" },
  { token: "size:",  example: "size:>50mb",    desc: "File size comparison",   values: ">500mb · <1gb · 10mb" },
  { token: "date:",  example: "date:>2024-01", desc: "Modification date",      values: ">2024 · <2023-06 · 2024-01-15" },
  { token: "tag:",   example: "tag:vacation",  desc: "AI-generated tag",       values: "any AI-extracted keyword" },
];

const EXAMPLES = [
  "beach sunset type:video date:>2024",
  "holiday portrait type:image tag:family",
  "interview ext:.mp4 date:>2023-06",
  "meeting notes type:document size:<10mb",
  "lo-fi chill music ext:.flac",
  "type:video size:>1gb",
];

export default function SearchSyntax() {
  return (
    <section className="section-sm relative">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">

          {/* Left */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-6"
                 style={{ background: "rgba(0,210,255,0.06)", border: "1px solid rgba(0,210,255,0.12)" }}>
              Search syntax
            </div>
            <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-5">
              Search like<br />
              <span className="text-white/25">you think.</span>
            </h2>
            <p className="text-white/40 text-lg leading-relaxed mb-10">
              Type natural language and combine with precise filter tokens.
              ARQYV understands meaning, not just filenames.
            </p>

            {/* Token table */}
            <div className="space-y-2">
              {TOKENS.map((t) => (
                <div key={t.token}
                     className="flex items-start gap-4 px-4 py-3 rounded-xl transition-colors hover:bg-white/[0.02]"
                     style={{ border: "1px solid rgba(255,255,255,0.04)" }}>
                  <code className="text-[#00d2ff] font-mono text-sm shrink-0 w-28">{t.example}</code>
                  <div>
                    <div className="text-sm text-white/60">{t.desc}</div>
                    <div className="text-[10px] text-white/20 font-mono mt-0.5">{t.values}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: example queries */}
          <div className="space-y-3">
            <div className="text-xs font-semibold text-white/20 uppercase tracking-widest mb-4">
              Example queries
            </div>
            {EXAMPLES.map((q) => (
              <div key={q}
                   className="group px-4 py-3 rounded-xl font-mono text-sm transition-all cursor-default"
                   style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)" }}
                   onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "rgba(0,210,255,0.15)"; }}
                   onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.04)"; }}>
                {q.split(" ").map((word, i) => (
                  <span key={i}>
                    {i > 0 && " "}
                    {word.includes(":") ? (
                      <span className="text-[#00d2ff]">{word}</span>
                    ) : (
                      <span className="text-white/50">{word}</span>
                    )}
                  </span>
                ))}
              </div>
            ))}

            {/* Live query box */}
            <div className="mt-8 p-5 rounded-2xl"
                 style={{ background: "rgba(0,210,255,0.03)", border: "1px solid rgba(0,210,255,0.1)" }}>
              <div className="text-xs text-white/20 uppercase tracking-widest mb-3">Try it in the app</div>
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg font-mono text-sm"
                   style={{ background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.06)" }}>
                <span className="text-white/20">›</span>
                <span className="text-[#00d2ff]">beach vacation <span className="text-white/25">type:video date:&gt;2023</span></span>
                <span className="ml-auto w-[2px] h-4 bg-[#00d2ff] animate-pulse rounded-full" />
              </div>
              <p className="text-xs text-white/25 mt-3">
                Or press the mic button to speak your query — Whisper transcribes it locally.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
