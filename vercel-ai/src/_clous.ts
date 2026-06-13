/**
 * Tiny shared HTTP helper for the Clous SEC data API (Vercel AI SDK folder).
 *
 * Reads `CLOUS_API_KEY` from the environment, sends bearer auth, and returns the
 * parsed JSON envelope `{ data, page, as_of, source, query_echo, warnings }`.
 * Uses the global `fetch` (Node 18+ / edge runtimes), so there are no runtime
 * dependencies beyond the AI SDK + zod used by `clous-tools.ts`.
 */

const BASE_URL = (process.env.CLOUS_BASE_URL ?? "https://api.clous.ai").replace(/\/+$/, "");

function apiKey(): string {
  const key = process.env.CLOUS_API_KEY;
  if (!key) {
    throw new Error(
      "CLOUS_API_KEY is not set. Get a key at https://clous.ai and set CLOUS_API_KEY.",
    );
  }
  return key;
}

function headers(): Record<string, string> {
  return {
    Authorization: `Bearer ${apiKey()}`,
    Accept: "application/json",
    "User-Agent": "clous-integrations/0.1 (+https://github.com/clousai/integrations)",
  };
}

type Params = Record<string, string | number | boolean | string[] | undefined | null>;

function toQuery(params?: Params): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null) continue;
    sp.set(k, Array.isArray(v) ? v.join(",") : String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

export async function clousGet(path: string, params?: Params): Promise<unknown> {
  const res = await fetch(`${BASE_URL}${path}${toQuery(params)}`, {
    method: "GET",
    headers: headers(),
  });
  if (!res.ok) {
    throw new Error(`Clous GET ${path} failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

export async function clousPost(path: string, body?: Record<string, unknown>): Promise<unknown> {
  const clean = Object.fromEntries(
    Object.entries(body ?? {}).filter(([, v]) => v !== undefined && v !== null),
  );
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify(clean),
  });
  if (!res.ok) {
    throw new Error(`Clous POST ${path} failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}
