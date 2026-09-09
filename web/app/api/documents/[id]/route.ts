import { proxyToFastApi } from "@/lib/fastapi";

export const dynamic = "force-dynamic";

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  return proxyToFastApi(`/api/documents/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}
