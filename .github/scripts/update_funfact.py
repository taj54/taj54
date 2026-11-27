import html
import json
import random
import re
import secrets
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

README_PATH = Path("README.md")
STATE_PATH = Path(".github/fact_state.json")
ASSETS_DIR = Path(".github/assets")

START_MARKER = "<!-- RANDOM_FACT_START -->"
END_MARKER = "<!-- RANDOM_FACT_END -->"


@dataclass(frozen=True)
class FactCard:
    emblem: str
    category: str
    primary_hex: str
    secondary_hex: str
    text: str


CURATED_FACTS: list[FactCard] = [
    FactCard("arch", "ARCHITECTURE", "#0EA5E9", "#38BDF8", "Built a Laravel MCP starter kit for tenant-aware apps."),
    FactCard("ai", "AI & MIGRATION", "#8B5CF6", "#C084FC", "Migrated legacy CodeIgniter apps into Laravel with AI help."),
    FactCard("tools", "DEV TOOLS", "#10B981", "#34D399", "I create custom VS Code extensions just for fun."),
    FactCard("auto", "AUTOMATION", "#F59E0B", "#FBBF24", "Automated version bumping with my own GitHub Action."),
    FactCard("media", "MEDIA & API", "#EC4899", "#F472B6", "Love mixing FastAPI with video workflows."),
    FactCard("flow", "FLOW STATE", "#6366F1", "#818CF8", "Dark mode and lofi = peak productivity."),
    FactCard("war", "WAR STORIES", "#EF4444", "#F87171", "I once broke production with a single missing comma."),
    FactCard("coffee", "DEBUGGING", "#D97706", "#F59E0B", "I debug best with strong coffee in hand."),
    FactCard("tools", "BUILDER MINDSET", "#14B8A6", "#2DD4BF", "I write tools I wish already existed."),
    FactCard("ai", "BOTS & HOOKS", "#3B82F6", "#60A5FA", "I built a Telegram bot with modular handlers."),
    FactCard("git", "GIT CRAFT", "#F97316", "#FB923C", "Git commit messages are my form of storytelling."),
    FactCard("media", "VIDEO LABS", "#EC4899", "#F472B6", "MoviePy and FastAPI power my video experiments."),
    FactCard("git", "OPEN SOURCE", "#22C55E", "#4ADE80", "I forked youtube_metadata_verifier and made it better."),
    FactCard("tools", "CLEAN CODE", "#06B6D4", "#22D3EE", "I prefer clean, modular code over quick hacks."),
    FactCard("auto", "META CODING", "#8B5CF6", "#A78BFA", "Sometimes I code just to automate coding itself."),
    FactCard("spark", "SETUP TWEAKS", "#A855F7", "#C084FC", "My VS Code setup changes more often than my wallpaper."),
    FactCard("arch", "SAAS SCALE", "#2563EB", "#60A5FA", "I enjoy turning monoliths into SaaS platforms."),
    FactCard("ai", "AI AGENTS", "#7C3AED", "#A78BFA", "I use CrewAI to teach old code new tricks."),
    FactCard("spark", "WORKFLOW", "#8B5CF6", "#EC4899", "My projects usually start as scratchpads, then evolve."),
    FactCard("arch", "UI & UX", "#0284C7", "#38BDF8", "I think admins deserve beautiful dashboards too."),
    FactCard("war", "REFACTORING", "#DC2626", "#F87171", "I once fixed a bug by rewriting the whole module."),
    FactCard("git", "GIT LORE", "#4F46E5", "#818CF8", "I push commits with names only I can understand."),
    FactCard("spark", "PHILOSOPHY", "#16A34A", "#4ADE80", "I like making tech feel fun, not scary."),
]


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"used_indices": []}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def pick_next_fact(state: dict, rng: random.Random) -> tuple[int, int, FactCard]:
    used = set(state.get("used_indices", []))
    available = [i for i in range(len(CURATED_FACTS)) if i not in used]
    if not available:
        used = set()
        available = list(range(len(CURATED_FACTS)))

    chosen_idx = rng.choice(available)
    used.add(chosen_idx)
    state["used_indices"] = sorted(used)
    return chosen_idx + 1, len(used), CURATED_FACTS[chosen_idx]


