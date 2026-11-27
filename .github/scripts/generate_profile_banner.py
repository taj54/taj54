
#!/usr/bin/env python3
"""
Animated GitHub Profile Banner Generator
-----------------------------------------
Generates:
    .github/assets/profile-banner.svg

Updates:
    README.md

Run:
    python scripts/generate_profile_banner.py
"""

from pathlib import Path
from datetime import datetime, timezone
import html
import random
import re

# --------------------------------------------------
# Configuration
# --------------------------------------------------

README_PATH = Path("README.md")
SVG_PATH = Path(".github/assets/profile-banner.svg")

START_MARKER = "<!-- PROFILE_BANNER_START -->"
END_MARKER = "<!-- PROFILE_BANNER_END -->"

WIDTH = 1000
HEIGHT = 320

PROFILE = {
    "name": "Hi, I'm Taj!",
    "title": "Late-Night Code Whisperer & Full-Stack Product Engineer",
    "stack": "Laravel  •  React  •  TypeScript  •  Node.js",
    "subtitle": (
        "Architecting scalable multi-tenant systems, "
        "developer tools, and elegant apps since 2020."
    ),
}


# --------------------------------------------------
# SVG Particle Generator
# --------------------------------------------------

def generate_particles(count=40):
    rng = random.Random()
    particles = []

    colors = [
        "#38BDF8",
        "#67E8F9",
        "#A78BFA",
        "#93C5FD",
    ]

    for _ in range(count):
        x = rng.randint(20, WIDTH - 20)
        y = rng.randint(20, HEIGHT - 20)

        radius = rng.uniform(1, 2.5)
        duration = rng.uniform(3, 8)
        delay = rng.uniform(0, 5)

        color = rng.choice(colors)

        particles.append(f"""
        <circle
            cx="{x}"
            cy="{y}"
            r="{radius:.1f}"
            fill="{color}"
            opacity="0.4">

            <animate
                attributeName="opacity"
                values="0.1;0.9;0.1"
                dur="{duration:.1f}s"
                begin="{delay:.1f}s"
                repeatCount="indefinite"/>

            <animateTransform
                attributeName="transform"
                type="translate"
                values="0,0; 12,-15; 0,0"
                dur="{duration:.1f}s"
                begin="{delay:.1f}s"
                repeatCount="indefinite"/>

        </circle>
        """)

    return "\n".join(particles)


# --------------------------------------------------
# SVG Generator
# --------------------------------------------------

