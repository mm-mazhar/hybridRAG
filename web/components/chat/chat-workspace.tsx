"use client";

import { useCallback, useEffect, useState } from "react";

import { DocumentPanel } from "@/components/chat/document-panel";
import { RagConversation } from "@/components/chat/rag-conversation";
import type { DocumentOut, PublicConfig } from "@/lib/types";

export function ChatWorkspace() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [model, setModel] = useState("gpt-4o-mini");
  const [models, setModels] = useState<string[]>(["gpt-4o-mini"]);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    setBusy(true);
    try {
      const [docsRes, cfgRes] = await Promise.all([
        fetch("/api/documents"),
        fetch("/api/config"),
      ]);
      if (docsRes.ok) {
        const docs = (await docsRes.json()) as DocumentOut[];
        setDocuments(docs);
        setSelectedId((current) => {
          if (current && docs.some((doc) => doc.id === current)) {
            return current;
          }
          return docs[0]?.id ?? null;
        });
      }
      if (cfgRes.ok) {
        const cfg = (await cfgRes.json()) as PublicConfig;
        setModels(cfg.models.length > 0 ? cfg.models : [cfg.model]);
        setModel((current) => (cfg.models.includes(current) ? current : cfg.model));
      }
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
      <DocumentPanel
        documents={documents}
        selectedId={selectedId}
        busy={busy}
        onSelect={setSelectedId}
        onRefresh={refresh}
      />
      <RagConversation
        documentId={selectedId}
        model={model}
        models={models}
        onModelChange={setModel}
      />
    </div>
  );
}
