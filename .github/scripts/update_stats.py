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


def fetch_metrics(username: str):
    user = github_get(f"https://api.github.com/users/{username}")
    repos = github_get(
        f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
    )
    own_repos = [r for r in repos if not r.get("fork")]
    total_stars = sum(r.get("stargazers_count", 0) for r in own_repos)
    total_forks = sum(r.get("forks_count", 0) for r in own_repos)

    lang_counts = Counter()
    for repo in own_repos:
        lang = repo.get("language")
        if lang:
            lang_counts[lang] += repo.get("size", 1)

    return {
        "public_repos": user.get("public_repos", len(own_repos)),
        "followers": user.get("followers", 0),
        "stars": total_stars,
        "forks": total_forks,
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
    items = [
        ("TOTAL STARS", str(metrics["stars"]), "#FBBF24"),
        ("PUBLIC REPOS", str(metrics["public_repos"]), "#38BDF8"),
        ("TOTAL FORKS", str(metrics["forks"]), "#34D399"),
        ("FOLLOWERS", str(metrics["followers"]), "#C084FC"),
    ]
    rows = []
    for idx, (label, val, color) in enumerate(items):
        y = 74 + idx * 24
        rows.append(
            f'<circle cx="34" cy="{y - 4}" r="4" fill="{color}"/>'
            f'<text x="48" y="{y}" fill="#94A3B8" font-size="12" font-weight="600" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{label}</text>'
            f'<text x="366" y="{y}" text-anchor="end" fill="#F8FAFC" font-size="13" font-weight="700" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(val)}</text>'
        )

    return f"""<svg width="400" height="195" viewBox="0 0 400 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="1" y="1" width="398" height="193" rx="14" fill="#0D1117" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="36" fill="#7AA2F7" font-size="14" font-weight="700"
        font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">⚡ GitHub Overview (@{html.escape(USERNAME)})</text>
  <line x1="28" y1="48" x2="372" y2="48" stroke="#1E293B" stroke-width="1"/>
  {''.join(rows)}
  <text x="372" y="178" text-anchor="end" fill="#64748B" font-size="10"
        font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">SYNCED {updated}</text>
</svg>
"""


def build_langs_svg(top_langs: list[tuple[str, int]]) -> str:
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
            f'<rect x="{cursor}" y="58" width="{seg_w}" height="10" fill="{color}"/>'
        )
        cursor += seg_w

        col = idx % 2
        row = idx // 2
        lx = 28 + col * 175
        ly = 96 + row * 24
        legend.append(
            f'<circle cx="{lx + 4}" cy="{ly - 4}" r="4.5" fill="{color}"/>'
            f'<text x="{lx + 15}" y="{ly}" fill="#E2E8F0" font-size="11.5" font-weight="600" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">{html.escape(lang)} {pct:.1f}%</text>'
        )

    return f"""<svg width="400" height="195" viewBox="0 0 400 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="1" y="1" width="398" height="193" rx="14" fill="#0D1117" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="36" fill="#BB9AF7" font-size="14" font-weight="700"
        font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">🧩 Top Languages (Owned Repos)</text>
  <rect x="{bar_x}" y="58" width="{bar_w}" height="10" rx="5" fill="#1E293B"/>
  {''.join(segments)}
  {''.join(legend)}
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
        build_langs_svg(metrics["top_langs"]), encoding="utf-8"
    )
    update_readme_stats(stats_file, langs_file)
    print(f"Generated .github/assets/{stats_file} and {langs_file}")


if __name__ == "__main__":
    main()