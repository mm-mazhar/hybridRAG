import { fastapiUrl } from "@/lib/fastapi";

export const dynamic = "force-dynamic";

export async function GET() {
  const response = await fetch(fastapiUrl("/api/config"), { cache: "no-store" });
  return new Response(await response.text(), {
    status: response.status,
    headers: { "content-type": "application/json" },
  });
}
