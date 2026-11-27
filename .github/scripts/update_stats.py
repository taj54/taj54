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

LANG_COLORS = {
    "TypeScript": "#3178C6",
    "JavaScript": "#F7DF1E",
    "Python": "#3776AB",
    "PHP": "#777BB4",
    "HTML": "#E34F26",
    "CSS": "#1572B6",
    "Vue": "#4FC08D",
    "Shell": "#89E051",
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
    summary_items = [
        ("STARS", str(metrics["stars"]), "#FBBF24"),
        ("FORKS", str(metrics["forks"]), "#34D399"),
        ("OWNED REPOS", str(metrics["public_repos"]), "#38BDF8"),
        ("FOLLOWERS", str(metrics["followers"]), "#C084FC"),
    ]

    stat_cells = []
    for idx, (label, val, color) in enumerate(summary_items):
        col = idx % 2
        row = idx // 2
        x = 28 + col * 176
        y = 74 + row * 34
        stat_cells.append(
            f'<text x="{x}" y="{y}" fill="#94A3B8" font-size="10.5" font-weight="700" letter-spacing="0.6" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{label}:</text>'
            f'<text x="{x + 156}" y="{y}" text-anchor="end" fill="{color}" font-size="12.5" font-weight="700" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(val)}</text>'
        )

    repo_lines = []
    for i, (repo_name, stars) in enumerate(metrics["top_starred"]):
        ry = 138 + i * 19
        display_name = repo_name if len(repo_name) <= 28 else repo_name[:25] + "..."
        repo_lines.append(
            f'<text x="28" y="{ry}" fill="#E2E8F0" font-size="11.5" font-weight="600" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">★ {stars}  {html.escape(display_name)}</text>'
        )

    latest_display = metrics["latest_push"]
    if len(latest_display) > 46:
        latest_display = latest_display[:43] + "..."

    return f"""<svg width="400" height="210" viewBox="0 0 400 210" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="1" y="1" width="398" height="208" rx="14" fill="#0D1117" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="34" fill="#7AA2F7" font-size="14" font-weight="700"
        font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">⚡ Engineering Snapshot (@{html.escape(USERNAME)})</text>
  <line x1="28" y1="46" x2="372" y2="46" stroke="#1E293B" stroke-width="1"/>

  {''.join(stat_cells)}

  <line x1="28" y1="116" x2="372" y2="116" stroke="#1E293B" stroke-width="1"/>
  <text x="28" y="120" fill="#64748B" font-size="9.5" font-weight="700" letter-spacing="0.8"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" dominant-baseline="hanging">TOP STARRED REPOS</text>
  {''.join(repo_lines)}

  <text x="28" y="176" fill="#94A3B8" font-size="10.5"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">LATEST PUSH: {html.escape(latest_display)}</text>
  <text x="372" y="196" text-anchor="end" fill="#64748B" font-size="10"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">SYNCED {updated}</text>
</svg>
"""


def build_langs_svg(top_langs: list[tuple[str, int]], total_size_kb: int) -> str:
    total = sum(size for _, size in top_langs) or 1
    bar_x = 28
    bar_w = 344
    segments = []
    legend = []

    cursor = bar_x
    for idx, (lang, size) in enumerate(top_langs):
        pct = (size / total) * 100
        seg_w = max(4, round((size / total) * bar_w))
        color = LANG_COLORS.get(lang, "#7AA2F7")
        segments.append(
            f'<rect x="{cursor}" y="58" width="{seg_w}" height="11" fill="{color}"/>'
        )
        cursor += seg_w

        col = idx % 2
        row = idx // 2
        lx = 28 + col * 175
        ly = 98 + row * 23
        legend.append(
            f'<circle cx="{lx + 4}" cy="{ly - 4}" r="4.5" fill="{color}"/>'
            f'<text x="{lx + 15}" y="{ly}" fill="#E2E8F0" font-size="11.5" font-weight="600" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(lang)} {pct:.1f}%</text>'
        )

    footprint_label = f"CODEBASE FOOTPRINT: {format_size_kb(total_size_kb)} ACROSS {len(top_langs)} TOP LANGS"

    return f"""<svg width="400" height="210" viewBox="0 0 400 210" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="1" y="1" width="398" height="208" rx="14" fill="#0D1117" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="34" fill="#BB9AF7" font-size="14" font-weight="700"
        font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">🧩 Language &amp; Repo Mix</text>
  <line x1="28" y1="46" x2="372" y2="46" stroke="#1E293B" stroke-width="1"/>
  <rect x="{bar_x}" y="58" width="{bar_w}" height="11" rx="5.5" fill="#1E293B"/>
  {''.join(segments)}
  {''.join(legend)}
  <line x1="28" y1="166" x2="372" y2="166" stroke="#1E293B" stroke-width="1"/>
  <text x="28" y="192" fill="#94A3B8" font-size="10" font-weight="600"
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