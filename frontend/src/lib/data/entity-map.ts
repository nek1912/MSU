/**
 * Maps frontend slugs to backend entity_ids.
 * Handles duplicate slugs that map to the same canonical entity.
 */

export const SLUG_TO_ENTITY_ID: Record<string, string> = {
  // Schemes
  "pmfby": "pmfby",
  "kisan-credit-card": "kcc",
  
  // Services
  "pacs-membership": "pacs-membership",
  "short-term-crop-credit": "short-term-crop-credit",
  "godown-storage": "godown-storage",
  "agro-input-supply": "agro-input-supply",
  "pmfby-enrolment": "pmfby-enrolment",
  "pm-fb-enrollment": "pmfby-enrolment",  // duplicate → canonical
  "cooperative-subsidy": "cooperative-subsidy",
  "cooperative-training": "cooperative-training",
  "digital-banking": "digital-banking",
  
  // Legal
  "mscs-act-2002": "mscs-act-2002",
  "model-pacs-bye-laws": "model-pacs-bye-laws",
  "pac-model-bye-laws-moc": "model-pacs-bye-laws",  // duplicate → canonical
  "model-pacs-bylaws": "model-pacs-bye-laws",  // duplicate → canonical
  "board-election-rules": "board-election-rules",
  "cooperative-disputes": "cooperative-disputes",
  "state-coop-act": "state-coop-act",
};

export const ENTITY_TYPE_MAP: Record<string, "scheme" | "service" | "legal"> = {
  "pmfby": "scheme",
  "kcc": "scheme",
  "pacs-membership": "service",
  "short-term-crop-credit": "service",
  "godown-storage": "service",
  "agro-input-supply": "service",
  "pmfby-enrolment": "service",
  "cooperative-subsidy": "service",
  "cooperative-training": "service",
  "digital-banking": "service",
  "mscs-act-2002": "legal",
  "model-pacs-bye-laws": "legal",
  "board-election-rules": "legal",
  "cooperative-disputes": "legal",
  "state-coop-act": "legal",
};

export function getEntityId(slug: string): string | undefined {
  return SLUG_TO_ENTITY_ID[slug];
}

export function getEntityType(entityId: string): "scheme" | "service" | "legal" | undefined {
  return ENTITY_TYPE_MAP[entityId];
}