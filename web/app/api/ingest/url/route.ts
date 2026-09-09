import { proxyToFastApi } from "@/lib/fastapi";

export const maxDuration = 300;

export async function POST(req: Request) {
  return proxyToFastApi("/api/ingest/url", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: await req.text(),
  });
}
