"use client";

import { useState } from "react";
import { useInView } from "@/hooks/useInView";
import { Copy, Check } from "lucide-react";

const TABS = [
  { id: "mac",     label: "macOS / Linux" },
  { id: "windows", label: "Windows" },
  { id: "source",  label: "From Source" },
] as const;
type TabId = typeof TABS[number]["id"];

const COMMANDS: Record<TabId, { lines: { text: string; color?: string }[] }> = {
  mac: {
    lines: [
      { text: "$ curl -fsSL https://arqyv.app/install.sh | bash", color: "#00d2ff" },
      { text: "" },
      { text: "    _    ____   _____   ____", color: "#00d2ff" },
      { text: "   / \\  |  _ \\ / _ \\ \\ / /\\ \\ / /", color: "#00d2ff" },
      { text: "  / _ \\ | |_) | | | \\ V /  \\ V /", color: "#00d2ff" },
      { text: " / ___ \\|  _ <| |_| || |    | |", color: "#00d2ff" },
      { text: "/_/   \\_\\_| \\_\\\\__\\_\\|_|    |_|", color: "#00d2ff" },
      { text: "" },
      { text: "  -> Checking prerequisites…" },
      { text: "  OK Python 3.12.3 found", color: "#22c55e" },
      { text: "  -> Cloning ARQYV…" },
      { text: "  OK Source ready at ~/.local/share/arqyv", color: "#22c55e" },
      { text: "  -> Installing dependencies…" },
      { text: "  OK Dependencies installed", color: "#22c55e" },
      { text: "  -> Installing AI packages…" },
      { text: "  OK AI packages installed", color: "#22c55e" },
      { text: "  OK Launcher created at ~/.local/bin/arqyv", color: "#22c55e" },
      { text: "" },
      { text: "  ARQYV installed. Run: arqyv", color: "#22c55e" },
      { text: "" },
      { text: "$ arqyv", color: "#00d2ff" },
      { text: "" },
      { text: "  ARQYV starting…  API ready on :8765  ✓", color: "#a855f7" },
    ],
  },
  windows: {
    lines: [
      { text: "PS> irm https://arqyv.app/install.ps1 | iex", color: "#00d2ff" },
      { text: "" },
      { text: "    ___  ____  ___  _   _ _     __", color: "#00d2ff" },
      { text: "   / _ \\|  _ \\/ _ \\| | | \\ \\   / /", color: "#00d2ff" },
      { text: "  / /_\\ \\ |_)| | | | |_| |\\ \\ / /", color: "#00d2ff" },
      { text: " /  _  |  _ \\| |_| |  _  | \\ V /", color: "#00d2ff" },
      { text: "/_/   \\_\\_| \\_\\\\__\\_\\_| |_|  \\_/", color: "#00d2ff" },
      { text: "" },
      { text: "  -> Checking prerequisites…" },
      { text: "  OK Python 3.12.3 found", color: "#22c55e" },
      { text: "  -> Cloning ARQYV into %LOCALAPPDATA%\\ARQYV…" },
      { text: "  OK Source ready", color: "#22c55e" },
      { text: "  -> Installing dependencies…" },
      { text: "  OK Dependencies installed", color: "#22c55e" },
      { text: "  OK Launcher: %LOCALAPPDATA%\\...\\arqyv.bat", color: "#22c55e" },
      { text: "  OK Start Menu shortcut created", color: "#22c55e" },
      { text: "" },
      { text: "  ARQYV installed. Run: arqyv", color: "#22c55e" },
    ],
  },
  source: {
    lines: [
      { text: "$ git clone https://github.com/Alaustrup/arqyv", color: "#00d2ff" },
      { text: "$ cd arqyv" },
      { text: "$ pip install -e .", color: "#00d2ff" },
      { text: "" },
      { text: "  Installing arqyv-0.1.0…" },
      { text: "  Successfully installed arqyv-0.1.0", color: "#22c55e" },
      { text: "" },
      { text: "# Optional: AI analysis features" },
      { text: "$ pip install sentence-transformers openai-whisper chromadb", color: "#00d2ff" },
      { text: "" },
      { text: "# Launch" },
      { text: "$ python run.py", color: "#00d2ff" },
      { text: "" },
      { text: "  [INFO]  services_ready" },
      { text: "  [INFO]  api_ready port=8765" },
      { text: "  [INFO]  event_loop_enter" },
      { text: "  [INFO]  ARQYV running  ✓", color: "#22c55e" },
    ],
  },
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={async () => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="p-1.5 rounded text-white/25 hover:text-white/70 hover:bg-white/[0.05] transition-all"
      title="Copy command"
    >
      {copied ? <Check size={13} className="text-[#22c55e]" /> : <Copy size={13} />}
    </button>
  );
}

