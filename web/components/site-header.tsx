import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="flex shrink-0 items-end justify-between border-b border-[var(--rule)] bg-[var(--paper)] px-6 py-4">
      <Link href="/" className="group">
        <p className="font-mono text-[11px] tracking-[0.28em] text-[var(--copper)] uppercase">
          hybridRAG
        </p>
        <p className="font-[family-name:var(--font-display)] text-xl leading-none group-hover:text-[var(--copper)]">
          Document foundry
        </p>
      </Link>
      <nav className="flex gap-6 font-mono text-[12px] tracking-widest uppercase">
        <Link href="/" className="hover:text-[var(--copper)]">
          Architecture
        </Link>
        <Link href="/chat" className="hover:text-[var(--copper)]">
          Chat
        </Link>
      </nav>
    </header>
  );
}
