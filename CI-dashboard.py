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
from datetime import datetime, date

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

# ---------------------------------------------------
# FETCH ALL ALZHEIMER STUDIES (PAGINATED)
# ---------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_all_alzheimer_trials():
    studies = []
    next_page = None

    while True:
        params = {
            "query.cond": "Alzheimer Disease",
            "pageSize": 100,
        }
        if next_page:
            params["pageToken"] = next_page

        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        studies.extend(data.get("studies", []))
        next_page = data.get("nextPageToken")

        if not next_page:
            break

    return studies


# ---------------------------------------------------
# PARSE CORE FIELDS
# ---------------------------------------------------
def parse_study(study):
    ps = study.get("protocolSection", {})

    id_mod = ps.get("identificationModule", {})
    status_mod = ps.get("statusModule", {})
    sponsor_mod = ps.get("sponsorCollaboratorsModule", {})
    design_mod = ps.get("designModule", {})
    enroll_mod = ps.get("enrollmentModule", {})
    outcomes_mod = ps.get("outcomesModule", {})

    # Dates
    try:
        post_date = datetime.strptime(
            status_mod.get("studyFirstPostDate", ""), "%Y-%m-%d"
        ).date()
    except:
        post_date = None

    return {
        "NCT": id_mod.get("nctId"),
        "Title": id_mod.get("officialTitle"),
        "Phase": ", ".join(design_mod.get("phases", [])),
        "Status": status_mod.get("overallStatus"),
        "Sponsor": sponsor_mod.get("leadSponsor", {}).get("name"),
        "SponsorType": sponsor_mod.get("leadSponsor", {}).get("class"),
        "Enrollment": enroll_mod.get("count"),
        "PostDate": post_date,
        "Outcomes": outcomes_mod,
    }


# ---------------------------------------------------
# PIPELINE TAB
# ---------------------------------------------------
def pipeline_tab():
    st.header("🧠 Alzheimer’s Disease Clinical Trial Pipeline")

    col1, col2, col3 = st.columns(3)

    with col1:
        phase = st.selectbox(
            "Phase",
            ["All", "EARLY_PHASE1", "PHASE1", "PHASE1_PHASE2",
             "PHASE2", "PHASE2_PHASE3", "PHASE3"]
        )

    with col2:
        status = st.selectbox(
            "Recruitment Status",
            ["All", "NOT_YET_RECRUITING", "RECRUITING", "COMPLETED",
             "WITHDRAWN", "TERMINATED", "SUSPENDED", "UNKNOWN"]
        )

    with col3:
        sponsor_type = st.selectbox(
            "Sponsor Type",
            ["All", "INDUSTRY", "NIH", "OTHER"]
        )

    from_date = st.date_input("From Date", date(2020, 1, 1))
    to_date = st.date_input("To Date", date(2025, 12, 31))

    st.divider()

    # ----------------------------
    # LOAD DATA
    # ----------------------------
    raw_trials = fetch_all_alzheimer_trials()
    parsed_trials = [parse_study(s) for s in raw_trials]

    # ----------------------------
    # APPLY FILTERS
    # ----------------------------
    filtered = []
    for t in parsed_trials:
        if not t["PostDate"]:
            continue

        if phase != "All" and phase not in (t["Phase"] or ""):
            continue
        if status != "All" and status != t["Status"]:
            continue
        if sponsor_type != "All" and sponsor_type != t["SponsorType"]:
            continue
        if not (from_date <= t["PostDate"] <= to_date):
            continue

        filtered.append(t)

    # ----------------------------
    # OUTPUT (Pg2 STYLE)
    # ----------------------------
    st.subheader(f"Filtered Trials ({len(filtered)})")

    if not filtered:
        st.warning("No trials found for selected filters.")
        return

    for t in filtered:
        st.markdown(f"### {t['Title']}")
        st.markdown(
            f"""
**NCT ID:** {t['NCT']}  
**Phase:** {t['Phase']}  
**Status:** {t['Status']}  
**Enrollment:** {t['Enrollment']}  
**Sponsor:** {t['Sponsor']}  
**First Posted:** {t['PostDate']}  
"""
        )

        # Outcomes
        outcomes = t["Outcomes"]
        if outcomes:
            st.markdown("**Outcomes**")
            for o in outcomes.get("primaryOutcomes", []):
                st.markdown(f"- **Primary:** {o.get('measure')} ({o.get('timeFrame')})")
            for o in outcomes.get("secondaryOutcomes", []):
                st.markdown(f"- **Secondary:** {o.get('measure')} ({o.get('timeFrame')})")

        st.markdown(
            f"[View on ClinicalTrials.gov]"
            f"(https://clinicaltrials.gov/study/{t['NCT']})"
        )
        st.divider()


# ---------------------------------------------------
# RUN
# ---------------------------------------------------
pipeline_tab()





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
    date_range = st.date_input("Select date range", [datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)])

    congress_data = [
        ["AAIC 2026", "July 12–15, 2026", "London, UK", "https://aaic.alz.org/abstracts/overview.asp"],
        ["ADI 2026", "April 14–16, 2026", "Lyon, France", "https://www.alzint.org/news-events/events/the-37th-global-conference-of-alzheimers-disease-international/"],
        ["AD/PD 2026", "March 5–9, 2026", "Copenhagen, Denmark", "https://adpd.kenes.com/"],
        ["ISAD 2026", "Sept 7–8, 2026", "Paris, France", "https://alzheimers-dementia.org/"]
    ]
    df = pd.DataFrame(congress_data, columns=["Congress Name", "Date", "Location", "Link"])
    st.dataframe(df, use_container_width=True)
