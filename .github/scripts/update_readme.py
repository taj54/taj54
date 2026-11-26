import html
import json
import random
import re
import secrets
import textwrap
from datetime import datetime, timezone
from pathlib import Path

README_PATH = Path("README.md")
STATE_PATH = Path(".github/fact_state.json")
ASSETS_DIR = Path(".github/assets")

START_MARKER = "<!-- RANDOM_FACT_START -->"
END_MARKER = "<!-- RANDOM_FACT_END -->"

# (icon, category, primary_hex, secondary_hex, fact_text)
CURATED_FACTS = [
    ("🏗️", "ARCHITECTURE", "#0EA5E9", "#38BDF8", "Built a Laravel MCP starter kit for tenant-aware apps."),
    ("🤖", "AI & MIGRATION", "#8B5CF6", "#C084FC", "Migrated legacy CodeIgniter apps into Laravel with AI help."),
    ("🧩", "DEV TOOLS", "#10B981", "#34D399", "I create custom VS Code extensions just for fun."),
    ("⚙️", "AUTOMATION", "#F59E0B", "#FBBF24", "Automated version bumping with my own GitHub Action."),
    ("🎬", "MEDIA & API", "#EC4899", "#F472B6", "Love mixing FastAPI with video workflows."),
    ("🎧", "FLOW STATE", "#6366F1", "#818CF8", "Dark mode and lofi = peak productivity."),
    ("💥", "WAR STORIES", "#EF4444", "#F87171", "I once broke production with a single missing comma."),
    ("☕", "DEBUGGING", "#D97706", "#F59E0B", "I debug best with strong coffee in hand."),
    ("🛠️", "BUILDER MINDSET", "#14B8A6", "#2DD4BF", "I write tools I wish already existed."),
    ("🤖", "BOTS & HOOKS", "#3B82F6", "#60A5FA", "I built a Telegram bot with modular handlers."),
    ("📖", "GIT CRAFT", "#F97316", "#FB923C", "Git commit messages are my form of storytelling."),
    ("🎞️", "VIDEO LABS", "#EC4899", "#F472B6", "MoviePy and FastAPI power my video experiments."),
    ("🔍", "OPEN SOURCE", "#22C55E", "#4ADE80", "I forked youtube_metadata_verifier and made it better."),
    ("🧼", "CLEAN CODE", "#06B6D4", "#22D3EE", "I prefer clean, modular code over quick hacks."),
    ("♾️", "META CODING", "#8B5CF6", "#A78BFA", "Sometimes I code just to automate coding itself."),
    ("🎨", "SETUP TWEAKS", "#A855F7", "#C084FC", "My VS Code setup changes more often than my wallpaper."),
    ("🚀", "SAAS SCALE", "#2563EB", "#60A5FA", "I enjoy turning monoliths into SaaS platforms."),
    ("🧠", "AI AGENTS", "#7C3AED", "#A78BFA", "I use CrewAI to teach old code new tricks."),
    ("✨", "WORKFLOW", "#8B5CF6", "#EC4899", "My projects usually start as scratchpads, then evolve."),
    ("📊", "UI & UX", "#0284C7", "#38BDF8", "I think admins deserve beautiful dashboards too."),
    ("🔥", "REFACTORING", "#DC2626", "#F87171", "I once fixed a bug by rewriting the whole module."),
    ("🕵️", "GIT LORE", "#4F46E5", "#818CF8", "I push commits with names only I can understand."),
    ("🎉", "PHILOSOPHY", "#16A34A", "#4ADE80", "I like making tech feel fun, not scary."),
]


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"used_indices": []}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def pick_next_fact(state: dict) -> tuple[int, int, tuple[str, str, str, str, str]]:
    used = set(state.get("used_indices", []))
    available = [i for i in range(len(CURATED_FACTS)) if i not in used]
    if not available:
        used = set()
        available = list(range(len(CURATED_FACTS)))

    chosen_idx = random.choice(available)
    used.add(chosen_idx)
    state["used_indices"] = sorted(used)
    return chosen_idx + 1, len(used), CURATED_FACTS[chosen_idx]


def cleanup_old_svgs(assets_dir: Path) -> None:
    if not assets_dir.exists():
        return
    for old_file in assets_dir.glob("dev-trivia-*.svg"):
        old_file.unlink()


