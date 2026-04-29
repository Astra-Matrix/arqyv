import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "ARQYV — AI Media Organizer",
    short_name: "ARQYV",
    description:
      "AI-powered personal data unifier. Media player, semantic search, instant P2P sharing. Free, open-source.",
    start_url: "/",
    display: "standalone",
    background_color: "#1a1a2e",
    theme_color: "#00b4d8",
    orientation: "portrait-primary",
    categories: ["productivity", "utilities", "multimedia"],
    icons: [
      {
        src: "/favicon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "any",
      },
      {
        src: "/favicon-32.png",
        sizes: "32x32",
        type: "image/png",
      },
      {
        src: "/apple-touch-icon.png",
        sizes: "180x180",
        type: "image/png",
        purpose: "any",
      },
    ],
  };
}
