"use client";

import { useInView } from "@/hooks/useInView";

function Card({ children, className = "", style = {} }: {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <div
      className={`bento p-7 relative overflow-hidden ${className}`}
      style={style}
    >
      {children}
    </div>
  );
}

function Icon({ emoji, color }: { emoji: string; color: string }) {
  return (
    <div
      className="w-10 h-10 rounded-xl mb-5 flex items-center justify-center text-xl"
      style={{ background: `${color}14`, border: `1px solid ${color}20` }}
    >
      {emoji}
    </div>
  );
}

function Tag({ label, color = "#00d2ff" }: { label: string; color?: string }) {
  return (
    <span
      className="text-[10px] font-mono px-2 py-1 rounded-md"
      style={{ background: `${color}0a`, border: `1px solid ${color}15`, color: `${color}aa` }}
    >
      {label}
    </span>
  );
}

export default function Features() {
  const { ref, inView } = useInView<HTMLDivElement>({ threshold: 0.05 });

  return (
    <section id="features" className="section relative" ref={ref}>
      <div className="max-w-6xl mx-auto">

        <div className={`text-center mb-20 reveal ${inView ? "in-view" : ""}`}>
          <div className="label-pill inline-flex">Built different</div>
          <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-5 leading-tight">
            Everything you need.<br />
            <span className="text-white/22">Nothing you don&apos;t.</span>
          </h2>
          <p className="text-white/40 text-lg max-w-lg mx-auto">
            Every component is purpose-built — media engine, search stack, sharing system.
            All offline. All yours.
          </p>
        </div>

        <div className="grid grid-cols-12 gap-4">

          {/* Media Engine — large */}
          <div className={`col-span-12 md:col-span-7 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.05s" }}>
            <Card>
              <div className="absolute -right-16 -top-16 w-72 h-72 rounded-full opacity-8 blur-3xl"
                   style={{ background: "radial-gradient(circle, #00d2ff, transparent)" }} />
              <Icon emoji="▶" color="#00d2ff" />
              <div className="text-[10px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-2">
                ARQYVMediaEngine
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Custom media engine.<br />Zero dependencies.
              </h3>
              <p className="text-white/35 text-sm leading-relaxed max-w-sm mb-5">
                Magic-byte format detection for 40+ formats. Pure-Python subtitle engine
                (SRT / VTT / ASS). Smart playback resume. Audio DSP with EQ presets.
                Qt Multimedia primary — VLC auto-detected as an upgrade.
              </p>
              <div className="flex flex-wrap gap-2">
                {["MP4","MKV","AVI","FLAC","MP3","WebM","AAC","OGG","M4V","WAV","MOV","+30 more"].map((f) => (
                  <Tag key={f} label={f} />
                ))}
              </div>
            </Card>
          </div>

          {/* On-device AI */}
          <div className={`col-span-12 md:col-span-5 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.1s" }}>
            <Card>
              <div className="absolute -left-10 -bottom-10 w-56 h-56 rounded-full opacity-8 blur-3xl"
                   style={{ background: "radial-gradient(circle, #7c3aed, transparent)" }} />
              <Icon emoji="🧠" color="#7c3aed" />
              <div className="text-[10px] font-semibold uppercase tracking-widest text-purple-400 mb-2">
                On-device AI
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Understands every file.</h3>
              <p className="text-white/35 text-sm leading-relaxed mb-5">
                Whisper transcription. BLIP image captions. Sentence-transformer embeddings.
                spaCy entity tagging. No API keys. No internet. All local.
              </p>
              <div className="space-y-2">
                {[
                  { label: "Whisper",               sub: "Audio & video transcription", color: "#7c3aed" },
                  { label: "BLIP",                  sub: "Image captioning",            color: "#9333ea" },
                  { label: "sentence-transformers", sub: "Semantic embeddings → Chroma",color: "#a855f7" },
                  { label: "spaCy NLP",             sub: "Entity & keyword tags",       color: "#c084fc" },
                ].map((m) => (
                  <div key={m.label} className="flex items-center gap-3 px-3 py-2 rounded-lg"
                       style={{ background: "rgba(255,255,255,0.018)", border: "1px solid rgba(255,255,255,0.04)" }}>
                    <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: m.color }} />
                    <div>
                      <div className="text-[11px] font-semibold text-white/75 font-mono">{m.label}</div>
                      <div className="text-[10px] text-white/25">{m.sub}</div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Three-tier Search */}
          <div className={`col-span-12 md:col-span-5 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.15s" }}>
            <Card>
              <Icon emoji="🔍" color="#00d2ff" />
              <div className="text-[10px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-2">
                3-tier search
              </div>
              <h3 className="text-xl font-bold text-white mb-3">
                Semantic · BM25 · Full-text.<br />
                <span className="text-white/30">Merged and ranked.</span>
              </h3>
              <p className="text-white/35 text-sm mb-5">
                ChromaDB vector similarity + rank-bm25 keyword precision + SQLite full-text — all three
                run in parallel, results deduplicated and ranked.
              </p>
              <div className="space-y-1.5">
                {[
                  { tier: "1", label: "Semantic",  desc: "Meaning, not keywords", color: "#00d2ff" },
                  { tier: "2", label: "BM25",       desc: "Keyword precision",     color: "#7c3aed" },
                  { tier: "3", label: "SQLite LIKE",desc: "Full-text fallback",    color: "#f97316" },
                ].map((t) => (
                  <div key={t.tier} className="flex items-center gap-3 text-[11px]">
                    <span className="w-4 h-4 rounded flex items-center justify-center text-[9px] font-bold shrink-0"
                          style={{ background: `${t.color}15`, color: t.color }}>
                      {t.tier}
                    </span>
                    <span className="font-mono text-white/60">{t.label}</span>
                    <span className="text-white/25">{t.desc}</span>
                  </div>
                ))}
              </div>
              <div className="mt-5 px-3 py-2 rounded-lg font-mono text-xs text-[#00d2ff]"
                   style={{ background: "rgba(0,210,255,0.04)", border: "1px solid rgba(0,210,255,0.1)" }}>
                beach vacation&nbsp;
                <span className="text-white/35">type:video date:&gt;2024</span>
              </div>
            </Card>
          </div>

          {/* P2P Sharing */}
          <div className={`col-span-12 md:col-span-4 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.2s" }}>
            <Card>
              <Icon emoji="⬆" color="#00d2ff" />
              <div className="text-[10px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-2">
                ARQYVShare
              </div>
              <h3 className="text-xl font-bold text-white mb-3">
                Share in seconds.<br />
                <span className="text-white/30">No accounts.</span>
              </h3>
              <p className="text-white/35 text-sm mb-5">
                Select a file. Click Share. A QR code appears — scan with any phone.
                mDNS discovers ARQYV peers on your LAN automatically.
              </p>
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl grid grid-cols-4 grid-rows-4 gap-0.5 p-1.5 shrink-0"
                     style={{ background: "rgba(0,210,255,0.07)", border: "1px solid rgba(0,210,255,0.14)" }}>
                  {Array.from({ length: 16 }).map((_, i) => (
                    <div key={i} className="rounded-sm"
                         style={{ background: [0,1,4,5,8,10,11,13,15].includes(i) ? "rgba(0,210,255,0.85)" : "transparent" }} />
                  ))}
                </div>
                <div className="text-sm">
                  <div className="text-white/65 font-medium mb-1 text-sm">Scan to download</div>
                  <div className="text-[10px] text-white/25">LAN only · auto-expires · streaming</div>
                </div>
              </div>
            </Card>
          </div>

          {/* Voice Search */}
          <div className={`col-span-12 md:col-span-3 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.22s" }}>
            <Card>
              <div className="absolute right-4 bottom-4 text-5xl opacity-[0.03]">🎙</div>
              <Icon emoji="🎙" color="#7c3aed" />
              <h3 className="text-lg font-bold text-white mb-2">Voice Search</h3>
              <p className="text-white/35 text-sm leading-relaxed">
                Speak your query. Whisper transcribes it locally.
                No microphone data leaves your machine.
              </p>
            </Card>
          </div>

          {/* Local-first */}
          <div className={`col-span-12 md:col-span-3 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.24s" }}>
            <Card style={{ background: "linear-gradient(135deg, #09091a, #0e0e22)" }}>
              <div className="absolute inset-0 dot-bg opacity-[0.4]" />
              <div className="relative">
                <Icon emoji="🔒" color="#ffffff" />
                <h3 className="text-lg font-bold text-white mb-2">Local-first</h3>
                <p className="text-white/35 text-sm leading-relaxed">
                  No accounts. No telemetry. No cloud dependency.
                  Every byte stays on your machine.
                </p>
              </div>
            </Card>
          </div>

          {/* Smart Collections + Dedup */}
          <div className={`col-span-12 md:col-span-6 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.26s" }}>
            <Card>
              <Icon emoji="✦" color="#7c3aed" />
              <h3 className="text-lg font-bold text-white mb-2">Smart Collections & Dedup</h3>
              <p className="text-white/35 text-sm leading-relaxed mb-4">
                Auto-collections by type, year, and AI tag clusters. SHA-256 exact dedup +
                perceptual hash near-dedup for images — with wasted-space report.
              </p>
              <div className="flex flex-wrap gap-2">
                {["By Type","By Year","By AI Tag","Exact Hash","pHash Images"].map((l) => (
                  <Tag key={l} label={l} color="#7c3aed" />
                ))}
              </div>
            </Card>
          </div>

          {/* Smart Metadata */}
          <div className={`col-span-12 md:col-span-6 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.28s" }}>
            <Card className="flex items-start gap-6">
              <div className="flex-1">
                <Icon emoji="📋" color="#00d2ff" />
                <h3 className="text-lg font-bold text-white mb-2">Deep Metadata</h3>
                <p className="text-white/35 text-sm leading-relaxed">
                  mutagen · EXIF · MediaInfo · PyMuPDF · spaCy — every technical
                  and semantic detail extracted from every format.
                </p>
              </div>
              <div className="shrink-0 hidden sm:block">
                <div className="space-y-1.5 mt-8">
                  {[
                    ["Resolution","3840×2160"],
                    ["Duration","4:37"],
                    ["Codec","H.264"],
                    ["AI caption","Beach sunset…"],
                    ["Tags","beach · sunset · 4K"],
                  ].map(([k,v]) => (
                    <div key={k} className="flex items-center gap-3 text-[10px]">
                      <span className="text-white/22 w-18 text-right">{k}</span>
                      <span className="text-white/55 font-mono">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>

          {/* Cloud Sync */}
          <div className={`col-span-12 md:col-span-4 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.3s" }}>
            <Card>
              <Icon emoji="☁" color="#00d2ff" />
              <h3 className="text-lg font-bold text-white mb-2">Cloud Sync</h3>
              <p className="text-white/35 text-sm leading-relaxed mb-4">
                Google Drive · OneDrive · Dropbox via OAuth2.
                No data ever sent to ARQYV.
              </p>
              <div className="flex gap-2">
                {["Drive","OneDrive","Dropbox"].map((c) => (
                  <Tag key={c} label={c} />
                ))}
              </div>
            </Card>
          </div>

          {/* Plugin system */}
          <div className={`col-span-12 md:col-span-4 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.32s" }}>
            <Card>
              <Icon emoji="🔌" color="#f97316" />
              <h3 className="text-lg font-bold text-white mb-2">Plugin System</h3>
              <p className="text-white/35 text-sm leading-relaxed mb-4">
                Drop in any Python package registered as an entry-point.
                MetadataPlugin · TaggerPlugin · PostProcessPlugin.
              </p>
              <div className="font-mono text-[11px] px-3 py-2 rounded-lg"
                   style={{ background: "rgba(249,115,22,0.05)", border: "1px solid rgba(249,115,22,0.1)" }}>
                <span className="text-orange-400/70">[project.entry-points.</span>
                <span className="text-orange-300">&quot;arqyv.plugins&quot;</span>
                <span className="text-orange-400/70">]</span>
              </div>
            </Card>
          </div>

          {/* REST API */}
          <div className={`col-span-12 md:col-span-4 reveal ${inView ? "in-view" : ""}`}
               style={{ transitionDelay: "0.34s" }}>
            <Card>
              <Icon emoji="⚡" color="#00d2ff" />
              <h3 className="text-lg font-bold text-white mb-2">Local REST API</h3>
              <p className="text-white/35 text-sm leading-relaxed mb-4">
                FastAPI on :8765. WebSocket real-time events. Full OpenAPI docs.
                Drive ARQYV from any script or Flutter mobile companion.
              </p>
              <div className="font-mono text-[11px] px-3 py-2 rounded-lg text-[#00d2ff]/70"
                   style={{ background: "rgba(0,210,255,0.04)", border: "1px solid rgba(0,210,255,0.08)" }}>
                GET /api/v1/search?q=beach+sunset
              </div>
            </Card>
          </div>

        </div>
      </div>
    </section>
  );
}
