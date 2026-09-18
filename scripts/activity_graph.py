import json
import os
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta, timezone
from html import escape


USERNAME = os.environ.get("GITHUB_USERNAME", "MohamedTBadr")
TOKEN = os.environ.get("GH_TOKEN")

OUTPUT_PATH = "dist/activity-graph.svg"

WIDTH = 950
HEIGHT = 180

CELL_SIZE = 12
CELL_GAP = 3

BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b949e"
TITLE_COLOR = "#f0f6fc"

# GitHub-like contribution colors.
LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


def graphql_request(query, variables):
    if not TOKEN:
        raise RuntimeError("GH_TOKEN environment variable is missing.")

    payload = json.dumps({
        "query": query,
        "variables": variables
    }).encode("utf-8")

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
        raise RuntimeError(
            f"GitHub GraphQL request failed: HTTP {error.code}\n{body}"
        )

    if "errors" in result:
        raise RuntimeError(
            "GitHub GraphQL returned errors:\n"
            + json.dumps(result["errors"], indent=2)
        )

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
            colors
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
        for contribution_day in week["contributionDays"]:
            days.append({
                "date": contribution_day["date"],
                "count": contribution_day["contributionCount"]
            })

    # Guarantee exactly the requested 365-day window.
    start_string = start_date.isoformat()
    end_string = today.isoformat()

    days = [
        day
        for day in days
        if start_string <= day["date"] <= end_string
    ]

    return days, calendar["totalContributions"]


def calculate_level(count, maximum):
    if count == 0:
        return 0

    if maximum <= 0:
        return 0

    ratio = count / maximum

    if ratio <= 0.25:
        return 1
    elif ratio <= 0.50:
        return 2
    elif ratio <= 0.75:
        return 3
    else:
        return 4


def month_labels(days, start_x, cell_width):
    labels = []

    seen = set()

    for index, item in enumerate(days):
        current = date.fromisoformat(item["date"])

        if current.day <= 7:
            month_name = current.strftime("%b")

            if month_name not in seen:
                x = start_x + index * cell_width
                labels.append((x, month_name))
                seen.add(month_name)

    return labels


