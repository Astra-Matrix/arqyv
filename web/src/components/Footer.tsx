import GitHubIcon from "./GitHubIcon";

const GITHUB_URL = "https://github.com/Alaustrup/arqyv";

const LINKS = {
  Product: [
    { label: "Features",    href: "#features" },
    { label: "Download",    href: "#download" },
    { label: "How it works",href: "#how" },
    { label: "FAQ",         href: "#faq" },
  ],
  Resources: [
    { label: "Documentation",     href: "/docs" },
    { label: "Getting Started",   href: "/docs/getting-started" },
    { label: "User Manual",       href: "/docs/user-manual" },
    { label: "Plugin System",     href: "/docs/plugins" },
  ],
  Install: [
    { label: "macOS / Linux script", href: "/install.sh",  download: "install.sh" },
    { label: "Windows script",       href: "/install.ps1", download: "install.ps1" },
    { label: "GitHub Releases",      href: `${GITHUB_URL}/releases`, target: "_blank" },
    { label: "Source on GitHub",     href: GITHUB_URL,               target: "_blank" },
  ],
};

export default function Footer() {
  return (
    <footer className="relative pt-20 pb-10"
            style={{ borderTop: "1px solid rgba(255,255,255,0.045)" }}>
      {/* Subtle top glow */}
      <div className="absolute top-0 inset-x-0 h-px"
           style={{ background: "linear-gradient(to right, transparent, rgba(0,210,255,0.15), transparent)" }} />

      <div className="max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-16">

          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <a href="/" className="flex items-center gap-2.5 mb-5 group w-fit">
              <div className="relative w-8 h-8">
                <div className="absolute inset-0 rounded-lg bg-[#00d2ff] opacity-20 blur-md group-hover:opacity-35 transition-opacity" />
                <div className="relative w-8 h-8 rounded-lg bg-gradient-to-br from-[#00c9f5] to-[#0ea5e9] flex items-center justify-center">
                  <span className="text-[11px] font-black text-black tracking-tight">AQ</span>
                </div>
              </div>
              <span className="font-bold text-white/90 tracking-tight text-lg">ARQYV</span>
            </a>
            <p className="text-sm text-white/30 leading-relaxed mb-5 max-w-[200px]">
              AI-powered personal media library. Local-first, forever free, open source.
            </p>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-white/35 hover:text-white/70 transition-colors"
            >
              <GitHubIcon size={14} />
              Alaustrup/arqyv
            </a>
          </div>

          {/* Link columns */}
          {Object.entries(LINKS).map(([title, links]) => (
            <div key={title}>
              <div className="text-[11px] font-semibold uppercase tracking-widest text-white/25 mb-5">
                {title}
              </div>
              <ul className="space-y-3">
                {links.map((l) => (
                  <li key={l.label}>
                    <a
                      href={l.href}
                      target={"target" in l ? (l as { target: string }).target : undefined}
                      download={"download" in l ? (l as { download: string }).download : undefined}
                      rel={"target" in l ? "noopener noreferrer" : undefined}
                      className="text-sm text-white/35 hover:text-white/75 transition-colors"
                    >
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="sep mb-8" />
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/22">
          <span>© {new Date().getFullYear()} ARQYV · MIT License · Made by Alaustrup</span>
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e] animate-pulse inline-block" />
              v0.1.0
            </span>
            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
               className="hover:text-white/50 transition-colors flex items-center gap-1.5">
              <GitHubIcon size={13} /> Open Source
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
