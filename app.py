import re
from io import BytesIO

import pandas as pd
import streamlit as st


# =========================
# EZ BRACKETS - DEV v2
# =========================

st.set_page_config(
    page_title="EZ Brackets",
    page_icon="🥋",
    layout="wide",
)

st.markdown(
    '''
<style>
    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #0f172a 45%, #111827 100%);
        color: #f8fafc;
    }

    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #f8fafc !important;
    }

    .ez-hero {
        padding: 28px 32px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(34,197,94,0.18), rgba(59,130,246,0.12));
        border: 1px solid rgba(255,255,255,0.14);
        box-shadow: 0 20px 50px rgba(0,0,0,0.35);
        margin-bottom: 22px;
    }

    .ez-logo-row {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .ez-logo {
        width: 64px;
        height: 64px;
        border-radius: 18px;
        background: linear-gradient(135deg, #22c55e, #16a34a);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        font-weight: 900;
        color: white;
        box-shadow: 0 10px 30px rgba(34,197,94,0.35);
    }

    .ez-title {
        font-size: 54px;
        line-height: 1;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -1.5px;
        margin: 0;
    }

    .ez-subtitle {
        font-size: 18px;
        color: #cbd5e1 !important;
        margin-top: 10px;
        max-width: 950px;
    }

    .ez-badge {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(34,197,94,0.16);
        color: #bbf7d0 !important;
        border: 1px solid rgba(34,197,94,0.35);
        font-size: 13px;
        font-weight: 700;
        margin-top: 16px;
        margin-right: 8px;
    }

    .metric-card {
        padding: 22px 24px;
        border-radius: 20px;
        background: rgba(15,23,42,0.78);
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 12px 35px rgba(0,0,0,0.28);
        margin-bottom: 16px;
    }

    .metric-label {
        color: #94a3b8 !important;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: 6px;
    }

    .metric-value {
        color: #22c55e !important;
        font-size: 44px;
        font-weight: 900;
        line-height: 1;
    }

    .metric-help {
        color: #cbd5e1 !important;
        font-size: 13px;
        margin-top: 8px;
    }

    .section-card {
        padding: 22px;
        border-radius: 20px;
        background: rgba(15,23,42,0.66);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        margin-top: 16px;
        margin-bottom: 16px;
    }

    .warning-card {
        padding: 18px 20px;
        border-radius: 16px;
        background: rgba(239,68,68,0.13);
        border: 1px solid rgba(239,68,68,0.35);
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .success-card {
        padding: 18px 20px;
        border-radius: 16px;
        background: rgba(34,197,94,0.13);
        border: 1px solid rgba(34,197,94,0.35);
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .small-muted {
        color: #94a3b8 !important;
        font-size: 14px;
    }

    section[data-testid="stSidebar"] {
        background-color: #060b16 !important;
        border-right: 1px solid rgba(255,255,255,0.10);
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="select"] * {
        color: #111827 !important;
    }

    ul[role="listbox"] {
        background-color: white !important;
    }

    ul[role="listbox"] * {
        color: #111827 !important;
    }

    li[role="option"] {
        color: #111827 !important;
        background-color: white !important;
    }

    li[role="option"]:hover {
        background-color: #e5e7eb !important;
        color: #111827 !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.97) !important;
        border-radius: 16px;
        padding: 6px;
    }

    [data-testid="stFileUploader"] * {
        color: #111827 !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.12);
    }

    button[kind="secondary"] {
        border-radius: 12px !important;
        border: 1px solid rgba(34,197,94,0.45) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        background-color: rgba(255,255,255,0.06);
        color: #f8fafc !important;
        padding: 10px 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(34,197,94,0.18) !important;
        border-bottom: 3px solid #22c55e !important;
    }
</style>
''',
    unsafe_allow_html=True,
)