const COPY_COMMANDS: Record<TabId, string> = {
  mac:     "curl -fsSL https://arqyv.app/install.sh | bash",
  windows: "irm https://arqyv.app/install.ps1 | iex",
  source:  "git clone https://github.com/Alaustrup/arqyv && cd arqyv && pip install -e .",
};

export default function TerminalShowcase() {
  const { ref, inView } = useInView<HTMLDivElement>({ threshold: 0.1 });
  const [tab, setTab] = useState<TabId>("mac");
  const lines = COMMANDS[tab].lines;

  return (
    <section className="section-sm relative" ref={ref}>
      <div className="max-w-4xl mx-auto px-6">

        <div className={`reveal ${inView ? "in-view" : ""}`}>
          <div className="text-center mb-10">
            <div className="label-pill inline-flex">Install in seconds</div>
            <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-4">
              One command.<br />
              <span className="text-white/25">Up and running.</span>
            </h2>
            <p className="text-white/40 text-base max-w-sm mx-auto">
              Python 3.11+ required. Everything else — bundled and automatic.
            </p>
          </div>

          {/* Terminal window */}
          <div className="rounded-2xl overflow-hidden shadow-2xl"
               style={{
                 border: "1px solid rgba(255,255,255,0.07)",
                 background: "#07070e",
                 boxShadow: "0 32px 80px rgba(0,0,0,0.7)",
               }}>
            {/* Header */}
            <div className="flex items-center gap-3 px-4 py-3"
                 style={{ background: "rgba(255,255,255,0.02)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
                <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
                <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
              </div>

              {/* Tab bar */}
              <div className="flex items-center gap-1 ml-2">
                {TABS.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTab(t.id)}
                    className={`text-[11px] font-medium px-3 py-1.5 rounded-md transition-all ${
                      tab === t.id
                        ? "text-white bg-white/[0.07] border border-white/[0.08]"
                        : "text-white/30 hover:text-white/60"
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              <div className="ml-auto">
                <CopyButton text={COPY_COMMANDS[tab]} />
              </div>
            </div>

            {/* Terminal body */}
            <div className="p-6 font-mono text-[12px] leading-relaxed min-h-[280px]">
              {lines.map((line, i) => (
                <div key={`${tab}-${i}`} className="flex">
                  <span style={{ color: line.color ?? "rgba(255,255,255,0.38)" }}>
                    {line.text || "\u00a0"}
                  </span>
                </div>
              ))}
              <span className="cursor-blink text-[#00d2ff]">█</span>
            </div>
          </div>

          {/* Quick copy strip */}
          <div className="mt-4 flex items-center justify-between px-4 py-3 rounded-xl"
               style={{ background: "rgba(255,255,255,0.015)", border: "1px solid rgba(255,255,255,0.05)" }}>
            <code className="text-[12px] font-mono text-white/45">{COPY_COMMANDS[tab]}</code>
            <CopyButton text={COPY_COMMANDS[tab]} />
          </div>
        </div>
      </div>
    </section>
  );
}