def build_svg_card(
    fact_num: int,
    seen_count: int,
    total: int,
    icon: str,
    category: str,
    c1: str,
    c2: str,
    fact: str,
) -> str:
    wrapped = textwrap.wrap(f'"{fact}"', width=56)[:2]
    line1 = html.escape(wrapped[0]) if wrapped else ""
    line2 = html.escape(wrapped[1]) if len(wrapped) > 1 else ""
    cat_escaped = html.escape(category)
    updated_date = datetime.now(timezone.utc).strftime("%b %d, %Y")
    progress_width = max(12, int((seen_count / total) * 220))
    cat_pill_width = max(96, len(category) * 8 + 28)

    quote_svg = (
        f'<text x="32" y="102" fill="#F8FAFC" font-size="21" font-weight="600" '
        f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">{line1}</text>'
    )
    if line2:
        quote_svg += (
            f'\n  <text x="32" y="130" fill="#E2E8F0" font-size="21" font-weight="600" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">{line2}</text>'
        )

    return f"""<svg width="800" height="195" viewBox="0 0 800 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="800" y2="195" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0D1117"/>
      <stop offset="55%" stop-color="#131926"/>
      <stop offset="100%" stop-color="#0D1117"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0" y1="0" x2="800" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
    <radialGradient id="glowOrb" cx="0.88" cy="0.2" r="0.55">
      <stop offset="0%" stop-color="{c1}" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="{c1}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#FFFFFF" fill-opacity="0.04"/>
    </pattern>
  </defs>

  <rect x="1" y="1" width="798" height="193" rx="16" fill="url(#bgGrad)" stroke="url(#accentGrad)" stroke-width="1.5"/>
  <rect x="1" y="1" width="798" height="193" rx="16" fill="url(#dots)"/>
  <rect x="1" y="1" width="798" height="193" rx="16" fill="url(#glowOrb)"/>

  <rect x="32" y="1" width="140" height="3" rx="1.5" fill="url(#accentGrad)"/>

  <g transform="translate(32, 24)">
    <rect width="152" height="28" rx="14" fill="#1E293B" stroke="{c1}" stroke-opacity="0.5"/>
    <circle cx="16" cy="14" r="4" fill="{c1}">
      <animate attributeName="opacity" values="1;0.3;1" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <text x="28" y="18" fill="#F1F5F9" font-size="11" font-weight="700" letter-spacing="1.1"
          font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">DEV TRIVIA #{fact_num:02d}</text>
  </g>

  <g transform="translate(194, 24)">
    <rect width="{cat_pill_width}" height="28" rx="14" fill="{c1}" fill-opacity="0.14" stroke="{c1}" stroke-opacity="0.35"/>
    <text x="{cat_pill_width // 2}" y="18" text-anchor="middle" fill="{c2}" font-size="11" font-weight="700" letter-spacing="1"
          font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{cat_escaped}</text>
  </g>

  <g transform="translate(716, 22)">
    <rect width="52" height="52" rx="14" fill="#161F30" stroke="#334155" stroke-width="1"/>
    <text x="26" y="34" text-anchor="middle" font-size="25">{icon}</text>
  </g>

  {quote_svg}

  <line x1="32" y1="154" x2="768" y2="154" stroke="#1E293B" stroke-width="1"/>

  <text x="32" y="176" fill="#94A3B8" font-size="11" font-weight="600"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">CYCLE {seen_count:02d}/{total:02d}</text>
  <rect x="118" y="168" width="220" height="7" rx="3.5" fill="#1E293B"/>
  <rect x="118" y="168" width="{progress_width}" height="7" rx="3.5" fill="url(#accentGrad)"/>

  <text x="768" y="176" text-anchor="end" fill="#64748B" font-size="11"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">UPDATED {updated_date.upper()} • GITHUB ACTIONS</text>
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
    state = load_state()
    total = len(CURATED_FACTS)
    fact_num, seen_count, (icon, category, c1, c2, fact) = pick_next_fact(state)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_old_svgs(ASSETS_DIR)

    token = secrets.token_hex(3)
    svg_filename = f"dev-trivia-{fact_num:02d}-{token}.svg"
    svg_path = ASSETS_DIR / svg_filename
    svg_path.write_text(
        build_svg_card(fact_num, seen_count, total, icon, category, c1, c2, fact),
        encoding="utf-8",
    )

    block_body = (
        '<p align="center">\n'
        f'  <img src=".github/assets/{svg_filename}" alt="Dev Trivia Card" width="100%" />\n'
        '</p>'
    )

    update_readme(block_body)
    save_state(state)
    print(f"Generated {svg_path} for Dev Trivia #{fact_num:02d} ({category}).")


if __name__ == "__main__":
    main()