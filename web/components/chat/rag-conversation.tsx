"use client";

import { useChat } from "@ai-sdk/react";
import type { PromptInputMessage } from "@/components/ai-elements/prompt-input";
import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSelect,
  PromptInputSelectContent,
  PromptInputSelectItem,
  PromptInputSelectTrigger,
  PromptInputSelectValue,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputTools,
} from "@/components/ai-elements/prompt-input";
import {
  Source,
  Sources,
  SourcesContent,
  SourcesTrigger,
} from "@/components/ai-elements/sources";
import { Tool, ToolContent, ToolHeader, ToolInput, ToolOutput } from "@/components/ai-elements/tool";
import type { ChunkOut, RetrieveMeta } from "@/lib/types";
import type { DynamicToolUIPart, ToolUIPart, UIMessage } from "ai";

type RagMessage = UIMessage<RetrieveMeta>;

function isToolPart(
  part: RagMessage["parts"][number],
): part is ToolUIPart | DynamicToolUIPart {
  return part.type === "dynamic-tool" || part.type.startsWith("tool-");
}

function chunksFromOutput(output: unknown): ChunkOut[] {
  if (!output || typeof output !== "object" || !("chunks" in output)) {
    return [];
  }
  const chunks = (output as { chunks: unknown }).chunks;
  return Array.isArray(chunks) ? (chunks as ChunkOut[]) : [];
}

function isRetrieveMeta(value: unknown): value is RetrieveMeta {
  if (!value || typeof value !== "object") {
    return false;
  }
  const record = value as Record<string, unknown>;
  return (
    typeof record.hybrid === "boolean" &&
    typeof record.fts === "boolean" &&
    typeof record.multi_query === "boolean" &&
    Array.isArray(record.queries)
  );
}

function retrievalLabel(meta: RetrieveMeta): string {
  const hybrid = meta.hybrid ? "hybrid" : "vector-only";
  const fts = meta.fts ? "fts" : "no-fts";
  const queries = meta.multi_query
    ? `multi-query ×${meta.queries.length}`
    : "single query";
  return `${hybrid} · ${fts} · ${queries}`;
}

type RagConversationProps = {
  documentId: string | null;
  model: string;
  models: string[];
  onModelChange: (model: string) => void;
};

