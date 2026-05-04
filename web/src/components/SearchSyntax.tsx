"use client";

import { useInView } from "@/hooks/useInView";

const TOKENS = [
  { token: "type:",  example: "type:video",       desc: "Filter by media type: video · audio · image · document" },
  { token: "ext:",   example: "ext:.flac",         desc: "Filter by file extension" },
  { token: "date:",  example: "date:>2024-01-01",  desc: "Modified date — supports >, <, >=, <=, = operators" },
  { token: "size:",  example: "size:>100mb",       desc: "File size with kb · mb · gb units" },
];

const EXAMPLES = [
  { query: "beach sunset type:video",        hits: "24 results — semantic + keyword" },
  { query: "interviews ext:.mp4 date:>2024", hits: "8 results — filtered by ext + date" },
  { query: "spiderman",                      hits: "AI tags, transcripts, filenames" },
  { query: "family photos",                  hits: "Semantic search → meaning match" },
  { query: ".flac size:>50mb",               hits: "High-quality audio, large files" },
  { query: "contract type:document",         hits: "PDF, DOCX, TXT files" },
];

export default function SearchSyntax() {
  const { ref, inView } = useInView<HTMLDivElement>({ threshold: 0.1 });

  return (
    <section id="docs" className="section-sm relative" ref={ref}>
      <div className="max-w-5xl mx-auto">

        <div className={`text-center mb-16 reveal ${inView ? "in-view" : ""}`}>
          <div className="label-pill inline-flex">Search Syntax</div>
          <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-5">
            Search the way<br />
            <span className="text-white/22">you think.</span>
          </h2>
          <p className="text-white/40 text-base max-w-sm mx-auto">
            Natural language. Filter tokens. Type qualifiers. Mix and match.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Filters */}
          <div className={`reveal ${inView ? "in-view" : ""}`} style={{ transitionDelay: "0.1s" }}>
            <h3 className="text-sm font-semibold uppercase tracking-widest text-white/30 mb-5">Filter tokens</h3>
            <div className="space-y-3">
              {TOKENS.map((t) => (
                <div key={t.token}
                     className="flex items-start gap-4 rounded-xl p-4"
                     style={{ background: "rgba(255,255,255,0.018)", border: "1px solid rgba(255,255,255,0.055)" }}>
                  <code className="text-[12px] font-mono text-[#00d2ff] shrink-0 w-12">{t.token}</code>
                  <div>
                    <code className="text-xs font-mono text-white/55">{t.example}</code>
                    <p className="text-xs text-white/30 mt-1">{t.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Example queries */}
          <div className={`reveal ${inView ? "in-view" : ""}`} style={{ transitionDelay: "0.15s" }}>
            <h3 className="text-sm font-semibold uppercase tracking-widest text-white/30 mb-5">Example queries</h3>
            <div className="space-y-2">
              {EXAMPLES.map((e) => (
                <div key={e.query}
                     className="rounded-xl px-4 py-3"
                     style={{ background: "rgba(255,255,255,0.018)", border: "1px solid rgba(255,255,255,0.04)" }}>
                  <code className="text-[12px] font-mono text-[#00d2ff]/80 block mb-1">{e.query}</code>
                  <span className="text-[10px] text-white/25">{e.hits}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Live search note */}
        <div className={`reveal ${inView ? "in-view" : ""} text-center rounded-2xl py-8 px-6`}
             style={{
               transitionDelay: "0.2s",
               background: "rgba(0,210,255,0.025)",
               border: "1px solid rgba(0,210,255,0.1)",
             }}>
          <p className="text-white/50 text-sm leading-relaxed max-w-xl mx-auto">
            <span className="text-white/80 font-semibold">Live search</span> — results appear within 150 ms as you type, powered
            by a background thread that queries the database and scans the filesystem in parallel.
            No Enter key required.
          </p>
        </div>
      </div>
    </section>
  );
}
