import json
import os
import random
import re
import urllib.request
from pathlib import Path

README_PATH = Path("README.md")
STATE_PATH = Path(".github/fact_state.json")

START_MARKER = "<!-- RANDOM_FACT_START -->"
END_MARKER = "<!-- RANDOM_FACT_END -->"

FACT_BADGES = ["🎲", "💡", "🚀", "🛠️", "⚡", "🧠", "✨", "🔥"]

CURATED_FACTS = [
    "Built a Laravel MCP starter kit for tenant-aware apps.",
    "Migrated legacy CodeIgniter apps into Laravel with AI help.",
    "I create custom VS Code extensions just for fun.",
    "Automated version bumping with my own GitHub Action.",
    "Love mixing FastAPI with video workflows.",
    "Dark mode and lofi = peak productivity.",
    "I once broke production with a single missing comma.",
    "I debug best with strong coffee in hand.",
    "I write tools I wish already existed.",
    "I built a Telegram bot with modular handlers.",
    "Git commit messages are my form of storytelling.",
    "MoviePy and FastAPI power my video experiments.",
    "I forked youtube_metadata_verifier and made it better.",
    "I prefer clean, modular code over quick hacks.",
    "Sometimes I code just to automate coding itself.",
    "My VS Code setup changes more often than my wallpaper.",
    "I enjoy turning monoliths into SaaS platforms.",
    "I use CrewAI to teach old code new tricks.",
    "My projects usually start as scratchpads, then evolve.",
    "I think admins deserve beautiful dashboards too.",
    "I once fixed a bug by rewriting the whole module.",
    "I push commits with names only I can understand.",
    "I like making tech feel fun, not scary.",
]


def fetch_latest_push(username: str, token: str | None) -> str | None:
    if not username:
        return None
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "readme-dynamic-updater",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def get_json(url: str):
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        events = get_json(f"https://api.github.com/users/{username}/events/public?per_page=30")
    except Exception as exc:
        print(f"Warning: could not fetch GitHub events ({exc})")
        return None

    for event in events:
        if event.get("type") == "PushEvent":
            repo = event.get("repo", {}).get("name", "")
            if not repo:
                continue
            commits = event.get("payload", {}).get("commits", [])
            msg = commits[-1].get("message", "").splitlines()[0] if commits else ""
            if not msg:
                try:
                    repo_commits = get_json(f"https://api.github.com/repos/{repo}/commits?per_page=1")
                    if repo_commits:
                        msg = repo_commits[0]["commit"]["message"].splitlines()[0]
                except Exception:
                    pass
            repo_link = f"[`{repo}`](https://github.com/{repo})"
            if msg:
                return f"Pushed to {repo_link} — *\"{msg}\"*"
            return f"Building in {repo_link}"
    return None


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"used_indices": []}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def pick_next_fact(state: dict) -> tuple[int, str]:
    used = set(state.get("used_indices", []))
    available = [i for i in range(len(CURATED_FACTS)) if i not in used]
    if not available:
        used = set()
        available = list(range(len(CURATED_FACTS)))

    chosen_idx = random.choice(available)
    used.add(chosen_idx)
    state["used_indices"] = sorted(used)
    return chosen_idx + 1, CURATED_FACTS[chosen_idx]


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
    fact_num, fact = pick_next_fact(state)
    badge = random.choice(FACT_BADGES)
    activity = fetch_latest_push(
        os.getenv("GITHUB_ACTOR", ""),
        os.getenv("GITHUB_TOKEN"),
    )

    lines = [
        "> [!TIP]",
        f"> **{badge} Dev Trivia #{fact_num:02d}** — *{fact}*",
    ]
    if activity:
        lines.extend([
            ">",
            f"> **⚡ Latest Signal:** {activity}",
        ])

    update_readme("\n".join(lines))
    save_state(state)
    print(f"Updated README with Dev Trivia #{fact_num:02d}.")


if __name__ == "__main__":
    main()