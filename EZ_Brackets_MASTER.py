import re
from io import BytesIO

import pandas as pd
import streamlit as st

st.set_page_config(page_title="EZ Brackets", layout="wide")
st.title("EZ Brackets")
st.caption("Smart division matching for tournament directors. Includes athlete filter, color coding, export, and academy warnings.")

SKILL_ORDER = {
    "White": 0, "Grey": 1, "Gray": 1, "Yellow": 2, "Orange": 3, "Green": 4,
    "Novice": 10, "Beginner": 11, "Intermediate": 12, "Advanced": 13,
    "Blue": 20, "Purple": 21, "Brown": 22, "Black": 23,
}

AGE_ORDER_HINTS = [
    ("Mighty Mite", 1), ("Pee Wee", 2), ("Kindergarten", 3), ("Youth", 4),
    ("Pre Teen", 5), ("Junior Teen", 6), ("Teen", 7), ("Juvenile", 8),
    ("Adult", 20), ("Master 1", 21), ("Master 2", 22), ("Master 3", 23),
    ("Master 4", 24), ("Master 5", 25),
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
        rows.append({
            "group": group,
            "athletes": len(g),
            "entry": sample.get("entry_clean", ""),
            "skill": sample.get("skill_clean", ""),
            "age": sample.get("age_clean", ""),
            "weight": sample.get("weight_clean", ""),
            "names": ", ".join(g["athlete_name"].astype(str).tolist()),
            "academies": ", ".join(sorted(set(g["academy_clean"].dropna().astype(str).tolist()))),
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

    if academy_count <= 1 and target_size >= 1:
        score -= 35
        academy_warning = "⚠️ All same academy"
        reasons.append("would create/keep all-same-academy bracket")
    else:
        academy_warning = ""

    if target_size >= 3:
        score += 5
        reasons.append("target has 3+ athletes")
    elif target_size == 2:
        score += 2
        reasons.append("target has 2 athletes")

    score = max(0, min(100, int(round(score))))
    return score, "; ".join(reasons), weight_diff, age_diff, skill_diff, academy_warning, academy_mix


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
                "Athlete": single["athlete_name"],
                "Quality": quality_label(score),
                "Match Score": score,
                "Current Division": group,
                "Suggested Division": cand["group"],
                "Target Athletes": cand["athletes"],
                "Age Difference": age_diff if age_diff != 999 else "",
                "Weight Difference": round(weight_diff, 1) if weight_diff != 999 else "",
                "Skill Difference": skill_diff if skill_diff != 999 else "",
                "Academy Warning": academy_warning,
                "Academy Mix": academy_mix,
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
        for rank, row in enumerate(sorted(scored, key=lambda x: x["Match Score"], reverse=True)[:top_n], start=1):
            row["Rank"] = rank
            rows.append(row)

    recs = pd.DataFrame(rows)
    if recs.empty:
        return recs
    first_cols = ["Rank", "Athlete", "Quality", "Match Score", "Current Division", "Suggested Division", "Target Athletes", "Age Difference", "Weight Difference", "Skill Difference", "Academy Warning", "Academy Mix", "Why"]
    rest = [c for c in recs.columns if c not in first_cols]
    return recs[first_cols + rest]


def style_quality_rows(df):
    def row_style(row):
        quality = str(row.get("Quality", "")).lower()
        warning = str(row.get("Academy Warning", "")).lower()
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
        return [f"background-color: {color}" for _ in row]
    return df.style.apply(row_style, axis=1)


def to_excel_bytes(recommendations, singles, summary):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        recommendations.to_excel(writer, index=False, sheet_name="Recommendations")
        singles.to_excel(writer, index=False, sheet_name="Singles")
        summary.to_excel(writer, index=False, sheet_name="All Groups")
    return output.getvalue()


uploaded = st.file_uploader("Upload Smoothcomp registrations CSV", type=["csv"])

if uploaded:
    raw_df = pd.read_csv(uploaded)
    df = normalize_dataframe(raw_df)

    with st.sidebar:
        st.header("Settings")
        only_approved = st.checkbox("Only analyze approved athletes", value=True)
        min_target_size = st.selectbox("Suggest moving singles into groups with at least:", [1, 2, 3], index=0)
        top_n = st.slider("Top suggestions per single", min_value=1, max_value=5, value=3)
        allow_entry_crossover = st.checkbox("Show Gi/No-Gi crossover emergency options", value=False)

    working_df = df.copy()
    if only_approved and "approved_clean" in df.columns:
        approved_df = df[df["approved_clean"].astype(str).str.lower().eq("approved")]
        if not approved_df.empty:
            working_df = approved_df

    summary = group_summary(working_df)
    singles = summary[summary["athletes"] == 1].copy()
    recommendations = make_recommendations(df, only_approved, min_target_size, top_n, allow_entry_crossover)

    c1, c2, c3 = st.columns(3)
    c1.metric("Registrations", len(working_df))
    c2.metric("Groups", len(summary))
    c3.metric("Single-athlete groups", len(singles))

    st.subheader("Single-Athlete Divisions")
    if not singles.empty:
        st.dataframe(singles[["group", "athletes", "entry", "skill", "age", "weight", "names", "academies"]], use_container_width=True)
    else:
        st.success("No single-athlete groups found.")

    st.subheader("Recommended Merge Options")
    st.caption("Scores are suggestions only. Use coach/parent approval and safety judgment before moving athletes.")

    if recommendations.empty:
        st.warning("No recommendations generated.")
    else:
        athlete_options = ["All Athletes"] + sorted(recommendations["Athlete"].dropna().unique().tolist())
        selected_athlete = st.selectbox("Filter by Athlete", athlete_options)
        filtered_recommendations = recommendations.copy()
        if selected_athlete != "All Athletes":
            filtered_recommendations = filtered_recommendations[filtered_recommendations["Athlete"] == selected_athlete]
        best_matches = filtered_recommendations[filtered_recommendations["Rank"] == 1].copy()

        tab1, tab2, tab3 = st.tabs(["Best Match Only", "All Suggestions", "Export"])
        with tab1:
            st.dataframe(style_quality_rows(best_matches), use_container_width=True)
        with tab2:
            st.dataframe(style_quality_rows(filtered_recommendations), use_container_width=True)
        with tab3:
            st.write("Download reports you can review while updating brackets.")
            rank1_all = recommendations[recommendations["Rank"] == 1].copy()
            st.download_button("Download Rank #1 Excel Report", data=to_excel_bytes(rank1_all, singles, summary), file_name="ez_brackets_rank1_recommendations.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.download_button("Download Full Excel Report", data=to_excel_bytes(recommendations, singles, summary), file_name="ez_brackets_full_recommendations.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown("**Color Key:** 🟢 Excellent / Good · 🟡 Review · 🔴 Last Resort / Academy Warning · ⚪ No Strong Match")
else:
    st.info("Upload your Smoothcomp CSV to begin.")
