import Link from "next/link";

import { SiteHeader } from "@/components/site-header";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)]">
      <SiteHeader />
      <main className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 foundry-grid opacity-40" />
        <section className="relative mx-auto grid max-w-[90rem] gap-12 px-6 py-16 lg:grid-cols-[1.15fr_0.85fr] lg:py-24">
          <div>
            <p className="font-mono text-[11px] tracking-[0.32em] text-[var(--copper)] uppercase">
              Local hybrid retrieval
            </p>
            <h1 className="mt-4 max-w-xl font-[family-name:var(--font-display)] text-5xl leading-[0.95] tracking-tight md:text-7xl">
              Ask the paper,
              <span className="block italic text-[var(--blueprint)]">not the cloud.</span>
            </h1>
            <p className="mt-6 max-w-lg text-lg leading-relaxed text-[var(--ink-soft)]">
              A showcase RAG bench: Docling hybrid chunking, LanceDB on disk, SQLite memory, and an
              OpenAI-compatible model router. Next.js streams the answer; FastAPI keeps the index.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                href="/chat"
                className="rounded-sm bg-[var(--ink)] px-5 py-3 font-mono text-xs tracking-widest text-[var(--paper)] uppercase"
              >
                Open the foundry
              </Link>
              <a
                href="#diagrams"
                className="rounded-sm border border-[var(--rule)] px-5 py-3 font-mono text-xs tracking-widest uppercase"
              >
                Read the drawings
              </a>
            </div>
          </div>
          <aside className="self-end border border-[var(--rule)] bg-[var(--paper-2)] p-6 shadow-[8px_8px_0_0_var(--ink)]">
            <p className="font-mono text-[11px] tracking-[0.2em] uppercase">Runtime split</p>
            <ul className="mt-4 space-y-3 text-sm leading-relaxed">
              <li>
                <strong>Browser</strong> — AI Elements + <code>useChat</code>
              </li>
              <li>
                <strong>Next.js /api/chat</strong> — OpenRouter via AI SDK, RAG as a tool
              </li>
              <li>
                <strong>FastAPI</strong> — ingest, embeddings, LanceDB, SQLite
              </li>
            </ul>
          </aside>
        </section>

        <section id="diagrams" className="relative border-t border-[var(--rule)] bg-[var(--paper-2)] px-6 py-16">
          <div className="mx-auto max-w-[90rem]">
            <p className="font-mono text-[11px] tracking-[0.28em] text-[var(--copper)] uppercase">
              Drawings
            </p>
            <h2 className="font-[family-name:var(--font-display)] text-4xl">How a question moves</h2>
            <div className="mt-10 grid gap-8">
              <figure className="border border-[var(--rule)] bg-[var(--paper)]">
                <figcaption className="border-b border-[var(--rule)] px-4 py-2 font-mono text-[11px] tracking-widest uppercase">
                  Architecture
                </figcaption>
                <iframe
                  title="Runtime architecture"
                  src="/diagrams/architecture.html?theme=dark"
                  className="h-[820px] w-full bg-[var(--paper)]"
                />
              </figure>
              <figure className="border border-[var(--rule)] bg-[var(--paper)]">
                <figcaption className="border-b border-[var(--rule)] px-4 py-2 font-mono text-[11px] tracking-widest uppercase">
                  Ingest data flow
                </figcaption>
                <iframe
                  title="Ingest data flow"
                  src="/diagrams/dataflow.html?theme=dark&v=compact"
                  className="h-[820px] w-full bg-[var(--paper)]"
                />
              </figure>
              <figure className="border border-[var(--rule)] bg-[var(--paper)]">
                <figcaption className="border-b border-[var(--rule)] px-4 py-2 font-mono text-[11px] tracking-widest uppercase">
                  Chat sequence
                </figcaption>
                <iframe
                  title="Chat sequence"
                  src="/diagrams/sequence.html?theme=dark&v=compact"
                  className="h-[860px] w-full bg-[var(--paper)]"
                />
              </figure>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
