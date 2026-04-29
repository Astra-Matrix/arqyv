"use client";

import { useEffect, useState } from "react";
import { Download, ChevronDown } from "lucide-react";

const VERSION = "v0.1.0";
const RELEASE_BASE = `https://github.com/ALaustrup/arqyv/releases/download/${VERSION}`;
const RELEASE_LATEST = "https://github.com/ALaustrup/arqyv/releases/latest";

type OS = "windows" | "macos" | "linux" | "unknown";

interface Platform {
  os: OS;
  label: string;
  icon: string;
  file: string;
  ext: string;
  url: string;
  note: string;
}

const PLATFORMS: Platform[] = [
  {
    os: "windows",
    label: "Download for Windows",
    icon: "⊞",
    file: "arqyv-windows",
    ext: ".zip",
    url: `${RELEASE_BASE}/arqyv-windows.zip`,
    note: "Windows 10 / 11 · 64-bit · ZIP",
  },
  {
    os: "macos",
    label: "Download for macOS",
    icon: "",
    file: "arqyv-macos",
    ext: ".zip",
    url: `${RELEASE_BASE}/arqyv-macos.zip`,
    note: "macOS 12+ · Intel & Apple Silicon · ZIP",
  },
  {
    os: "linux",
    label: "Download for Linux",
    icon: "🐧",
    file: "arqyv-linux",
    ext: ".zip",
    url: `${RELEASE_BASE}/arqyv-linux.zip`,
    note: "Ubuntu 22.04+ · Debian · Arch · ZIP",
  },
];

function detectOS(): OS {
  if (typeof navigator === "undefined") return "unknown";
  const ua = navigator.userAgent;
  const platform =
    (navigator as Navigator & { userAgentData?: { platform?: string } })
      .userAgentData?.platform ?? navigator.platform ?? "";

  if (/Win/i.test(platform) || /Win/i.test(ua)) return "windows";
  if (/Mac/i.test(platform) || /Mac/i.test(ua)) return "macos";
  if (/Linux/i.test(platform) || /Linux/i.test(ua)) return "linux";
  if (/iPhone|iPad|iPod/i.test(ua)) return "macos";   // iOS → link to macOS
  if (/Android/i.test(ua)) return "linux";              // Android → link to Linux
  return "unknown";
}

