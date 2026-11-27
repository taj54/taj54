
from pathlib import Path
from xml.sax.saxutils import escape
import re
import uuid

ROOT = Path.cwd()
ASSET_DIR = ROOT / ".github" / "assets"
README_PATH = ROOT / "README.md"

ASSET_DIR.mkdir(parents=True, exist_ok=True)

# Generate a unique banner filename
BANNER_NAME = f"profile-banner-{uuid.uuid4().hex[:12]}.svg"
SVG_PATH = ASSET_DIR / BANNER_NAME

NAME = "TAJ"
ROLE = "FULL-STACK PRODUCT ENGINEER"
TAGLINE = "Building scalable systems, developer tools & elegant digital experiences."
TECH = ["LARAVEL", "REACT", "TYPESCRIPT", "NODE.JS", "PYTHON"]

# Generate technology pills
tech_pills = ""
x = 64

for item in TECH:
    width = len(item) * 9 + 34
    tech_pills += f"""
    <g transform="translate({x}, 272)">
      <rect width="{width}" height="32" rx="16"
            fill="#111b35" stroke="#33466b" stroke-width="1"/>
      <text x="{width / 2}" y="21" text-anchor="middle"
            class="pill">{escape(item)}</text>
    </g>
    """
    x += width + 12

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  width="1200" height="360" viewBox="0 0 1200 360"
  role="img" aria-labelledby="title desc">

  <title id="title">{escape(NAME)} — {escape(ROLE)}</title>
  <desc id="desc">{escape(TAGLINE)}</desc>

  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070b18"/>
      <stop offset="55%" stop-color="#11132d"/>
      <stop offset="100%" stop-color="#071a2b"/>
    </linearGradient>

    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8b5cf6"/>
      <stop offset="50%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2dd4bf"/>
    </linearGradient>

    <radialGradient id="glow">
      <stop offset="0%" stop-color="#7c3aed" stop-opacity=".32"/>
      <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
    </radialGradient>

    <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse">
      <path d="M36 0H0V36" fill="none"
            stroke="#8ba4d8" stroke-opacity=".09" stroke-width="1"/>
    </pattern>

    <filter id="blur">
      <feGaussianBlur stdDeviation="35"/>
    </filter>

    <filter id="softGlow">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <style>
      .name {{
        font: 800 48px 'Segoe UI', Arial, sans-serif;
        letter-spacing: 3px;
        fill: #f8fafc;
      }}
      .role {{
        font: 700 16px 'Segoe UI', Arial, sans-serif;
        letter-spacing: 5px;
        fill: #67e8f9;
      }}
      .tagline {{
        font: 15px 'Segoe UI', Arial, sans-serif;
        fill: #aab8d0;
      }}
      .pill {{
        font: 700 10px 'Segoe UI', Arial, sans-serif;
        letter-spacing: 1px;
        fill: #dbeafe;
      }}
      .code {{
        font: 13px monospace;
        fill: #8da3c7;
      }}
      .particle {{
        animation: float 6s ease-in-out infinite alternate;
      }}
      .orbit {{
        transform-origin: 990px 180px;
        animation: rotate 24s linear infinite;
      }}
      .pulse {{
        animation: pulse 3s ease-in-out infinite;
      }}
      @keyframes float {{
        from {{ transform: translateY(0); opacity: .35; }}
        to {{ transform: translateY(-18px); opacity: .9; }}
      }}
      @keyframes rotate {{
        to {{ transform: rotate(360deg); }}
      }}
      @keyframes pulse {{
        0%, 100% {{ opacity: .35; }}
        50% {{ opacity: 1; }}
      }}
    </style>
  </defs>

  <rect width="1200" height="360" fill="url(#bg)"/>
  <rect width="1200" height="360" fill="url(#grid)"/>

  <ellipse cx="950" cy="170" rx="300" ry="230"
           fill="url(#glow)" filter="url(#blur)"/>
  <ellipse cx="180" cy="340" rx="250" ry="100"
           fill="#0891b2" opacity=".12" filter="url(#blur)"/>

  <g fill="none" stroke="url(#accent)" opacity=".55">
    <circle cx="990" cy="180" r="105" stroke-width="1.2"
            stroke-dasharray="5 10"/>
    <circle cx="990" cy="180" r="145" stroke-width="1"
            stroke-dasharray="2 12" class="orbit"/>
    <ellipse cx="990" cy="180" rx="190" ry="75"
             transform="rotate(-35 990 180)" stroke-width="1"/>
  </g>

  <g class="pulse" filter="url(#softGlow)">
    <circle cx="990" cy="75" r="5" fill="#67e8f9"/>
    <circle cx="1134" cy="180" r="4" fill="#a78bfa"/>
    <circle cx="900" cy="270" r="5" fill="#2dd4bf"/>
  </g>

  <g fill="#a5f3fc">
    <circle class="particle" cx="790" cy="70" r="2"/>
    <circle class="particle" cx="850" cy="310" r="2"/>
    <circle class="particle" cx="1080" cy="90" r="2"/>
    <circle class="particle" cx="1150" cy="290" r="2"/>
    <circle class="particle" cx="720" cy="210" r="1.5"/>
    <circle class="particle" cx="1030" cy="320" r="1.5"/>
  </g>

  <g transform="translate(64 0)">
    <text x="0" y="55" class="code">// HELLO, WORLD. I'M</text>
    <text x="0" y="125" class="name">{escape(NAME)}</text>

    <rect x="0" y="151" width="74" height="3"
          rx="2" fill="url(#accent)" filter="url(#softGlow)"/>

    <text x="0" y="194" class="role">{escape(ROLE)}</text>

    <text x="0" y="230" class="tagline">
      {escape(TAGLINE)}
    </text>

    {tech_pills}
  </g>

  <rect x="0" y="354" width="1200" height="6" fill="#17233d"/>
  <rect x="0" y="354" width="360" height="6"
        fill="url(#accent)" filter="url(#softGlow)">
    <animate attributeName="x"
      values="-360;1200" dur="7s" repeatCount="indefinite"/>
  </rect>

</svg>
"""

# Write new SVG
SVG_PATH.write_text(svg, encoding="utf-8")

# Update README with the new filename
banner = (
    "<!-- PROFILE_BANNER_START -->\n"
    '<p align="center">\n'
    f'  <img src=".github/assets/{BANNER_NAME}" '
    'alt="Tajul Islam — Full-Stack Product Engineer" width="100%">\n'
    '</p>\n'
    "<!-- PROFILE_BANNER_END -->"
)

if README_PATH.exists():
    readme = README_PATH.read_text(encoding="utf-8")

    pattern = r"<!-- PROFILE_BANNER_START -->.*?<!-- PROFILE_BANNER_END -->"

    if re.search(pattern, readme, flags=re.DOTALL):
        readme = re.sub(
            pattern,
            lambda _: banner,
            readme,
            count=1,
            flags=re.DOTALL
        )
    else:
        readme = banner + "\n\n" + readme

    README_PATH.write_text(readme, encoding="utf-8")

# Remove older generated banners, keeping the current one
for old_banner in ASSET_DIR.glob("profile-banner-*.svg"):
    if old_banner != SVG_PATH:
        old_banner.unlink()

print(f"Generated: {SVG_PATH.relative_to(ROOT)}")
print("README banner updated successfully.")
