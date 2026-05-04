"use client";

import { useInView } from "@/hooks/useInView";

const STEPS = [
  {
    n: "1",
    label: "Install",
    code: "curl -fsSL https://arqyv.app/install.sh | bash",
    lang: "bash",
    note: "Windows: irm https://arqyv.app/install.ps1 | iex",
  },
  {
    n: "2",
    label: "Launch",
    code: "arqyv\n# or: python run.py --debug",
    lang: "bash",
    note: "API starts on localhost:8765 · UI window appears automatically",
  },
  {
    n: "3",
    label: "Add your library",
    code: "# Ctrl+O in the app\n# or: Settings → Library → Add Folder",
    lang: "bash",
    note: "Indexing runs in the background — watch the status bar",
  },
  {
    n: "4",
    label: "Search",
    code: 'GET http://localhost:8765/api/v1/search?q=beach+sunset',
    lang: "http",
    note: "Or type in the search bar — results appear as you type",
  },
];

export default function GettingStarted() {
  const { ref, inView } = useInView<HTMLDivElement>({ threshold: 0.1 });

  return (
    <section className="section-sm relative" ref={ref}>
      <div className="max-w-4xl mx-auto">

        <div className={`text-center mb-14 reveal ${inView ? "in-view" : ""}`}>
          <div className="label-pill inline-flex">Quick start</div>
          <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-4">
            Zero to searching<br />
            <span className="text-white/22">in under a minute.</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {STEPS.map((step, i) => (
            <div
              key={step.n}
              className={`reveal ${inView ? "in-view" : ""} rounded-2xl p-6`}
              style={{
                transitionDelay: `${i * 0.08}s`,
                background: "rgba(255,255,255,0.018)",
                border: "1px solid rgba(255,255,255,0.055)",
              }}
            >
              <div className="flex items-center gap-3 mb-4">
                <span
                  className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-black shrink-0"
                  style={{ background: "rgba(0,210,255,0.12)", color: "#00d2ff", border: "1px solid rgba(0,210,255,0.2)" }}
                >
                  {step.n}
                </span>
                <span className="font-semibold text-white/80 text-sm">{step.label}</span>
              </div>
              <div
                className="rounded-xl px-4 py-3 mb-3 font-mono text-[12px] text-[#00d2ff]/80"
                style={{ background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.04)" }}
              >
                {step.code.split("\n").map((line, j) => (
                  <div key={j}>{line}</div>
                ))}
              </div>
              <p className="text-[11px] text-white/28 leading-relaxed">{step.note}</p>
            </div>
          ))}
        </div>

        <div className={`reveal ${inView ? "in-view" : ""} text-center mt-10`}
             style={{ transitionDelay: "0.35s" }}>
          <a
            href="https://github.com/Alaustrup/arqyv/blob/main/docs/getting-started.md"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm text-white/40 hover:text-white/80 transition-colors"
          >
            Read the full Getting Started guide →
          </a>
        </div>
      </div>
    </section>
  );
}