/** Primary button shown in Nav and Hero */
export function OSDownloadButton({
  size = "md",
  className = "",
}: {
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const [os, setOS] = useState<OS>("unknown");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOS(detectOS());
  }, []);

  const primary =
    PLATFORMS.find((p) => p.os === os) ?? PLATFORMS[0];
  const others = PLATFORMS.filter((p) => p.os !== primary.os);

  const sizePad = {
    sm: { main: "px-4 py-2 text-sm gap-2",       chevron: "px-2.5", icon: 14 },
    md: { main: "px-5 py-2.5 text-sm gap-2",     chevron: "px-2.5", icon: 15 },
    lg: { main: "px-7 py-3.5 text-base gap-2.5", chevron: "px-3",   icon: 18 },
  }[size];

  return (
    <div className={`relative inline-flex ${className}`}>
      {/* Primary */}
      <a
        href={primary.url}
        className={`btn-accent flex items-center ${sizePad.main} rounded-l-xl`}
        aria-label={primary.label}
      >
        <Download size={sizePad.icon} />
        <span>{primary.label}</span>
        <span className="opacity-50 font-normal text-xs hidden sm:inline">{primary.ext}</span>
      </a>

      {/* Chevron */}
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-label="Other platforms"
        className={`btn-accent flex items-center justify-center ${sizePad.chevron} rounded-r-xl`}
        style={{ borderLeft: "1px solid rgba(0,0,0,0.2)" }}
      >
        <ChevronDown size={13} className={`transition-transform duration-200 ${open ? "rotate-180" : ""}`} />
      </button>

      {/* Dropdown */}
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute top-full right-0 mt-2 z-50 min-w-[260px] rounded-2xl shadow-2xl overflow-hidden"
               style={{ background: "#0d0d18", border: "1px solid rgba(255,255,255,0.08)" }}>
            <div className="px-4 py-2.5 text-[10px] text-white/20 uppercase tracking-widest font-semibold"
                 style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              Other platforms
            </div>
            {others.map((p) => (
              <a key={p.os} href={p.url} onClick={() => setOpen(false)}
                 className="flex items-center gap-3 px-4 py-3.5 hover:bg-white/[0.03] transition-colors">
                <span className="text-xl w-7 text-center">{p.icon}</span>
                <div>
                  <div className="text-sm font-medium text-white/70">{p.label}</div>
                  <div className="text-[11px] text-white/25">{p.note}</div>
                </div>
                <Download size={12} className="ml-auto text-white/20" />
              </a>
            ))}
            <div style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
              <a href={RELEASE_LATEST} target="_blank" rel="noopener noreferrer" onClick={() => setOpen(false)}
                 className="flex items-center justify-center gap-2 px-4 py-2.5 text-xs text-white/20 hover:text-[#00d2ff] transition-colors">
                All releases on GitHub →
              </a>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

/** Full platform card grid used in the Downloads section */
export function PlatformCards() {
  const [os, setOS] = useState<OS>("unknown");

  useEffect(() => {
    setOS(detectOS());
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {PLATFORMS.map((p) => {
        const detected = p.os === os;
        const osLabel = p.os === "macos" ? "macOS" : p.os.charAt(0).toUpperCase() + p.os.slice(1);
        return (
          <div
            key={p.os}
            className="relative rounded-2xl p-6 flex flex-col transition-all hover:-translate-y-1"
            style={{
              background: detected
                ? "linear-gradient(135deg, rgba(0,210,255,0.06) 0%, rgba(0,0,0,0) 100%), #0d0d18"
                : "#0d0d18",
              border: detected
                ? "1px solid rgba(0,210,255,0.2)"
                : "1px solid rgba(255,255,255,0.06)",
              boxShadow: detected ? "0 0 40px rgba(0,210,255,0.07)" : "none",
            }}
          >
            {detected && (
              <div className="absolute -top-3 left-6 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full"
                   style={{ background: "#00d2ff", color: "#000" }}>
                Your Platform
              </div>
            )}

            <div className="text-4xl mb-4">{p.icon}</div>
            <div className="text-xl font-bold text-white mb-1">{osLabel}</div>
            <div className="text-xs text-white/30 mb-6">{p.note}</div>

            <div className="flex-1 space-y-2.5 mb-6">
              {p.os === "windows" && (
                <>
                  <Step n={1}>Download <code className="text-[#00d2ff] font-mono">{p.file}{p.ext}</code></Step>
                  <Step n={2}>Extract the ZIP to any folder</Step>
                  <Step n={3}>Double-click <code className="text-[#00d2ff] font-mono">ARQYV.exe</code></Step>
                </>
              )}
              {p.os === "macos" && (
                <>
                  <Step n={1}>Download <code className="text-[#00d2ff] font-mono">{p.file}{p.ext}</code></Step>
                  <Step n={2}>Move <code className="text-[#00d2ff] font-mono">ARQYV.app</code> to Applications</Step>
                  <Step n={3}>Right-click → Open to bypass Gatekeeper</Step>
                </>
              )}
              {p.os === "linux" && (
                <>
                  <Step n={1}>Download <code className="text-[#00d2ff] font-mono">{p.file}{p.ext}</code></Step>
                  <Step n={2}><code className="text-[#00d2ff] font-mono">unzip {p.file}{p.ext}</code></Step>
                  <Step n={3}><code className="text-[#00d2ff] font-mono">./ARQYV/ARQYV</code></Step>
                </>
              )}
            </div>

            <a
              href={p.url}
              className={`flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-all ${
                detected ? "btn-accent" : ""
              }`}
              style={!detected ? {
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "rgba(255,255,255,0.6)",
              } : {}}
              onMouseEnter={(e) => { if (!detected) { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.07)"; }}}
              onMouseLeave={(e) => { if (!detected) { (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)"; }}}
            >
              <Download size={15} />
              {p.file}{p.ext}
            </a>
          </div>
        );
      })}
    </div>
  );
}

function Step({ n, children }: { n: number; children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-2 text-sm text-[#9e9e9e]">
      <span className="text-[#00b4d8] font-mono text-xs mt-0.5 shrink-0">{n}.</span>
      <span>{children}</span>
    </div>
  );
}
