#!/usr/bin/env python3

import os
import json
import urllib.request
from datetime import datetime


USERNAME = os.environ["GITHUB_ACTOR"]
TOKEN = os.environ["GH_TOKEN"]

OUTPUT = "assets/card-stats.svg"


def github_graphql(query):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "GitHub-Metrics-Card",
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.load(response)


query = f"""
query {{
  user(login: "{USERNAME}") {{
    login
    followers {{
      totalCount
    }}
    repositories(
      first: 100
      ownerAffiliations: OWNER
      isFork: false
    ) {{
      totalCount
      nodes {{
        stargazerCount
      }}
    }}
    contributionsCollection {{
      contributionCalendar {{
        totalContributions
        weeks {{
          contributionDays {{
            contributionCount
            date
          }}
        }}
      }}
    }}
  }}
}}
"""


data = github_graphql(query)["data"]["user"]

username = data["login"]
followers = data["followers"]["totalCount"]

repos = data["repositories"]
public_repos = repos["totalCount"]
stars = sum(repo["stargazerCount"] for repo in repos["nodes"])

calendar = data["contributionsCollection"]["contributionCalendar"]
contributions = calendar["totalContributions"]

days = []

for week in calendar["weeks"]:
    for day in week["contributionDays"]:
        days.append(day)

days.sort(key=lambda day: day["date"])


# Calculate longest streak
longest_streak = 0
current_longest = 0

for day in days:
    if day["contributionCount"] > 0:
        current_longest += 1
        longest_streak = max(longest_streak, current_longest)
    else:
        current_longest = 0


# Calculate current streak
current_streak = 0

for day in reversed(days):
    if day["contributionCount"] > 0:
        current_streak += 1
    elif current_streak > 0:
        break


svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="720"
height="280"
viewBox="0 0 720 280"
>

<rect
x="1"
y="1"
width="718"
height="278"
rx="16"
fill="#0d1117"
stroke="#30363d"
/>

<!-- Header -->

<text
x="36"
y="48"
font-family="JetBrains Mono, monospace"
font-size="20"
font-weight="700"
fill="#39d353"
>
{username}
</text>

<text
x="684"
y="48"
text-anchor="end"
font-family="Arial, sans-serif"
font-size="13"
fill="#8b949e"
>
at a glance
</text>

<line
x1="36"
y1="65"
x2="684"
y2="65"
stroke="#30363d"
/>


<!-- Row 1 -->

<text
x="80"
y="115"
font-family="Arial, sans-serif"
font-size="30"
font-weight="700"
fill="#c9d1d9"
>
{stars}
</text>

<text
x="80"
y="140"
font-family="Arial, sans-serif"
font-size="14"
fill="#8b949e"
>
Total stars
</text>


<text
x="300"
y="115"
font-family="Arial, sans-serif"
font-size="30"
font-weight="700"
fill="#c9d1d9"
>
{public_repos}
</text>

<text
x="300"
y="140"
font-family="Arial, sans-serif"
font-size="14"
fill="#8b949e"
>
Public repos
</text>


<text
x="520"
y="115"
font-family="Arial, sans-serif"
font-size="30"
font-weight="700"
fill="#c9d1d9"
>
{followers}
</text>

<text
x="520"
y="140"
font-family="Arial, sans-serif"
font-size="14"
fill="#8b949e"
>
Followers
</text>


<!-- Row 2 -->

<text
x="80"
y="205"
font-family="Arial, sans-serif"
font-size="30"
font-weight="700"
fill="#c9d1d9"
>
{contributions}
</text>

<text
x="80"
y="230"
font-family="Arial, sans-serif"
font-size="14"
fill="#8b949e"
>
Contributions
</text>


<text
x="300"
y="205"
font-family="Arial, sans-serif"
font-size="30"
font-weight="700"
fill="#c9d1d9"
>
{current_streak}
</text>

<text
x="300"
y="230"
font-family="Arial, sans-serif"
font-size="14"
fill="#8b949e"
>
Current streak
</text>


<text
x="520"
y="205"
font-family="Arial, sans-serif"
font-size="30"
font-weight="700"
fill="#c9d1d9"
>
{longest_streak}
</text>

<text
x="520"
y="230"
font-family="Arial, sans-serif"
font-size="14"
fill="#8b949e"
>
Longest streak
</text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open(OUTPUT, "w") as file:
    file.write(svg)

print(f"Generated {OUTPUT}")
