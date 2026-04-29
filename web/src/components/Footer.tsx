import { Download } from "lucide-react";
import GitHubIcon from "./GitHubIcon";

const GITHUB_URL = "https://github.com/ALaustrup/arqyv";
const RELEASE_URL = "https://github.com/ALaustrup/arqyv/releases/latest";

const LINKS = [
  {
    heading: "Product",
    items: [
      { label: "Features", href: "#features" },
      { label: "Download", href: "#download" },
      { label: "Documentation", href: "#docs" },
      { label: "FAQ", href: "#faq" },
    ],
  },
  {
    heading: "Resources",
    items: [
      { label: "GitHub Repository", href: GITHUB_URL, external: true },
      { label: "All Releases", href: RELEASE_URL, external: true },
      { label: "Issues & Bugs", href: `${GITHUB_URL}/issues`, external: true },
      { label: "Roadmap", href: `${GITHUB_URL}#roadmap`, external: true },
    ],
  },
  {
    heading: "Developers",
    items: [
      { label: "Source Code", href: GITHUB_URL, external: true },
      { label: "API Reference", href: `${GITHUB_URL}#readme`, external: true },
      { label: "Contributing", href: `${GITHUB_URL}/blob/main/README.md`, external: true },
      { label: "CI / Actions", href: `${GITHUB_URL}/actions`, external: true },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-[#2a2a4a] bg-[#16213e]/50">
      {/* CTA strip */}
      <div className="py-16 px-6 text-center border-b border-[#2a2a4a] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#00b4d8]/5 to-transparent" />
        <div className="relative max-w-2xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-[#e0e0e0] mb-4">
            Ready to own your data?
          </h2>
          <p className="text-[#9e9e9e] mb-8">
            Free. Open source. No accounts. No cloud. Just your files, intelligently organized.
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <a
              href={RELEASE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-[#00b4d8] hover:bg-[#48cae4] text-[#1a1a2e] font-bold px-8 py-3 rounded-xl text-sm transition-all hover:shadow-[0_0_20px_rgba(0,180,216,0.4)]"
            >
              <Download size={16} />
              Download ARQYV — It&apos;s Free
            </a>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 border border-[#2a2a4a] text-[#9e9e9e] hover:text-[#00b4d8] hover:border-[#00b4d8]/40 px-8 py-3 rounded-xl text-sm transition-all"
            >
              <GitHubIcon size={16} />
              View Source
            </a>
          </div>
        </div>
      </div>

      {/* Links */}
      <div className="max-w-7xl mx-auto px-6 py-14 grid grid-cols-2 md:grid-cols-4 gap-10">
        {/* Brand */}
        <div className="col-span-2 md:col-span-1">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-[#00b4d8] flex items-center justify-center font-bold text-[#1a1a2e] text-sm">
              AQ
            </div>
            <span className="font-semibold text-[#e0e0e0] text-lg">ARQYV</span>
          </div>
          <p className="text-sm text-[#9e9e9e] leading-relaxed max-w-[220px]">
            The last great desktop application. Local-first AI media organizer with instant P2P sharing.
          </p>
          <div className="flex gap-3 mt-5">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="w-8 h-8 rounded-lg bg-[#0f3460] border border-[#2a2a4a] flex items-center justify-center text-[#9e9e9e] hover:text-[#00b4d8] hover:border-[#00b4d8]/40 transition-all"
              aria-label="GitHub"
            >
              <GitHubIcon size={15} />
            </a>
          </div>
        </div>

        {LINKS.map((section) => (
          <div key={section.heading}>
            <h3 className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-widest mb-4">
              {section.heading}
            </h3>
            <ul className="space-y-3">
              {section.items.map((item) => (
                <li key={item.label}>
                  <a
                    href={item.href}
                    target={"external" in item && item.external ? "_blank" : undefined}
                    rel={"external" in item && item.external ? "noopener noreferrer" : undefined}
                    className="text-sm text-[#9e9e9e] hover:text-[#00b4d8] transition-colors"
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Bottom bar */}
      <div className="border-t border-[#2a2a4a] px-6 py-5 flex flex-col md:flex-row items-center justify-between gap-3 max-w-7xl mx-auto">
        <p className="text-xs text-[#9e9e9e]">
          © {new Date().getFullYear()} Alaustrup · MIT License · Built with PyQt6, FastAPI, and sentence-transformers
        </p>
        <div className="flex items-center gap-4 text-xs text-[#9e9e9e]">
          <span>v0.1.0</span>
          <span className="w-1 h-1 rounded-full bg-[#2a2a4a]" />
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="hover:text-[#00b4d8] transition-colors">
            Open Source
          </a>
          <span className="w-1 h-1 rounded-full bg-[#2a2a4a]" />
          <span className="text-[#4caf50]">● All systems operational</span>
        </div>
      </div>
    </footer>
  );
}