def generate_svg():

    particles = generate_particles()

    name = html.escape(PROFILE["name"])
    title = html.escape(PROFILE["title"])
    stack = html.escape(PROFILE["stack"])
    subtitle = html.escape(PROFILE["subtitle"])

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
    aria-labelledby="banner-title">

    <title id="banner-title">
        {name} - Full-Stack Product Engineer
    </title>

    <defs>

        <!-- Background -->
        <linearGradient id="background"
            x1="0" y1="0" x2="1" y2="1">

            <stop offset="0%" stop-color="#080D1B"/>
            <stop offset="50%" stop-color="#101A32"/>
            <stop offset="100%" stop-color="#071421"/>

        </linearGradient>

        <!-- Accent Gradient -->
        <linearGradient id="accent"
            x1="0" y1="0" x2="1" y2="0">

            <stop offset="0%" stop-color="#38BDF8"/>
            <stop offset="50%" stop-color="#A78BFA"/>
            <stop offset="100%" stop-color="#22D3EE"/>

            <animate
                attributeName="x1"
                values="0;1;0"
                dur="10s"
                repeatCount="indefinite"/>

        </linearGradient>

        <!-- Wave Gradient -->
        <linearGradient id="wave"
            x1="0" y1="0" x2="1" y2="0">

            <stop offset="0%"
                stop-color="#0EA5E9"
                stop-opacity="0.04"/>

            <stop offset="50%"
                stop-color="#8B5CF6"
                stop-opacity="0.25"/>

            <stop offset="100%"
                stop-color="#22D3EE"
                stop-opacity="0.08"/>

        </linearGradient>

        <!-- Blue Glow -->
        <radialGradient id="blueGlow">
            <stop offset="0%"
                stop-color="#38BDF8"
                stop-opacity="0.25"/>

            <stop offset="100%"
                stop-color="#38BDF8"
                stop-opacity="0"/>
        </radialGradient>

        <!-- Violet Glow -->
        <radialGradient id="violetGlow">
            <stop offset="0%"
                stop-color="#8B5CF6"
                stop-opacity="0.25"/>

            <stop offset="100%"
                stop-color="#8B5CF6"
                stop-opacity="0"/>
        </radialGradient>

        <!-- Grid -->
        <pattern id="grid"
            width="64"
            height="64"
            patternUnits="userSpaceOnUse">

            <path
                d="M64 0H0V64"
                fill="none"
                stroke="#94A3B8"
                stroke-opacity="0.05"/>

        </pattern>

        <clipPath id="clip">
            <rect
                width="{WIDTH}"
                height="{HEIGHT}"
                rx="16"/>
        </clipPath>

    </defs>

    <g clip-path="url(#clip)">

        <!-- Main Background -->
        <rect
            width="{WIDTH}"
            height="{HEIGHT}"
            fill="url(#background)"/>

        <rect
            width="{WIDTH}"
            height="{HEIGHT}"
            fill="url(#grid)"/>

        <!-- Moving Blue Glow -->
        <circle
            cx="180"
            cy="100"
            r="280"
            fill="url(#blueGlow)">

            <animate
                attributeName="cx"
                values="180;350;180"
                dur="17s"
                repeatCount="indefinite"/>

            <animate
                attributeName="cy"
                values="100;150;100"
                dur="13s"
                repeatCount="indefinite"/>

        </circle>

        <!-- Moving Violet Glow -->
        <circle
            cx="850"
            cy="260"
            r="300"
            fill="url(#violetGlow)">

            <animate
                attributeName="cx"
                values="850;680;850"
                dur="19s"
                repeatCount="indefinite"/>

        </circle>

        <!-- Floating Particles -->
        {particles}

        <!-- Animated Wave -->
        <path
            d="M0 210
               C170 155 300 255 500 205
               S820 155 1000 220
               L1000 320 L0 320 Z"
            fill="url(#wave)">

            <animate
                attributeName="d"
                values="
                M0 210 C170 155 300 255 500 205 S820 155 1000 220 L1000 320 L0 320 Z;
                M0 230 C170 280 300 165 500 230 S820 260 1000 195 L1000 320 L0 320 Z;
                M0 210 C170 155 300 255 500 205 S820 155 1000 220 L1000 320 L0 320 Z"
                dur="12s"
                repeatCount="indefinite"/>

        </path>

        <!-- Wave Outline -->
        <path
            d="M0 235
               C180 250 310 215 500 235
               S820 210 1000 240"
            fill="none"
            stroke="url(#accent)"
            stroke-opacity="0.4"
            stroke-width="1.5">

            <animate
                attributeName="d"
                values="
                M0 235 C180 250 310 215 500 235 S820 210 1000 240;
                M0 220 C180 205 310 250 500 220 S820 250 1000 220;
                M0 235 C180 250 310 215 500 235 S820 210 1000 240"
                dur="10s"
                repeatCount="indefinite"/>

        </path>

        <!-- Profile Text -->
        <g
            text-anchor="middle"
            font-family="Segoe UI, Arial, sans-serif">

            <text
                x="500"
                y="105"
                font-size="43"
                font-weight="750"
                fill="#F8FAFC">

                {name}

            </text>

            <text
                x="500"
                y="151"
                font-size="23"
                font-weight="650"
                fill="#D8E4F4">

                {title}

            </text>

            <text
                x="500"
                y="197"
                font-size="19"
                font-weight="600"
                fill="#67E8F9">

                {stack}

            </text>

            <text
                x="500"
                y="278"
                font-size="15"
                fill="#AABBD1">

                {subtitle}

            </text>

        </g>

        <!-- Moving Accent Line -->
        <rect
            x="90"
            y="25"
            width="150"
            height="3"
            rx="2"
            fill="url(#accent)">

            <animateTransform
                attributeName="transform"
                type="translate"
                values="0,0; 670,0; 0,0"
                dur="8s"
                repeatCount="indefinite"/>

        </rect>

    </g>

    <!-- Border -->
    <rect
        x="1"
        y="1"
        width="{WIDTH - 2}"
        height="{HEIGHT - 2}"
        rx="16"
        fill="none"
        stroke="url(#accent)"
        stroke-opacity="0.25"/>

    <!-- Generated: {generated} -->

</svg>
"""


# --------------------------------------------------
# README Updater
# --------------------------------------------------

def update_readme():

    if not README_PATH.exists():
        raise FileNotFoundError(
            f"README file not found: {README_PATH}"
        )

    content = README_PATH.read_text(encoding="utf-8")

    banner_block = f"""{START_MARKER}
<div align="center">
  <img
    src=".github/assets/profile-banner.svg"
    width="100%"
    alt="Taj - Full-Stack Product Engineer"/>
</div>
{END_MARKER}"""

    pattern = re.compile(
        re.escape(START_MARKER)
        + r".*?"
        + re.escape(END_MARKER),
        re.DOTALL
    )

    if pattern.search(content):

        content = pattern.sub(
            lambda _: banner_block,
            content,
            count=1
        )

    else:

        content = banner_block + "\n\n" + content.lstrip()

    README_PATH.write_text(
        content,
        encoding="utf-8"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    SVG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    svg = generate_svg()

    SVG_PATH.write_text(
        svg,
        encoding="utf-8"
    )

    update_readme()

    print("===================================")
    print(" Animated Profile Banner Generated ")
    print("===================================")
    print(f"SVG:     {SVG_PATH}")
    print(f"README:  {README_PATH}")
    print("Status:  Success")


if __name__ == "__main__":
    main()
