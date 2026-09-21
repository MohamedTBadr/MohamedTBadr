import json
import os
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta, timezone
from html import escape
import math

USERNAME = os.environ.get("GITHUB_USERNAME", "MohamedTBadr")
TOKEN = os.environ.get("GH_TOKEN")

OUTPUT_PATH = "dist/activity-graph.svg"

# Beautiful line graph config - matches screenshot 1200x420
WIDTH = 1200
HEIGHT = 420
CHART_LEFT = 90
CHART_RIGHT = 1150
CHART_TOP = 80
CHART_BOTTOM = 350

BG_COLOR = "#0d1117"
ACCENT = "#512BD4"
GRID_COLOR = "#1a1f2e"
TEXT_COLOR = "#512BD4"
AXIS_COLOR = "#8b949e"


def graphql_request(query, variables):
    if not TOKEN:
        raise RuntimeError("GH_TOKEN environment variable is missing.")
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "github-activity-graph"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub GraphQL request failed: HTTP {error.code}\n{body}")
    if "errors" in result:
        raise RuntimeError("GitHub GraphQL returned errors:\n" + json.dumps(result["errors"], indent=2))
    return result["data"]


def fetch_contributions(username):
    today = date.today()
    start_date = today - timedelta(days=364)
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    variables = {
        "login": username,
        "from": f"{start_date.isoformat()}T00:00:00Z",
        "to": f"{today.isoformat()}T23:59:59Z"
    }
    data = graphql_request(query, variables)
    user = data.get("user")
    if not user:
        raise RuntimeError(f"GitHub user '{username}' was not found.")
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in calendar["weeks"]:
        for d in week["contributionDays"]:
            days.append({"date": d["date"], "count": d["contributionCount"]})
    # Guarantee sorted and windowed
    days = sorted(days, key=lambda x: x["date"])
    start_string = start_date.isoformat()
    end_string = today.isoformat()
    days = [d for d in days if start_string <= d["date"] <= end_string]
    return days, calendar["totalContributions"]


