import GitHubIcon from "./GitHubIcon";
import { OSDownloadButton } from "./OSDownloadButton";

const GITHUB_URL  = "https://github.com/ALaustrup/arqyv";
const RELEASE_URL = "https://github.com/ALaustrup/arqyv/releases/latest";

const COLS = [
  {
    heading: "Product",
    links: [
      { label: "Features",       href: "#features" },
      { label: "Download",       href: "#download" },
      { label: "Documentation",  href: "#docs" },
      { label: "FAQ",            href: "#faq" },
    ],
  },
  {
    heading: "Open Source",
    links: [
      { label: "GitHub",          href: GITHUB_URL,                              ext: true },
      { label: "Releases",        href: RELEASE_URL,                             ext: true },
      { label: "Issues",          href: `${GITHUB_URL}/issues`,                  ext: true },
      { label: "Contributing",    href: `${GITHUB_URL}/blob/main/README.md`,     ext: true },
    ],
  },
  {
    heading: "Developer",
    links: [
      { label: "Source Code",    href: GITHUB_URL,                               ext: true },
      { label: "REST API",       href: `${GITHUB_URL}#readme`,                   ext: true },
      { label: "CI / Actions",   href: `${GITHUB_URL}/actions`,                  ext: true },
      { label: "Roadmap",        href: `${GITHUB_URL}#roadmap`,                  ext: true },
    ],
  },
];

export default function Footer() {
  return (
    <footer>
      {/* CTA strip */}
      <div className="relative overflow-hidden py-24 px-6 text-center"
           style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
        {/* Glow */}
        <div className="absolute inset-0 pointer-events-none"
             style={{ background: "radial-gradient(ellipse 60% 80% at 50% 100%, rgba(0,210,255,0.06) 0%, transparent 70%)" }} />

        <div className="relative max-w-2xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-4">
            Ready to own<br />your data?
          </h2>
          <p className="text-white/35 mb-10 text-lg">
            Free. Open source. No accounts. No cloud.<br />Just your files, intelligently organized.
          </p>
          <div className="flex justify-center items-center gap-4 flex-wrap">
            <OSDownloadButton size="lg" />
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-white/40 hover:text-white/70 px-6 py-3.5 rounded-xl transition-all"
              style={{ border: "1px solid rgba(255,255,255,0.07)" }}
            >
              <GitHubIcon size={15} /> View Source
            </a>
          </div>
        </div>
      </div>

      {/* Links grid */}
      <div className="max-w-6xl mx-auto px-6 py-16 grid grid-cols-2 md:grid-cols-4 gap-12"
           style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>

        {/* Brand col */}
        <div className="col-span-2 md:col-span-1">
          <div className="flex items-center gap-2 mb-5">
            <div className="relative w-7 h-7 rounded-lg bg-gradient-to-br from-[#00d2ff] to-[#0ea5e9] flex items-center justify-center">
              <span className="text-[10px] font-black text-black">AQ</span>
            </div>
            <span className="font-semibold text-white/70">ARQYV</span>
          </div>
          <p className="text-sm text-white/25 leading-relaxed max-w-[200px] mb-5">
            The last great desktop application. Local-first AI media organizer.
          </p>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-white/30 hover:text-white/70 transition-all"
            style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}
            aria-label="GitHub"
          >
            <GitHubIcon size={14} />
          </a>
        </div>

        {COLS.map((col) => (
          <div key={col.heading}>
            <h3 className="text-[10px] font-semibold text-white/20 uppercase tracking-widest mb-5">
              {col.heading}
            </h3>
            <ul className="space-y-3.5">
              {col.links.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    target={"ext" in link && link.ext ? "_blank" : undefined}
                    rel={"ext" in link && link.ext ? "noopener noreferrer" : undefined}
                    className="text-sm text-white/30 hover:text-white/70 transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Bottom bar */}
      <div className="max-w-6xl mx-auto px-6 py-5 flex flex-col md:flex-row items-center justify-between gap-3"
           style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
        <p className="text-xs text-white/20">
          © {new Date().getFullYear()} Alaustrup · MIT License
        </p>
        <div className="flex items-center gap-4 text-xs text-white/20">
          <span>v0.1.0</span>
          <span className="w-px h-3 bg-white/10" />
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="hover:text-white/50 transition-colors">
            Open Source
          </a>
          <span className="w-px h-3 bg-white/10" />
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            All systems go
          </span>
        </div>
      </div>
    </footer>
  );
}