SKILL_ORDER = {
    "White": 0, "Grey": 1, "Gray": 1, "Yellow": 2, "Orange": 3, "Green": 4,
    "Novice": 10, "Beginner": 11, "Intermediate": 12, "Advanced": 13,
    "Blue": 20, "Purple": 21, "Brown": 22, "Black": 23,
}


AGE_ORDER_HINTS = [
    ("Mighty Mite", 1),
    ("Pee Wee", 2),
    ("Kindergarten", 3),
    ("Youth", 4),
    ("Pre Teen", 5),
    ("Junior Teen", 6),
    ("Teen", 7),
    ("Juvenile", 8),
    ("Adult", 20),
    ("Master 1", 21),
    ("Master 2", 22),
    ("Master 3", 23),
    ("Master 4", 24),
    ("Master 5", 25),
]


def find_col(df, possible_names):
    clean_map = {str(c).strip().lower(): c for c in df.columns}
    for name in possible_names:
        key = name.strip().lower()
        if key in clean_map:
            return clean_map[key]
    for c in df.columns:
        low = str(c).strip().lower()
        for name in possible_names:
            if name.strip().lower() in low:
                return c
    return None


def parse_group(group):
    parts = [p.strip() for p in str(group).split("/")]
    return (
        parts[0] if len(parts) > 0 else "",
        parts[1] if len(parts) > 1 else "",
        parts[2] if len(parts) > 2 else "",
        parts[3] if len(parts) > 3 else "",
    )


def skill_value(skill):
    s = str(skill)
    for key, value in SKILL_ORDER.items():
        if key.lower() in s.lower():
            return value
    return 999


def age_value(age):
    a = str(age)
    for key, value in AGE_ORDER_HINTS:
        if key.lower() in a.lower():
            return value
    nums = re.findall(r"\d+", a)
    return int(nums[0]) if nums else 999


def weight_mid(weight):
    w = str(weight).lower()
    nums = re.findall(r"\d+\.?\d*", w)
    if "over" in w and nums:
        return float(nums[0]) + 10
    if len(nums) >= 2:
        return (float(nums[0]) + float(nums[1])) / 2
    if len(nums) == 1:
        return float(nums[0])
    return None


def normalize_dataframe(raw_df):
    df = raw_df.copy()

    group_col = find_col(df, ["group", "division", "bracket", "category"])
    name_col = find_col(df, ["name", "athlete", "competitor", "full name"])
    approved_col = find_col(df, ["approved", "status"])
    academy_col = find_col(df, ["academy", "affiliation", "team", "club", "school"])

    if group_col is None:
        st.error("Could not find a division/group column in this CSV.")
        st.stop()

    df["athlete_name"] = df[name_col].astype(str).str.strip() if name_col else df.index.astype(str)
    df["approved_clean"] = df[approved_col].astype(str).str.strip() if approved_col else "Approved"
    df["academy_clean"] = df[academy_col].astype(str).str.strip() if academy_col else ""
    df["group_clean"] = df[group_col].astype(str).str.strip()

    parsed = df["group_clean"].apply(parse_group)
    df["entry_clean"] = parsed.apply(lambda x: x[0])
    df["skill_clean"] = parsed.apply(lambda x: x[1])
    df["age_clean"] = parsed.apply(lambda x: x[2])
    df["weight_clean"] = parsed.apply(lambda x: x[3])

    return df


def group_summary(df):
    rows = []
    for group, g in df.groupby("group_clean", dropna=False):
        sample = g.iloc[0]
        academies = sorted(set([a for a in g["academy_clean"].dropna().astype(str).tolist() if a.strip()]))
        rows.append({
            "group": group,
            "athletes": len(g),
            "entry": sample.get("entry_clean", ""),
            "skill": sample.get("skill_clean", ""),
            "age": sample.get("age_clean", ""),
            "weight": sample.get("weight_clean", ""),
            "names": ", ".join(g["athlete_name"].astype(str).tolist()),
            "academies": ", ".join(academies),
            "academy_count": len(academies),
        })
    return pd.DataFrame(rows).sort_values(["athletes", "group"]).reset_index(drop=True)