def nice_max(value):
    """Round up to nice max for Y axis (even, at least 4)"""
    if value <= 4:
        return 4
    if value <= 14:
        # round to even
        return ((value + 1) // 2) * 2
    # for larger values round to next multiple of 5 or 10
    if value < 50:
        return ((value + 4) // 5) * 5
    return ((value + 9) // 10) * 10


def build_svg(days, total_contributions, generated_at=None):
    if not days:
        raise RuntimeError("No contribution data was returned by GitHub.")

    # Use last 31 days for the beautiful line graph (like screenshot)
    last_n = 31
    recent = days[-last_n:] if len(days) >= last_n else days
    n = len(recent)
    counts = [d["count"] for d in recent]
    labels = [date.fromisoformat(d["date"]).day for d in recent]

    max_count = max(counts) if counts else 0
    max_y = nice_max(max_count)
    if max_y == 0:
        max_y = 4

    # chart geometry
    chart_w = CHART_RIGHT - CHART_LEFT
    chart_h = CHART_BOTTOM - CHART_TOP
    step_x = chart_w / (n - 1) if n > 1 else chart_w

    # compute points
    points = []
    for i, c in enumerate(counts):
        x = CHART_LEFT + i * step_x
        # y inverted: 0 at bottom, max at top
        y = CHART_BOTTOM - (c / max_y) * chart_h if max_y else CHART_BOTTOM
        points.append((x, y, c))

    # Build smooth path using Catmull-Rom to Bezier conversion
    def smooth_path(pts):
        if len(pts) == 0:
            return ""
        if len(pts) == 1:
            return f"M{pts[0][0]},{pts[0][1]}"
        d = f"M{pts[0][0]},{pts[0][1]}"
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else pts[0]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else pts[-1]
            # control points
            cp1x = p1[0] + (p2[0] - p0[0]) / 6
            cp1y = p1[1] + (p2[1] - p0[1]) / 6
            cp2x = p2[0] - (p3[0] - p1[0]) / 6
            cp2y = p2[1] - (p3[1] - p1[1]) / 6
            d += f"C{cp1x},{cp1y} {cp2x},{cp2y} {p2[0]},{p2[1]}"
        return d

    line_d = smooth_path(points)
    area_d = line_d + f"L{CHART_RIGHT},{CHART_BOTTOM}L{CHART_LEFT},{CHART_BOTTOM}Z"

    # Y ticks: 0 to max_y step 2 (or 5 if large)
    if max_y <= 14:
        y_step = 2
    elif max_y <= 50:
        y_step = 5
    else:
        y_step = 10

    y_ticks = list(range(0, max_y + 1, y_step))

    svg = []
    svg.append(f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Contribution graph">')
    svg.append(f'<rect data-testid="card_bg" x="0" y="0" width="100%" height="100%" rx="8" fill="{BG_COLOR}" />')
    # subtle top accent line
    svg.append(f'<rect x="0" y="0" width="{WIDTH}" height="2" rx="8" fill="{ACCENT}" opacity="0.35"/>')

    svg.append('<style>')
    svg.append('  .header { font: 600 20px \'Segoe UI\', Ubuntu, Sans-Serif; fill: #512BD4; }')
    svg.append('  .ct-label { fill: #512BD4; color: #512BD4; font: 600 13px \'Segoe UI\', Ubuntu, Sans-Serif; }')
    svg.append('  .ct-grid { stroke: #1e2436; stroke-width: 1; stroke-dasharray: 3 3; opacity: 0.9; }')
    svg.append('  .ct-grid.ct-vertical { stroke: #1e2436; }')
    svg.append('  .ct-line { fill: none; stroke: #512BD4; stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; }')
    svg.append('  .ct-area { fill: #512BD4; fill-opacity: 0.14; }')
    svg.append('  .ct-point { stroke: #512BD4; stroke-width: 3.5; stroke-linecap: round; }')
    svg.append('  .axis-title { fill: #512BD4; font: 500 14px \'Segoe UI\', Ubuntu, Sans-Serif; }')
    svg.append('</style>')

    # Header centered
    safe_name = escape(USERNAME)
    # Try to get real display name: Mohamed Tarek
    display = "Mohamed Tarek" if USERNAME.lower() == "mohamedtbadr" else USERNAME
    svg.append(f'<text x="{WIDTH//2}" y="38" text-anchor="middle" class="header">{escape(display)}\'s Contribution Graph</text>')

    # Grid vertical and horizontal
    svg.append('<g class="ct-grids">')
    # vertical grid lines (per day)
    for i in range(n):
        x = CHART_LEFT + i * step_x
        svg.append(f'<line x1="{x:.2f}" x2="{x:.2f}" y1="{CHART_TOP}" y2="{CHART_BOTTOM}" class="ct-grid ct-horizontal" />')
    # horizontal grid lines (per y tick)
    for tick in y_ticks:
        y = CHART_BOTTOM - (tick / max_y) * chart_h
        svg.append(f'<line y1="{y:.2f}" y2="{y:.2f}" x1="{CHART_LEFT}" x2="{CHART_RIGHT}" class="ct-grid ct-vertical" />')
    svg.append('</g>')

    # Area and line
    svg.append('<g class="ct-series ct-series-a">')
    svg.append(f'<path d="{area_d}" class="ct-area" />')
    svg.append(f'<path d="{line_d}" class="ct-line" />')
    # points
    for (x, y, c) in points:
        # point as small line (like chartist) with title
        svg.append(f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{x+0.01:.2f}" y2="{y:.2f}" class="ct-point"><title>{c} contributions on {recent[points.index((x,y,c))]["date"]}</title></line>')
        # visible dot
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.2" fill="{ACCENT}" stroke="#0d1117" stroke-width="1.2"><title>{c} contributions</title></circle>')
    svg.append('</g>')

    # Labels
    svg.append('<g class="ct-labels">')
    for i, day_num in enumerate(labels):
        x = CHART_LEFT + i * step_x
        # center label
        svg.append(f'<text x="{x:.2f}" y="{CHART_BOTTOM + 22}" text-anchor="middle" class="ct-label">{day_num}</text>')
    for tick in y_ticks:
        y = CHART_BOTTOM - (tick / max_y) * chart_h
        svg.append(f'<text y="{y+4:.2f}" x="{CHART_LEFT - 12}" text-anchor="end" class="ct-label">{tick}</text>')
    svg.append('</g>')

    # Axis titles
    svg.append(f'<text x="{(CHART_LEFT+CHART_RIGHT)//2}" y="{HEIGHT - 14}" text-anchor="middle" class="axis-title">Days</text>')
    # rotated Contributions
    svg.append(f'<text x="20" y="{(CHART_TOP+CHART_BOTTOM)//2}" transform="rotate(-90, 20, {(CHART_TOP+CHART_BOTTOM)//2})" text-anchor="middle" class="axis-title">Contributions</text>')

    svg.append('</svg>')
    return "\n".join(svg)


def main():
    print(f"Generating beautiful activity graph for: {USERNAME}")
    days, total = fetch_contributions(USERNAME)
    print(f"Received {len(days)} days, total {total}")
    recent_n = 31
    print(f"Building line graph for last {min(recent_n, len(days))} days")
    svg = build_svg(days, total, datetime.now(timezone.utc))
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
