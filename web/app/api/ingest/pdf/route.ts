import { proxyToFastApi } from "@/lib/fastapi";

export const maxDuration = 300;

export async function POST(req: Request) {
  return proxyToFastApi("/api/ingest/pdf", {
    method: "POST",
    body: await req.formData(),
  });
}
