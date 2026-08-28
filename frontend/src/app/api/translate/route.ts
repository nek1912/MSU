import { NextResponse } from "next/server";

/**
 * Server proxy to Azure Translator v3.
 * Keeps AZURE_TRANSLATOR_KEY server-side. Body: { texts: string[], to: string, from?: string }.
 * Returns { translations: string[] } (one per input, in order).
 */

const ENDPOINT = (process.env.AZURE_TRANSLATOR_ENDPOINT ?? "https://api.cognitive.microsofttranslator.com").replace(/\/$/, "");

export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  const { texts, to, from } = (body ?? {}) as {
    texts?: unknown;
    to?: unknown;
    from?: unknown;
  };
  if (!Array.isArray(texts) || texts.length === 0 || typeof to !== "string") {
    return NextResponse.json({ error: "Expected { texts: string[], to: string }" }, { status: 400 });
  }
  const key = process.env.AZURE_TRANSLATOR_KEY;
  if (!key) {
    return NextResponse.json({ error: "Translator not configured (AZURE_TRANSLATOR_KEY missing)" }, { status: 503 });
  }

  const url = new URL(`${ENDPOINT}/translate`);
  url.searchParams.set("api-version", "3.0");
  url.searchParams.set("to", to);
  if (from && typeof from === "string") url.searchParams.set("from", from);

  try {
    const res = await fetch(url.toString(), {
      method: "POST",
      headers: {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": process.env.AZURE_TRANSLATOR_REGION ?? "global",
        "Content-Type": "application/json",
      },
      body: JSON.stringify((texts as string[]).map((text) => ({ text }))),
    });

    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      return NextResponse.json({ error: `Translator ${res.status}`, detail }, { status: 502 });
    }

    const data = (await res.json()) as Array<{ translations: { text: string }[] }>;
    const translations = data.map((d) => d.translations?.[0]?.text ?? "");
    return NextResponse.json({ translations });
  } catch {
    return NextResponse.json({ error: "Translate failed" }, { status: 500 });
  }
}
