"""Render the profile README badges into .github/assets.

Matches shields.io's for-the-badge style: Verdana 10px, uppercase, 1.25px
letter spacing, with text widths from shields' own Verdana metrics
(anafanafo), so these sit alongside the shields-rendered tool badges.

Secrets come only from env vars (Actions secrets / the workflow token) and are
sent as request headers, never in URLs, logs, or files. Only public counts
are written to this public repo.
"""

import json
import math
import os
import sys
import urllib.request
from pathlib import Path

YOUTUBE_CHANNEL_ID = "UC2WHjPDvbE6O328n17ZGcfg"
GITHUB_USER = "ForrestKnight"
X_HANDLE = "ForrestPKnight"
ASSETS = Path(__file__).resolve().parents[2] / ".github" / "assets"

# Verdana 10px advance widths for ASCII 32..126 (anafanafo 2.0.0).
VERDANA_NORMAL = (
    "3.52 3.94 4.59 8.18 6.36 10.76 7.27 2.69 4.54 4.54 6.36 8.18 3.64 4.54 3.64 4.54 "
    "6.36 6.36 6.36 6.36 6.36 6.36 6.36 6.36 6.36 6.36 4.54 4.54 8.18 8.18 8.18 5.45 10 "
    "6.84 6.86 6.98 7.71 6.32 5.75 7.75 7.51 4.21 4.55 6.93 5.57 8.43 7.48 7.87 6.03 7.87 "
    "6.95 6.84 6.16 7.32 6.84 9.89 6.85 6.15 6.85 4.54 4.54 4.54 8.18 6.36 6.36 6.01 6.23 "
    "5.21 6.23 5.96 3.52 6.23 6.33 2.74 3.44 5.92 2.74 9.73 6.33 6.07 6.23 6.23 4.27 5.21 "
    "3.94 6.33 5.92 8.18 5.92 5.92 5.25 6.35 4.54 6.35 8.18 "
).split()
VERDANA_BOLD = (
    "3.42 4.02 5.87 8.67 7.11 12.72 8.62 3.32 5.43 5.43 7.11 8.67 3.61 4.8 3.61 6.89 7.11 "
    "7.11 7.11 7.11 7.11 7.11 7.11 7.11 7.11 7.11 4.02 4.02 8.67 8.67 8.67 6.17 9.64 7.76 "
    "7.62 7.24 8.3 6.83 6.5 8.11 8.37 5.46 5.55 7.71 6.37 9.48 8.47 8.5 7.33 8.5 7.82 7.1 "
    "6.82 8.12 7.64 11.28 7.64 7.37 6.92 5.43 6.89 5.43 8.67 7.11 7.11 6.68 6.99 5.88 "
    "6.99 6.64 4.22 6.99 7.12 3.42 4.03 6.71 3.42 10.58 7.12 6.87 6.99 6.99 4.97 5.93 "
    "4.56 7.12 6.5 9.79 6.69 6.51 5.97 7.11 5.43 7.11 8.67 "
).split()

# 14x14 white glyphs, drawn at (9, 7).
ICON_PLAY = (
    '<rect x="0.9" y="1.9" width="12.2" height="10.2" rx="1.6" fill="none" stroke="#fff" stroke-width="1.6"/>'
    '<path d="M5.4 4.4v5.2L9.8 7z" fill="#fff"/>'
)
ICON_EYE = (
    '<path d="M7 2.5C3.6 2.5 1 5.2 0 7c1 1.8 3.6 4.5 7 4.5s6-2.7 7-4.5c-1-1.8-3.6-4.5-7-4.5z" fill="#fff"/>'
    '<circle cx="7" cy="7" r="2.6" fill="{bg}"/>'
)
ICON_STAR = (
    '<path transform="scale(.875)" fill="#fff" d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 '
    '.416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194'
    'L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>'
)
ICON_X = (
    '<path transform="scale(.5833)" fill="#fff" d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 '
    '7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>'
)


def text_length(s, bold):
    table = VERDANA_BOLD if bold else VERDANA_NORMAL
    width = sum(float(table[ord(c) - 32]) if 32 <= ord(c) <= 126 else 10.0 for c in s)
    return math.floor(width) + 1.25 * len(s)


def badge(label, value, icon, label_bg, value_bg):
    label, value = label.upper(), value.upper()
    lt, vt = text_length(label, False), text_length(value, True)
    lx = 9 + 14 + 9
    lw = lx + lt + 12
    vw = 12 + vt + 12
    w = lw + vw
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="28" role="img" aria-label="{label}: {value}"><title>{label}: {value}</title><g shape-rendering="crispEdges"><rect width="{lw:g}" height="28" fill="{label_bg}"/><rect x="{lw:g}" width="{vw:g}" height="28" fill="{value_bg}"/></g><g transform="translate(9 7)">{icon.format(bg=label_bg)}</g><g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="100"><text transform="scale(.1)" x="{(lx + lt / 2) * 10:g}" y="175" textLength="{lt * 10:g}">{label}</text><text transform="scale(.1)" x="{(lw + 12 + vt / 2) * 10:g}" y="175" textLength="{vt * 10:g}" font-weight="bold">{value}</text></g></svg>
"""


def get_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def youtube_stats():
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is not set")
    data = get_json(
        f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}",
        {"X-Goog-Api-Key": key},
    )
    stats = data["items"][0]["statistics"]
    return int(stats["subscriberCount"]), int(stats["viewCount"])


def github_stars():
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    total, page = 0, 1
    while True:
        repos = get_json(
            f"https://api.github.com/users/{GITHUB_USER}/repos?type=owner&per_page=100&page={page}",
            headers,
        )
        total += sum(r["stargazers_count"] for r in repos)
        if len(repos) < 100:
            return total
        page += 1


def short(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B".replace(".0B", "B")
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}k".replace(".0k", "k") if n < 10_000 else f"{n // 1_000}k"
    return str(n)


def write(name, svg):
    (ASSETS / name).write_text(svg)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    failed = False

    write("x-follow.svg", badge("Follow", f"@{X_HANDLE}", ICON_X, "#000000", "#2F3336"))

    # Each source is independent: a failure keeps that badge's last good file.
    try:
        subs, views = youtube_stats()
        write("youtube-subscribers.svg", badge("Subscribe", short(subs), ICON_PLAY, "#CE4630", "#E05D44"))
        write("youtube-views.svg", badge("Views", short(views), ICON_EYE, "#C79600", "#E1AD0E"))
        print(f"subscribers={short(subs)} views={short(views)}")
    except Exception as e:  # type name only, so nothing request-related reaches the logs
        print(f"YouTube stats failed: {type(e).__name__}")
        failed = True

    try:
        stars = github_stars()
        write("github-stars.svg", badge("Stars", short(stars), ICON_STAR, "#488207", "#55960C"))
        print(f"stars={short(stars)}")
    except Exception as e:
        print(f"GitHub stars failed: {type(e).__name__}")
        failed = True

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
