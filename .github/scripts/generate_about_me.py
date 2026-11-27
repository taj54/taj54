#!/usr/bin/env python3
"""Generate a unique About Me SVG banner and update the profile README."""

from datetime import datetime
from pathlib import Path
import re


ROOT = Path.cwd()
ASSET_DIR = ROOT / ".github" / "assets"
README_PATH = ROOT / "README.md"

# A timestamp makes each generated SVG filename unique.
BANNER_NAME = f"about-me-{datetime.now():%Y%m%d-%H%M%S}.svg"
SVG_PATH = ASSET_DIR / BANNER_NAME

INTRO = (
    "I build software that feels effortless on the surface and stays rock-solid "
    "under load. From multi-tenant SaaS architectures to framework-agnostic "
    "open-source SDKs, I care deeply about clean boundaries, developer "
    "ergonomics, and shipping products that scale."
)

ITEMS = [
    (
        "CORE FOCUS",
        "Clean architecture, scalable multi-tenant systems, and high-craft user experiences",
    ),
    (
        "ENGINEERING MINDSET",
        "Lifelong builder exploring distributed systems, agentic AI workflows, and open-source tooling",
    ),
    (
        "COLLABORATION",
        "Open to technical partnerships, high-impact product engineering, and open-source quests",
    ),
]

QUOTE = "Clean architecture is about intent: your system should scream what it does."
ATTRIBUTION = "ROBERT C. MARTIN (UNCLE BOB)"


def wrap_words(text: str, limit: int) -> list[str]:
    words = text.split()
    lines = []
    line = ""

    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) > limit and line:
            lines.append(line)
            line = word
        else:
            line = candidate

    if line:
        lines.append(line)

    return lines


def svg_text_lines(
    text: str,
    x: int,
    y: int,
    limit: int,
    line_height: int,
    css_class: str,
) -> str:
    return "\n".join(
        f'<text class="{css_class}" x="{x}" y="{y + index * line_height}">'
        f"{line}</text>"
        for index, line in enumerate(wrap_words(text, limit))
    )


def build_svg() -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">',
        """<defs>
          <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#0b1220"/>
            <stop offset="100%" stop-color="#111c32"/>
          </linearGradient>
          <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#62e6c5"/>
            <stop offset="100%" stop-color="#70a7ff"/>
          </linearGradient>
          <style>
            .eyebrow { font: 700 15px Arial, sans-serif; letter-spacing: 3px; fill: #70e3c4; }
            .heading { font: 700 54px Arial, sans-serif; fill: #f4f7fb; }
            .intro { font: 400 21px Arial, sans-serif; fill: #b8c5d8; }
            .item-title { font: 700 15px Arial, sans-serif; letter-spacing: 2px; fill: #75e3c5; }
            .item-body { font: 400 18px Arial, sans-serif; fill: #dce5f1; }
            .quote { font: italic 24px Georgia, serif; fill: #f4f7fb; }
            .attribution { font: 700 13px Arial, sans-serif; letter-spacing: 2px; fill: #8ea2bd; }
            .number { font: 700 14px Arial, sans-serif; fill: #71849e; }
          </style>
        </defs>""",
        '<rect width="1200" height="900" rx="30" fill="url(#bg)"/>',
        '<circle cx="1080" cy="80" r="210" fill="#284d66" opacity=".15"/>',
        '<circle cx="1100" cy="70" r="135" fill="none" stroke="#62e6c5" stroke-opacity=".18"/>',
        '<rect x="72" y="68" width="1056" height="764" rx="24" fill="#111d30" stroke="#2a3a51" stroke-width="1.5"/>',
        '<rect x="72" y="68" width="7" height="764" rx="3.5" fill="url(#accent)"/>',
        '<text class="heading" x="120" y="210">About Me</text>',
        '<rect x="120" y="239" width="90" height="4" rx="2" fill="url(#accent)"/>',
        svg_text_lines(INTRO, 120, 294, 92, 31, "intro"),
    ]

    y_positions = [450, 555, 675]

    for index, ((label, body), y) in enumerate(zip(ITEMS, y_positions), start=1):
        parts.append(f'<text class="number" x="120" y="{y}">0{index}</text>')
        parts.append(
            f'<text class="item-title" x="170" y="{y}">{label}</text>'
        )
        parts.append(svg_text_lines(body, 170, y + 34, 82, 26, "item-body"))

    parts.extend(
        [
            '<rect x="120" y="765" width="960" height="48" rx="10" fill="#172840" stroke="#2d4560"/>',
            '<text x="145" y="800" font-size="32" fill="#62e6c5">“</text>',
            f'<text class="quote" x="185" y="793">{QUOTE}</text>',
            f'<text class="attribution" x="185" y="832">— {ATTRIBUTION}</text>',
            "</svg>",
        ]
    )

    return "\n".join(parts)


def update_readme_banner() -> None:
    banner = (
        "<!-- ABOUT-ME:START -->\n"
        '<p align="center">\n'
        f'  <img src=".github/assets/{BANNER_NAME}" '
        'alt="TAJ - Full-Stack Product Engineer" width="100%">\n'
        "</p>\n"
        "<!-- ABOUT-ME:END -->"
    )

    if README_PATH.exists():
        readme = README_PATH.read_text(encoding="utf-8")

        pattern = (
            r"<!-- ABOUT-ME:START -->"
            r".*?"
            r"<!-- ABOUT-ME:END -->"
        )

        if re.search(pattern, readme, flags=re.DOTALL):
            readme = re.sub(
                pattern,
                lambda _: banner,
                readme,
                count=1,
                flags=re.DOTALL,
            )
        else:
            readme = banner + "\n\n" + readme

        README_PATH.write_text(readme, encoding="utf-8")
    else:
        README_PATH.write_text(banner + "\n", encoding="utf-8")


def clean_previous_banners() -> None:
    for old_file in ASSET_DIR.glob("about-me-*.svg"):
        if old_file != SVG_PATH:
            old_file.unlink()


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    # Save the uniquely named SVG.
    svg = build_svg()
    SVG_PATH.write_text(svg, encoding="utf-8")

    # Update the README banner reference.
    update_readme_banner()

    # Remove older generated banners after README points to the new one.
    clean_previous_banners()

    print(f"Generated banner: {SVG_PATH.relative_to(ROOT)}")
    print("README banner reference updated.")
    print("Previous generated banner files cleaned.")


if __name__ == "__main__":
    main()
