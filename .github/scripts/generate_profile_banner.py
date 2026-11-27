
from pathlib import Path
from xml.sax.saxutils import escape
import re
import uuid

ROOT = Path.cwd()
ASSET_DIR = ROOT / ".github" / "assets"
README_PATH = ROOT / "README.md"

ASSET_DIR.mkdir(parents=True, exist_ok=True)

# Unique filename prevents stale asset caching
BANNER_NAME = f"profile-banner-{uuid.uuid4().hex[:12]}.svg"
SVG_PATH = ASSET_DIR / BANNER_NAME

# Profile information
NAME = "TAJ"
ROLE = "FULL-STACK PRODUCT ENGINEER"
TAGLINE = "Engineering scalable systems."
SUBTITLE = "Building developer tools & elegant digital experiences."

TECH = ["LARAVEL", "REACT", "TYPESCRIPT", "NODE.JS", "PYTHON"]

# Technology badges
tech_pills = ""
x = 64

for item in TECH:
    width = len(item) * 9 + 34

    tech_pills += f"""
    <g transform="translate({x}, 286)">
      <rect width="{width}" height="34" rx="10"
            fill="#111d35" fill-opacity=".9"
            stroke="#435b82" stroke-opacity=".65"/>
      <circle cx="13" cy="17" r="3" fill="#67e8f9"/>
      <text x="25" y="21" class="pill">{escape(item)}</text>
    </g>
    """

    x += width + 10

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
  width="1200" height="380" viewBox="0 0 1200 380"
  role="img" aria-labelledby="title desc">

  <title id="title">{escape(NAME)} | {escape(ROLE)}</title>
  <desc id="desc">{escape(TAGLINE)} {escape(SUBTITLE)}</desc>

  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070b18"/>
      <stop offset="55%" stop-color="#10152c"/>
      <stop offset="100%" stop-color="#071b2c"/>
    </linearGradient>

    <linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#a78bfa"/>
      <stop offset="45%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2dd4bf"/>
    </linearGradient>

    <linearGradient id="nameGradient" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="55%" stop-color="#c4b5fd"/>
      <stop offset="100%" stop-color="#67e8f9"/>
    </linearGradient>

    <radialGradient id="ambient">
      <stop offset="0%" stop-color="#6d28d9" stop-opacity=".32"/>
      <stop offset="100%" stop-color="#6d28d9" stop-opacity="0"/>
    </radialGradient>

    <pattern id="grid" width="32" height="32"
             patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none"
            stroke="#8ba4d8" stroke-opacity=".08"/>
    </pattern>

    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="7" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="softBlur">
      <feGaussianBlur stdDeviation="35"/>
    </filter>

    <style>
      .eyebrow {{
        font: 12px monospace;
        letter-spacing: 3px;
        fill: #8ba3c7;
      }}

      .name {{
        font: 900 76px 'Segoe UI', Arial, sans-serif;
        letter-spacing: 5px;
        fill: url(#nameGradient);
      }}

      .role {{
        font: 700 15px 'Segoe UI', Arial, sans-serif;
        letter-spacing: 3px;
        fill: #67e8f9;
      }}

      .tagline {{
        font: 16px 'Segoe UI', Arial, sans-serif;
        fill: #e2e8f0;
      }}

      .subtitle {{
        font: 14px 'Segoe UI', Arial, sans-serif;
        fill: #94a3b8;
      }}

      .pill {{
        font: 700 10px 'Segoe UI', Arial, sans-serif;
        letter-spacing: .8px;
        fill: #dbeafe;
      }}

      .mono {{
        font: 12px monospace;
        fill: #9fb3d2;
      }}

      .circuit {{
        fill: none;
        stroke: url(#neon);
        stroke-width: 1.4;
        stroke-opacity: .55;
        stroke-linecap: round;
        stroke-linejoin: round;
      }}

      .flow {{
        stroke-dasharray: 5 12;
        animation: dataFlow 5s linear infinite;
      }}

      .orbit {{
        transform-box: view-box;
        transform-origin: 960px 185px;
        animation: rotate 32s linear infinite;
      }}

      .particle {{
        animation: float 4s ease-in-out infinite alternate;
      }}

      .pulse {{
        animation: pulse 3s ease-in-out infinite;
      }}

      @keyframes dataFlow {{
        to {{ stroke-dashoffset: -100; }}
      }}

      @keyframes rotate {{
        to {{ transform: rotate(360deg); }}
      }}

      @keyframes float {{
        from {{ transform: translateY(0); opacity: .3; }}
        to {{ transform: translateY(-15px); opacity: 1; }}
      }}

      @keyframes pulse {{
        0%, 100% {{ opacity: .4; }}
        50% {{ opacity: 1; }}
      }}
    </style>
  </defs>

  <!-- Main background -->
  <rect width="1200" height="380" fill="url(#background)"/>
  <rect width="1200" height="380" fill="url(#grid)"/>

  <!-- Ambient lighting -->
  <ellipse cx="950" cy="180" rx="300" ry="240"
           fill="url(#ambient)" filter="url(#softBlur)"/>

  <ellipse cx="180" cy="350" rx="220" ry="110"
           fill="#0891b2" opacity=".12" filter="url(#softBlur)"/>

  <!-- Decorative border -->
  <rect x="12" y="12" width="1176" height="356" rx="18"
        fill="none" stroke="#64748b" stroke-opacity=".16"/>

  <!-- Left content -->
  <g transform="translate(64 0)">
    <text x="0" y="62" class="eyebrow">
      &lt; BUILDING THE FUTURE /&gt;
    </text>

    <text x="0" y="155" class="name">{escape(NAME)}</text>

    <rect x="0" y="177" width="100" height="3" rx="2"
          fill="url(#neon)" filter="url(#glow)"/>

    <text x="0" y="216" class="role">{escape(ROLE)}</text>

    <text x="0" y="246" class="tagline">
      {escape(TAGLINE)}
    </text>

    <text x="0" y="268" class="subtitle">
      {escape(SUBTITLE)}
    </text>

    {tech_pills}
  </g>

  <!-- Right-side engineering visual -->
  <g>
    <!-- Orbit rings -->
    <g fill="none" stroke="url(#neon)" stroke-opacity=".32">
      <circle cx="960" cy="185" r="115" stroke-width="1"
              stroke-dasharray="4 9"/>
      <circle cx="960" cy="185" r="150" stroke-width="1"
              stroke-dasharray="2 14" class="orbit"/>
      <ellipse cx="960" cy="185" rx="195" ry="75"
               transform="rotate(-30 960 185)"/>
    </g>

    <!-- Circuit paths -->
    <g class="circuit">
      <path d="M760 95 H830 V125 H865"/>
      <path d="M760 275 H825 V245 H865"/>
      <path d="M1050 115 H1090 V85 H1135"/>
      <path d="M1050 255 H1095 V285 H1140"/>
      <path d="M900 50 V75 H930"/>
      <path d="M990 295 V320 H1040"/>
    </g>

    <g class="circuit flow">
      <path d="M760 95 H830 V125 H865"/>
      <path d="M760 275 H825 V245 H865"/>
      <path d="M1050 115 H1090 V85 H1135"/>
      <path d="M1050 255 H1095 V285 H1140"/>
    </g>

    <!-- Core glowing processor -->
    <circle cx="960" cy="185" r="72"
            fill="#0b1830" stroke="#334d77" stroke-width="1.5"/>

    <circle cx="960" cy="185" r="62"
            fill="none" stroke="url(#neon)"
            stroke-width="2" stroke-opacity=".8"
            filter="url(#glow)"/>

    <circle cx="960" cy="185" r="48"
            fill="#111d39" stroke="#64748b"
            stroke-opacity=".35"/>

    <text x="960" y="194" text-anchor="middle"
          font-size="27" font-weight="800"
          font-family="monospace" fill="#e0f2fe">
      &lt;/&gt;
    </text>

    <!-- Floating data points -->
    <g fill="#67e8f9" filter="url(#glow)">
      <circle class="particle" cx="830" cy="125" r="4"/>
      <circle class="particle" cx="825" cy="245" r="3"/>
      <circle class="particle" cx="1090" cy="85" r="4"/>
      <circle class="particle" cx="1095" cy="285" r="4"/>
      <circle class="particle" cx="900" cy="50" r="3"/>
      <circle class="particle" cx="1040" cy="320" r="3"/>
    </g>

    <!-- Floating code panel -->
    <g transform="translate(1000 135)">
      <rect width="150" height="104" rx="10"
            fill="#0b1224" fill-opacity=".94"
            stroke="#475b80" stroke-opacity=".7"/>

      <path d="M0 28 H150" stroke="#334155"/>

      <circle cx="13" cy="14" r="3" fill="#f87171"/>
      <circle cx="25" cy="14" r="3" fill="#fbbf24"/>
      <circle cx="37" cy="14" r="3" fill="#34d399"/>

      <text x="12" y="47" class="mono">
        const developer =
      </text>
      <text x="12" y="64" class="mono" fill="#67e8f9">
        "TAJ";
      </text>
      <text x="12" y="84" class="mono">
        build(ideas);
      </text>
    </g>

    <!-- Small decorative nodes -->
    <circle cx="790" cy="190" r="2" fill="#a78bfa"/>
    <circle cx="1120" cy="180" r="2" fill="#2dd4bf"/>
  </g>

  <!-- Bottom accent -->
  <rect x="0" y="374" width="1200" height="6"
        fill="#17233d"/>

  <rect x="0" y="374" width="300" height="6"
        fill="url(#neon)">
    <animate attributeName="x"
      values="-300;1200" dur="8s"
      repeatCount="indefinite"/>
  </rect>

</svg>
"""

# Save unique SVG
SVG_PATH.write_text(svg, encoding="utf-8")

# README banner
banner = (
    "<!-- PROFILE_BANNER_START -->\n"
    '<p align="center">\n'
    f'  <img src=".github/assets/{BANNER_NAME}" '
    'alt="TAJ - Full-Stack Product Engineer" width="100%">\n'
    '</p>\n'
    "<!-- PROFILE_BANNER_END -->"
)

if README_PATH.exists():
    readme = README_PATH.read_text(encoding="utf-8")

    pattern = (
        r"<!-- PROFILE_BANNER_START -->"
        r".*?"
        r"<!-- PROFILE_BANNER_END -->"
    )

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

# Clean previous generated banner files
for old_file in ASSET_DIR.glob("profile-banner-*.svg"):
    if old_file != SVG_PATH:
        old_file.unlink()

print(f"Generated banner: {SVG_PATH.relative_to(ROOT)}")
print("README banner reference updated.")
