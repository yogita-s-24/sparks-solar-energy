// Builds static/images/icons/sprite.svg from the Lucide icons used by the templates.
// Run with: npm run build:icons  (only needed when adding a new icon)
const fs = require("fs");
const path = require("path");

const ICONS = [
  "sun", "sun-medium", "sunrise", "leaf", "zap", "house", "tractor", "sprout",
  "building-2", "phone", "map-pin", "arrow-right", "arrow-up-right", "arrow-up", "arrow-down",
  "check", "menu", "x", "chevron-down", "message-circle", "calculator",
  "clipboard-list", "scan-search", "file-text", "wrench", "mail", "instagram",
  "shield-check", "plug-zap", "droplets", "battery-charging", "trending-down",
  "indian-rupee", "gauge", "recycle", "sliders-horizontal", "sparkles", "users",
  "hard-hat", "calendar-check", "info", "circle-alert", "circle-check",
  "loader-circle", "lightbulb", "ruler", "compass", "image", "heart-handshake",
  "settings-2", "landmark", "plus", "external-link", "quote", "cable", "construction", "wifi", "badge-indian-rupee", "wallet", "layers", "circuit-board", "badge-check", "banknote", "grid-2x2",
];

const srcDir = path.join(__dirname, "..", "node_modules", "lucide-static", "icons");
const out = path.join(__dirname, "..", "static", "images", "icons", "sprite.svg");

const symbols = ICONS.map((name) => {
  const svg = fs.readFileSync(path.join(srcDir, `${name}.svg`), "utf8");
  const inner = svg
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/^[\s\S]*?<svg[^>]*>/, "")
    .replace(/<\/svg>\s*$/, "")
    .replace(/\s*\n\s*/g, "");
  return `<symbol id="${name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${inner}</symbol>`;
});

fs.writeFileSync(
  out,
  `<svg xmlns="http://www.w3.org/2000/svg">\n<!-- Lucide icons (ISC licence) https://lucide.dev -->\n${symbols.join("\n")}\n</svg>\n`
);
console.log(`Wrote ${ICONS.length} icons to ${path.relative(process.cwd(), out)}`);