def cleanup_old_svgs(assets_dir: Path) -> None:
    if not assets_dir.exists():
        return
    for old_file in assets_dir.glob("dev-trivia-*.svg"):
        old_file.unlink()


def animated_emblem_svg(icon_key: str, primary: str, secondary: str) -> str:
    icons = {
        "arch": (
            f'<rect x="14" y="15" width="10" height="10" rx="2" stroke="{secondary}" stroke-width="2.2">'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; -2.5,-2.5; 0,0" dur="2.6s" repeatCount="indefinite"/>'
            f"</rect>"
            f'<rect x="28" y="15" width="10" height="10" rx="2" stroke="{secondary}" stroke-width="2.2">'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; 2.5,-2.5; 0,0" dur="2.6s" repeatCount="indefinite"/>'
            f"</rect>"
            f'<rect x="21" y="28" width="10" height="10" rx="2" fill="{primary}" fill-opacity="0.25" stroke="{primary}" stroke-width="2.2">'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; 0,2.5; 0,0" dur="2.6s" repeatCount="indefinite"/>'
            f"</rect>"
        ),
        "ai": (
            f'<g>'
            f'<circle cx="26" cy="26" r="7.5" stroke="{secondary}" stroke-width="2.2" stroke-dasharray="14 6"/>'
            f'<circle cx="26" cy="26" r="3" fill="{secondary}">'
            f'<animate attributeName="r" values="2.2;4;2.2" dur="1.7s" repeatCount="indefinite"/>'
            f"</circle>"
            f'<path d="M26 11v5M26 36v5M11 26h5M36 26h5" stroke="{primary}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<animateTransform attributeName="transform" type="rotate" from="0 26 26" to="360 26 26" dur="8s" repeatCount="indefinite"/>'
            f"</g>"
        ),
        "tools": (
            f'<path d="M21 18l-7 8 7 8" stroke="{secondary}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; -2.5,0; 0,0" dur="2s" repeatCount="indefinite"/>'
            f"</path>"
            f'<path d="M31 18l7 8-7 8" stroke="{secondary}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; 2.5,0; 0,0" dur="2s" repeatCount="indefinite"/>'
            f"</path>"
            f'<path d="M28 15l-4 22" stroke="{primary}" stroke-width="2.2" stroke-linecap="round"/>'
        ),
        "auto": (
            f'<path d="M28 13L16 28h9l-1 11 12-15h-9l1-11z" fill="{secondary}">'
            f'<animate attributeName="opacity" values="1;0.45;1" dur="1.3s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; 0,-2.5; 0,0" dur="1.3s" repeatCount="indefinite"/>'
            f"</path>"
        ),
        "media": (
            f'<rect x="14" y="16" width="24" height="20" rx="3" stroke="{secondary}" stroke-width="2.2">'
            f'<animate attributeName="stroke-opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>'
            f"</rect>"
            f'<polygon points="23,21 31,26 23,31" fill="{primary}">'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; 2,0; 0,0" dur="1.8s" repeatCount="indefinite"/>'
            f"</polygon>"
        ),
        "flow": (
            f'<path d="M13 26c3.5-8 9.5-8 13 0s9.5 8 13 0" stroke="{secondary}" stroke-width="2.4" stroke-linecap="round" fill="none">'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; 0,-3; 0,3; 0,0" dur="2.4s" repeatCount="indefinite"/>'
            f"</path>"
        ),
        "war": (
            f'<g>'
            f'<path d="M26 14l11 21H15L26 14z" fill="{primary}" fill-opacity="0.16" stroke="{secondary}" stroke-width="2.2" stroke-linejoin="round"/>'
            f'<line x1="26" y1="22" x2="26" y2="29" stroke="{secondary}" stroke-width="2.4" stroke-linecap="round"/>'
            f'<circle cx="26" cy="32.5" r="1.5" fill="{secondary}"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0,0; -1.8,0; 1.8,0; -1.8,0; 0,0" dur="1.8s" repeatCount="indefinite"/>'
            f"</g>"
        ),
        "coffee": (
            f'<path d="M16 20h16v9a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6v-9z" stroke="{secondary}" stroke-width="2.2"/>'
            f'<path d="M32 22h3a3 3 0 0 1 0 6h-3" stroke="{secondary}" stroke-width="2.2"/>'
            f'<line x1="16" y1="38" x2="32" y2="38" stroke="{secondary}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<path d="M20 16c0-2.5 2.5-2.5 2.5-5M27 16c0-2.5 2.5-2.5 2.5-5" stroke="{primary}" stroke-width="2" stroke-linecap="round" fill="none">'
            f'<animate attributeName="opacity" values="0.15;1;0.15" dur="1.9s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0,2.5; 0,-2.5; 0,2.5" dur="1.9s" repeatCount="indefinite"/>'
            f"</path>"
        ),
        "git": (
            f'<circle cx="19" cy="18" r="3.2" stroke="{secondary}" stroke-width="2.2"/>'
            f'<circle cx="19" cy="34" r="3.2" stroke="{secondary}" stroke-width="2.2"/>'
            f'<circle cx="33" cy="24" r="3.2" fill="{primary}" stroke="{primary}" stroke-width="2">'
            f'<animate attributeName="r" values="2.8;4.8;2.8" dur="1.8s" repeatCount="indefinite"/>'
            f"</circle>"
            f'<path d="M19 21v10M19 24c0 3 14 3 14 0" stroke="{secondary}" stroke-width="2.2"/>'
        ),
        "spark": (
            f'<path d="M26 13l3 9 9 3-9 3-3 9-3-9-9-3 9-3 3-9z" fill="{secondary}">'
            f'<animateTransform attributeName="transform" type="scale" values="0.92;1.18;0.92" additive="sum" dur="1.9s" repeatCount="indefinite"/>'
            f"</path>"
        ),
    }
    body = icons.get(icon_key, icons["spark"])
    return (
        '<g transform="translate(716, 22)">\n'
        f'  <rect width="52" height="52" rx="14" fill="#161F30" stroke="{secondary}" stroke-opacity="0.6" stroke-width="1.2"/>\n'
        f"  {body}\n"
        "</g>"
    )


