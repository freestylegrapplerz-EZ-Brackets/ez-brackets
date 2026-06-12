# EZ Brackets

EZ Brackets is a Streamlit app for tournament directors who need to find single-athlete divisions in Smoothcomp registration exports and identify the best possible bracket merge options.

Built for Freestyle Grapplerz, the app reviews Smoothcomp CSV data, detects divisions with only one athlete, scores possible matches, flags academy-only matchups, marks unsafe jumps as Do Not Match, and exports director-ready Excel reports.

## What It Does

- Upload a Smoothcomp registrations CSV.
- Find single-athlete divisions.
- Suggest possible merge divisions.
- Score matches by entry type, weight, age, skill or belt, bracket size, and academy mix.
- Let staff adjust safety limits and scoring weights.
- Show a scoring breakdown for each recommendation.
- Export rank-one and full Excel reports.

## Match Scoring

EZ Brackets starts each possible match at 100 points, then adjusts the score based on:

- Gi vs No-Gi entry type.
- Weight difference.
- Age group difference.
- Skill or belt difference.
- Whether the target bracket has two or more athletes.
- Whether the resulting bracket would be all one academy.

Recommendations are suggestions only. Tournament staff should still use coach or parent approval and safety judgment before moving athletes.

## Required CSV Columns

The app tries to recognize common Smoothcomp column names automatically. It works best when the CSV includes:

- Name, Athlete, Competitor, or Full Name.
- Group, Division, Bracket, or Category.
- Academy, Affiliation, Team, Club, or School.
- Approved or Status.

The division/group text should follow a Smoothcomp-style pattern such as:

```text
No-Gi / Beginner / Teen / 120 - 130 lbs
```

## Requirements

- streamlit
- pandas
- openpyxl

## Run Locally

```bash
streamlit run app.py
```

## Live App

https://ez-brackets-pc6appxh4cvycfxvkhv5nc4.streamlit.app/
