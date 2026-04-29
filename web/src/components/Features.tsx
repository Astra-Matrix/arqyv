const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-6"
       style={{ background: "rgba(0,210,255,0.06)", border: "1px solid rgba(0,210,255,0.12)" }}>
    {children}
  </div>
);

export default function Features() {
  return (
    <section id="features" className="section relative">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-20">
          <SectionLabel>Built different</SectionLabel>
          <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-5">
            Everything you need.<br />
            <span className="text-white/30">Nothing you don&apos;t.</span>
          </h2>
          <p className="text-white/40 text-lg max-w-lg mx-auto">
            Every component is purpose-built — the media engine, the search
            stack, the sharing system. All run offline. Forever.
          </p>
        </div>

        {/* Bento grid */}
        <div className="grid grid-cols-12 grid-rows-auto gap-4">

          {/* ── Card 1: Media Engine (large, spans 7 cols) */}
          <div className="bento col-span-12 md:col-span-7 p-8 relative overflow-hidden">
            {/* Background glow */}
            <div className="absolute -right-20 -top-20 w-80 h-80 rounded-full opacity-10 blur-3xl"
                 style={{ background: "radial-gradient(circle, #00d2ff, transparent)" }} />
            <div className="relative">
              <div className="w-10 h-10 rounded-xl mb-5 flex items-center justify-center text-xl"
                   style={{ background: "rgba(0,210,255,0.1)", border: "1px solid rgba(0,210,255,0.15)" }}>
                ▶
              </div>
              <div className="text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-2">
                ARQYVMediaEngine
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Custom media engine.<br />Zero dependencies.
              </h3>
              <p className="text-white/40 text-sm leading-relaxed max-w-sm">
                Magic-byte format detection for 40+ formats. Pure-Python subtitle
                engine (SRT/VTT/ASS). Smart resume. Audio DSP with EQ presets.
                Qt Multimedia primary — VLC auto-detected as an upgrade.
              </p>
              {/* Mini format badge strip */}
              <div className="flex flex-wrap gap-2 mt-6">
                {["MP4","MKV","AVI","FLAC","MP3","WebM","AAC","OGG","M4V","WAV","MOV","+30"].map((f) => (
                  <span key={f} className="text-[10px] font-mono px-2 py-1 rounded-md text-white/40"
                        style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}>
                    {f}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* ── Card 2: AI (tall, spans 5 cols) */}
          <div className="bento col-span-12 md:col-span-5 p-8 relative overflow-hidden">
            <div className="absolute -left-10 -bottom-10 w-60 h-60 rounded-full opacity-10 blur-3xl"
                 style={{ background: "radial-gradient(circle, #7c3aed, transparent)" }} />
            <div className="relative">
              <div className="w-10 h-10 rounded-xl mb-5 flex items-center justify-center text-xl"
                   style={{ background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.15)" }}>
                🧠
              </div>
              <div className="text-[11px] font-semibold uppercase tracking-widest text-purple-400 mb-2">
                On-device AI
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Understands every file.
              </h3>
              <p className="text-white/40 text-sm leading-relaxed">
                Whisper transcription, BLIP image captioning,
                sentence-transformers embeddings, spaCy NLP tagging.
                No API keys. No internet. All local.
              </p>
              {/* AI pipeline visual */}
              <div className="mt-6 space-y-2">
                {[
                  { label: "Whisper",               sub: "Audio & video transcription", color: "#7c3aed" },
                  { label: "BLIP",                  sub: "Image captioning",           color: "#9333ea" },
                  { label: "sentence-transformers", sub: "Semantic embeddings",         color: "#a855f7" },
                  { label: "spaCy NLP",             sub: "Entity & keyword tags",      color: "#c084fc" },
                ].map((m) => (
                  <div key={m.label} className="flex items-center gap-3 px-3 py-2 rounded-lg"
                       style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)" }}>
                    <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: m.color }} />
                    <div>
                      <div className="text-xs font-semibold text-white/80 font-mono">{m.label}</div>
                      <div className="text-[10px] text-white/25">{m.sub}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── Card 3: P2P Sharing (spans 5 cols) */}
          <div className="bento col-span-12 md:col-span-5 p-8 relative overflow-hidden">
            <div className="absolute -right-10 -top-10 w-60 h-60 rounded-full opacity-10 blur-3xl"
                 style={{ background: "radial-gradient(circle, #00d2ff, transparent)" }} />
            <div className="relative">
              <div className="w-10 h-10 rounded-xl mb-5 flex items-center justify-center text-xl"
                   style={{ background: "rgba(0,210,255,0.1)", border: "1px solid rgba(0,210,255,0.15)" }}>
                ⬆
              </div>
              <div className="text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-2">
                ARQYVShare
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Share in seconds.<br />
                <span className="text-white/30">No accounts.</span>
              </h3>
              <p className="text-white/40 text-sm leading-relaxed">
                Select a file. Click share. A QR code appears.
                Scan it on any device — download starts instantly.
                mDNS discovers ARQYV peers on your LAN automatically.
              </p>
              {/* QR mockup */}
              <div className="mt-6 flex items-center gap-4">
                <div className="w-16 h-16 rounded-xl grid grid-cols-4 grid-rows-4 gap-0.5 p-1.5 shrink-0"
                     style={{ background: "rgba(0,210,255,0.08)", border: "1px solid rgba(0,210,255,0.15)" }}>
                  {Array.from({ length: 16 }).map((_, i) => (
                    <div key={i} className="rounded-sm"
                         style={{ background: [0,1,4,5,8,10,11,13,14,15].includes(i) ? "rgba(0,210,255,0.8)" : "transparent" }} />
                  ))}
                </div>
                <div className="text-sm">
                  <div className="text-white/70 font-medium mb-1">Scan to download</div>
                  <div className="text-xs text-white/25">LAN only · token auth · auto-expires</div>
                </div>
              </div>
            </div>
          </div>

          {/* ── Card 4: Semantic Search (spans 4 cols) */}
          <div className="bento col-span-12 md:col-span-4 p-7 relative">
            <div className="w-9 h-9 rounded-xl mb-4 flex items-center justify-center text-lg"
                 style={{ background: "rgba(0,210,255,0.08)", border: "1px solid rgba(0,210,255,0.1)" }}>
              🔍
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Semantic Search</h3>
            <p className="text-white/40 text-sm leading-relaxed mb-5">
              ChromaDB vector store. Search by meaning, not filename.
              Filter with <code className="text-[#00d2ff]">type:</code> <code className="text-[#00d2ff]">date:</code> <code className="text-[#00d2ff]">tag:</code> tokens.
            </p>
            <div className="px-3 py-2 rounded-lg font-mono text-xs text-[#00d2ff]"
                 style={{ background: "rgba(0,210,255,0.05)", border: "1px solid rgba(0,210,255,0.1)" }}>
              beach vacation <span className="text-white/40">type:video date:&gt;2024</span>
            </div>
          </div>

          {/* ── Card 5: Voice Search (spans 3 cols) */}
          <div className="bento col-span-12 md:col-span-3 p-7 relative overflow-hidden">
            <div className="absolute right-4 bottom-4 text-6xl opacity-[0.04]">🎙</div>
            <div className="w-9 h-9 rounded-xl mb-4 flex items-center justify-center text-lg"
                 style={{ background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.15)" }}>
              🎙
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Voice Search</h3>
            <p className="text-white/40 text-sm leading-relaxed">
              Speak your query. Whisper transcribes locally. No mic permissions sent anywhere.
            </p>
          </div>

          {/* ── Card 6: Cloud Sync (spans 3 cols) */}
          <div className="bento col-span-12 md:col-span-3 p-7 relative overflow-hidden">
            <div className="w-9 h-9 rounded-xl mb-4 flex items-center justify-center text-lg"
                 style={{ background: "rgba(0,210,255,0.08)", border: "1px solid rgba(0,210,255,0.1)" }}>
              ☁
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Cloud Sync</h3>
            <p className="text-white/40 text-sm leading-relaxed mb-4">
              Google Drive, OneDrive, Dropbox via OAuth2. No data sent to ARQYV.
            </p>
            <div className="flex gap-2 text-xs text-white/30">
              {["Drive","OneDrive","Dropbox"].map((c) => (
                <span key={c} className="px-2 py-1 rounded-md"
                      style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)" }}>
                  {c}
                </span>
              ))}
            </div>
          </div>

          {/* ── Card 7: Local-first principle (spans 3 cols) */}
          <div className="bento col-span-12 md:col-span-3 p-7 relative overflow-hidden"
               style={{ background: "linear-gradient(135deg, #0a0a12, #0f0f20)" }}>
            <div className="absolute inset-0 opacity-[0.015]"
                 style={{ backgroundImage: "radial-gradient(#fff 1px, transparent 1px)", backgroundSize: "20px 20px" }} />
            <div className="relative">
              <div className="w-9 h-9 rounded-xl mb-4 flex items-center justify-center text-lg"
                   style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.07)" }}>
                🔒
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Local-first</h3>
              <p className="text-white/40 text-sm leading-relaxed">
                No accounts. No telemetry. No cloud dependency.
                Every byte stays on your machine.
              </p>
            </div>
          </div>

          {/* ── Card 8: Smart Metadata (spans 6 cols) */}
          <div className="bento col-span-12 md:col-span-6 p-7 flex items-start gap-6">
            <div>
              <div className="w-9 h-9 rounded-xl mb-4 flex items-center justify-center text-lg"
                   style={{ background: "rgba(0,210,255,0.08)", border: "1px solid rgba(0,210,255,0.1)" }}>
                📋
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Smart Metadata</h3>
              <p className="text-white/40 text-sm leading-relaxed">
                mutagen, EXIF, MediaInfo, PyMuPDF, spaCy — every technical
                and semantic detail auto-extracted from every format.
              </p>
            </div>
            <div className="shrink-0 hidden sm:block">
              <div className="space-y-1.5 mt-8">
                {[
                  ["Resolution", "3840 × 2160"],
                  ["Duration",   "4:37"],
                  ["Codec",      "H.264"],
                  ["FPS",        "60"],
                  ["AI caption", "Beach sunset…"],
                ].map(([k, v]) => (
                  <div key={k} className="flex items-center gap-3 text-[10px]">
                    <span className="text-white/25 w-16 text-right">{k}</span>
                    <span className="text-white/60 font-mono">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── Card 9: Batch Rename + Resume (spans 6 cols) */}
          <div className="bento col-span-12 md:col-span-6 p-7">
            <div className="w-9 h-9 rounded-xl mb-4 flex items-center justify-center text-lg"
                 style={{ background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.15)" }}>
              ✦
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Batch Rename + Smart Resume</h3>
            <p className="text-white/40 text-sm leading-relaxed mb-5">
              Template engine with <code className="text-purple-400">{"{name}"}</code> <code className="text-purple-400">{"{date}"}</code> <code className="text-purple-400">{"{ai_tag}"}</code> tokens.
              Every video remembers exactly where you left off.
            </p>
            <div className="font-mono text-xs px-3 py-2 rounded-lg text-purple-300"
                 style={{ background: "rgba(124,58,237,0.05)", border: "1px solid rgba(124,58,237,0.1)" }}>
              {"{date}"}_{"{ai_tag}"}_{"{name}"}.mp4
              <span className="text-white/25 ml-3">→ 2024_beach_sunset.mp4</span>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
