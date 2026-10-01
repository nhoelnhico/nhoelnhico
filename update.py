"""Regenerates README.md with live uptime and GitHub stats."""
import json, os, urllib.request
from datetime import date, datetime, timedelta, timezone

# ---- Edit these ---------------------------------------------------------
BIRTHDAY = date(1996, 8, 11)
CONFIG = {
    "OS": "Windows",
    "Host": "GRWM Cosmetics",
    "Kernel": "Full-Stack Developer",
    "IDE": "VS Code, Claude Code",
    "Languages.Programming": "PHP, JS, SQL",
    "Languages.Real": "English, Filipino",
    "Hobbies": "reading, writing, gaming, coding, music, anime",
    "Email": "nhico.ortazon@email.com",
    "LinkedIn": "in/nhico-noel-ortazon",
}
WIDTH = 46          # width of the right-hand info column
# -------------------------------------------------------------------------

USER = os.environ.get("GITHUB_REPOSITORY_OWNER") or os.environ.get("GH_USER", "octocat")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TODAY = datetime.now(timezone(timedelta(hours=8))).date()  # Philippine time


def uptime(born, today):
    y, m, d = today.year - born.year, today.month - born.month, today.day - born.day
    if d < 0:
        m -= 1
        prev_month_end = today.replace(day=1) - timedelta(days=1)
        d += prev_month_end.day
    if m < 0:
        y -= 1
        m += 12
    s = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return f"{s(y, 'year')}, {s(m, 'month')}, {s(d, 'day')}"


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-readme-updater")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def stats():
    user = api(f"/users/{USER}")
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    stars = sum(r["stargazers_count"] for r in repos if not r["fork"])
    try:
        commits = api(f"/search/commits?q=author:{USER}&per_page=1")["total_count"]
    except Exception:
        commits = 0
    return {
        "Repos": user["public_repos"],
        "Stars": stars,
        "Commits": commits,
        "Followers": user["followers"],
    }


def row(k, v):
    k, v = f"{k}:", str(v)
    return f"{k} {'.' * max(1, WIDTH - len(k) - len(v) - 2)} {v}"


def head(t):
    return f"- {t} " + "-" * (WIDTH - len(t) - 3)


def build():
    st = stats()
    c = CONFIG
    info = [
        "", "", "", "",
        f"{USER.lower()}@github " + "-" * max(1, WIDTH - len(USER) - 8),
        "",
        row("OS", c["OS"]),
        row("Uptime", uptime(BIRTHDAY, TODAY)),
        row("Host", c["Host"]),
        row("Kernel", c["Kernel"]),
        row("IDE", c["IDE"]),
        "",
        row("Languages.Programming", c["Languages.Programming"]),
        row("Languages.Real", c["Languages.Real"]),
        row("Hobbies", c["Hobbies"]),
        "",
        head("Contact"),
        row("Email", c["Email"]),
        row("LinkedIn", c["LinkedIn"]),
        "",
        head("GitHub Stats"),
        row("Repos", st["Repos"]),
        row("Stars", st["Stars"]),
        row("Commits", st["Commits"]),
        row("Followers", st["Followers"]),
    ]
    here = os.path.dirname(os.path.abspath(__file__))
    art = open(os.path.join(here, "art.txt"), encoding="utf-8").read().rstrip("\n").split("\n")
    aw = max(map(len, art))
    n = max(len(art), len(info))
    art += [""] * (n - len(art))
    info += [""] * (n - len(info))
    body = "\n".join(f"{a.ljust(aw)}    {b}".rstrip() for a, b in zip(art, info))
    with open(os.path.join(here, "README.md"), "w", encoding="utf-8") as f:
        f.write("```text\n" + body + "\n```\n")
    print(body)


if __name__ == "__main__":
    build()