def vibrant_particles_svg(rng: random.Random, c1: str, c2: str) -> str:
    """Generate bright floating orbs and shooting spark streaks."""
    elements: list[str] = []

    for idx in range(14):
        x = rng.randint(36, 764)
        y = rng.randint(20, 145)
        r = round(rng.uniform(1.6, 3.6), 1)
        color = c1 if idx % 2 == 0 else c2
        dy = rng.choice([-16, -12, 12, 16])
        dx = rng.choice([-14, 14])
        dur = round(rng.uniform(3.2, 6.4), 1)
        begin = round(rng.uniform(0.0, 2.5), 1)
        elements.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" fill-opacity="0.55">'
            f'<animate attributeName="opacity" values="0.2;0.85;0.2" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,0; {dx},{dy}; 0,0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f"</circle>"
        )

    for streak_idx in range(3):
        sy = 34 + streak_idx * 38
        sdur = round(rng.uniform(4.2, 6.2), 1)
        sbegin = round(streak_idx * 1.4, 1)
        scolor = c2 if streak_idx % 2 == 0 else c1
        elements.append(
            f'<line x1="-90" y1="{sy}" x2="-10" y2="{sy}" stroke="{scolor}" stroke-width="1.5" stroke-opacity="0.35" stroke-linecap="round">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,0; 920,0" dur="{sdur}s" begin="{sbegin}s" repeatCount="indefinite"/>'
            f"</line>"
        )

    return "\n    ".join(elements)