def same_entry(a, b):
    a = str(a).lower()
    b = str(b).lower()
    a_nogi = "no-gi" in a or "no gi" in a
    b_nogi = "no-gi" in b or "no gi" in b
    if "gi" in a and "gi" in b:
        return a_nogi == b_nogi
    return a == b


def academy_mix_after_move(single_academy, target_academies):
    academies = []
    if str(target_academies).strip():
        academies += [a.strip() for a in str(target_academies).split(",") if a.strip()]
    if str(single_academy).strip():
        academies.append(str(single_academy).strip())
    unique = sorted(set([a for a in academies if a]))
    return " + ".join(unique), len(unique)


def quality_label(score):
    if score >= 85:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Review"
    if score >= 40:
        return "Last resort"
    return "No strong match"


def score_candidate(single, cand, allow_entry_crossover=False):
    if not allow_entry_crossover and not same_entry(single.get("entry_clean", ""), cand.get("entry", "")):
        return None

    skill_diff = abs(skill_value(single.get("skill_clean", "")) - skill_value(cand.get("skill", "")))
    age_diff = abs(age_value(single.get("age_clean", "")) - age_value(cand.get("age", "")))

    sw = weight_mid(single.get("weight_clean", ""))
    cw = weight_mid(cand.get("weight", ""))
    weight_diff = abs(sw - cw) if sw is not None and cw is not None else 999

    score = 100
    reasons = []

    if not same_entry(single.get("entry_clean", ""), cand.get("entry", "")):
        score -= 30
        reasons.append("Gi/No-Gi crossover")

    if weight_diff == 999:
        score -= 10
        reasons.append("unknown weight difference")
    elif weight_diff <= 10:
        reasons.append(f"good weight match ({weight_diff:.1f} lbs)")
    elif weight_diff <= 20:
        score -= 12
        reasons.append(f"moderate weight jump ({weight_diff:.1f} lbs)")
    elif weight_diff <= 30:
        score -= 25
        reasons.append(f"large weight jump ({weight_diff:.1f} lbs)")
    else:
        score -= 45
        reasons.append(f"very large weight jump ({weight_diff:.1f} lbs)")

    if skill_diff == 0:
        reasons.append("same skill/belt")
    elif skill_diff == 1:
        score -= 10
        reasons.append("one skill/belt level difference")
    elif skill_diff <= 3:
        score -= 25
        reasons.append("skill/belt difference")
    else:
        score -= 45
        reasons.append("major skill/belt difference")

    if age_diff == 0:
        reasons.append("same age group")
    elif age_diff == 1:
        score -= 10
        reasons.append("one age group difference")
    elif age_diff <= 3:
        score -= 22
        reasons.append("age group jump")
    else:
        score -= 40
        reasons.append("major age group jump")

    academy_mix, academy_count = academy_mix_after_move(single.get("academy_clean", ""), cand.get("academies", ""))

    target_size = int(cand.get("athletes", 1))
    academy_warning = ""
    if academy_count <= 1 and target_size >= 1:
        score -= 35
        academy_warning = "⚠️ All same academy"
        reasons.append("would create/keep all-same-academy bracket")
    elif academy_count >= 2:
        score += 4
        reasons.append("mixed academy bracket")

    if target_size >= 3:
        score += 5
        reasons.append("target has 3+ athletes")
    elif target_size == 2:
        score += 2
        reasons.append("target has 2 athletes")

    score = max(0, min(100, int(round(score))))

    return score, "; ".join(reasons), weight_diff, age_diff, skill_diff, academy_warning, academy_mix


