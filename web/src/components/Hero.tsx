"use client";

import { ArrowRight, Zap } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { OSDownloadButton } from "./OSDownloadButton";

const GITHUB_URL = "https://github.com/ALaustrup/arqyv";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center pt-16 overflow-hidden">
      {/* Background glow + grid */}
      <div className="absolute inset-0 hero-glow grid-bg" />

      {/* Radial orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-[#00b4d8]/5 blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 w-72 h-72 rounded-full bg-[#0f3460]/40 blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto px-6 flex flex-col items-center text-center">
        {/* Badge */}
        <div className="flex items-center gap-2 text-xs font-medium text-[#00b4d8] bg-[#00b4d8]/10 border border-[#00b4d8]/20 rounded-full px-4 py-1.5 mb-8 animate-fade-up">
          <Zap size={12} className="fill-[#00b4d8]" />
          v0.1.0 — Now available · AI · P2P Sharing · Zero dependencies
        </div>

        {/* Headline */}
        <h1
          className="text-5xl md:text-7xl font-bold leading-tight tracking-tight mb-6 animate-fade-up"
          style={{ animationDelay: "0.1s" }}
        >
          The last great{" "}
          <span className="gradient-text text-glow">
            desktop application.
          </span>
        </h1>

        {/* Sub-headline */}
        <p
          className="text-lg md:text-xl text-[#9e9e9e] max-w-2xl leading-relaxed mb-10 animate-fade-up"
          style={{ animationDelay: "0.2s" }}
        >
          ARQYV unifies every file you own — video, audio, documents, photos —
          into one intelligent, searchable library. It plays anything,
          understands everything, and lets you share instantly. No accounts.
          No subscriptions. Forever local-first.
        </p>

        {/* Primary CTAs */}
        <div
          className="flex flex-col sm:flex-row items-center gap-4 mb-8 animate-fade-up"
          style={{ animationDelay: "0.3s" }}
        >
          <OSDownloadButton size="lg" />
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2.5 border border-[#2a2a4a] text-[#e0e0e0] hover:border-[#00b4d8] hover:text-[#00b4d8] px-8 py-3.5 rounded-xl text-base transition-all hover:bg-[#00b4d8]/5"
          >
            <GitHubIcon size={18} />
            View on GitHub
          </a>
        </div>

        {/* Scroll-to-downloads link */}
        <div
          className="flex items-center gap-2 text-sm text-[#9e9e9e] hover:text-[#00b4d8] transition-colors cursor-pointer animate-fade-up mb-6"
          style={{ animationDelay: "0.4s" }}
          onClick={() => document.getElementById("download")?.scrollIntoView({ behavior: "smooth" })}
        >
          <ArrowRight size={14} />
          See all platforms &amp; install instructions
        </div>

        {/* Social proof */}
        <p
          className="text-xs text-[#9e9e9e] mt-8 animate-fade-up"
          style={{ animationDelay: "0.5s" }}
        >
          Open source · MIT License · Python 3.11+ · PyQt6
        </p>
      </div>

      {/* App mockup */}
      <div
        className="relative z-10 mt-20 w-full max-w-5xl mx-auto px-6 animate-fade-up"
        style={{ animationDelay: "0.5s" }}
      >
        <div className="relative rounded-2xl border border-[#2a2a4a] bg-[#16213e] overflow-hidden glow-accent">
          {/* Window chrome */}
          <div className="flex items-center gap-1.5 px-4 py-3 bg-[#0f3460] border-b border-[#2a2a4a]">
            <div className="w-3 h-3 rounded-full bg-[#f44336]/80" />
            <div className="w-3 h-3 rounded-full bg-[#ff9800]/80" />
            <div className="w-3 h-3 rounded-full bg-[#4caf50]/80" />
            <div className="flex-1 mx-4 bg-[#1a1a2e] rounded px-3 py-1 text-xs text-[#9e9e9e] font-mono">
              ARQYV — AI-powered media organizer
            </div>
          </div>

          {/* App UI mockup */}
          <div className="flex h-[380px]">
            {/* Sidebar */}
            <div className="w-52 bg-[#16213e] border-r border-[#2a2a4a] p-3 flex flex-col gap-1 shrink-0">
              <div className="text-[10px] text-[#9e9e9e] uppercase tracking-widest px-2 py-1">Library</div>
              {["Videos", "Music", "Photos", "Documents", "Cloud"].map((item, i) => (
                <div
                  key={item}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors ${
                    i === 0 ? "bg-[#00b4d8]/15 text-[#00b4d8]" : "text-[#9e9e9e] hover:text-[#e0e0e0] hover:bg-[#0f3460]"
                  }`}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
                  {item}
                </div>
              ))}
              <div className="mt-4 text-[10px] text-[#9e9e9e] uppercase tracking-widest px-2 py-1">Recent</div>
              {["interview_final.mp4", "beach_2024.jpg", "report_q1.pdf"].map((f) => (
                <div key={f} className="px-2 py-1 text-[10px] text-[#9e9e9e] truncate hover:text-[#e0e0e0] cursor-pointer">
                  {f}
                </div>
              ))}
            </div>

            {/* Main area */}
            <div className="flex-1 flex flex-col">
              {/* Search bar */}
              <div className="px-4 py-3 border-b border-[#2a2a4a] flex items-center gap-3">
                <div className="flex-1 bg-[#0f3460] rounded-lg px-3 py-1.5 text-xs text-[#00b4d8] font-mono">
                  beach sunset type:video date:&gt;2024
                </div>
                <div className="text-[10px] text-[#9e9e9e] whitespace-nowrap">24 results</div>
              </div>

              {/* Grid */}
              <div className="flex-1 p-4 grid grid-cols-4 gap-3 content-start overflow-hidden">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div
                    key={i}
                    className={`aspect-video rounded-lg border border-[#2a2a4a] flex items-end p-1.5 ${
                      i === 0 ? "border-[#00b4d8]/60 bg-[#00b4d8]/5" : "bg-[#0f3460]/40"
                    }`}
                    style={{
                      background: i === 0
                        ? "linear-gradient(135deg, #0f3460 0%, #00b4d8 200%)"
                        : `hsl(${220 + i * 8}deg 30% ${10 + i * 2}%)`,
                    }}
                  >
                    <div className="text-[9px] text-[#e0e0e0]/70 truncate w-full">
                      {["▶ beach_4k.mp4","▶ sunset.mkv","🎵 waves.flac","📄 journal.pdf","▶ travel.mp4","🖼 portrait.jpg","▶ night.mp4","📄 notes.md"][i]}
                    </div>
                  </div>
                ))}
              </div>

              {/* Player bar */}
              <div className="border-t border-[#2a2a4a] px-4 py-2.5 flex items-center gap-4 bg-[#16213e]">
                <div className="flex items-center gap-2 text-[#00b4d8]">
                  <span className="text-xs">⏮</span>
                  <span className="text-base">▶</span>
                  <span className="text-xs">⏭</span>
                </div>
                <div className="text-[10px] text-[#9e9e9e] font-mono whitespace-nowrap">1:24 / 4:37</div>
                <div className="flex-1 h-1 bg-[#2a2a4a] rounded-full overflow-hidden">
                  <div className="h-full w-[30%] bg-[#00b4d8] rounded-full" />
                </div>
                <div className="text-[10px] text-[#9e9e9e]">H.264 · 4K</div>
                <div className="text-[10px] text-[#00b4d8]">Qt Backend</div>
              </div>
            </div>

            {/* Info panel */}
            <div className="w-44 bg-[#16213e] border-l border-[#2a2a4a] p-3 text-[10px] shrink-0 hidden lg:block">
              <div className="text-[#9e9e9e] uppercase tracking-widest mb-2">AI Analysis</div>
              <div className="text-[#00b4d8] mb-1">beach_4k.mp4</div>
              <div className="text-[#9e9e9e] leading-relaxed mb-3">Sunset beach timelapse with golden hour lighting and ocean waves.</div>
              <div className="text-[#9e9e9e] uppercase tracking-widest mb-1.5">Tags</div>
              <div className="flex flex-wrap gap-1">
                {["beach","sunset","4K","travel","ocean"].map(t => (
                  <span key={t} className="bg-[#00b4d8]/10 text-[#00b4d8] rounded px-1.5 py-0.5">{t}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom fade */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#1a1a2e] to-transparent pointer-events-none" />
      </div>
    </section>
  );
}
