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

  const sizeCls = {
    sm: "px-4 py-1.5 text-sm gap-2",
    md: "px-6 py-2.5 text-sm gap-2",
    lg: "px-8 py-3.5 text-base gap-2.5",
  }[size];

  return (
    <div className={`relative inline-flex ${className}`}>
      {/* Primary download */}
      <a
        href={primary.url}
        className={`flex items-center ${sizeCls} bg-[#00b4d8] hover:bg-[#48cae4] text-[#1a1a2e] font-bold rounded-l-xl transition-all hover:shadow-[0_0_20px_rgba(0,180,216,0.4)]`}
        aria-label={primary.label}
      >
        <Download size={size === "lg" ? 18 : 15} />
        <span>{primary.label}</span>
        <span className="text-[#1a1a2e]/60 font-normal text-xs hidden sm:inline">
          {primary.ext}
        </span>
      </a>

      {/* Chevron dropdown trigger */}
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-label="Other platforms"
        className={`flex items-center justify-center ${
          size === "lg" ? "px-3" : "px-2"
        } bg-[#00b4d8] hover:bg-[#48cae4] text-[#1a1a2e] font-bold rounded-r-xl border-l border-[#1a1a2e]/20 transition-all`}
      >
        <ChevronDown
          size={14}
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {/* Dropdown */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <div className="absolute top-full right-0 mt-2 z-50 min-w-[240px] bg-[#16213e] border border-[#2a2a4a] rounded-xl shadow-2xl overflow-hidden">
            <div className="px-3 py-2 text-[10px] text-[#9e9e9e] uppercase tracking-widest border-b border-[#2a2a4a]">
              Other platforms
            </div>
            {others.map((p) => (
              <a
                key={p.os}
                href={p.url}
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 px-4 py-3 hover:bg-[#0f3460] transition-colors"
              >
                <span className="text-lg w-6 text-center">{p.icon}</span>
                <div>
                  <div className="text-sm font-medium text-[#e0e0e0]">
                    {p.label}
                  </div>
                  <div className="text-[11px] text-[#9e9e9e]">{p.note}</div>
                </div>
                <Download size={13} className="ml-auto text-[#9e9e9e]" />
              </a>
            ))}
            <div className="border-t border-[#2a2a4a]">
              <a
                href={RELEASE_LATEST}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setOpen(false)}
                className="flex items-center justify-center gap-2 px-4 py-2.5 text-xs text-[#9e9e9e] hover:text-[#00b4d8] transition-colors"
              >
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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {PLATFORMS.map((p) => {
        const isDetected = p.os === os;
        return (
          <div
            key={p.os}
            className={`relative rounded-2xl border p-6 flex flex-col transition-all hover:-translate-y-1 ${
              isDetected
                ? "border-[#00b4d8]/50 bg-gradient-to-br from-[#16213e] to-[#0f3460] shadow-[0_0_40px_rgba(0,180,216,0.12)]"
                : "border-[#2a2a4a] bg-[#16213e]"
            }`}
          >
            {isDetected && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#00b4d8] text-[#1a1a2e] text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest whitespace-nowrap">
                Your Platform
              </div>
            )}

            <div className="text-4xl mb-3">{p.icon}</div>

            <div className="text-xl font-bold text-[#e0e0e0] mb-1 capitalize">
              {p.os === "macos" ? "macOS" : p.os.charAt(0).toUpperCase() + p.os.slice(1)}
            </div>
            <div className="text-xs text-[#9e9e9e] mb-5">{p.note}</div>

            {/* Install steps */}
            <div className="flex-1 space-y-2 mb-6">
              {p.os === "windows" && (
                <>
                  <Step n={1}>Download <code className="text-[#00b4d8] font-mono">{p.file}{p.ext}</code></Step>
                  <Step n={2}>Extract the ZIP to any folder</Step>
                  <Step n={3}>Double-click <code className="text-[#00b4d8] font-mono">ARQYV.exe</code></Step>
                </>
              )}
              {p.os === "macos" && (
                <>
                  <Step n={1}>Download <code className="text-[#00b4d8] font-mono">{p.file}{p.ext}</code></Step>
                  <Step n={2}>Extract and move <code className="text-[#00b4d8] font-mono">ARQYV.app</code> to Applications</Step>
                  <Step n={3}>Right-click → Open to bypass Gatekeeper on first launch</Step>
                </>
              )}
              {p.os === "linux" && (
                <>
                  <Step n={1}>Download <code className="text-[#00b4d8] font-mono">{p.file}{p.ext}</code></Step>
                  <Step n={2}><code className="text-[#00b4d8] font-mono">unzip {p.file}{p.ext}</code></Step>
                  <Step n={3}><code className="text-[#00b4d8] font-mono">./ARQYV/ARQYV</code></Step>
                </>
              )}
            </div>

            <a
              href={p.url}
              className={`flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-all ${
                isDetected
                  ? "bg-[#00b4d8] hover:bg-[#48cae4] text-[#1a1a2e] hover:shadow-[0_0_20px_rgba(0,180,216,0.4)]"
                  : "bg-[#0f3460] hover:bg-[#00b4d8] text-[#e0e0e0] hover:text-[#1a1a2e] border border-[#2a2a4a] hover:border-[#00b4d8]"
              }`}
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
