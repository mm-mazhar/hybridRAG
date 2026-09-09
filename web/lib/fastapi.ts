export function fastapiUrl(path: string): string {
  const base = process.env.FASTAPI_URL ?? "http://127.0.0.1:8000";
  return `${base.replace(/\/$/, "")}${path}`;
}

function messageFromValidationItem(item: unknown): string | null {
  if (!item || typeof item !== "object" || !("msg" in item)) {
    return null;
  }
  const msg = (item as { msg: unknown }).msg;
  return typeof msg === "string" && msg.trim() ? msg : null;
}

export function errorDetailFromBody(text: string, status: number): string {
  try {
    const payload = JSON.parse(text) as { detail?: unknown };
    if (typeof payload.detail === "string" && payload.detail.trim()) {
      return payload.detail;
    }
    if (Array.isArray(payload.detail) && payload.detail.length > 0) {
      const first = messageFromValidationItem(payload.detail[0]);
      if (first) {
        return first;
      }
    }
  } catch {
    // HTML or plain-text proxy bodies
  }
  const compact = text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  if (!compact || compact.startsWith("Internal")) {
    return `Request failed (${status}).`;
  }
  return compact.slice(0, 280);
}

export async function proxyToFastApi(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(fastapiUrl(path), init);
  const text = await response.text();
  const contentType = response.headers.get("content-type") ?? "application/json";
  return new Response(text, {
    status: response.status,
    headers: { "content-type": contentType },
  });
}

export async function fastapiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(fastapiUrl(path), {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
    cache: "no-store",
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(errorDetailFromBody(text, response.status));
  }
  return JSON.parse(text) as T;
}
