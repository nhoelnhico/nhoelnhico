"""Regenerates README.md with live uptime and GitHub stats."""
import json, os, urllib.request
from datetime import date, datetime, timedelta, timezone

from update import CONFIG

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


THEMES = {
    "dark":  {"bg": "#161b22", "text": "#c9d1d9", "key": "#ffa657", "value": "#a5d6ff",
              "dots": "#616e7f", "head": "#ff7b72", "art": "#c9d1d9", "border": "#30363d"},
    "light": {"bg": "#f6f8fa", "text": "#24292f", "key": "#953800", "value": "#0a3069",
              "dots": "#afb8c1", "head": "#cf222e", "art": "#24292f", "border": "#d0d7de"},
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Each info line is a list of (text, style) segments so we can colour them.
def row(k, v):
    k, v = f"{k}:", str(v)
    return [(k, "key"), (" " + "." * max(1, WIDTH - len(k) - len(v) - 2) + " ", "dots"), (v, "value")]


def head(t):
    return [("- ", "dots"), (t, "head"), (" " + "-" * (WIDTH - len(t) - 3), "dots")]


def make_svg(art, info, theme):
    c = THEMES[theme]
    fs, lh, cw, pad = 14, 18, 8.4, 20          # font size, line height, char width, padding
    aw = max(map(len, art))
    gap = 4
    cols = aw + gap + WIDTH
    n = max(len(art), len(info))
    w = int(cols * cw + pad * 2)
    h = int(n * lh + pad * 2)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="Consolas, \'Courier New\', monospace" font-size="{fs}px">',
        "<style>"
        + "".join(f".{k}{{fill:{v}}}" for k, v in c.items() if k not in ("bg", "border"))
        + "</style>",
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" fill="{c["bg"]}" stroke="{c["border"]}"/>',
    ]
    for i in range(n):
        y = pad + (i + 1) * lh - 4
        a = art[i] if i < len(art) else ""
        if a.strip():
            out.append(f'<text x="{pad}" y="{y}" class="art" xml:space="preserve">{esc(a)}</text>')
        segs = info[i] if i < len(info) else []
        if segs:
            x = pad + (aw + gap) * cw
            spans = "".join(f'<tspan class="{cls}">{esc(t)}</tspan>' for t, cls in segs)
            out.append(f'<text x="{x:.1f}" y="{y}" xml:space="preserve">{spans}</text>')
    out.append("</svg>")
    return "\n".join(out)


def build():
    st = stats()
    c = CONFIG
    info = [
        [], [], [], [],
        [(f"{USER.lower()}@github", "head"), (" " + "-" * max(1, WIDTH - len(USER) - 8), "dots")],
        [],
        row("OS", c["OS"]),
        row("Uptime", uptime(BIRTHDAY, TODAY)),
        row("Host", c["Host"]),
        row("Kernel", c["Kernel"]),
        row("IDE", c["IDE"]),
        [],
        row("Languages.Programming", c["Languages.Programming"]),
        row("Languages.Real", c["Languages.Real"]),
        row("Hobbies", c["Hobbies"]),
        [],
        head("Contact"),
        row("Email", c["Email"]),
        row("LinkedIn", c["LinkedIn"]),
        [],
        head("GitHub Stats"),
        row("Repos", st["Repos"]),
        row("Stars", st["Stars"]),
        row("Commits", st["Commits"]),
        row("Followers", st["Followers"]),
    ]
    here = os.path.dirname(os.path.abspath(__file__))
    art = open(os.path.join(here, "art.txt"), encoding="utf-8").read().rstrip("\n").split("\n")
    for theme in THEMES:
        with open(os.path.join(here, f"{theme}_mode.svg"), "w", encoding="utf-8") as f:
            f.write(make_svg(art, info, theme))
    readme = (
        "<picture>\n"
        '  <source media="(prefers-color-scheme: dark)" srcset="dark_mode.svg">\n'
        f'  <img alt="{USER} GitHub profile" src="light_mode.svg">\n'
        "</picture>\n"
    )
    with open(os.path.join(here, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)
    print("Generated README.md, dark_mode.svg, light_mode.svg")


if __name__ == "__main__":
    build()