def build_svg(days, total_contributions, generated_at):
    if not days:
        raise RuntimeError("No contribution data was returned by GitHub.")

    maximum = max(day["count"] for day in days)

    start_date = date.fromisoformat(days[0]["date"])
    end_date = date.fromisoformat(days[-1]["date"])

    # Arrange the 365 days into a GitHub-style calendar.
    #
    # Each column is one week.
    # Each row is a weekday.
    #
    # The first column may contain empty cells because the
    # 365-day window does not necessarily start on Sunday.

    start_weekday = (start_date.weekday() + 1) % 7

    columns = (start_weekday + len(days) + 6) // 7

    cell_width = CELL_SIZE + CELL_GAP
    cell_height = CELL_SIZE + CELL_GAP

    graph_width = columns * cell_width

    left_margin = 45
    top_margin = 48

    graph_area_width = graph_width

    svg_width = max(WIDTH, left_margin + graph_area_width + 30)

    svg_height = HEIGHT

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_width}" height="{svg_height}" '
        f'viewBox="0 0 {svg_width} {svg_height}">'
    )

    svg.append(
        f'<rect width="100%" height="100%" rx="8" fill="{BG_COLOR}"/>'
    )

    # Title
    svg.append(
        f'<text x="{left_margin}" y="24" '
        f'fill="{TITLE_COLOR}" '
        f'font-family="Arial, Helvetica, sans-serif" '
        f'font-size="14" font-weight="600">'
        f"{escape(USERNAME)}'s GitHub Activity"
        f"</text>"
    )

    # Total contributions
    svg.append(
        f'<text x="{svg_width - 20}" y="24" '
        f'fill="{TEXT_COLOR}" '
        f'font-family="Arial, Helvetica, sans-serif" '
        f'font-size="12" text-anchor="end">'
        f"{total_contributions:,} contributions"
        f"</text>"
    )

    # Weekday labels
    weekday_labels = [
        ("Mon", 1),
        ("Wed", 3),
        ("Fri", 5)
    ]

    for label, row in weekday_labels:
        y = top_margin + row * cell_height + 10

        svg.append(
            f'<text x="5" y="{y}" '
            f'fill="{TEXT_COLOR}" '
            f'font-family="Arial, Helvetica, sans-serif" '
            f'font-size="9">'
            f"{label}"
            f"</text>"
        )

    # Month labels
    for index, item in enumerate(days):
        current = date.fromisoformat(item["date"])

        if current.day <= 7:
            column = (start_weekday + index) // 7

            x = left_margin + column * cell_width

            month_name = current.strftime("%b")

            svg.append(
                f'<text x="{x}" y="{top_margin - 10}" '
                f'fill="{TEXT_COLOR}" '
                f'font-family="Arial, Helvetica, sans-serif" '
                f'font-size="9">'
                f"{month_name}"
                f"</text>"
            )

    # Contribution cells
    for index, item in enumerate(days):
        current = date.fromisoformat(item["date"])

        position = start_weekday + index

        column = position // 7
        row = position % 7

        x = left_margin + column * cell_width
        y = top_margin + row * cell_height

        count = item["count"]

        level = calculate_level(count, maximum)

        color = LEVEL_COLORS[level]

        tooltip = (
            f"{count} contribution"
            f"{'' if count == 1 else 's'} on "
            f"{current.strftime('%b %d, %Y')}"
        )

        svg.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" fill="{color}">'
            f"<title>{escape(tooltip)}</title>"
            f"</rect>"
        )

    # Legend
    legend_y = top_margin + 7 * cell_height + 20

    svg.append(
        f'<text x="{left_margin}" y="{legend_y}" '
        f'fill="{TEXT_COLOR}" '
        f'font-family="Arial, Helvetica, sans-serif" '
        f'font-size="9">'
        f"Less"
        f"</text>"
    )

    legend_x = left_margin + 32

    for level in range(5):
        x = legend_x + level * (CELL_SIZE + 4)

        svg.append(
            f'<rect x="{x}" y="{legend_y - 10}" '
            f'width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" fill="{LEVEL_COLORS[level]}"/>'
        )

    svg.append(
        f'<text x="{legend_x + 5 * (CELL_SIZE + 4) + 4}" '
        f'y="{legend_y}" '
        f'fill="{TEXT_COLOR}" '
        f'font-family="Arial, Helvetica, sans-serif" '
        f'font-size="9">'
        f"More"
        f"</text>"
    )

    # Footer / range
    generated_label = generated_at.strftime("%Y-%m-%d %H:%M UTC")

    svg.append(
        f'<text x="{left_margin}" y="{svg_height - 10}" '
        f'fill="{TEXT_COLOR}" '
        f'font-family="Arial, Helvetica, sans-serif" '
        f'font-size="9">'
        f"Updated: {generated_label}"
        f"</text>"
    )

    svg.append(
        f'<text x="{svg_width - 20}" y="{svg_height - 10}" '
        f'fill="{TEXT_COLOR}" '
        f'font-family="Arial, Helvetica, sans-serif" '
        f'font-size="9" text-anchor="end">'
        f"{start_date.strftime('%b %d, %Y')} — "
        f"{end_date.strftime('%b %d, %Y')}"
        f"</text>"
    )

    svg.append("</svg>")

    return "\n".join(svg)


def main():
    print(f"Generating activity graph for: {USERNAME}")

    days, total_contributions = fetch_contributions(USERNAME)

    print(f"Received {len(days)} contribution days.")
    print(f"Total contributions: {total_contributions}")

    if len(days) != 365:
        print(
            f"Warning: expected 365 days, "
            f"but received {len(days)} days."
        )

    generated_at = datetime.now(timezone.utc)

    svg = build_svg(days, total_contributions, generated_at)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write(svg)

    print(f"Activity graph generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