def wrap_quote_lines(text: str, width: int = 58, max_lines: int = 2) -> list[str]:
    lines = textwrap.wrap(f'"{text}"', width=width)
    if len(lines) <= max_lines:
        return lines
    trimmed = lines[:max_lines]
    trimmed[-1] = trimmed[-1].rstrip('"').rstrip(".") + '…"'
    return trimmed


def build_svg_card(
    fact_num: int,
    seen_count: int,
    total: int,
    card: FactCard,
    rng: random.Random,
) -> str:
    lines = wrap_quote_lines(card.text, width=58, max_lines=2)
    escaped_lines = [html.escape(line) for line in lines]
    cat_escaped = html.escape(card.category)
    updated_date = datetime.now(timezone.utc).strftime("%b %d, %Y").upper()

    progress_width = max(12, int((seen_count / total) * 220))
    cat_pill_width = max(96, len(card.category) * 8 + 28)

    quote_elements: list[str] = []
    start_y = 98 if len(escaped_lines) == 1 else 92
    line_gap = 28
    for i, line in enumerate(escaped_lines):
        y_pos = start_y + i * line_gap
        fill_color = "#F8FAFC" if i == 0 else "#E2E8F0"
        quote_elements.append(
            f'<text x="32" y="{y_pos}" fill="{fill_color}" font-size="20" font-weight="600" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">{line}</text>'
        )
    quote_svg = "\n    ".join(quote_elements)
    particles_svg = vibrant_particles_svg(rng, card.primary_hex, card.secondary_hex)

    return f"""<svg width="800" height="195" viewBox="0 0 800 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="800" y2="195" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0D1117"/>
      <stop offset="50%" stop-color="#151C2C"/>
      <stop offset="100%" stop-color="#0D1117"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0" y1="0" x2="800" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{card.primary_hex}"/>
      <stop offset="50%" stop-color="{card.secondary_hex}"/>
      <stop offset="100%" stop-color="{card.primary_hex}"/>
    </linearGradient>
    <linearGradient id="sheenGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="{card.secondary_hex}" stop-opacity="0.11"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glowOrbA" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="{card.primary_hex}" stop-opacity="0.34"/>
      <stop offset="100%" stop-color="{card.primary_hex}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowOrbB" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="{card.secondary_hex}" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="{card.secondary_hex}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.1" fill="#FFFFFF" fill-opacity="0.06"/>
      <animateTransform attributeName="patternTransform" type="translate" values="0,0; 20,20" dur="12s" repeatCount="indefinite"/>
    </pattern>
    <clipPath id="cardClip">
      <rect x="1" y="1" width="798" height="193" rx="16"/>
    </clipPath>
  </defs>

  <g clip-path="url(#cardClip)">
    <rect x="1" y="1" width="798" height="193" rx="16" fill="url(#bgGrad)"/>
    <rect x="1" y="1" width="798" height="193" rx="16" fill="url(#dots)"/>

    <!-- Dual orbiting glow orbs -->
    <circle cx="670" cy="45" r="200" fill="url(#glowOrbA)">
      <animateTransform attributeName="transform" type="translate" values="0,0; -140,35; -40,75; 0,0" dur="9s" repeatCount="indefinite"/>
    </circle>
    <circle cx="160" cy="145" r="180" fill="url(#glowOrbB)">
      <animateTransform attributeName="transform" type="translate" values="0,0; 160,-45; 60,-85; 0,0" dur="11s" repeatCount="indefinite"/>
    </circle>

    <!-- Sweeping diagonal light sheen -->
    <polygon points="-140,0 -20,0 80,195 -40,195" fill="url(#sheenGrad)">
      <animateTransform attributeName="transform" type="translate" values="0,0; 940,0" dur="5.5s" repeatCount="indefinite"/>
    </polygon>

    <!-- Floating particles & light streaks -->
    {particles_svg}

    <!-- Animated top accent bar -->
    <rect x="32" y="1" width="180" height="3.5" rx="1.75" fill="url(#accentGrad)">
      <animateTransform attributeName="transform" type="translate" values="0,0; 556,0; 0,0" dur="4.8s" repeatCount="indefinite"/>
    </rect>

    <!-- Trivia badge -->
    <g transform="translate(32, 24)">
      <rect width="152" height="28" rx="14" fill="#1E293B" stroke="{card.secondary_hex}" stroke-opacity="0.65"/>
      <circle cx="16" cy="14" r="4.2" fill="{card.secondary_hex}">
        <animate attributeName="opacity" values="1;0.2;1" dur="1.5s" repeatCount="indefinite"/>
        <animate attributeName="r" values="3.2;5.4;3.2" dur="1.5s" repeatCount="indefinite"/>
      </circle>
      <text x="28" y="18" fill="#F8FAFC" font-size="11" font-weight="700" letter-spacing="1.1"
            font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">DEV TRIVIA #{fact_num:02d}</text>
    </g>

    <!-- Category pill -->
    <g transform="translate(194, 24)">
      <rect width="{cat_pill_width}" height="28" rx="14" fill="{card.primary_hex}" fill-opacity="0.18" stroke="{card.secondary_hex}" stroke-opacity="0.5"/>
      <text x="{cat_pill_width // 2}" y="18" text-anchor="middle" fill="{card.secondary_hex}" font-size="11" font-weight="700" letter-spacing="1"
            font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{cat_escaped}</text>
    </g>

    {animated_emblem_svg(card.emblem, card.primary_hex, card.secondary_hex)}

    {quote_svg}

    <line x1="32" y1="154" x2="768" y2="154" stroke="#1E293B" stroke-width="1"/>

    <text x="32" y="176" fill="#94A3B8" font-size="11" font-weight="600"
          font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">CYCLE {seen_count:02d}/{total:02d}</text>
    <rect x="118" y="168" width="220" height="7" rx="3.5" fill="#1E293B"/>
    <rect x="118" y="168" width="{progress_width}" height="7" rx="3.5" fill="url(#accentGrad)">
      <animate attributeName="opacity" values="0.75;1;0.75" dur="2s" repeatCount="indefinite"/>
    </rect>

    <text x="768" y="176" text-anchor="end" fill="#64748B" font-size="11"
          font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">UPDATED {updated_date} • GITHUB ACTIONS</text>
  </g>

  <rect x="1" y="1" width="798" height="193" rx="16" stroke="url(#accentGrad)" stroke-width="1.6"/>
</svg>
"""


