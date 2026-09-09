import { fastapiUrl, proxyToFastApi } from "@/lib/fastapi";

export const dynamic = "force-dynamic";

export async function GET() {
  const response = await fetch(fastapiUrl("/api/documents"), { cache: "no-store" });
  return new Response(await response.text(), {
    status: response.status,
    headers: { "content-type": "application/json" },
  });
}

export async function DELETE() {
  return proxyToFastApi("/api/documents", { method: "DELETE" });
}
