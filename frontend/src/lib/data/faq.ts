export type FaqCategory = "crop-insurance" | "pacs" | "financial" | "grievance" | "legal";

export interface FaqItem {
  id: string;
  category: FaqCategory;
  question: string;
  answer: string;
}

export const faqItems: FaqItem[] = [
  {
    id: "f1",
    category: "crop-insurance",
    question: "What is PMFBY crop insurance?",
    answer:
      "PMFBY (Pradhan Mantri Fasal Bima Yojana) is a crop insurance scheme. Farmers pay a small premium and the rest is subsidised by the government, covering crop loss from natural calamities, pests and diseases.",
  },
  {
    id: "f2",
    category: "crop-insurance",
    question: "How do I claim under PMFBY?",
    answer:
      "File a claim before the deadline at your PACS, bank, or CSC with land records and sowing details. Compensation is disbursed after assessment of the insured crop loss.",
  },
  {
    id: "f3",
    category: "pacs",
    question: "How do I join a PACS as a member?",
    answer:
      "Visit your local PACS office, fill the membership form, submit identity and residence documents, and pay the small share/entrance fee as notified.",
  },
  {
    id: "f4",
    category: "pacs",
    question: "What services does a PACS provide?",
    answer:
      "PACS provide short-term crop loans, storage/godown facilities, agro-inputs (seed, fertiliser, equipment), insurance enrolment and a channel to raise grievances.",
  },
  {
    id: "f5",
    category: "financial",
    question: "What is a Kisan Credit Card (KCC)?",
    answer:
      "The KCC is a crop credit card for farmers offering short-term credit at competitive rates, flexible repayment after harvest, and a personal accident insurance cover.",
  },
  {
    id: "f6",
    category: "financial",
    question: "How can I improve my financial literacy?",
    answer:
      "Attend village-level camps organised by PACS and banks, and ask this chatbot plain-language questions on savings, borrowing, insurance and safe digital banking.",
  },
  {
    id: "f7",
    category: "grievance",
    question: "How do I complain about my cooperative?",
    answer:
      "Use the Grievance page to file a complaint with a category and description. You will get an ID to track the status on the grievance status page.",
  },
  {
    id: "f8",
    category: "grievance",
    question: "What categories of grievances can I raise?",
    answer:
      "Grievances can belong to crop insurance / PMFBY, PACS service, scheme or subsidy, or other cooperative matters.",
  },
  {
    id: "f9",
    category: "legal",
    question: "Which law governs multi-state cooperatives?",
    answer:
      "The Multi-State Cooperative Societies Act, 2002 governs cooperative societies operating across more than one state.",
  },
  {
    id: "f10",
    category: "legal",
    question: "How are cooperative disputes resolved?",
    answer:
      "Disputes between a cooperative and its members are resolved through arbitration or a designated dispute authority, not regular civil courts.",
  },
  {
    id: "f11",
    category: "legal",
    question: "What are a cooperative society's by-laws?",
    answer:
      "By-laws are the society's internal rulebook covering membership, share capital, board powers, meetings and business activities, consistent with the governing Act.",
  },
];

export function getFaqItems(): FaqItem[] {
  return faqItems;
}
