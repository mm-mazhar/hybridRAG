import { fastapiUrl } from "@/lib/fastapi";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const documentId = url.searchParams.get("document_id") ?? "";
  const response = await fetch(
    fastapiUrl(`/api/memory?document_id=${encodeURIComponent(documentId)}`),
    { cache: "no-store" },
  );
  return new Response(await response.text(), {
    status: response.status,
    headers: { "content-type": "application/json" },
  });
}
