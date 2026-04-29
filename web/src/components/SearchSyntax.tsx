const TOKENS = [
  { token: "type:", example: "type:video", desc: "Filter by media type group", values: "video · audio · image · document" },
  { token: "ext:", example: "ext:.flac", desc: "Exact file extension match", values: ".mp4 · .mkv · .flac · .pdf …" },
  { token: "size:", example: "size:>50mb", desc: "File size comparison", values: ">500mb · <1gb · 10mb" },
  { token: "date:", example: "date:>2024-01", desc: "Modification date filter", values: ">2024 · <2023-06 · 2024-01-15" },
  { token: "tag:", example: "tag:vacation", desc: "AI-generated tag contains", values: "any AI-extracted keyword" },
];

const EXAMPLES = [
  { query: "beach sunset type:video date:>2024", note: "Semantic search + type + date" },
  { query: "holiday portrait type:image tag:family", note: "Semantic + type + AI tag" },
  { query: "interview ext:.mp4 date:>2023-06", note: "Extension + date range" },
  { query: "meeting notes type:document size:<10mb", note: "Document search with size cap" },
  { query: "lo-fi chill music ext:.flac", note: "Semantic audio search" },
  { query: "type:video size:>1gb", note: "Find all large videos" },
];

export default function SearchSyntax() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-sm font-medium text-[#00b4d8] uppercase tracking-widest mb-4">
            Intelligent search
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-[#e0e0e0] mb-5">
            Search like you think.
          </h2>
          <p className="text-[#9e9e9e] text-lg max-w-2xl mx-auto">
            Type natural language queries and combine them with precise filter
            tokens. ARQYV understands meaning, not just filenames.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* Token table */}
          <div>
            <h3 className="text-sm font-semibold text-[#e0e0e0] uppercase tracking-widest mb-5">
              Filter Tokens
            </h3>
            <div className="space-y-3">
              {TOKENS.map((t) => (
                <div
                  key={t.token}
                  className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-4 hover:border-[#00b4d8]/30 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <code className="text-[#00b4d8] font-mono text-sm bg-[#00b4d8]/10 px-2 py-0.5 rounded">
                        {t.example}
                      </code>
                      <p className="text-[#9e9e9e] text-sm mt-2">{t.desc}</p>
                    </div>
                    <div className="shrink-0 text-right">
                      <span className="font-mono text-xs text-[#2a2a4a] bg-[#0f3460] rounded px-2 py-1">
                        {t.token}*
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-[#9e9e9e]/60 mt-2 font-mono">{t.values}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Example queries */}
          <div>
            <h3 className="text-sm font-semibold text-[#e0e0e0] uppercase tracking-widest mb-5">
              Example Queries
            </h3>
            <div className="space-y-3">
              {EXAMPLES.map((e) => (
                <div
                  key={e.query}
                  className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-4 group hover:border-[#00b4d8]/30 transition-colors"
                >
                  <div className="font-mono text-sm text-[#e0e0e0] group-hover:text-[#00b4d8] transition-colors">
                    {e.query.split(" ").map((word, i) => {
                      const isToken = word.includes(":");
                      return (
                        <span key={i}>
                          {i > 0 && " "}
                          {isToken ? (
                            <span className="text-[#00b4d8]">{word}</span>
                          ) : (
                            <span className="text-[#e0e0e0]">{word}</span>
                          )}
                        </span>
                      );
                    })}
                  </div>
                  <p className="text-xs text-[#9e9e9e] mt-2">{e.note}</p>
                </div>
              ))}
            </div>

            {/* Search box demo */}
            <div className="mt-6 bg-[#0f3460]/40 border border-[#00b4d8]/20 rounded-xl p-4">
              <p className="text-xs text-[#9e9e9e] mb-3 uppercase tracking-widest">Try it in the app</p>
              <div className="bg-[#1a1a2e] border border-[#2a2a4a] rounded-lg px-4 py-3 flex items-center gap-3">
                <span className="text-[#9e9e9e] text-sm">🔍</span>
                <span className="font-mono text-sm text-[#00b4d8] flex-1">
                  beach vacation type:video date:&gt;2023
                </span>
                <span className="text-[10px] text-[#9e9e9e] whitespace-nowrap">↵ Enter</span>
              </div>
              <p className="text-xs text-[#9e9e9e] mt-2">
                Or press the mic button to speak your query — Whisper transcribes it locally.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
