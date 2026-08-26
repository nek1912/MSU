import { BAND_LABEL, evidenceBand } from "@/lib/band";

export function EvidenceBand({ confidence }: { confidence: number }) {
  const band = evidenceBand(confidence);
  const color = band === "strong" ? "bg-green-100 text-green-800"
    : band === "moderate" ? "bg-amber-100 text-amber-800" : "bg-red-100 text-red-800";
  return <span className={`rounded px-2 py-0.5 text-xs font-medium ${color}`}>
    {BAND_LABEL[band]}</span>;
}
