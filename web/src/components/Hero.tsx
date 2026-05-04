"use client";

import { useEffect, useState } from "react";
import { ArrowRight, Download } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { OSDownloadButton } from "./OSDownloadButton";

const GITHUB_URL = "https://github.com/Alaustrup/arqyv";

const TYPED_QUERIES = [
  "beach sunset type:video",
  "interview footage 2024",
  "my favourite songs",
  "spiderman movie",
  ".flac music collection",
  "family photos date:>2023",
  "client contract.pdf",
];

const STATS = [
  { value: "40+",   label: "Formats" },
  { value: "100%",  label: "Offline" },
  { value: "0",     label: "Accounts" },
  { value: "Free",  label: "Forever" },
];

function TypingText() {
  const [qi, setQi] = useState(0);
  const [chars, setChars] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const current = TYPED_QUERIES[qi];
    let timer: ReturnType<typeof setTimeout>;

    if (!deleting && chars < current.length) {
      timer = setTimeout(() => setChars((c) => c + 1), 55);
    } else if (!deleting && chars === current.length) {
      timer = setTimeout(() => setDeleting(true), 1600);
    } else if (deleting && chars > 0) {
      timer = setTimeout(() => setChars((c) => c - 1), 28);
    } else {
      setDeleting(false);
      setQi((i) => (i + 1) % TYPED_QUERIES.length);
    }
    return () => clearTimeout(timer);
  }, [chars, deleting, qi]);

  return (
    <span className="text-[#00d2ff]">
      {TYPED_QUERIES[qi].slice(0, chars)}
      <span className="cursor-blink ml-px inline-block w-[2px] h-[1em] bg-[#00d2ff] align-middle" />
    </span>
  );
}

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden pt-[60px]">

      {/* ── Background ── */}
      <div className="absolute inset-0 grid-bg" />
      <div className="absolute inset-0"
           style={{ background: "radial-gradient(ellipse 100% 60% at 50% -10%, rgba(0,210,255,0.055) 0%, transparent 70%)" }} />
      <div className="absolute top-[40%] left-[8%] w-[600px] h-[600px] rounded-full blur-[120px] opacity-[0.04]"
           style={{ background: "#7c3aed" }} />
      <div className="absolute top-[20%] right-[5%] w-[400px] h-[400px] rounded-full blur-[100px] opacity-[0.04]"
           style={{ background: "#00d2ff" }} />

      {/* ── Content ── */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 flex flex-col items-center text-center">

        {/* Badge */}
        <div className="animate-fade-up label-pill" style={{ animationDelay: "0s" }}>
          <span className="w-1.5 h-1.5 rounded-full bg-[#00d2ff] animate-pulse inline-block" />
          v0.1.0 · Open Source · Local AI
        </div>

        {/* Headline */}
        <h1
          className="animate-fade-up text-[clamp(2.8rem,8.5vw,6.5rem)] font-black leading-[0.92] tracking-[-0.03em] mb-6"
          style={{ animationDelay: "0.07s" }}
        >
          <span className="gradient-text-white block">Your files.</span>
          <span className="gradient-text block">Finally intelligent.</span>
        </h1>

        {/* Sub-headline */}
        <p
          className="animate-fade-up text-base md:text-xl text-white/40 max-w-[520px] leading-relaxed mb-10"
          style={{ animationDelay: "0.14s" }}
        >
          One desktop app that unifies every video, audio track, photo, and
          document into an AI-searchable library — with instant P2P sharing.
          No cloud. No accounts. Yours forever.
        </p>

        {/* Live search bar mockup */}
        <div
          className="animate-fade-up w-full max-w-lg mb-10 px-4 py-3 rounded-xl flex items-center gap-3 text-sm font-mono"
          style={{
            animationDelay: "0.18s",
            background: "rgba(0,210,255,0.04)",
            border: "1px solid rgba(0,210,255,0.12)",
          }}
        >
          <svg className="w-4 h-4 text-white/25 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" strokeWidth="2" />
            <path d="m21 21-4.35-4.35" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <TypingText />
        </div>

        {/* CTAs */}
        <div
          className="animate-fade-up flex flex-col sm:flex-row items-center gap-4 mb-14"
          style={{ animationDelay: "0.22s" }}
        >
          <OSDownloadButton size="lg" />
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2.5 text-sm text-white/45 hover:text-white/90 transition-colors px-6 py-3.5 rounded-xl border border-white/[0.07] hover:border-white/20 hover:bg-white/[0.025]"
          >
            <GitHubIcon size={15} />
            View on GitHub
            <ArrowRight size={13} className="opacity-40" />
          </a>
        </div>

        {/* Stats */}
        <div
          className="animate-fade-up w-full max-w-xl"
          style={{ animationDelay: "0.28s" }}
        >
          <div
            className="grid grid-cols-4 rounded-2xl overflow-hidden"
            style={{ background: "rgba(255,255,255,0.018)", border: "1px solid rgba(255,255,255,0.055)" }}
          >
            {STATS.map((s, i) => (
              <div
                key={s.label}
                className="py-5 px-4 text-center"
                style={i > 0 ? { borderLeft: "1px solid rgba(255,255,255,0.055)" } : {}}
              >
                <div className="text-2xl font-black text-white mb-0.5 tracking-tight">{s.value}</div>
                <div className="text-[10px] text-white/25 uppercase tracking-widest font-medium">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── App window mockup ── */}
      <div
        className="animate-fade-up relative z-10 mt-20 w-full max-w-5xl mx-auto px-6"
        style={{ animationDelay: "0.35s" }}
      >
        {/* Glow underneath */}
        <div className="absolute inset-x-16 -bottom-4 h-16 blur-3xl opacity-20"
             style={{ background: "linear-gradient(to top, #00d2ff, transparent)" }} />

        <div
          className="relative rounded-2xl overflow-hidden shadow-2xl"
          style={{
            border: "1px solid rgba(255,255,255,0.06)",
            background: "#08080f",
            boxShadow: "0 48px 128px rgba(0,0,0,0.9), 0 0 0 1px rgba(255,255,255,0.035)",
          }}
        >
          {/* Title bar */}
          <div className="flex items-center gap-2 px-4 py-3"
               style={{ background: "rgba(255,255,255,0.015)", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
            <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
            <div className="flex-1 flex justify-center">
              <div className="px-4 py-1 rounded-md text-xs font-mono text-white/18"
                   style={{ background: "rgba(255,255,255,0.025)", border: "1px solid rgba(255,255,255,0.04)" }}>
                ARQYV — beach sunset type:video&nbsp;&nbsp;
                <span className="animate-blink text-[#00d2ff]/80">|</span>
              </div>
            </div>
          </div>

          {/* App body */}
          <div className="flex h-[340px]">
            {/* Sidebar */}
            <div className="w-44 shrink-0 flex flex-col p-3 gap-0.5"
                 style={{ borderRight: "1px solid rgba(255,255,255,0.04)" }}>
              <div className="text-[9px] font-semibold text-white/18 uppercase tracking-widest px-2 pt-1 pb-2">Library</div>
              {[
                { icon: "▶", label: "Videos",    active: true,  count: "24" },
                { icon: "♫", label: "Music",     active: false, count: "138" },
                { icon: "⬛", label: "Photos",   active: false, count: "512" },
                { icon: "📄", label: "Documents", active: false, count: "89" },
                { icon: "☁", label: "Cloud",     active: false, count: "" },
              ].map((item) => (
                <div key={item.label}
                     className={`flex items-center justify-between px-2 py-1.5 rounded-lg text-[11px] ${
                       item.active ? "text-[#00d2ff] bg-[#00d2ff]/[0.07]" : "text-white/22"
                     }`}>
                  <span className="flex items-center gap-2">
                    <span className="text-[10px] w-3 text-center">{item.icon}</span>
                    {item.label}
                  </span>
                  {item.count && (
                    <span className={`text-[9px] ${item.active ? "text-[#00d2ff]/60" : "text-white/18"}`}>
                      {item.count}
                    </span>
                  )}
                </div>
              ))}

              <div className="mt-3 pt-3" style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
                <div className="text-[9px] font-semibold text-white/18 uppercase tracking-widest px-2 pb-2">Collections</div>
                {["Beach Trip","Concerts","Work"].map((c) => (
                  <div key={c} className="flex items-center gap-2 px-2 py-1.5 text-[10px] text-white/20 rounded-lg">
                    <span className="w-1 h-1 rounded-full bg-[#7c3aed]/60 shrink-0" />
                    {c}
                  </div>
                ))}
              </div>
            </div>

            {/* Main */}
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5"
                   style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                <div className="flex items-center gap-2 text-[10px] text-white/30">
                  <span className="text-[#00d2ff]">24 results</span>
                  <span>·</span>
                  <span>beach sunset type:video</span>
                </div>
                <div className="flex items-center gap-1.5 text-[9px] text-white/20">
                  <span className="px-2 py-0.5 rounded border border-white/[0.05]">Grid</span>
                  <span className="px-2 py-0.5 rounded border border-[#00d2ff]/20 text-[#00d2ff]/50">List</span>
                </div>
              </div>

              {/* Grid */}
              <div className="flex-1 p-3.5 grid grid-cols-5 gap-2 content-start overflow-hidden">
                {[
                  { label: "beach_4k.mp4",  bg: "linear-gradient(135deg,#0c3654,#00d2ff18)", ring: true },
                  { label: "sunset.mkv",    bg: "linear-gradient(135deg,#1a1a2e,#16213e)",   ring: false },
                  { label: "vacation.mp4",  bg: "linear-gradient(135deg,#1a1030,#2d1b69)",   ring: false },
                  { label: "waves.mp4",     bg: "linear-gradient(135deg,#0f2027,#203a43)",   ring: false },
                  { label: "travel.mkv",    bg: "linear-gradient(135deg,#1e2a1e,#2d4a2d)",   ring: false },
                  { label: "portrait.jpg",  bg: "linear-gradient(135deg,#2a1a14,#4a2a18)",   ring: false },
                  { label: "concert.mp4",   bg: "linear-gradient(135deg,#2a1a1a,#3a2020)",   ring: false },
                  { label: "podcast.mp3",   bg: "linear-gradient(135deg,#1a1a2e,#0f3460)",   ring: false },
                  { label: "report.pdf",    bg: "linear-gradient(135deg,#1a1a1a,#2a2a2a)",   ring: false },
                  { label: "timelapse.mp4", bg: "linear-gradient(135deg,#0d2137,#1a3a5c)",   ring: false },
                ].map((f, i) => (
                  <div key={i}
                       className={`aspect-video rounded-lg relative overflow-hidden flex flex-col justify-end p-1.5 ${
                         f.ring ? "ring-1 ring-[#00d2ff]/25" : ""
                       }`}
                       style={{ background: f.bg, border: "1px solid rgba(255,255,255,0.04)" }}>
                    {f.ring && <div className="absolute inset-0 bg-[#00d2ff]/[0.04]" />}
                    <span className="relative text-[7.5px] text-white/35 truncate">{f.label}</span>
                  </div>
                ))}
              </div>

              {/* Player bar */}
              <div className="flex items-center gap-3 px-4 py-2.5"
                   style={{ borderTop: "1px solid rgba(255,255,255,0.04)", background: "rgba(0,0,0,0.25)" }}>
                <div className="flex items-center gap-2 text-[#00d2ff]/80 text-xs">⏮ ▶ ⏭</div>
                <div className="font-mono text-[9px] text-white/22">1:24 / 4:37</div>
                <div className="flex-1 h-[2px] rounded-full bg-white/[0.06] overflow-hidden">
                  <div className="h-full w-[30%] rounded-full bg-[#00d2ff]" />
                </div>
                <div className="text-[9px] text-[#00d2ff]/55 font-mono">H.264 · 4K</div>
              </div>
            </div>

            {/* Metadata panel */}
            <div className="w-40 shrink-0 hidden lg:flex flex-col p-3.5 gap-2.5"
                 style={{ borderLeft: "1px solid rgba(255,255,255,0.04)" }}>
              <div className="text-[9px] text-white/18 uppercase tracking-widest font-semibold">AI Analysis</div>
              <div className="text-[10px] font-semibold text-[#00d2ff] truncate">beach_4k.mp4</div>
              <p className="text-[8.5px] text-white/28 leading-relaxed">
                Sunset beach timelapse with golden hour lighting, crashing waves, and silhouetted palm trees.
              </p>
              <div className="text-[9px] text-white/18 uppercase tracking-widest font-semibold mt-1">Tags</div>
              <div className="flex flex-wrap gap-1">
                {["beach","sunset","4K","golden hour","travel"].map((t) => (
                  <span key={t} className="text-[7.5px] px-1.5 py-0.5 rounded text-[#00d2ff]/70"
                        style={{ background: "rgba(0,210,255,0.07)", border: "1px solid rgba(0,210,255,0.12)" }}>
                    {t}
                  </span>
                ))}
              </div>
              <div className="mt-auto pt-2" style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
                <div className="flex flex-col gap-1">
                  {[["Codec","H.264"],["Res","3840×2160"],["FPS","60"]].map(([k,v])=>(
                    <div key={k} className="flex justify-between text-[8px]">
                      <span className="text-white/20">{k}</span>
                      <span className="text-white/40 font-mono">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom fade */}
      <div className="absolute bottom-0 inset-x-0 h-48 pointer-events-none"
           style={{ background: "linear-gradient(to top, #030305, transparent)" }} />
    </section>
  );
}
