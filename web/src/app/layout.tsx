import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ARQYV — The Last Great Desktop Application",
  description:
    "AI-powered personal data unifier. Media player, semantic search, and instant P2P sharing. No accounts. No subscriptions. Local-first.",
  keywords: [
    "ARQYV", "media organizer", "semantic search", "AI", "desktop app",
    "media player", "P2P sharing", "local-first", "cross-platform",
  ],
  authors: [{ name: "Alaustrup", url: "https://github.com/ALaustrup" }],
  openGraph: {
    title: "ARQYV — The Last Great Desktop Application",
    description:
      "AI-powered personal data unifier. Media player, semantic search, and instant P2P sharing.",
    type: "website",
    url: "https://arqyv.vercel.app",
    images: [{ url: "/og.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ARQYV",
    description: "AI-powered personal data unifier. Local-first.",
  },
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
