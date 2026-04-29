import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const BASE_URL = "https://arqyv.vercel.app";

export const viewport: Viewport = {
  themeColor: "#00b4d8",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),

  title: {
    default: "ARQYV — AI-Powered Media Organizer & Semantic Search",
    template: "%s | ARQYV",
  },
  description:
    "ARQYV is a free, open-source desktop application that unifies every file you own — videos, audio, documents, photos — into one intelligent, AI-searchable library. Instant P2P sharing, no accounts, no subscriptions. Windows, macOS, Linux.",

  keywords: [
    "ARQYV",
    "media organizer",
    "AI media player",
    "semantic search",
    "local-first",
    "P2P file sharing",
    "desktop application",
    "open source media player",
    "cross-platform media manager",
    "AI file organizer",
    "offline AI",
    "PyQt6 app",
    "personal data manager",
    "file search software",
    "smart media library",
    "no subscription media player",
    "free media organizer",
    "Windows media organizer",
    "macOS media organizer",
    "Linux media player",
  ],

  authors: [{ name: "Alaustrup", url: "https://github.com/ALaustrup" }],
  creator: "Alaustrup",
  publisher: "Alaustrup",

  category: "software",

  alternates: {
    canonical: BASE_URL,
  },

  openGraph: {
    type: "website",
    url: BASE_URL,
    siteName: "ARQYV",
    title: "ARQYV — The Last Great Desktop Application",
    description:
      "AI-powered personal data unifier. Media player, semantic search, and instant P2P sharing. Free, open-source, no accounts.",
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "ARQYV — AI-powered media organizer and semantic search tool",
        type: "image/png",
      },
    ],
    locale: "en_US",
  },

  twitter: {
    card: "summary_large_image",
    title: "ARQYV — AI-Powered Media Organizer & Semantic Search",
    description:
      "Free, open-source desktop app. AI search, instant P2P sharing, zero accounts. Windows / macOS / Linux.",
    images: ["/og.png"],
    creator: "@ALaustrup",
  },

  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },

  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180" }],
    shortcut: "/favicon.svg",
  },

  manifest: "/manifest.json",

  verification: {
    // Add Google Search Console verification token here when available:
    // google: "YOUR_VERIFICATION_TOKEN",
  },
};

// ── JSON-LD Structured Data ────────────────────────────────────────────────

const softwareAppSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "ARQYV",
  alternateName: "ARQYV Media Organizer",
  url: BASE_URL,
  downloadUrl: "https://github.com/ALaustrup/arqyv/releases/latest",
  applicationCategory: "MultimediaApplication",
  applicationSubCategory: "Media Organizer",
  operatingSystem: "Windows 10, Windows 11, macOS 12, macOS 13, macOS 14, Ubuntu 22.04, Debian, Linux",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
  },
  aggregateRating: {
    "@type": "AggregateRating",
    ratingValue: "5",
    ratingCount: "1",
    bestRating: "5",
    worstRating: "1",
  },
  description:
    "ARQYV is a free, open-source, AI-powered desktop media organizer and semantic search tool. It unifies every file you own — videos, audio, documents, and photos — into one intelligent, searchable library with instant P2P file sharing.",
  softwareVersion: "0.1.0",
  releaseNotes: "https://github.com/ALaustrup/arqyv/releases/tag/v0.1.0",
  license: "https://github.com/ALaustrup/arqyv/blob/main/LICENSE",
  author: {
    "@type": "Person",
    name: "Alaustrup",
    url: "https://github.com/ALaustrup",
  },
  featureList: [
    "AI-powered semantic search (offline, no API keys)",
    "Custom media engine with zero external dependencies",
    "Instant P2P file sharing via QR code",
    "LAN peer discovery via mDNS",
    "Voice search with local Whisper transcription",
    "Google Drive, OneDrive, and Dropbox cloud sync",
    "Smart metadata extraction (EXIF, MediaInfo, mutagen)",
    "Batch rename with template tokens",
    "Subtitle engine (SRT, WebVTT, ASS)",
    "Smart resume — remembers playback position",
    "Audio DSP with EQ presets",
    "Local REST + WebSocket API for mobile clients",
    "Cross-platform: Windows, macOS, Linux",
  ],
  screenshot: `${BASE_URL}/og.png`,
  isAccessibleForFree: true,
  isFamilyFriendly: true,
  keywords:
    "media organizer, AI search, semantic search, P2P sharing, media player, open source, free, desktop app, local-first",
};

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "Is ARQYV free?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. ARQYV is completely free and open-source under the MIT license. There is no subscription, no account, and no telemetry.",
      },
    },
    {
      "@type": "Question",
      name: "Does ARQYV require VLC or FFmpeg?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "No. ARQYV ships with Qt Multimedia as the primary playback engine using platform-native codecs. VLC is optionally auto-detected for extended codec support.",
      },
    },
    {
      "@type": "Question",
      name: "Does ARQYV send my files to the cloud?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Never. Every AI model (Whisper, BLIP, sentence-transformers, spaCy) runs locally on your machine. No internet connection is required for any AI feature.",
      },
    },
    {
      "@type": "Question",
      name: "What operating systems does ARQYV support?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "ARQYV runs on Windows 10/11, macOS 12 (Monterey) and newer (Intel and Apple Silicon), and Linux (Ubuntu 22.04, Debian, Arch).",
      },
    },
    {
      "@type": "Question",
      name: "How does ARQYV P2P file sharing work?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "ARQYV starts a local HTTP server and generates a QR code with a one-time token. Scan the QR code on any device on the same network to download the file directly. No ARQYV servers are involved.",
      },
    },
  ],
};

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: "Alaustrup",
  url: "https://github.com/ALaustrup",
  sameAs: ["https://github.com/ALaustrup"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(softwareAppSchema) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