def update_readme(block_body: str) -> None:
    content = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"({re.escape(START_MARKER)}).*?({re.escape(END_MARKER)})",
        re.DOTALL,
    )
    if not pattern.search(content):
        raise RuntimeError(f"Missing {START_MARKER} or {END_MARKER} in {README_PATH}")

    replacement = f"{START_MARKER}\n{block_body}\n{END_MARKER}"
    updated = pattern.sub(replacement, content, count=1)
    if not updated.endswith("\n"):
        updated += "\n"
    README_PATH.write_text(updated, encoding="utf-8")


def main() -> None:
    seed = secrets.randbits(64)
    rng = random.Random(seed)

    state = load_state()
    total = len(CURATED_FACTS)
    fact_num, seen_count, card = pick_next_fact(state, rng)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_old_svgs(ASSETS_DIR)

    token = secrets.token_hex(3)
    svg_filename = f"dev-trivia-{fact_num:02d}-{token}.svg"
    svg_path = ASSETS_DIR / svg_filename
    svg_path.write_text(
        build_svg_card(fact_num, seen_count, total, card, rng),
        encoding="utf-8",
    )

    block_body = (
        '<p align="center">\n'
        f'  <img src=".github/assets/{svg_filename}" alt="{html.escape(card.category)}: {html.escape(card.text)}" width="100%" />\n'
        '</p>'
    )

    update_readme(block_body)
    save_state(state)
    print(f"Generated {svg_path} for Dev Trivia #{fact_num:02d} ({card.category}).")


if __name__ == "__main__":
    main()