import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
  Noto_Serif_Devanagari,
  Noto_Serif_Bengali,
  Noto_Serif_Tamil,
  Noto_Serif_Telugu,
  Noto_Serif_Kannada,
  Noto_Serif_Gurmukhi,
  Noto_Serif_Gujarati,
  Noto_Serif_Oriya,
  Noto_Serif_Malayalam,
} from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "@/lib/i18n/provider";
import { TopNav } from "@/components/layout/TopNav";
import { MobileNav } from "@/components/layout/MobileNav";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });
const devanagari = Noto_Serif_Devanagari({
  variable: "--font-devanagari",
  subsets: ["devanagari", "latin"],
  weight: ["400", "500", "600", "700"],
});
const bengali = Noto_Serif_Bengali({
  variable: "--font-bengali",
  subsets: ["bengali", "latin"],
  weight: ["400", "500", "600", "700"],
});
const tamil = Noto_Serif_Tamil({
  variable: "--font-tamil",
  subsets: ["tamil", "latin"],
  weight: ["400", "500", "600", "700"],
});
const telugu = Noto_Serif_Telugu({
  variable: "--font-telugu",
  subsets: ["telugu", "latin"],
  weight: ["400", "500", "600", "700"],
});
const kannada = Noto_Serif_Kannada({
  variable: "--font-kannada",
  subsets: ["kannada", "latin"],
  weight: ["400", "500", "600", "700"],
});
const gurmukhi = Noto_Serif_Gurmukhi({
  variable: "--font-gurmukhi",
  subsets: ["gurmukhi", "latin"],
  weight: ["400", "500", "600", "700"],
});
const gujarati = Noto_Serif_Gujarati({
  variable: "--font-gujarati",
  subsets: ["gujarati", "latin"],
  weight: ["400", "500", "600", "700"],
});
const odia = Noto_Serif_Oriya({
  variable: "--font-odia",
  subsets: ["oriya", "latin"],
  weight: ["400", "500", "600", "700"],
});
const malayalam = Noto_Serif_Malayalam({
  variable: "--font-malayalam",
  subsets: ["malayalam", "latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "सहकारिता — Cooperative Governance Assistant",
  description:
    "Multilingual AI assistant for cooperative governance, PMFBY, PACS, financial literacy and grievance redressal.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${devanagari.variable} ${bengali.variable} ${tamil.variable} ${telugu.variable} ${kannada.variable} ${gurmukhi.variable} ${gujarati.variable} ${odia.variable} ${malayalam.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">
        <LanguageProvider>
          <TopNav />
          <main className="flex-1 pb-16 md:pb-0">{children}</main>
          <MobileNav />
        </LanguageProvider>
      </body>
    </html>
  );
}
