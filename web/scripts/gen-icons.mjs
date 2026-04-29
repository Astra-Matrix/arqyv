/**
 * Generates all required PNG icons and the OG image from SVG source.
 * Run: node scripts/gen-icons.mjs
 */
import sharp from "sharp";
import { writeFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dir = dirname(fileURLToPath(import.meta.url));
const pub = join(__dir, "..", "public");

// ── Icon SVG ──────────────────────────────────────────────────────────────

const iconSvg = (size) => Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" rx="${size * 0.22}" fill="#00b4d8"/>
  <text
    x="${size / 2}" y="${size * 0.72}"
    font-family="system-ui, -apple-system, sans-serif"
    font-size="${size * 0.44}"
    font-weight="700"
    text-anchor="middle"
    fill="#1a1a2e"
  >AQ</text>
</svg>`);

// ── OG Image SVG (1200×630) ───────────────────────────────────────────────

const ogSvg = Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
  <!-- Background -->
  <rect width="1200" height="630" fill="#1a1a2e"/>
  <!-- Grid lines -->
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0,180,216,0.06)" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="1200" height="630" fill="url(#grid)"/>
  <!-- Glow -->
  <radialGradient id="glow" cx="50%" cy="0%" r="60%">
    <stop offset="0%" stop-color="#00b4d8" stop-opacity="0.18"/>
    <stop offset="100%" stop-color="#1a1a2e" stop-opacity="0"/>
  </radialGradient>
  <rect width="1200" height="630" fill="url(#glow)"/>
  <!-- Card -->
  <rect x="80" y="80" width="1040" height="470" rx="24" fill="#16213e" stroke="#2a2a4a" stroke-width="1.5"/>
  <!-- Logo badge -->
  <rect x="536" y="150" width="128" height="128" rx="24" fill="#00b4d8"/>
  <text x="600" y="234" font-family="system-ui,-apple-system,sans-serif" font-size="54" font-weight="700" text-anchor="middle" fill="#1a1a2e">AQ</text>
  <!-- Title -->
  <text x="600" y="340" font-family="system-ui,-apple-system,sans-serif" font-size="72" font-weight="700" text-anchor="middle" fill="#e0e0e0">ARQYV</text>
  <!-- Subtitle -->
  <text x="600" y="400" font-family="system-ui,-apple-system,sans-serif" font-size="24" text-anchor="middle" fill="#9e9e9e">AI Media Organizer · Semantic Search · Instant P2P Sharing</text>
  <!-- Tags -->
  <text x="600" y="460" font-family="system-ui,-apple-system,sans-serif" font-size="18" text-anchor="middle" fill="#00b4d8">Free · Open Source · No Accounts · Windows · macOS · Linux</text>
  <!-- Bottom line -->
  <rect x="480" y="494" width="240" height="2" rx="1" fill="#00b4d8" opacity="0.4"/>
</svg>`);

async function generate() {
  // Favicon sizes
  for (const size of [16, 32, 180]) {
    const name =
      size === 180 ? "apple-touch-icon.png" : `favicon-${size}.png`;
    await sharp(iconSvg(size))
      .resize(size, size)
      .png()
      .toFile(join(pub, name));
    console.log(`✓ ${name}`);
  }

  // OG image
  await sharp(ogSvg)
    .resize(1200, 630)
    .png()
    .toFile(join(pub, "og.png"));
  console.log("✓ og.png (1200×630)");
}

generate().catch(console.error);
