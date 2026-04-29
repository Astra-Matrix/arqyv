"use client";

import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { OSDownloadButton } from "./OSDownloadButton";

const GITHUB_URL = "https://github.com/ALaustrup/arqyv";

const NAV_LINKS = [
  { href: "#features", label: "Features" },
  { href: "#download", label: "Download" },
  { href: "#docs",     label: "Docs" },
  { href: "#faq",      label: "FAQ" },
];

export default function Nav() {
  const [scrolled,  setScrolled]  = useState(false);
  const [menuOpen,  setMenuOpen]  = useState(false);

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  return (
    <nav
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-500 ${
        scrolled
          ? "bg-[#050508]/90 backdrop-blur-xl border-b border-white/[0.04]"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-6xl mx-auto px-6 h-[60px] flex items-center justify-between">

        {/* Logo */}
        <a href="/" className="flex items-center gap-2.5 group shrink-0">
          <div className="relative w-7 h-7">
            <div className="absolute inset-0 rounded-lg bg-[#00d2ff] opacity-20 group-hover:opacity-40 blur-md transition-opacity" />
            <div className="relative w-7 h-7 rounded-lg bg-gradient-to-br from-[#00d2ff] to-[#0ea5e9] flex items-center justify-center">
              <span className="text-[10px] font-black text-black tracking-tight">AQ</span>
            </div>
          </div>
          <span className="font-semibold text-white/90 tracking-tight">ARQYV</span>
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm text-white/40 hover:text-white/90 transition-colors tracking-wide"
            >
              {l.label}
            </a>
          ))}
        </div>

        {/* CTAs */}
        <div className="hidden md:flex items-center gap-3 shrink-0">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub"
            className="flex items-center gap-1.5 text-sm text-white/40 hover:text-white/80 transition-colors px-3 py-1.5 rounded-lg hover:bg-white/[0.04]"
          >
            <GitHubIcon size={15} />
            <span>GitHub</span>
          </a>
          <OSDownloadButton size="sm" />
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden text-white/50 hover:text-white transition-colors"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-[#050508]/98 backdrop-blur-xl border-b border-white/[0.04] px-6 py-5 flex flex-col gap-5">
          {NAV_LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setMenuOpen(false)}
              className="text-sm text-white/50 hover:text-white transition-colors"
            >
              {l.label}
            </a>
          ))}
          <div className="flex gap-3 pt-2 border-t border-white/[0.04]">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-white/50 border border-white/[0.06] px-4 py-2 rounded-lg flex-1 justify-center hover:text-white hover:border-white/[0.15] transition-all"
            >
              <GitHubIcon size={14} /> GitHub
            </a>
            <OSDownloadButton size="sm" className="flex-1 justify-center" />
          </div>
        </div>
      )}
    </nav>
  );
}
