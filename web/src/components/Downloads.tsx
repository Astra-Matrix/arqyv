import { Download, ExternalLink, CheckCircle } from "lucide-react";
import GitHubIcon from "./GitHubIcon";

const GITHUB_URL = "https://github.com/ALaustrup/arqyv";
const RELEASE_URL = "https://github.com/ALaustrup/arqyv/releases/latest";

const PLATFORMS = [
  {
    os: "Windows",
    icon: "⊞",
    req: "Windows 10 / 11 · 64-bit",
    file: "arqyv-windows.zip",
    size: "~85 MB",
    href: "https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-windows.zip",
    steps: [
      "Download arqyv-windows.zip",
      "Extract to any folder",
      "Double-click ARQYV.exe",
    ],
  },
  {
    os: "macOS",
    icon: "",
    req: "macOS 12 Monterey+ · Intel & Apple Silicon",
    file: "arqyv-macos.zip",
    size: "~90 MB",
    href: "https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-macos.zip",
    steps: [
      "Download arqyv-macos.zip",
      "Extract and drag ARQYV.app to /Applications",
      'Right-click → Open to bypass Gatekeeper on first launch',
    ],
    featured: true,
  },
  {
    os: "Linux",
    icon: "🐧",
    req: "Ubuntu 22.04+ · Debian · Arch",
    file: "arqyv-linux.zip",
    size: "~80 MB",
    href: "https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-linux.zip",
    steps: [
      "Download arqyv-linux.zip",
      "Extract: unzip arqyv-linux.zip",
      "Run: ./ARQYV/ARQYV",
    ],
  },
];

const REQUIREMENTS = [
  "Python 3.11+ (only if running from source)",
  "No VLC required — Qt Multimedia handles playback out of the box",
  "VLC optional for extended codecs (H.265, AV1, AC3, DTS…)",
  "4 GB RAM recommended for AI features",
  "~500 MB disk space for the application",
];

export default function Downloads() {
  return (
    <section id="download" className="py-32 px-6 relative">
      {/* Background accent */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#00b4d8]/3 to-transparent pointer-events-none" />

      <div className="relative max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <p className="text-sm font-medium text-[#00b4d8] uppercase tracking-widest mb-4">
            Free. Forever.
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-[#e0e0e0] mb-5">
            Download ARQYV
          </h2>
          <p className="text-[#9e9e9e] text-lg max-w-xl mx-auto">
            Standalone executables — no installer, no Python needed.
            Unzip and run.
          </p>
        </div>

        {/* Platform cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-14">
          {PLATFORMS.map((p) => (
            <div
              key={p.os}
              className={`relative rounded-2xl border p-6 flex flex-col transition-all hover:-translate-y-1 ${
                p.featured
                  ? "border-[#00b4d8]/50 bg-gradient-to-br from-[#16213e] to-[#0f3460] shadow-[0_0_40px_rgba(0,180,216,0.12)]"
                  : "border-[#2a2a4a] bg-[#16213e]"
              }`}
            >
              {p.featured && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#00b4d8] text-[#1a1a2e] text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest">
                  Recommended
                </div>
              )}

              <div className="text-4xl mb-3">{p.icon}</div>
              <div className="text-xl font-bold text-[#e0e0e0] mb-1">{p.os}</div>
              <div className="text-xs text-[#9e9e9e] mb-5">{p.req}</div>

              {/* Steps */}
              <div className="flex-1 space-y-2 mb-6">
                {p.steps.map((s, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-[#9e9e9e]">
                    <span className="text-[#00b4d8] font-mono text-xs mt-0.5 shrink-0">{i + 1}.</span>
                    <span>{s}</span>
                  </div>
                ))}
              </div>

              <a
                href={p.href}
                className={`flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-all ${
                  p.featured
                    ? "bg-[#00b4d8] hover:bg-[#48cae4] text-[#1a1a2e] hover:shadow-[0_0_20px_rgba(0,180,216,0.4)]"
                    : "bg-[#0f3460] hover:bg-[#00b4d8] text-[#e0e0e0] hover:text-[#1a1a2e] border border-[#2a2a4a] hover:border-[#00b4d8]"
                }`}
              >
                <Download size={15} />
                {p.file}
                <span className="text-xs opacity-70">({p.size})</span>
              </a>
            </div>
          ))}
        </div>

        {/* Requirements */}
        <div className="bg-[#16213e] border border-[#2a2a4a] rounded-2xl p-6 mb-8">
          <h3 className="font-semibold text-[#e0e0e0] mb-4 flex items-center gap-2">
            <CheckCircle size={16} className="text-[#00b4d8]" />
            System Requirements
          </h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {REQUIREMENTS.map((r) => (
              <li key={r} className="flex items-center gap-2 text-sm text-[#9e9e9e]">
                <span className="w-1 h-1 rounded-full bg-[#00b4d8] shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </div>

        {/* Source install */}
        <div className="bg-[#0f3460]/40 border border-[#2a2a4a] rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center gap-6">
          <div className="flex-1">
            <h3 className="font-semibold text-[#e0e0e0] mb-1">Prefer running from source?</h3>
            <p className="text-sm text-[#9e9e9e]">
              Clone the repo, install deps, and run — the full experience in under two minutes.
            </p>
          </div>
          <div className="flex gap-3 shrink-0">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 border border-[#2a2a4a] text-[#9e9e9e] hover:text-[#00b4d8] hover:border-[#00b4d8]/40 px-4 py-2 rounded-lg text-sm transition-all"
            >
              <GitHubIcon size={15} />
              GitHub
            </a>
            <a
              href={RELEASE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 border border-[#2a2a4a] text-[#9e9e9e] hover:text-[#00b4d8] hover:border-[#00b4d8]/40 px-4 py-2 rounded-lg text-sm transition-all"
            >
              <ExternalLink size={15} />
              All Releases
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
