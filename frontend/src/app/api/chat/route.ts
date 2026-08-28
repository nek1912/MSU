import { NextResponse } from "next/server";
import { getSchemes, getServices, getFaqItems, getLegalDocs, getLibraryDocs } from "@/lib/data";
import type { Locale } from "@/lib/i18n/i18n";

/**
 * Server API route /api/chat
 * Proxy to local Python backend (port 8000) with fallback to local knowledge retrieval & Azure Translator.
 */

export async function POST(req: Request) {
  let body: { question?: string; session_id?: string; language?: string; state?: string | null };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const question = body.question?.trim() || "";
  const language = (body.language as Locale) || "en";
  const backendUrl = process.env.BACKEND_API_URL || "http://localhost:8000/chat";

  // 1. Try forwarding to Python backend on port 8000 if available
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2000);
    const backendRes = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch {
    // Backend offline or unreachable, fall back to local knowledge engine
  }

  // 2. Local Knowledge Base Search Engine (schemes, services, faq, legal, library)
  const q = question.toLowerCase();

  const schemes = getSchemes("en");
  const services = getServices("en");
  const faqs = getFaqItems("en");
  const legals = getLegalDocs("en");
  const docs = getLibraryDocs("en");

  // Matching logic
  const matchedFaq = faqs.find(
    (f) => q.includes(f.category) || f.question.toLowerCase().split(" ").some((w) => w.length > 3 && q.includes(w))
  );

  const matchedScheme = schemes.find(
    (s) => q.includes(s.slug) || q.includes(s.category) || s.name.toLowerCase().split(" ").some((w) => w.length > 3 && q.includes(w))
  );

  const matchedService = services.find(
    (sv) => q.includes(sv.slug) || q.includes(sv.category) || sv.name.toLowerCase().split(" ").some((w) => w.length > 3 && q.includes(w))
  );

  const matchedLegal = legals.find(
    (l) => q.includes(l.category) || l.title.toLowerCase().split(" ").some((w) => w.length > 3 && q.includes(w))
  );

  let answer = "";
  let domain = "general";
  let confidence = 0.85;
  const citations: { title: string; page: number; url: string }[] = [];

  if (matchedFaq) {
    answer = matchedFaq.answer;
    domain = matchedFaq.category || "faq";
    confidence = 0.92;
    citations.push({ title: matchedFaq.question, page: 1, url: "/faq" });
  } else if (matchedScheme) {
    answer = `${matchedScheme.name}: ${matchedScheme.benefit}. Overview: ${matchedScheme.overview}`;
    domain = "schemes";
    confidence = 0.89;
    citations.push({ title: matchedScheme.name, page: 1, url: `/schemes/${matchedScheme.slug}` });
  } else if (matchedService) {
    answer = `${matchedService.name}: ${matchedService.summary}. Description: ${matchedService.description}`;
    domain = "services";
    confidence = 0.88;
    citations.push({ title: matchedService.name, page: 1, url: `/services/${matchedService.slug}` });
  } else if (matchedLegal) {
    answer = `${matchedLegal.title}: ${matchedLegal.overview}`;
    domain = "legal";
    confidence = 0.86;
    citations.push({ title: matchedLegal.title, page: 1, url: `/legal/${matchedLegal.slug}` });
  } else if (docs.length > 0) {
    const doc = docs[0];
    answer = `Based on official documents: ${doc.title} (${doc.source}). You can review cooperative governance guidelines and scheme benefits across PACS and PMFBY.`;
    domain = "library";
    confidence = 0.82;
    citations.push({ title: doc.title, page: doc.page, url: doc.url });
  } else {
    answer = "Sahakarita AI Assistant provides information on PMFBY crop insurance, PACS services, financial literacy, cooperative laws, and grievance redressal.";
    domain = "cooperative";
    confidence = 0.75;
  }

  // Translate answer if language is not English and Azure key exists
  const azureKey = process.env.AZURE_TRANSLATOR_KEY;
  if (azureKey && language !== "en") {
    try {
      const endpoint = (process.env.AZURE_TRANSLATOR_ENDPOINT || "https://api.cognitive.microsofttranslator.com").replace(/\/$/, "");
      const url = `${endpoint}/translate?api-version=3.0&to=${language}`;
      const transRes = await fetch(url, {
        method: "POST",
        headers: {
          "Ocp-Apim-Subscription-Key": azureKey,
          "Ocp-Apim-Subscription-Region": process.env.AZURE_TRANSLATOR_REGION || "global",
          "Content-Type": "application/json",
        },
        body: JSON.stringify([{ text: answer }]),
      });

      if (transRes.ok) {
        const transData = (await transRes.json()) as Array<{ translations: { text: string }[] }>;
        const translatedText = transData[0]?.translations?.[0]?.text;
        if (translatedText) {
          answer = translatedText;
        }
      }
    } catch {
      // Keep English answer on translation failure
    }
  }

  return NextResponse.json({
    answer,
    language,
    domain,
    confidence,
    citations,
    abstained: false,
    follow_up_question: null,
  });
}
