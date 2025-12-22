import streamlit as st
import datetime
import pandas as pd
import feedparser

st.set_page_config(page_title="Pharma CI Dashboard", layout="wide")

st.title("Pharma CI Dashboard")
st.write("Welcome! This dashboard tracks pipeline, congress, and competitor insights.")

# ---------------- Tabs ----------------
pipeline_tab, news_tab, congress_tab = st.tabs(["Pipeline", "News", "Congress Planner"])

# ---------------- Pipeline Tab ----------------
import streamlit as st
import requests
from datetime import datetime, timedelta

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

# -------------------------------
# Phase label mapping
# -------------------------------
PHASE_LABELS = {
    "EARLY_PHASE1": "Early Phase 1",
    "PHASE_1": "Phase 1",
    "PHASE_1_2": "Phase 1/2",
    "PHASE_2": "Phase 2",
    "PHASE_2_3": "Phase 2/3",
    "PHASE_3": "Phase 3",
}
LABEL_TO_PHASE = {v: k for k, v in PHASE_LABELS.items()}

# -------------------------------
# Time window: past 3 months
# -------------------------------
TODAY = datetime.utcnow().date()
PAST_3_MONTHS = TODAY - timedelta(days=90)

# -------------------------------
# Fetch Alzheimer trials
# -------------------------------
@st.cache_data(ttl=3600)  # refresh hourly
def fetch_trials():
    trials = []
    token = None

    while True:
        params = {
            "query.cond": "Alzheimer Disease",
            "pageSize": 100
        }
        if token:
            params["pageToken"] = token

        r = requests.get(BASE_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()

        trials.extend(data.get("studies", []))
        token = data.get("nextPageToken")
        if not token:
            break

    return trials

# -------------------------------
# Parse trial safely
# -------------------------------
def parse_trial(study):
    ps = study.get("protocolSection", {})

    idm = ps.get("identificationModule", {})
    sm = ps.get("statusModule", {})
    dm = ps.get("designModule", {})
    sp = ps.get("sponsorCollaboratorsModule", {})
    em = ps.get("enrollmentModule", {})
    lm = ps.get("contactsLocationsModule", {})

    # First posted date
    post_date = None
    try:
        post_date = datetime.strptime(
            sm.get("studyFirstPostDate", ""),
            "%Y-%m-%d"
        ).date()
    except:
        pass

    # Countries
    countries = sorted({
        loc.get("country")
        for loc in lm.get("locations", [])
        if loc.get("country")
    })

    return {
        "NCT": idm.get("nctId"),
        "Title": idm.get("officialTitle"),
        "Phases": dm.get("phases") or [],
        "Status": (sm.get("overallStatus") or "").strip(),
        "Sponsor": sp.get("leadSponsor", {}).get("name"),
        "SponsorType": sp.get("leadSponsor", {}).get("class"),
        "Enrollment": em.get("count"),
        "PostDate": post_date,
        "Countries": countries,
    }

# -------------------------------
# PIPELINE UI
# -------------------------------
st.header("🧠 Alzheimer’s Disease Clinical Trial Pipeline")

st.caption("Showing trials first posted in the **past 3 months**")

col1, col2, col3, col4 = st.columns(4)

with col1:
    phase_label = st.selectbox("Phase", ["All"] + list(PHASE_LABELS.values()))
    phase_filter = LABEL_TO_PHASE.get(phase_label)

with col2:
    status = st.selectbox(
        "Recruitment Status",
        ["All", "Not yet recruiting", "Recruiting", "Completed",
         "Withdrawn", "Terminated", "Suspended", "Unknown"]
    )
    status_norm = status.lower()

with col3:
    sponsor_type = st.selectbox("Sponsor Type", ["All", "INDUSTRY", "NIH", "OTHER"])

with col4:
    country_filter = st.selectbox("Country", ["All"])

st.divider()

# -------------------------------
# Load & filter data
# -------------------------------
parsed_trials = [parse_trial(t) for t in fetch_trials()]

# Populate country dropdown dynamically
all_countries = sorted({c for t in parsed_trials for c in t["Countries"]})
country_filter = st.selectbox("Country", ["All"] + all_countries)

filtered = []
for t in parsed_trials:

    # Time filter: past 3 months
    if not t["PostDate"] or t["PostDate"] < PAST_3_MONTHS:
        continue

    # Phase filter
    if phase_label != "All" and t["Phases"]:
        if phase_filter not in t["Phases"]:
            continue

    # Status filter
    if status != "All" and t["Status"].lower() != status_norm:
        continue

    # Sponsor type
    if sponsor_type != "All" and t["SponsorType"] != sponsor_type:
        continue

    # Country filter
    if country_filter != "All" and country_filter not in t["Countries"]:
        continue

    filtered.append(t)

# -------------------------------
# Output
# -------------------------------
st.subheader(f"Filtered Trials ({len(filtered)})")

if not filtered:
    st.info("No Alzheimer’s trials were first posted in the past 3 months.")
else:
    for t in filtered:
        phase_display = (
            ", ".join(PHASE_LABELS.get(p, p) for p in t["Phases"])
            if t["Phases"] else "Not specified"
        )

        st.markdown(f"### {t['Title']}")
        st.markdown(
            f"""
**NCT ID:** {t['NCT']}  
**Phase:** {phase_display}  
**Status:** {t['Status']}  
**Sponsor:** {t['Sponsor']}  
**Enrollment:** {t['Enrollment']}  
**First Posted:** {t['PostDate']}  
**Countries:** {", ".join(t["Countries"]) if t["Countries"] else "Not specified"}
"""
        )
        st.markdown(
            f"[View on ClinicalTrials.gov]"
            f"(https://clinicaltrials.gov/study/{t['NCT']})"
        )
        st.divider()





# ---------------- News Tab ----------------
with news_tab:
    st.header("Latest Alzheimer’s News")
    st.write("Curated industry sources")

    news_sources = {
        "Alzheimer's Association": "https://www.alz.org/news",
        "Alzheimer's Disease International": "https://www.alzint.org/news-events/news/?filter_news_type=420&btn_filter_news=Search",
        "Global Alzheimer’s Platform": "https://globalalzplatform.org/category/in-the-news/",
        "Dementias Platform UK": "https://www.dementiasplatform.uk/news-and-media/latest-news"
    }

    for name, url in news_sources.items():
        st.markdown(f"- [{name}]({url})")

# ---------------- Congress Planner Tab ----------------
with congress_tab:
    st.header("Upcoming Congresses (2026)")
    st.write("Location and date filters with event list")

    location = st.selectbox("Select location", ["Global", "Europe", "US", "Asia"])
    

    congress_data = [
        ["AAIC 2026", "July 12–15, 2026", "London, UK", "https://aaic.alz.org/abstracts/overview.asp"],
        ["ADI 2026", "April 14–16, 2026", "Lyon, France", "https://www.alzint.org/news-events/events/the-37th-global-conference-of-alzheimers-disease-international/"],
        ["AD/PD 2026", "March 5–9, 2026", "Copenhagen, Denmark", "https://adpd.kenes.com/"],
        ["ISAD 2026", "Sept 7–8, 2026", "Paris, France", "https://alzheimers-dementia.org/"]
    ]
    df = pd.DataFrame(congress_data, columns=["Congress Name", "Date", "Location", "Link"])
    st.dataframe(df, use_container_width=True)
