"use client";

import { useRef, useState, type FormEvent } from "react";

import { Spinner } from "@/components/ui/spinner";
import { errorDetailFromBody } from "@/lib/fastapi";
import type { DocumentOut } from "@/lib/types";

type SourceKind = "pdf" | "url" | "website";

type DocumentPanelProps = {
  documents: DocumentOut[];
  selectedId: string | null;
  busy: boolean;
  onSelect: (id: string) => void;
  onRefresh: () => Promise<void>;
};

const SOURCE_MARK: Record<string, string> = {
  pdf: "PDF",
  url: "URL",
  website: "SITE",
};

export function DocumentPanel({
  documents,
  selectedId,
  busy,
  onSelect,
  onRefresh,
}: DocumentPanelProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [kind, setKind] = useState<SourceKind>("pdf");
  const [url, setUrl] = useState("");
  const [site, setSite] = useState("");
  const [sitemap, setSitemap] = useState("sitemap.xml");
  const [pdfName, setPdfName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  async function ingest(path: string, init: RequestInit) {
    setError(null);
    setPending(true);
    try {
      const response = await fetch(path, init);
      const text = await response.text();
      if (!response.ok) {
        throw new Error(errorDetailFromBody(text, response.status));
      }
      let payload: { document_id?: string };
      try {
        payload = JSON.parse(text) as { document_id?: string };
      } catch {
        throw new Error("Ingest returned an unexpected response.");
      }
      await onRefresh();
      if (payload.document_id) {
        onSelect(payload.document_id);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Ingest failed");
    } finally {
      setPending(false);
    }
  }

  async function mutateDocuments(path: string) {
    setError(null);
    setPending(true);
    try {
      const response = await fetch(path, { method: "DELETE" });
      const text = await response.text();
      if (!response.ok) {
        throw new Error(errorDetailFromBody(text, response.status));
      }
      setConfirmClear(false);
      await onRefresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not lift that plate.");
    } finally {
      setPending(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (kind === "pdf") {
      const file = fileRef.current?.files?.[0];
      if (!file) {
        setError("Choose a PDF first.");
        return;
      }
      const body = new FormData();
      body.append("file", file);
      await ingest("/api/ingest/pdf", { method: "POST", body });
      if (fileRef.current) {
        fileRef.current.value = "";
      }
      setPdfName(null);
      return;
    }
    if (kind === "url") {
      if (url.trim().length < 8) {
        setError("Enter a full URL, including https://");
        return;
      }
      await ingest("/api/ingest/url", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ url }),
      });
      return;
    }
    if (site.trim().length < 8) {
      setError("Enter the site origin, including https://");
      return;
    }
    await ingest("/api/ingest/website", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ base_url: site, sitemap_filename: sitemap }),
    });
  }

  return (
    <aside className="flex max-h-[46vh] min-h-0 w-full flex-col overflow-hidden bg-[var(--ink)] text-[var(--paper)] lg:h-full lg:max-h-none lg:w-[22rem] lg:shrink-0">
      <div className="border-b border-white/10 px-5 py-6">
        <p className="font-mono text-[10px] tracking-[0.32em] text-[var(--copper)] uppercase">
          Press bed
        </p>
        <h2 className="mt-2 font-[family-name:var(--font-display)] text-[1.65rem] leading-none">
          Plates
        </h2>
        <p className="mt-3 text-[13px] leading-relaxed text-[var(--paper)]/55">
          Local LanceDB only. Nothing leaves this machine except the model call.
        </p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="px-5 py-4">
          <div className="flex items-baseline justify-between gap-3">
            <p className="font-mono text-[10px] tracking-[0.24em] text-[var(--paper)]/40 uppercase">
              On the bed
            </p>
            {documents.length > 0 ? (
              <button
                type="button"
                disabled={pending || busy}
                onClick={() => {
                  if (!confirmClear) {
                    setConfirmClear(true);
                    return;
                  }
                  void mutateDocuments("/api/documents");
                }}
                className="font-mono text-[10px] tracking-[0.2em] text-[var(--copper)] uppercase hover:text-[var(--paper)] disabled:opacity-40"
              >
                {confirmClear ? "Confirm clear" : "Clear bed"}
              </button>
            ) : null}
          </div>
          {documents.length === 0 ? (
            <div className="mt-3 border border-dashed border-white/15 px-4 py-8">
              <p className="font-[family-name:var(--font-display)] text-xl italic leading-tight">
                The bed is empty.
              </p>
              <p className="mt-2 text-[13px] leading-relaxed text-[var(--paper)]/50">
                Index a source below. Each plate becomes a retrievable table.
              </p>
            </div>
          ) : (
            <ol className="mt-3 space-y-1">
              {documents.map((doc, index) => {
                const active = selectedId === doc.id;
                return (
                  <li key={doc.id} className="flex items-stretch">
                    <button
                      type="button"
                      onClick={() => onSelect(doc.id)}
                      className={`flex min-w-0 flex-1 items-start gap-3 px-3 py-3 text-left transition ${
                        active
                          ? "bg-[var(--paper)] text-[var(--ink)]"
                          : "text-[var(--paper)]/80 hover:bg-white/5"
                      }`}
                    >
                      <span
                        className={`font-mono text-[10px] tracking-widest ${
                          active ? "text-[var(--copper)]" : "text-[var(--paper)]/35"
                        }`}
                      >
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate font-[family-name:var(--font-display)] text-[15px] leading-tight">
                          {doc.source_name}
                        </span>
                        <span
                          className={`mt-1 block font-mono text-[10px] tracking-wider uppercase ${
                            active ? "text-[var(--ink-soft)]" : "text-[var(--paper)]/40"
                          }`}
                        >
                          {SOURCE_MARK[doc.source_type] ?? doc.source_type} · {doc.row_count}{" "}
                          chunks
                        </span>
                      </span>
                    </button>
                    <button
                      type="button"
                      disabled={pending || busy}
                      aria-label={`Lift ${doc.source_name} off the bed`}
                      onClick={() =>
                        void mutateDocuments(`/api/documents/${encodeURIComponent(doc.id)}`)
                      }
                      className={`shrink-0 px-2.5 font-mono text-[10px] tracking-widest uppercase disabled:opacity-40 ${
                        active
                          ? "bg-[var(--paper)] text-[var(--ink-soft)] hover:text-[var(--copper)]"
                          : "text-[var(--paper)]/30 hover:text-[var(--copper)]"
                      }`}
                    >
                      Lift
                    </button>
                  </li>
                );
              })}
            </ol>
          )}
        </div>
      </div>

      <form onSubmit={(event) => void onSubmit(event)} className="border-t border-white/10 px-5 py-5">
        <p className="font-mono text-[10px] tracking-[0.24em] text-[var(--paper)]/40 uppercase">
          Add a plate
        </p>
        <div className="mt-3 grid grid-cols-3 border border-white/15">
          {(
            [
              ["pdf", "PDF"],
              ["url", "URL"],
              ["website", "Site"],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => {
                setKind(value);
                setError(null);
              }}
              className={`py-2 font-mono text-[10px] tracking-[0.2em] uppercase ${
                kind === value
                  ? "bg-[var(--copper)] text-[var(--paper)]"
                  : "text-[var(--paper)]/55 hover:bg-white/5"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="mt-3 space-y-2">
          {kind === "pdf" ? (
            <>
              <input
                ref={fileRef}
                name="pdf"
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(event) => setPdfName(event.target.files?.[0]?.name ?? null)}
              />
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="flex w-full items-center justify-between border border-white/15 bg-black/20 px-3 py-2.5 text-left text-[13px]"
              >
                <span className={pdfName ? "truncate text-[var(--paper)]" : "text-[var(--paper)]/40"}>
                  {pdfName ?? "No PDF selected"}
                </span>
                <span className="font-mono text-[10px] tracking-widest text-[var(--copper)] uppercase">
                  Browse
                </span>
              </button>
            </>
          ) : null}

          {kind === "url" ? (
            <input
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://"
              className="h-10 w-full border border-white/15 bg-black/20 px-3 text-[13px] text-[var(--paper)] outline-none placeholder:text-[var(--paper)]/30 focus:border-[var(--copper)]"
            />
          ) : null}

          {kind === "website" ? (
            <div className="grid grid-cols-[1fr_7rem] gap-px bg-white/15">
              <input
                value={site}
                onChange={(event) => setSite(event.target.value)}
                placeholder="https://example.com"
                className="h-10 bg-black/30 px-3 text-[13px] text-[var(--paper)] outline-none placeholder:text-[var(--paper)]/30"
              />
              <input
                value={sitemap}
                onChange={(event) => setSitemap(event.target.value)}
                className="h-10 bg-black/30 px-3 font-mono text-[11px] text-[var(--paper)] outline-none"
              />
            </div>
          ) : null}
        </div>

        <button
          type="submit"
          disabled={pending || busy}
          className="mt-3 flex h-11 w-full items-center justify-center bg-[var(--paper)] font-mono text-[11px] tracking-[0.22em] text-[var(--ink)] uppercase disabled:opacity-50"
        >
          {pending ? <Spinner /> : "Index source"}
        </button>
        {error ? <p className="mt-3 text-[13px] text-[#f0b4a4]">{error}</p> : null}
      </form>
    </aside>
  );
}
