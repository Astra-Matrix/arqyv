import { ExternalLink, CheckCircle } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { PlatformCards } from "./OSDownloadButton";

const GITHUB_URL = "https://github.com/ALaustrup/arqyv";
const RELEASE_URL = "https://github.com/ALaustrup/arqyv/releases/latest";

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

        {/* Platform cards — OS auto-detected, user's platform is highlighted */}
        <div className="mb-14">
          <PlatformCards />
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