def make_recommendations(df, only_approved=True, min_target_size=1, top_n=3, allow_entry_crossover=False):
    working = df.copy()

    if only_approved and "approved_clean" in working.columns:
        approved_mask = working["approved_clean"].astype(str).str.lower().eq("approved")
        if approved_mask.any():
            working = working[approved_mask]

    summary = group_summary(working)
    singles_groups = summary[summary["athletes"] == 1]["group"].tolist()
    target_groups = summary[summary["athletes"] >= min_target_size].copy()

    rows = []

    for group in singles_groups:
        single = working[working["group_clean"] == group].iloc[0]
        candidates = target_groups[target_groups["group"] != group].copy()

        scored = []
        for _, cand in candidates.iterrows():
            result = score_candidate(single, cand, allow_entry_crossover)
            if result is None:
                continue

            score, why, weight_diff, age_diff, skill_diff, academy_warning, academy_mix = result

            scored.append({
                "Rank": 0,
                "Athlete": single["athlete_name"],
                "Quality": quality_label(score),
                "Match Score": score,
                "Current Division": group,
                "Suggested Division": cand["group"],
                "Target Athletes": cand["athletes"],
                "Academy Warning": academy_warning,
                "Academy Mix": academy_mix,
                "Weight Difference": round(weight_diff, 1) if weight_diff != 999 else "",
                "Age Difference": age_diff if age_diff != 999 else "",
                "Skill Difference": skill_diff if skill_diff != 999 else "",
                "Why": why,
                "Current Entry": single.get("entry_clean", ""),
                "Suggested Entry": cand.get("entry", ""),
                "Current Skill/Belt": single.get("skill_clean", ""),
                "Suggested Skill/Belt": cand.get("skill", ""),
                "Current Age": single.get("age_clean", ""),
                "Suggested Age": cand.get("age", ""),
                "Current Weight": single.get("weight_clean", ""),
                "Suggested Weight": cand.get("weight", ""),
            })

        scored = sorted(scored, key=lambda x: x["Match Score"], reverse=True)[:top_n]

        for rank, row in enumerate(scored, start=1):
            row["Rank"] = rank
            rows.append(row)

    recs = pd.DataFrame(rows)
    if recs.empty:
        return recs

    first_cols = [
        "Rank", "Athlete", "Quality", "Match Score", "Current Division", "Suggested Division",
        "Target Athletes", "Academy Warning", "Academy Mix", "Weight Difference",
        "Age Difference", "Skill Difference", "Why",
    ]
    rest = [c for c in recs.columns if c not in first_cols]
    return recs[first_cols + rest]


def style_quality_rows(df):
    def row_style(row):
        warning = str(row.get("Academy Warning", "")).lower()
        quality = str(row.get("Quality", "")).lower()

        if "all same academy" in warning:
            color = "#fecaca"
        elif "excellent" in quality:
            color = "#bbf7d0"
        elif "good" in quality:
            color = "#dcfce7"
        elif "review" in quality:
            color = "#fef08a"
        elif "last" in quality:
            color = "#fecaca"
        elif "no strong" in quality:
            color = "#e5e7eb"
        else:
            color = "#f3f4f6"

        return [f"background-color: {color}; color: #111827;" for _ in row]

    return df.style.apply(row_style, axis=1)


def to_excel_bytes(recommendations, singles, summary):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        recommendations.to_excel(writer, index=False, sheet_name="Recommendations")
        singles.to_excel(writer, index=False, sheet_name="Singles")
        summary.to_excel(writer, index=False, sheet_name="All Groups")
    return output.getvalue()


def metric_card(label, value, help_text):
    st.markdown(
        f'''
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


st.markdown(
    '''
    <div class="ez-hero">
        <div class="ez-logo-row">
            <div class="ez-logo">EZ</div>
            <div>
                <div class="ez-title">EZ Brackets</div>
                <div class="ez-subtitle">
                    Smart tournament division matching for Smoothcomp CSVs. Find singles, rank merge options,
                    flag academy-only brackets, and export director-ready reports.
                </div>
                <span class="ez-badge">Single-athlete detection</span>
                <span class="ez-badge">Academy warnings</span>
                <span class="ez-badge">Director reports</span>
            </div>
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)


