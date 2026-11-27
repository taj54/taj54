import html
import json
import os
import re
import secrets
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
ASSETS_DIR = REPO_ROOT / ".github" / "assets"
USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "taj54")
TOKEN = os.getenv("GITHUB_TOKEN", "")

START_MARKER = "<!-- STATS_CARDS_START -->"
END_MARKER = "<!-- STATS_CARDS_END -->"

# Tokyo Night palette tokens (Night / Storm / Accents)
BG_START = "#1a1b26"
BG_END = "#24283b"
SURFACE_TILE = "#1f2335"
BORDER_SUBTLE = "#292e42"
BORDER_FRAME = "#414868"
TEXT_PRIMARY = "#c0caf5"
TEXT_SECONDARY = "#9aa5ce"
TEXT_MUTED = "#565f89"
TN_BLUE = "#7aa2f7"
TN_PURPLE = "#bb9af7"
TN_CYAN = "#7dcfff"
TN_GREEN = "#9ece6a"
TN_YELLOW = "#e0af68"
TN_RED = "#f7768e"

LANG_COLORS = {
    "TypeScript": TN_BLUE,
    "JavaScript": TN_YELLOW,
    "Python": TN_CYAN,
    "PHP": TN_PURPLE,
    "HTML": TN_RED,
    "CSS": TN_BLUE,
    "Vue": TN_GREEN,
    "Shell": TN_GREEN,
}