export function RagConversation({
  documentId,
  model,
  models,
  onModelChange,
}: RagConversationProps) {
  const { messages, sendMessage, status, error } = useChat<RagMessage>({
    id: documentId ?? "none",
  });

  const lastRetrieval = (() => {
    const found = [...messages].reverse().find((message) => isRetrieveMeta(message.metadata));
    return found && isRetrieveMeta(found.metadata) ? found.metadata : null;
  })();

  const handleSubmit = (message: PromptInputMessage) => {
    if (!documentId || !message.text.trim()) {
      return;
    }
    void sendMessage({ text: message.text }, { body: { documentId, model } });
  };

  return (
    <div className="relative flex min-h-0 flex-1 flex-col bg-[var(--paper)]">
      <div className="pointer-events-none absolute inset-0 foundry-grid opacity-30" />
      <Conversation className="relative min-h-0">
        <ConversationContent>
          {messages.length === 0 ? (
            <ConversationEmptyState className="text-[var(--ink)]">
              <div className="max-w-md space-y-3">
                <p className="font-mono text-[10px] tracking-[0.32em] text-[var(--copper)] uppercase">
                  {documentId ? "Ready" : "Waiting"}
                </p>
                <h3 className="font-[family-name:var(--font-display)] text-4xl leading-none">
                  {documentId ? "Ask the plate" : "Choose a plate"}
                </h3>
                <p className="text-[15px] leading-relaxed text-[var(--ink-soft)]">
                  {documentId
                    ? "The model calls retrieveDocument, then answers only from LanceDB chunks."
                    : "Index a source in the press bed, then write in the console below."}
                </p>
              </div>
            </ConversationEmptyState>
          ) : (
            messages.map((message) => {
              const toolSources = message.parts.flatMap((part) =>
                isToolPart(part) ? chunksFromOutput(part.output) : [],
              );
              const retrieveMeta = isRetrieveMeta(message.metadata) ? message.metadata : null;
              return (
                <div key={message.id} className="space-y-3">
                  {retrieveMeta ? (
                    <div className="px-1 pt-1">
                      <p className="font-mono text-[10px] tracking-[0.24em] text-[var(--copper)] uppercase">
                        {retrievalLabel(retrieveMeta)}
                      </p>
                      {retrieveMeta.queries.length > 1 ? (
                        <p className="mt-1 text-[12px] leading-relaxed text-[var(--ink-soft)]">
                          {retrieveMeta.queries.join(" · ")}
                        </p>
                      ) : null}
                    </div>
                  ) : null}
                  {message.parts.map((part, index) => {
                    if (part.type === "text") {
                      return (
                        <Message key={`${message.id}-text-${index}`} from={message.role}>
                          <MessageContent>
                            <MessageResponse>{part.text}</MessageResponse>
                          </MessageContent>
                        </Message>
                      );
                    }
                    if (isToolPart(part)) {
                      return (
                        <Tool key={`${message.id}-tool-${index}`} defaultOpen>
                          {part.type === "dynamic-tool" ? (
                            <ToolHeader
                              title="retrieveDocument"
                              type="dynamic-tool"
                              state={part.state}
                              toolName={part.toolName}
                            />
                          ) : (
                            <ToolHeader
                              title="retrieveDocument"
                              type={part.type}
                              state={part.state}
                            />
                          )}
                          <ToolContent>
                            {part.input != null ? <ToolInput input={part.input} /> : null}
                            <ToolOutput output={part.output} errorText={part.errorText} />
                          </ToolContent>
                        </Tool>
                      );
                    }
                    return null;
                  })}
                  {message.role === "assistant" && toolSources.length > 0 ? (
                    <Sources>
                      <SourcesTrigger count={toolSources.length} />
                      <SourcesContent>
                        {toolSources.map((chunk, index) => (
                          <Source
                            key={`${message.id}-src-${index}`}
                            href={`#${chunk.filename ?? "chunk"}`}
                            title={chunk.source}
                          />
                        ))}
                      </SourcesContent>
                    </Sources>
                  ) : null}
                </div>
              );
            })
          )}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>

      {error ? (
        <p className="relative px-5 py-2 text-sm text-destructive">{error.message}</p>
      ) : null}

      <div className="relative shrink-0 border-t-2 border-[var(--ink)] bg-[var(--ink)] px-4 pt-4 pb-6 sm:px-6">
        <div className="mx-auto w-full max-w-5xl">
          <div className="mb-3 flex items-end justify-between">
            <p className="font-mono text-[10px] tracking-[0.32em] text-[var(--copper)] uppercase">
              Console
            </p>
            <p className="font-mono text-[10px] tracking-wider text-[var(--paper)]/40">
              {lastRetrieval
                ? retrievalLabel(lastRetrieval)
                : documentId
                  ? "retrieveDocument armed"
                  : "no plate selected"}
            </p>
          </div>
          <PromptInput
            onSubmit={handleSubmit}
            className="rounded-none border-2 border-[var(--copper)] bg-[var(--paper)] shadow-[6px_6px_0_0_#3a2418] [&_[data-slot=input-group]]:h-auto [&_[data-slot=input-group]]:min-h-[8.5rem] [&_[data-slot=input-group]]:rounded-none [&_[data-slot=input-group]]:border-0 [&_[data-slot=input-group]]:bg-transparent"
          >
            <PromptInputBody>
              <PromptInputTextarea
                className="min-h-24 bg-[var(--paper)] text-[15px] text-[var(--ink)] placeholder:text-[var(--ink)]/55"
                disabled={!documentId || status === "streaming" || status === "submitted"}
                placeholder={
                  documentId
                    ? "Ask a question about the selected plate"
                    : "Choose a plate in the press bed first"
                }
              />
            </PromptInputBody>
            <PromptInputFooter className="border-t border-[var(--rule)] bg-[var(--paper-2)]">
              <PromptInputTools>
                <PromptInputSelect
                  value={model}
                  onValueChange={(value) => onModelChange(String(value))}
                >
                  <PromptInputSelectTrigger>
                    <PromptInputSelectValue />
                  </PromptInputSelectTrigger>
                  <PromptInputSelectContent>
                    {models.map((item) => (
                      <PromptInputSelectItem key={item} value={item}>
                        {item}
                      </PromptInputSelectItem>
                    ))}
                  </PromptInputSelectContent>
                </PromptInputSelect>
              </PromptInputTools>
              <PromptInputSubmit status={status} disabled={!documentId} />
            </PromptInputFooter>
          </PromptInput>
        </div>
      </div>
    </div>
  );
}
