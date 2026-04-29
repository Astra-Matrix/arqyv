"use client";

import { useState, useEffect } from "react";
import { Download, Menu, X } from "lucide-react";
import GitHubIcon from "./GitHubIcon";
import { OSDownloadButton } from "./OSDownloadButton";

const GITHUB_URL = "https://github.com/ALaustrup/arqyv";
const RELEASE_URL = "https://github.com/ALaustrup/arqyv/releases/latest";

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const links = [
    { href: "#features", label: "Features" },
    { href: "#download", label: "Download" },
    { href: "#docs", label: "Docs" },
    { href: "#faq", label: "FAQ" },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[#16213e]/95 backdrop-blur-md border-b border-[#2a2a4a]"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-[#00b4d8] flex items-center justify-center font-bold text-[#1a1a2e] text-sm group-hover:shadow-[0_0_16px_rgba(0,180,216,0.6)] transition-shadow">
            AQ
          </div>
          <span className="font-semibold text-[#e0e0e0] tracking-tight text-lg">ARQYV</span>
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm text-[#9e9e9e] hover:text-[#e0e0e0] transition-colors"
            >
              {l.label}
            </a>
          ))}
        </div>

        {/* CTAs */}
        <div className="hidden md:flex items-center gap-3">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-[#9e9e9e] hover:text-[#e0e0e0] transition-colors px-3 py-1.5 rounded-md hover:bg-[#2a2a4a]"
          >
            <GitHubIcon size={16} />
            GitHub
          </a>
          <OSDownloadButton size="sm" />
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden text-[#9e9e9e] hover:text-[#e0e0e0]"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-[#16213e]/98 backdrop-blur-md border-b border-[#2a2a4a] px-6 pb-6 pt-2 flex flex-col gap-4">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm text-[#9e9e9e] hover:text-[#e0e0e0]"
              onClick={() => setMenuOpen(false)}
            >
              {l.label}
            </a>
          ))}
          <div className="flex gap-3 pt-2">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm border border-[#2a2a4a] text-[#9e9e9e] px-4 py-2 rounded-md flex-1 justify-center"
            >
              <GitHubIcon size={15} /> GitHub
            </a>
            <OSDownloadButton size="sm" className="flex-1 justify-center" />
          </div>
        </div>
      )}
    </nav>
  );
}
