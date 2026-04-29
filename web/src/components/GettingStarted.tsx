"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";

function CodeBlock({ code, lang = "bash" }: { code: string; lang?: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(code.trim());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="group relative rounded-xl overflow-hidden"
         style={{ background: "rgba(0,0,0,0.4)", border: "1px solid rgba(255,255,255,0.07)" }}>
      <div className="flex items-center justify-between px-4 py-2.5"
           style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
        <span className="text-[10px] font-mono font-semibold uppercase tracking-widest text-white/20">{lang}</span>
        <button
          onClick={copy}
          className="flex items-center gap-1.5 text-xs text-white/20 hover:text-white/60 transition-colors opacity-0 group-hover:opacity-100"
        >
          {copied ? <Check size={11} className="text-emerald-400" /> : <Copy size={11} />}
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <pre className="p-4 text-sm text-white/70 font-mono overflow-x-auto leading-relaxed whitespace-pre">
        {code.trim()}
      </pre>
    </div>
  );
}

const TABS = [
  { id: "binary", label: "Binary" },
  { id: "source", label: "From Source" },
  { id: "run",    label: "Running" },
];

export default function GettingStarted() {
  const [tab, setTab] = useState("binary");

  return (
    <section id="docs" className="section relative">
      <div className="absolute inset-x-0 top-0 h-px"
           style={{ background: "linear-gradient(to right, transparent, rgba(0,210,255,0.1), transparent)" }} />

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-widest text-[#00d2ff] mb-6"
               style={{ background: "rgba(0,210,255,0.06)", border: "1px solid rgba(0,210,255,0.12)" }}>
            Documentation
          </div>
          <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-5">
            Up and running<br /><span className="text-white/25">in minutes.</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Tab selector */}
          <div className="lg:col-span-3 flex lg:flex-col gap-2">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`text-sm text-left px-4 py-3 rounded-xl transition-all ${
                  tab === t.id
                    ? "text-[#00d2ff] font-medium"
                    : "text-white/35 hover:text-white/60"
                }`}
                style={{
                  background: tab === t.id ? "rgba(0,210,255,0.06)" : "transparent",
                  border: tab === t.id ? "1px solid rgba(0,210,255,0.15)" : "1px solid transparent",
                }}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="lg:col-span-9 rounded-2xl p-8 min-h-[440px] space-y-7"
               style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>

            {tab === "binary" && (
              <>
                <p className="text-white/40 text-sm">
                  Download the pre-built executable — no Python, no dependencies. Unzip and run.
                </p>
                <div className="space-y-5">
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">Windows</h4>
                    <CodeBlock lang="powershell" code={`Invoke-WebRequest -Uri "https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-windows.zip" -OutFile arqyv.zip
Expand-Archive arqyv.zip .
.\\ARQYV\\ARQYV.exe`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">macOS</h4>
                    <CodeBlock code={`curl -L https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-macos.zip -o arqyv.zip
unzip arqyv.zip && open ARQYV.app`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">Linux</h4>
                    <CodeBlock code={`wget https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-linux.zip
unzip arqyv-linux.zip && chmod +x ARQYV/ARQYV && ./ARQYV/ARQYV`} />
                  </div>
                </div>
              </>
            )}

            {tab === "source" && (
              <>
                <p className="text-white/40 text-sm">Requires Python 3.11+. Full dev setup in four steps.</p>
                <div className="space-y-5">
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">1 — Clone</h4>
                    <CodeBlock code={`git clone https://github.com/ALaustrup/arqyv.git
cd arqyv`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">2 — Virtual environment</h4>
                    <CodeBlock code={`python -m venv .venv
# Windows:  .venv\\Scripts\\activate
# mac/Linux: source .venv/bin/activate`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">3 — Install</h4>
                    <CodeBlock code={`pip install -e .
python -m spacy download en_core_web_sm`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">4 — Configure (optional)</h4>
                    <CodeBlock code={`cp .env.example .env
# Edit .env — cloud credentials, AI model sizes, API port…`} />
                  </div>
                </div>
              </>
            )}

            {tab === "run" && (
              <>
                <p className="text-white/40 text-sm">Launch options and environment variables.</p>
                <div className="space-y-5">
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">Launch</h4>
                    <CodeBlock code={`arqyv          # normal
arqyv --debug  # verbose logging
python -m arqyv --data-dir /path/to/data`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white/60 mb-2.5 uppercase tracking-widest">Environment flags</h4>
                    <CodeBlock lang="bash" code={`ARQYV_ENABLE_AI=false arqyv           # faster startup
ARQYV_AI_DEVICE=cuda arqyv            # GPU inference
ARQYV_ENABLE_API_SERVER=false arqyv   # disable REST/WS API
ARQYV_API_PORT=9000 arqyv             # custom port`} />
                  </div>
                  <div className="px-4 py-3 rounded-xl text-sm text-white/60"
                       style={{ background: "rgba(0,210,255,0.05)", border: "1px solid rgba(0,210,255,0.12)" }}>
                    <span className="text-[#00d2ff] font-semibold">First run:</span>{" "}
                    Open a folder via{" "}
                    <kbd className="px-1.5 py-0.5 rounded text-xs font-mono bg-white/[0.06] border border-white/[0.08]">
                      File → Open Folder
                    </kbd>{" "}
                    and indexing starts automatically in the background.
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
