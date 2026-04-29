"use client";

import { ArrowRight } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { OSDownloadButton } from "./OSDownloadButton";

const GITHUB_URL = "https://github.com/ALaustrup/arqyv";

const STATS = [
  { value: "40+",    label: "File formats" },
  { value: "100%",   label: "Local & offline" },
  { value: "0",      label: "Accounts needed" },
  { value: "Free",   label: "Forever" },
];

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden pt-[60px]">

      {/* ── Background layer ── */}
      <div className="absolute inset-0 grid-bg opacity-100" />

      {/* Large glow orbs */}
      <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[900px] h-[600px] rounded-full"
           style={{ background: "radial-gradient(ellipse, rgba(0,210,255,0.07) 0%, transparent 70%)" }} />
      <div className="absolute top-[30%] left-[5%] w-[500px] h-[500px] rounded-full"
           style={{ background: "radial-gradient(ellipse, rgba(124,58,237,0.06) 0%, transparent 70%)" }} />
      <div className="absolute top-[20%] right-[5%] w-[400px] h-[400px] rounded-full"
           style={{ background: "radial-gradient(ellipse, rgba(0,210,255,0.05) 0%, transparent 70%)" }} />

      {/* ── Content ── */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 flex flex-col items-center text-center">

        {/* Badge */}
        <div
          className="animate-fade-up inline-flex items-center gap-2 mb-10 px-4 py-1.5 rounded-full text-xs font-medium tracking-widest uppercase"
          style={{
            background: "rgba(0,210,255,0.06)",
            border: "1px solid rgba(0,210,255,0.15)",
            color: "#00d2ff",
            animationDelay: "0s",
          }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#00d2ff] animate-pulse" />
          v0.1.0 · Now available · Open Source
        </div>

        {/* Headline */}
        <h1
          className="animate-fade-up text-[clamp(3rem,8vw,6rem)] font-black leading-[0.95] tracking-tight mb-8"
          style={{ animationDelay: "0.08s" }}
        >
          <span className="gradient-text-white block">Your files.</span>
          <span className="gradient-text block">Finally intelligent.</span>
        </h1>

        {/* Sub-headline */}
        <p
          className="animate-fade-up text-lg md:text-xl text-white/40 max-w-xl leading-relaxed mb-12"
          style={{ animationDelay: "0.16s" }}
        >
          ARQYV is a free desktop application that unifies every file you own
          into one AI-searchable library — with instant P2P sharing and a
          built-in media engine. No accounts. No cloud. Yours forever.
        </p>

        {/* CTAs */}
        <div
          className="animate-fade-up flex flex-col sm:flex-row items-center gap-4 mb-16"
          style={{ animationDelay: "0.24s" }}
        >
          <OSDownloadButton size="lg" />
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2.5 text-sm text-white/50 hover:text-white/90 transition-colors px-6 py-3.5 rounded-xl border border-white/[0.07] hover:border-white/20 hover:bg-white/[0.02]"
          >
            <GitHubIcon size={16} />
            View on GitHub
            <ArrowRight size={14} className="opacity-50" />
          </a>
        </div>

        {/* Stats strip */}
        <div
          className="animate-fade-up w-full max-w-2xl"
          style={{ animationDelay: "0.32s" }}
        >
          <div
            className="grid grid-cols-4 divide-x rounded-2xl overflow-hidden"
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            {STATS.map((s, i) => (
              <div key={s.label} className="py-5 px-4 text-center"
                   style={i > 0 ? { borderLeft: "1px solid rgba(255,255,255,0.06)" } : {}}>
                <div className="text-2xl font-bold text-white mb-0.5">{s.value}</div>
                <div className="text-xs text-white/30 uppercase tracking-widest">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── App window mockup ── */}
      <div
        className="animate-fade-up relative z-10 mt-24 w-full max-w-5xl mx-auto px-6"
        style={{ animationDelay: "0.4s" }}
      >
        {/* Glow under window */}
        <div className="absolute inset-x-12 bottom-0 h-20 blur-2xl opacity-30"
             style={{ background: "linear-gradient(to top, #00d2ff, transparent)" }} />

        <div
          className="relative rounded-2xl overflow-hidden"
          style={{
            border: "1px solid rgba(255,255,255,0.07)",
            background: "linear-gradient(160deg, #0d0d18 0%, #090912 100%)",
            boxShadow: "0 40px 120px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.04)",
          }}
        >
          {/* Title bar */}
          <div
            className="flex items-center gap-2 px-4 py-3"
            style={{ background: "rgba(255,255,255,0.02)", borderBottom: "1px solid rgba(255,255,255,0.04)" }}
          >
            <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
            <div className="flex-1 flex justify-center">
              <div
                className="px-4 py-1 rounded-md text-xs font-mono text-white/20"
                style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.04)" }}
              >
                ARQYV — AI media organizer
              </div>
            </div>
          </div>

          {/* App layout */}
          <div className="flex h-[360px]">

            {/* Sidebar */}
            <div
              className="w-48 shrink-0 flex flex-col p-3 gap-0.5"
              style={{ borderRight: "1px solid rgba(255,255,255,0.04)" }}
            >
              <div className="text-[9px] font-semibold text-white/20 uppercase tracking-widest px-2 pt-1 pb-2">
                Library
              </div>
              {[
                { icon: "▶", label: "Videos",    active: true },
                { icon: "♫", label: "Music",     active: false },
                { icon: "⬛", label: "Photos",   active: false },
                { icon: "📄", label: "Documents", active: false },
                { icon: "☁", label: "Cloud",     active: false },
              ].map((item) => (
                <div
                  key={item.label}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs transition-colors ${
                    item.active
                      ? "text-[#00d2ff] bg-[#00d2ff]/[0.08]"
                      : "text-white/25 hover:text-white/50"
                  }`}
                >
                  <span className="text-[10px] w-3 text-center">{item.icon}</span>
                  {item.label}
                </div>
              ))}
            </div>

            {/* Main content */}
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Search bar */}
              <div
                className="flex items-center gap-3 px-4 py-3"
                style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}
              >
                <div
                  className="flex-1 flex items-center gap-2 px-3 py-1.5 rounded-lg font-mono text-xs text-[#00d2ff]"
                  style={{ background: "rgba(0,210,255,0.05)", border: "1px solid rgba(0,210,255,0.1)" }}
                >
                  <span className="text-white/20">🔍</span>
                  beach sunset type:video date:&gt;2024
                  <span className="ml-auto text-white/20 text-[10px]">24 results</span>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-white/20">
                  <span className="px-2 py-1 rounded border border-white/[0.06]">Grid</span>
                </div>
              </div>

              {/* File grid */}
              <div className="flex-1 p-4 grid grid-cols-5 gap-2.5 content-start overflow-hidden">
                {[
                  { label: "beach_4k.mp4",   accent: true,  bg: "linear-gradient(135deg,#0d3a5c,#00d2ff22)" },
                  { label: "sunset.mkv",      accent: false, bg: "linear-gradient(135deg,#1a1a2e,#16213e)" },
                  { label: "waves.flac",      accent: false, bg: "linear-gradient(135deg,#0f2027,#203a43)" },
                  { label: "travel.mp4",      accent: false, bg: "linear-gradient(135deg,#1a1a2e,#2d1b69)" },
                  { label: "portrait.jpg",    accent: false, bg: "linear-gradient(135deg,#1a2a1a,#1e3a2e)" },
                  { label: "concert.mp4",     accent: false, bg: "linear-gradient(135deg,#2a1a1a,#3a2020)" },
                  { label: "podcast.mp3",     accent: false, bg: "linear-gradient(135deg,#1a1a2e,#0f3460)" },
                  { label: "report.pdf",      accent: false, bg: "linear-gradient(135deg,#1a1a1a,#2a2a2a)" },
                  { label: "holiday.mp4",     accent: false, bg: "linear-gradient(135deg,#0d2137,#1a3a5c)" },
                  { label: "interview.mp4",   accent: false, bg: "linear-gradient(135deg,#1a1a2e,#16213e)" },
                ].map((f, i) => (
                  <div
                    key={i}
                    className={`aspect-video rounded-lg flex flex-col justify-end p-1.5 relative overflow-hidden ${
                      f.accent ? "ring-1 ring-[#00d2ff]/30" : ""
                    }`}
                    style={{ background: f.bg, border: "1px solid rgba(255,255,255,0.05)" }}
                  >
                    {f.accent && (
                      <div className="absolute inset-0 bg-[#00d2ff]/5" />
                    )}
                    <div className="relative text-[8px] text-white/40 truncate">{f.label}</div>
                  </div>
                ))}
              </div>

              {/* Player bar */}
              <div
                className="flex items-center gap-3 px-4 py-2.5"
                style={{ borderTop: "1px solid rgba(255,255,255,0.04)", background: "rgba(0,0,0,0.2)" }}
              >
                <div className="flex items-center gap-2 text-[#00d2ff] text-xs">⏮ ▶ ⏭</div>
                <div className="font-mono text-[9px] text-white/25">1:24 / 4:37</div>
                <div className="flex-1 h-[2px] rounded-full bg-white/[0.07] overflow-hidden">
                  <div className="h-full w-[30%] rounded-full" style={{ background: "#00d2ff" }} />
                </div>
                <div className="text-[9px] text-[#00d2ff]/70 font-mono">H.264 · 4K</div>
              </div>
            </div>

            {/* Info panel */}
            <div
              className="w-44 shrink-0 hidden lg:flex flex-col p-4 gap-3"
              style={{ borderLeft: "1px solid rgba(255,255,255,0.04)" }}
            >
              <div className="text-[9px] text-white/20 uppercase tracking-widest">AI Analysis</div>
              <div className="text-[10px] font-semibold text-[#00d2ff]">beach_4k.mp4</div>
              <p className="text-[9px] text-white/30 leading-relaxed">
                Sunset beach timelapse with golden hour lighting and ocean waves.
              </p>
              <div className="text-[9px] text-white/20 uppercase tracking-widest">Tags</div>
              <div className="flex flex-wrap gap-1">
                {["beach","sunset","4K","ocean","travel"].map((t) => (
                  <span
                    key={t}
                    className="text-[8px] px-1.5 py-0.5 rounded text-[#00d2ff]/80"
                    style={{ background: "rgba(0,210,255,0.08)", border: "1px solid rgba(0,210,255,0.12)" }}
                  >
                    {t}
                  </span>
                ))}
              </div>
              <div className="mt-auto pt-2" style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
                <div className="text-[8px] text-white/20 mb-1">Backend</div>
                <div className="text-[9px] text-[#00d2ff]/60">Qt Multimedia</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom fade */}
      <div
        className="absolute bottom-0 inset-x-0 h-40 pointer-events-none"
        style={{ background: "linear-gradient(to top, #050508, transparent)" }}
      />
    </section>
  );
}
