import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Mono, Source_Serif_4 } from "next/font/google";

import { cn } from "@/lib/utils";

import "./globals.css";

const display = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
});

const serif = Source_Serif_4({
  variable: "--font-serif",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

const mono = IBM_Plex_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "hybridRAG · document foundry",
  description: "Local hybrid RAG with FastAPI, LanceDB, and a Next.js AI Elements chat.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full" suppressHydrationWarning>
      <body
        className={cn(
          display.variable,
          serif.variable,
          mono.variable,
          "flex min-h-full flex-col font-[family-name:var(--font-serif)] antialiased",
        )}
      >
        {children}
      </body>
    </html>
  );
}
