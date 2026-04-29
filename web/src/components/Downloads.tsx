import { ExternalLink } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { PlatformCards } from "./OSDownloadButton";

const GITHUB_URL   = "https://github.com/ALaustrup/arqyv";
const RELEASE_URL  = "https://github.com/ALaustrup/arqyv/releases/latest";

const REQUIREMENTS = [
  "No Python required for the pre-built binary",
  "No VLC required — Qt Multimedia handles playback out of the box",
  "VLC optional for H.265, AV1, AC3, DTS extended codec support",
  "4 GB RAM recommended for AI features",
  "~500 MB disk for the application",
];

export default function Downloads() {
  return (
    <section id="download" className="section relative">
      {/* Glow accent */}
      <div className="absolute inset-0 pointer-events-none"
           style={{ background: "radial-gradient(ellipse 80% 50% at 50% 50%, rgba(0,210,255,0.03) 0%, transparent 70%)" }} />

      <div className="relative max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-6"
               style={{ background: "rgba(0,210,255,0.06)", border: "1px solid rgba(0,210,255,0.12)" }}>
            Free forever
          </div>
          <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-5">
            Download ARQYV.
          </h2>
          <p className="text-white/40 text-lg max-w-md mx-auto">
            Standalone executables — no installer, no Python.
            Unzip and run. Your platform is detected automatically.
          </p>
        </div>

        {/* Platform cards (OS auto-detected) */}
        <div className="mb-12">
          <PlatformCards />
        </div>

        {/* Requirements */}
        <div className="rounded-2xl p-6 mb-6"
             style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-widest mb-4">System Requirements</h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {REQUIREMENTS.map((r) => (
              <li key={r} className="flex items-center gap-2.5 text-sm text-white/40">
                <span className="w-1 h-1 rounded-full bg-[#00d2ff] shrink-0 opacity-60" />
                {r}
              </li>
            ))}
          </ul>
        </div>

        {/* Source install strip */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-5 px-6 py-5 rounded-2xl"
             style={{ background: "rgba(255,255,255,0.015)", border: "1px solid rgba(255,255,255,0.05)" }}>
          <div>
            <div className="font-semibold text-white/80 mb-1">Prefer running from source?</div>
            <p className="text-sm text-white/35">
              Python 3.11+ · Clone → install → run in under two minutes.
            </p>
          </div>
          <div className="flex gap-3 shrink-0">
            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm text-white/40 hover:text-white/70 px-4 py-2 rounded-xl transition-all"
               style={{ border: "1px solid rgba(255,255,255,0.07)" }}>
              <GitHubIcon size={14} /> GitHub
            </a>
            <a href={RELEASE_URL} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm text-white/40 hover:text-white/70 px-4 py-2 rounded-xl transition-all"
               style={{ border: "1px solid rgba(255,255,255,0.07)" }}>
              <ExternalLink size={13} /> All releases
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