def github_get(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-readme-sync",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def format_size_kb(kb: int) -> str:
    if kb >= 1024:
        return f"{kb / 1024:.1f} MB"
    return f"{kb} KB"


def fetch_metrics(username: str) -> dict:
    user = github_get(f"https://api.github.com/users/{username}")
    repos = github_get(
        f"https://api.github.com/users/{username}/repos?per_page=100&type=owner&sort=pushed"
    )
    own_repos = [r for r in repos if not r.get("fork")]
    total_stars = sum(r.get("stargazers_count", 0) for r in own_repos)
    total_forks = sum(r.get("forks_count", 0) for r in own_repos)
    total_size_kb = sum(r.get("size", 0) for r in own_repos)

    top_starred = sorted(
        own_repos,
        key=lambda r: (r.get("stargazers_count", 0), r.get("pushed_at", "")),
        reverse=True,
    )[:2]

    latest_repo = own_repos[0] if own_repos else None
    latest_push_label = "N/A"
    if latest_repo:
        pushed_str = latest_repo.get("pushed_at", "")[:10]
        latest_push_label = f"{latest_repo.get('name')} ({pushed_str})"

    lang_counts = Counter()
    for repo in own_repos:
        lang = repo.get("language")
        if lang:
            lang_counts[lang] += max(repo.get("size", 1), 1)

    return {
        "public_repos": len(own_repos),
        "followers": user.get("followers", 0),
        "stars": total_stars,
        "forks": total_forks,
        "total_size_kb": total_size_kb,
        "top_starred": [
            (r.get("name", ""), r.get("stargazers_count", 0)) for r in top_starred
        ],
        "latest_push": latest_push_label,
        "top_langs": lang_counts.most_common(5),
    }


def cleanup_old_stats_svgs(assets_dir: Path) -> None:
    if not assets_dir.exists():
        return
    for pattern in ("github-stats-*.svg", "top-langs-*.svg"):
        for old_file in assets_dir.glob(pattern):
            old_file.unlink()


def build_stats_svg(metrics: dict) -> str:
    updated = datetime.now(timezone.utc).strftime("%b %d, %Y").upper()
    tiles = [
        ("STARS", str(metrics["stars"]), TN_YELLOW),
        ("FORKS", str(metrics["forks"]), TN_GREEN),
        ("REPOS", str(metrics["public_repos"]), TN_CYAN),
        ("FOLLOWERS", str(metrics["followers"]), TN_PURPLE),
    ]

    tile_svg = []
    for idx, (label, val, accent) in enumerate(tiles):
        col = idx % 2
        row = idx // 2
        tx = 24 + col * 180
        ty = 56 + row * 48
        tile_svg.append(
            f'<rect x="{tx}" y="{ty}" width="172" height="40" rx="8" fill="{SURFACE_TILE}" stroke="{BORDER_SUBTLE}" stroke-width="1"/>'
            f'<rect x="{tx}" y="{ty + 8}" width="3" height="24" rx="1.5" fill="{accent}"/>'
            f'<text x="{tx + 12}" y="{ty + 17}" fill="{TEXT_MUTED}" font-size="9" font-weight="700" letter-spacing="0.8" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{label}</text>'
            f'<text x="{tx + 12}" y="{ty + 32}" fill="{TEXT_PRIMARY}" font-size="13" font-weight="700" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(val)}</text>'
        )

    repo_lines = []
    for i, (repo_name, stars) in enumerate(metrics["top_starred"]):
        ry = 172 + i * 16
        display_name = repo_name if len(repo_name) <= 27 else repo_name[:24] + "..."
        repo_lines.append(
            f'<text x="34" y="{ry}" fill="{TEXT_SECONDARY}" font-size="11" font-weight="600" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">'
            f'<tspan fill="{TN_YELLOW}">★ {stars}</tspan>  {html.escape(display_name)}</text>'
        )

    latest_display = metrics["latest_push"]
    if len(latest_display) > 42:
        latest_display = latest_display[:39] + "..."

    return f"""<svg width="400" height="228" viewBox="0 0 400 228" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="tnCardBg" x1="0" y1="0" x2="400" y2="228" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{BG_START}"/>
      <stop offset="100%" stop-color="{BG_END}"/>
    </linearGradient>
    <linearGradient id="tnTopBar" x1="24" y1="0" x2="376" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{TN_BLUE}"/>
      <stop offset="50%" stop-color="{TN_PURPLE}"/>
      <stop offset="100%" stop-color="{TN_CYAN}"/>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="398" height="226" rx="14" fill="url(#tnCardBg)" stroke="{BORDER_FRAME}" stroke-width="1.2"/>
  <rect x="24" y="1" width="120" height="2.5" rx="1.25" fill="url(#tnTopBar)"/>

  <text x="24" y="34" fill="{TN_BLUE}" font-size="13.5" font-weight="700"
        font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">⚡ Engineering Snapshot</text>
  <text x="376" y="34" text-anchor="end" fill="{TEXT_MUTED}" font-size="10.5" font-weight="600"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">@{html.escape(USERNAME)}</text>

  {''.join(tile_svg)}

  <rect x="24" y="158" width="352" height="44" rx="8" fill="{SURFACE_TILE}" stroke="{BORDER_SUBTLE}" stroke-width="1"/>
  {''.join(repo_lines)}

  <text x="24" y="216" fill="{TEXT_MUTED}" font-size="9.5"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">PUSH: {html.escape(latest_display)}</text>
  <text x="376" y="216" text-anchor="end" fill="{TEXT_MUTED}" font-size="9.5"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{updated}</text>
</svg>
"""


def build_langs_svg(top_langs: list[tuple[str, int]], total_size_kb: int) -> str:
    total = sum(size for _, size in top_langs) or 1
    bar_x = 24
    bar_w = 352
    segments = []
    legend = []

    cursor = bar_x
    for idx, (lang, size) in enumerate(top_langs):
        pct = (size / total) * 100
        seg_w = max(4, round((size / total) * bar_w))
        if idx == len(top_langs) - 1:
            seg_w = max(4, (bar_x + bar_w) - cursor)
        color = LANG_COLORS.get(lang, TN_BLUE)
        segments.append(
            f'<rect x="{cursor}" y="58" width="{seg_w}" height="10" rx="2" fill="{color}"/>'
        )
        cursor += seg_w

        col = idx % 2
        row = idx // 2
        lx = 24 + col * 178
        ly = 94 + row * 24
        legend.append(
            f'<rect x="{lx}" y="82" width="174" height="19" rx="6" fill="{SURFACE_TILE}" stroke="{BORDER_SUBTLE}" stroke-width="1"/>'
            if False
            else f'<circle cx="{lx + 8}" cy="{ly - 4}" r="4.5" fill="{color}"/>'
            f'<text x="{lx + 20}" y="{ly}" fill="{TEXT_PRIMARY}" font-size="11" font-weight="600" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(lang)} <tspan fill="{TEXT_SECONDARY}">{pct:.1f}%</tspan></text>'
        )

    footprint_label = f"{format_size_kb(total_size_kb)} FOOTPRINT • {len(top_langs)} ACTIVE LANGS"

    return f"""<svg width="400" height="228" viewBox="0 0 400 228" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="tnLangBg" x1="0" y1="0" x2="400" y2="228" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{BG_START}"/>
      <stop offset="100%" stop-color="{BG_END}"/>
    </linearGradient>
    <linearGradient id="tnLangBar" x1="24" y1="0" x2="376" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{TN_PURPLE}"/>
      <stop offset="100%" stop-color="{TN_CYAN}"/>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="398" height="226" rx="14" fill="url(#tnLangBg)" stroke="{BORDER_FRAME}" stroke-width="1.2"/>
  <rect x="24" y="1" width="120" height="2.5" rx="1.25" fill="url(#tnLangBar)"/>

  <text x="24" y="34" fill="{TN_PURPLE}" font-size="13.5" font-weight="700"
        font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">🧩 Language &amp; Repo Mix</text>
  <text x="376" y="34" text-anchor="end" fill="{TEXT_MUTED}" font-size="10.5" font-weight="600"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">OWNED</text>

  <rect x="{bar_x}" y="58" width="{bar_w}" height="10" rx="5" fill="{SURFACE_TILE}" stroke="{BORDER_SUBTLE}" stroke-width="1"/>
  {''.join(segments)}

  {''.join(legend)}

  <line x1="24" y1="184" x2="376" y2="184" stroke="{BORDER_SUBTLE}" stroke-width="1"/>
  <text x="24" y="216" fill="{TEXT_SECONDARY}" font-size="10" font-weight="600"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(footprint_label)}</text>
</svg>
"""


def update_readme_stats(stats_file: str, langs_file: str) -> None:
    content = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"({re.escape(START_MARKER)}).*?({re.escape(END_MARKER)})",
        re.DOTALL,
    )
    if not pattern.search(content):
        raise RuntimeError(f"Missing {START_MARKER} or {END_MARKER} in {README_PATH}")

    block_body = (
        '<div align="center">\n\n'
        f'<img src=".github/assets/{stats_file}" alt="Taj\'s GitHub Stats" width="48%" />\n'
        f'<img src=".github/assets/{langs_file}" alt="Top Languages" width="48%" />\n\n'
        '</div>'
    )
    replacement = f"{START_MARKER}\n{block_body}\n{END_MARKER}"
    updated = pattern.sub(replacement, content, count=1)
    if not updated.endswith("\n"):
        updated += "\n"
    README_PATH.write_text(updated, encoding="utf-8")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_old_stats_svgs(ASSETS_DIR)

    metrics = fetch_metrics(USERNAME)
    token = secrets.token_hex(3)
    stats_file = f"github-stats-{token}.svg"
    langs_file = f"top-langs-{token}.svg"

    (ASSETS_DIR / stats_file).write_text(
        build_stats_svg(metrics), encoding="utf-8"
    )
    (ASSETS_DIR / langs_file).write_text(
        build_langs_svg(metrics["top_langs"], metrics["total_size_kb"]),
        encoding="utf-8",
    )
    update_readme_stats(stats_file, langs_file)
    print(f"Generated .github/assets/{stats_file} and {langs_file}")


if __name__ == "__main__":
    main()