import { convertToModelMessages, stepCountIs, streamText, tool, type UIMessage } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { z } from "zod";

import { fastapiJson } from "@/lib/fastapi";
import { EMPTY_RETRIEVE, type ChunkOut, type DocumentOut, type RetrieveMeta, type RetrieveResponse } from "@/lib/types";

export const maxDuration = 60;

const RAG_SYSTEM_PROMPT = `You are a document Q&A assistant for a hybrid RAG demo.

The selected plate name below is the uploaded file or URL. Treat that name as a fact.
The first retrieved passages are the start of the document (title page, header, opening).
Use the retrieved passages as evidence for the document's own title, date, and people.
Never say you cannot access the file or attachment.
If the passages do not contain the answer, say so.
Cite filenames and page numbers when they are present.`;

function lastUserText(messages: UIMessage[]): string {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.role !== "user") {
      continue;
    }
    const text = message.parts
      .flatMap((part) => (part.type === "text" ? [part.text] : []))
      .join("\n")
      .trim();
    if (text) {
      return text;
    }
  }
  return "";
}

async function plateLabel(documentId: string): Promise<string> {
  try {
    const docs = await fastapiJson<DocumentOut[]>("/api/documents");
    const plate = docs.find((item) => item.id === documentId);
    if (!plate) {
      return documentId;
    }
    return `${plate.source_name} (${plate.source_type}, ${plate.row_count} chunks)`;
  } catch {
    return documentId;
  }
}

function passagesFromChunks(chunks: ChunkOut[]): string {
  if (chunks.length === 0) {
    return "No passages were retrieved for this question.";
  }
  return chunks
    .map((chunk, index) => `[${index + 1}] ${chunk.source}\n${chunk.text}`)
    .join("\n\n");
}

export async function POST(req: Request) {
  const body = (await req.json()) as {
    messages: UIMessage[];
    documentId?: string;
    model?: string;
  };
  const { messages, documentId, model } = body;

  if (!documentId) {
    return Response.json({ error: "Select a document before chatting." }, { status: 400 });
  }

  const apiKey = process.env.LLM_API_KEY ?? process.env.OPENAI_API_KEY;
  const baseURL = process.env.LLM_BASE_URL ?? "https://api.openai.com/v1";
  const modelId = model || process.env.LLM_MODEL || "gpt-4o-mini";

  if (!apiKey) {
    return Response.json({ error: "LLM_API_KEY is not set on the Next.js server." }, { status: 500 });
  }

  const llm = createOpenAI({
    apiKey,
    baseURL,
    headers: {
      "HTTP-Referer": process.env.LLM_HTTP_REFERER ?? "http://localhost:3000",
      "X-OpenRouter-Title": process.env.LLM_APP_TITLE ?? "hybridRAG",
    },
  });

  const retrieveDocument = tool({
    description: "Search the selected document for passages that answer the user.",
    inputSchema: z.object({
      query: z.string().describe("Search query derived from the user question"),
    }),
    execute: async ({ query }) => {
      return fastapiJson<RetrieveResponse>("/api/retrieve", {
        method: "POST",
        body: JSON.stringify({
          document_id: documentId,
          query,
          limit: 8,
        }),
      });
    },
  });

  const question = lastUserText(messages);
  const selectedPlate = await plateLabel(documentId);
  let retrieved: RetrieveResponse = EMPTY_RETRIEVE;
  if (question) {
    try {
      retrieved = await fastapiJson<RetrieveResponse>("/api/retrieve", {
        method: "POST",
        body: JSON.stringify({
          document_id: documentId,
          query: question,
          limit: 8,
        }),
      });
    } catch {
      retrieved = EMPTY_RETRIEVE;
    }
  }

  const retrievalMeta: RetrieveMeta = {
    hybrid: retrieved.hybrid,
    fts: retrieved.fts,
    multi_query: retrieved.multi_query,
    queries: retrieved.queries,
  };

  const result = streamText({
    model: llm.chat(modelId),
    messages: await convertToModelMessages(messages),
    tools: { retrieveDocument },
    stopWhen: stepCountIs(4),
    system: `${RAG_SYSTEM_PROMPT}\n\nSelected plate: ${selectedPlate}\n\nRetrieved passages:\n\n${passagesFromChunks(retrieved.chunks)}`,
  });

  return result.toUIMessageStreamResponse<UIMessage<RetrieveMeta>>({
    originalMessages: messages,
    sendSources: true,
    messageMetadata: ({ part }) => {
      if (part.type === "start") {
        return retrievalMeta;
      }
      return undefined;
    },
    onFinish: async ({ messages: next }) => {
      try {
        await fastapiJson("/api/memory", {
          method: "POST",
          body: JSON.stringify({ document_id: documentId, messages: next }),
        });
      } catch {
        // Persistence must not fail the stream.
      }
    },
  });
}
