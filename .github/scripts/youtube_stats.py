"""Render the YouTube subscriber and view badges for the profile README.

The API key is read from the YOUTUBE_API_KEY env var (a GitHub Actions secret)
and sent as a request header, so it never appears in a URL, log line, or any
file written to this public repo. Only the public counts are written out.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

CHANNEL_ID = "UC2WHjPDvbE6O328n17ZGcfg"
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / ".github" / "assets"

# 14x14 white glyphs, drawn at (x, 7).
ICON_PLAY = (
    '<rect x="0.9" y="1.9" width="12.2" height="10.2" rx="1.6" fill="none" stroke="#fff" stroke-width="1.6"/>'
    '<path d="M5.4 4.4v5.2L9.8 7z" fill="#fff"/>'
)
ICON_EYE = (
    '<path d="M7 2.5C3.6 2.5 1 5.2 0 7c1 1.8 3.6 4.5 7 4.5s6-2.7 7-4.5c-1-1.8-3.6-4.5-7-4.5z" fill="#fff"/>'
    '<circle cx="7" cy="7" r="2.6" fill="{bg}"/>'
)


def fetch_stats():
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        sys.exit("YOUTUBE_API_KEY is not set")
    req = urllib.request.Request(
        f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}",
        headers={"X-Goog-Api-Key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            items = json.load(resp).get("items") or []
    except Exception as e:  # don't let anything request-related leak into logs
        sys.exit(f"YouTube API request failed: {type(e).__name__}")
    if not items:
        sys.exit("YouTube API returned no channel")
    stats = items[0]["statistics"]
    return int(stats["subscriberCount"]), int(stats["viewCount"])


def short(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B".replace(".0B", "B")
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n // 1_000}k"
    return str(n)


def text_width(s, bold=False):
    # Rough Verdana 10px advance widths with for-the-badge letter spacing.
    w = sum(6.4 if c.isdigit() else 4.0 if c in ".," else 7.2 for c in s)
    return w * (1.08 if bold else 1.0) + 1.25 * max(len(s) - 1, 0)


def badge(label, value, icon, label_bg, value_bg):
    label, value = label.upper(), value.upper()
    lw = 9 + 14 + 6 + text_width(label) + 9
    vw = 9 + text_width(value, bold=True) + 9
    lt = text_width(label)
    vt = text_width(value, bold=True)
    w = lw + vw
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="28" viewBox="0 0 {w:.0f} 28" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <rect width="{lw:.1f}" height="28" fill="{label_bg}"/>
  <rect x="{lw:.1f}" width="{vw:.1f}" height="28" fill="{value_bg}"/>
  <g transform="translate(9 7)">{icon.format(bg=label_bg)}</g>
  <g fill="#fff" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="10" text-rendering="geometricPrecision">
    <text x="{9 + 14 + 6:.1f}" y="17.5" textLength="{lt:.1f}" lengthAdjust="spacingAndGlyphs">{label}</text>
    <text x="{lw + 9:.1f}" y="17.5" textLength="{vt:.1f}" lengthAdjust="spacingAndGlyphs" font-weight="bold">{value}</text>
  </g>
</svg>
"""


def main():
    subs, views = fetch_stats()
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "youtube-subscribers.svg").write_text(
        badge("Subscribe", short(subs), ICON_PLAY, "#CE4630", "#E05D44")
    )
    (ASSETS / "youtube-views.svg").write_text(
        badge("Views", short(views), ICON_EYE, "#C79600", "#E1AD0E")
    )
    print(f"subscribers={short(subs)} views={short(views)}")


if __name__ == "__main__":
    main()
