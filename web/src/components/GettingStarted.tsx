"use client";

import { useState } from "react";
import { Copy, Check, Terminal, Package, Play } from "lucide-react";

function CodeBlock({ code, lang = "bash" }: { code: string; lang?: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group rounded-xl bg-[#0f3460]/60 border border-[#2a2a4a] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#2a2a4a] bg-[#0f3460]/40">
        <span className="text-[10px] text-[#9e9e9e] uppercase tracking-widest font-mono">{lang}</span>
        <button
          onClick={copy}
          className="flex items-center gap-1.5 text-xs text-[#9e9e9e] hover:text-[#00b4d8] transition-colors opacity-0 group-hover:opacity-100"
        >
          {copied ? <Check size={12} className="text-[#4caf50]" /> : <Copy size={12} />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="p-4 text-sm text-[#e0e0e0] font-mono overflow-x-auto leading-relaxed whitespace-pre">
        {code}
      </pre>
    </div>
  );
}

const TABS = [
  { id: "binary", label: "Binary (Recommended)", icon: Package },
  { id: "source", label: "From Source", icon: Terminal },
  { id: "run", label: "Running the App", icon: Play },
];

const CONTENT: Record<string, React.ReactNode> = {
  binary: (
    <div className="space-y-6">
      <p className="text-[#9e9e9e] text-sm leading-relaxed">
        Download the pre-built executable for your platform. No Python, no
        dependencies — just unzip and run.
      </p>
      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-[#e0e0e0]">Windows</h4>
        <CodeBlock lang="powershell" code={`# Download and extract
Invoke-WebRequest -Uri "https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-windows.zip" -OutFile arqyv.zip
Expand-Archive arqyv.zip -DestinationPath .
# Launch
.\\ARQYV\\ARQYV.exe`} />

        <h4 className="text-sm font-semibold text-[#e0e0e0]">macOS</h4>
        <CodeBlock lang="bash" code={`curl -L https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-macos.zip -o arqyv.zip
unzip arqyv.zip
open ARQYV.app`} />

        <h4 className="text-sm font-semibold text-[#e0e0e0]">Linux</h4>
        <CodeBlock lang="bash" code={`wget https://github.com/ALaustrup/arqyv/releases/latest/download/arqyv-linux.zip
unzip arqyv-linux.zip
chmod +x ARQYV/ARQYV
./ARQYV/ARQYV`} />
      </div>
    </div>
  ),

  source: (
    <div className="space-y-5">
      <p className="text-[#9e9e9e] text-sm leading-relaxed">
        Run from source for development or if you want to modify ARQYV.
        Requires Python 3.11+.
      </p>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">1. Clone the repository</h4>
        <CodeBlock code={`git clone https://github.com/ALaustrup/arqyv.git
cd arqyv`} />
      </div>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">2. Create a virtual environment</h4>
        <CodeBlock code={`python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS / Linux
source .venv/bin/activate`} />
      </div>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">3. Install dependencies</h4>
        <CodeBlock code={`pip install -e .

# Download the spaCy NLP model (for AI tagging)
python -m spacy download en_core_web_sm`} />
      </div>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">4. Configure (optional)</h4>
        <CodeBlock code={`cp .env.example .env
# Edit .env to configure cloud credentials, AI model sizes, etc.`} />
      </div>
    </div>
  ),

  run: (
    <div className="space-y-5">
      <p className="text-[#9e9e9e] text-sm leading-relaxed">
        Launch ARQYV with optional flags. All settings persist between sessions.
      </p>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">Normal launch</h4>
        <CodeBlock code={`arqyv
# or
python -m arqyv`} />
      </div>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">Debug mode (verbose logging)</h4>
        <CodeBlock code={`arqyv --debug`} />
      </div>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">Custom data directory</h4>
        <CodeBlock code={`arqyv --data-dir /mnt/external/arqyv-data`} />
      </div>

      <div>
        <h4 className="text-sm font-semibold text-[#e0e0e0] mb-2">Environment variables</h4>
        <CodeBlock lang="bash" code={`# Disable AI pipeline for faster startup
ARQYV_ENABLE_AI=false arqyv

# Use a specific GPU device
ARQYV_AI_DEVICE=cuda arqyv

# Disable the local API server
ARQYV_ENABLE_API_SERVER=false arqyv`} />
      </div>

      <div className="rounded-xl bg-[#00b4d8]/8 border border-[#00b4d8]/20 p-4">
        <p className="text-sm text-[#e0e0e0]">
          <span className="text-[#00b4d8] font-semibold">First run:</span>{" "}
          ARQYV auto-creates its database and data directories. Open a folder
          via{" "}
          <kbd className="bg-[#0f3460] border border-[#2a2a4a] rounded px-1.5 py-0.5 text-xs font-mono">
            File → Open Folder
          </kbd>{" "}
          and the indexer will start cataloguing your files in the background.
        </p>
      </div>
    </div>
  ),
};

export default function GettingStarted() {
  const [activeTab, setActiveTab] = useState("binary");

  return (
    <section id="docs" className="py-32 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <p className="text-sm font-medium text-[#00b4d8] uppercase tracking-widest mb-4">
            Getting started
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-[#e0e0e0] mb-5">
            Up and running in minutes.
          </h2>
          <p className="text-[#9e9e9e] text-lg max-w-xl mx-auto">
            Choose your installation method below. The binary is the easiest;
            source gives you the full development setup.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Tabs */}
          <div className="lg:col-span-3 flex flex-row lg:flex-col gap-2">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const active = tab.id === activeTab;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-left transition-all w-full ${
                    active
                      ? "bg-[#00b4d8]/15 border border-[#00b4d8]/30 text-[#00b4d8] font-medium"
                      : "text-[#9e9e9e] hover:text-[#e0e0e0] hover:bg-[#16213e] border border-transparent"
                  }`}
                >
                  <Icon size={15} />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* Content */}
          <div className="lg:col-span-9 bg-[#16213e] border border-[#2a2a4a] rounded-2xl p-6 lg:p-8 min-h-[400px]">
            {CONTENT[activeTab]}
          </div>
        </div>
      </div>
    </section>
  );
}