uploaded = st.file_uploader("Upload Smoothcomp registrations CSV", type=["csv"])

if uploaded:
    raw_df = pd.read_csv(uploaded)
    df = normalize_dataframe(raw_df)

    with st.sidebar:
        st.header("Settings")
        only_approved = st.checkbox("Only analyze approved athletes", value=True)
        min_target_size = st.selectbox(
            "Suggest moving singles into groups with at least:",
            [1, 2, 3],
            index=0,
        )
        top_n = st.slider("Top suggestions per single", min_value=1, max_value=5, value=3)
        allow_entry_crossover = st.checkbox("Show Gi/No-Gi crossover emergency options", value=False)

    working_df = df.copy()
    if only_approved and "approved_clean" in df.columns:
        approved_df = df[df["approved_clean"].astype(str).str.lower().eq("approved")]
        if not approved_df.empty:
            working_df = approved_df

    summary = group_summary(working_df)
    singles = summary[summary["athletes"] == 1].copy()

    recommendations = make_recommendations(
        df,
        only_approved=only_approved,
        min_target_size=min_target_size,
        top_n=top_n,
        allow_entry_crossover=allow_entry_crossover,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Registrations", len(working_df), "Approved athletes currently analyzed")
    with c2:
        metric_card("Groups", len(summary), "Total active divisions/groups found")
    with c3:
        metric_card("Singles", len(singles), "Single-athlete divisions needing review")

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Single-Athlete Divisions")
    if not singles.empty:
        st.dataframe(
            singles[["group", "athletes", "entry", "skill", "age", "weight", "names", "academies"]],
            use_container_width=True,
        )
    else:
        st.markdown('<div class="success-card">No single-athlete groups found.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Recommended Merge Options")
    st.caption("Scores are suggestions only. Use coach/parent approval and safety judgment before moving athletes.")

    if recommendations.empty:
        st.warning("No recommendations generated.")
    else:
        academy_warning_count = recommendations["Academy Warning"].astype(str).str.contains("same academy", case=False, na=False).sum()
        if academy_warning_count:
            st.markdown(
                f'<div class="warning-card">⚠️ {academy_warning_count} recommendation(s) include an academy-only bracket warning.</div>',
                unsafe_allow_html=True,
            )

        athlete_options = ["All Athletes"] + sorted(recommendations["Athlete"].dropna().unique().tolist())
        selected_athlete = st.selectbox("Filter by Athlete", athlete_options)

        filtered_recommendations = recommendations.copy()
        if selected_athlete != "All Athletes":
            filtered_recommendations = filtered_recommendations[
                filtered_recommendations["Athlete"] == selected_athlete
            ]

        best_matches = filtered_recommendations[filtered_recommendations["Rank"] == 1].copy()

        tab1, tab2, tab3 = st.tabs(["Best Match Only", "All Suggestions", "Export"])

        with tab1:
            st.dataframe(style_quality_rows(best_matches), use_container_width=True)

        with tab2:
            st.dataframe(style_quality_rows(filtered_recommendations), use_container_width=True)

        with tab3:
            st.markdown("### Director Report")
            st.write("Download a report your staff can use to make bracket updates inside Smoothcomp.")
            rank1_all = recommendations[recommendations["Rank"] == 1].copy()

            st.download_button(
                "Download Rank #1 Excel Report",
                data=to_excel_bytes(rank1_all, singles, summary),
                file_name="ez_brackets_rank1_recommendations.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            st.download_button(
                "Download Full Excel Report",
                data=to_excel_bytes(recommendations, singles, summary),
                file_name="ez_brackets_full_recommendations.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.markdown(
            '<div class="small-muted">Color Key: 🟢 Excellent / Good · 🟡 Review · 🔴 Last Resort / Academy Warning · ⚪ No Strong Match</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown(
        '<div class="section-card">Upload your Smoothcomp CSV to begin analyzing divisions.</div>',
        unsafe_allow_html=True,
    )
