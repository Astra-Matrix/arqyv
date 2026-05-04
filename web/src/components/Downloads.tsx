"use client";

import { useInView } from "@/hooks/useInView";
import { ExternalLink, Download } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { PlatformCards } from "./OSDownloadButton";

const GITHUB_URL  = "https://github.com/Alaustrup/arqyv";
const RELEASE_URL = "https://github.com/Alaustrup/arqyv/releases/latest";

const REQUIREMENTS = [
  { icon: "🐍", text: "Python 3.11+ (bundled in pre-built binaries — not needed separately)" },
  { icon: "▶",  text: "No VLC required — Qt Multimedia handles playback out of the box" },
  { icon: "🎬", text: "VLC optional for H.265, AV1, AC3, DTS extended codec support" },
  { icon: "🧠", text: "4 GB RAM recommended for AI features; 2 GB minimum without AI" },
  { icon: "💾", text: "~500 MB disk space for the application + models cache on demand" },
];

export default function Downloads() {
  const { ref, inView } = useInView<HTMLDivElement>({ threshold: 0.1 });

  return (
    <section id="download" className="section relative" ref={ref}>
      {/* Ambient glow */}
      <div className="absolute inset-0 pointer-events-none"
           style={{ background: "radial-gradient(ellipse 80% 40% at 50% 50%, rgba(0,210,255,0.025) 0%, transparent 70%)" }} />

      <div className="relative max-w-6xl mx-auto">

        <div className={`text-center mb-16 reveal ${inView ? "in-view" : ""}`}>
          <div className="label-pill inline-flex">
            <Download size={10} />
            Free forever
          </div>
          <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-5">
            Download ARQYV.
          </h2>
          <p className="text-white/40 text-lg max-w-md mx-auto leading-relaxed">
            Standalone installer for your platform — or install from source
            in under two minutes. No subscriptions. No telemetry. Ever.
          </p>
        </div>

        {/* OS-detecting platform cards */}
        <div className={`mb-14 reveal ${inView ? "in-view" : ""}`}
             style={{ transitionDelay: "0.1s" }}>
          <PlatformCards />
        </div>

        {/* Quick install commands */}
        <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 mb-10 reveal ${inView ? "in-view" : ""}`}
             style={{ transitionDelay: "0.15s" }}>
          {[
            {
              os: "macOS / Linux",
              icon: "🍎",
              cmd: "curl -fsSL https://arqyv.app/install.sh | bash",
              href: "/install.sh",
              download: "install.sh",
            },
            {
              os: "Windows",
              icon: "🪟",
              cmd: "irm https://arqyv.app/install.ps1 | iex",
              href: "/install.ps1",
              download: "install.ps1",
            },
          ].map((p) => (
            <div key={p.os}
                 className="group rounded-2xl p-5"
                 style={{ background: "rgba(255,255,255,0.018)", border: "1px solid rgba(255,255,255,0.055)" }}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span>{p.icon}</span>
                  <span className="text-sm font-semibold text-white/70">{p.os}</span>
                </div>
                <a
                  href={p.href}
                  download={p.download}
                  className="text-[11px] text-white/30 hover:text-[#00d2ff] flex items-center gap-1 transition-colors"
                >
                  <Download size={10} /> Download script
                </a>
              </div>
              <code className="block text-[12px] font-mono text-[#00d2ff]/80 bg-transparent truncate">
                {p.cmd}
              </code>
            </div>
          ))}
        </div>

        {/* System requirements */}
        <div className={`rounded-2xl p-6 mb-5 reveal ${inView ? "in-view" : ""}`}
             style={{
               transitionDelay: "0.2s",
               background: "rgba(255,255,255,0.015)",
               border: "1px solid rgba(255,255,255,0.055)",
             }}>
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-5">
            System Requirements
          </h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {REQUIREMENTS.map((r) => (
              <li key={r.text} className="flex items-start gap-3 text-sm text-white/40">
                <span className="text-base mt-0.5 leading-none shrink-0">{r.icon}</span>
                {r.text}
              </li>
            ))}
          </ul>
        </div>

        {/* Source install strip */}
        <div className={`flex flex-col md:flex-row items-start md:items-center justify-between gap-5 px-6 py-5 rounded-2xl reveal ${inView ? "in-view" : ""}`}
             style={{
               transitionDelay: "0.24s",
               background: "rgba(255,255,255,0.01)",
               border: "1px solid rgba(255,255,255,0.04)",
             }}>
          <div>
            <div className="font-semibold text-white/70 mb-1">Prefer running from source?</div>
            <p className="text-sm text-white/30">
              Python 3.11+ · Clone → install → run in under two minutes. Full dev environment included.
            </p>
          </div>
          <div className="flex gap-3 shrink-0">
            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm text-white/40 hover:text-white/70 px-4 py-2.5 rounded-xl transition-all hover:bg-white/[0.03]"
               style={{ border: "1px solid rgba(255,255,255,0.07)" }}>
              <GitHubIcon size={14} /> GitHub
            </a>
            <a href={RELEASE_URL} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm text-white/40 hover:text-white/70 px-4 py-2.5 rounded-xl transition-all hover:bg-white/[0.03]"
               style={{ border: "1px solid rgba(255,255,255,0.07)" }}>
              <ExternalLink size={13} /> All releases
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
