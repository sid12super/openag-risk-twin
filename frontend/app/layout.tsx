import type { Metadata } from "next";
import { Inter, IBM_Plex_Mono, Space_Grotesk } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { StatusBadge } from "@/components/StatusBadge";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-display", display: "swap" });

export const metadata: Metadata = {
  title: "OpenAg Risk Twin",
  description: "Commodity risk modeling on regime uncertainty",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${plexMono.variable} ${spaceGrotesk.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[--bg]">
        <header className="border-b border-[--line] bg-[--surface]">
          <div className="px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
            <span className="font-display text-lg font-medium text-[--ink]">OpenAg Risk Twin</span>
            <nav className="flex items-center gap-8">
              <Link href="/" className="text-sm text-[--ink] hover:text-[--accent] transition-colors">Forecast</Link>
              <Link href="/scenario" className="text-sm text-[--ink] hover:text-[--accent] transition-colors">Scenario</Link>
              <Link href="/model-card" className="text-sm text-[--ink] hover:text-[--accent] transition-colors">Model card</Link>
              <StatusBadge />
            </nav>
          </div>
        </header>
        <main className="flex-1">
          <div className="px-6 py-8 max-w-6xl mx-auto">{children}</div>
        </main>
      </body>
    </html>
  );
}