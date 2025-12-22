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
from datetime import date, datetime

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

# --------------------------------------------------
# FETCH ALL ALZHEIMER TRIALS (v2 API, PAGINATED)
# --------------------------------------------------
@st.cache_data(ttl=86400)
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


# --------------------------------------------------
# SAFE PARSER (NO CRASHES)
# --------------------------------------------------
def parse_trial(study):
    ps = study.get("protocolSection", {})

    idm = ps.get("identificationModule", {})
    sm = ps.get("statusModule", {})
    dm = ps.get("designModule", {})
    sp = ps.get("sponsorCollaboratorsModule", {})
    em = ps.get("enrollmentModule", {})
    om = ps.get("outcomesModule", {})

    # Date parsing
    post_date = None
    try:
        post_date = datetime.strptime(
            sm.get("studyFirstPostDate", ""),
            "%Y-%m-%d"
        ).date()
    except:
        pass

    return {
        "NCT": idm.get("nctId"),
        "Title": idm.get("officialTitle"),
        "Phases": dm.get("phases") or [],   # ALWAYS LIST
        "Status": sm.get("overallStatus"),
        "Sponsor": sp.get("leadSponsor", {}).get("name"),
        "SponsorType": sp.get("leadSponsor", {}).get("class"),
        "Enrollment": em.get("count"),
        "PostDate": post_date,
        "Outcomes": om,
    }


# --------------------------------------------------
# PIPELINE TAB UI
# --------------------------------------------------
def pipeline_tab():
    st.header("🧠 Alzheimer’s Disease Clinical Trial Pipeline")

    col1, col2, col3 = st.columns(3)

    with col1:
        phase = st.selectbox(
            "Phase",
            ["All", "PHASE_3", "PHASE_2", "PHASE_2_3", "PHASE_1", "EARLY_PHASE1"]
        )

    with col2:
        status = st.selectbox(
            "Recruitment Status",
            ["All", "Not yet recruiting", "Recruiting", "Completed",
             "Withdrawn", "Terminated", "Suspended"]
        )

    with col3:
        sponsor_type = st.selectbox(
            "Sponsor Type",
            ["All", "INDUSTRY", "NIH", "OTHER"]
        )

    from_date = st.date_input("From Date", date(2020, 1, 1))
    to_date = st.date_input("To Date", date(2025, 12, 31))

    st.divider()

    # --------------------------------------------------
    # LOAD & PARSE
    # --------------------------------------------------
    parsed = [parse_trial(t) for t in fetch_trials()]

    # --------------------------------------------------
    # FILTER LOGIC (FIXED)
    # --------------------------------------------------
    filtered = []
    for t in parsed:
        if not t["PostDate"]:
            continue

        # Phase filter (lenient, correct)
        if phase != "All" and phase not in t["Phases"]:
            continue

        if status != "All" and t["Status"] != status:
            continue

        if sponsor_type != "All" and t["SponsorType"] != sponsor_type:
            continue

        if not (from_date <= t["PostDate"] <= to_date):
            continue

        filtered.append(t)

    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------
    st.subheader(f"Filtered Trials ({len(filtered)})")

    if not filtered:
        st.warning("No trials found for selected filters.")
        return

    for t in filtered:
        st.markdown(f"### {t['Title']}")
        st.markdown(
            f"""
**NCT ID:** {t['NCT']}  
**Phase:** {', '.join(t['Phases']) if t['Phases'] else 'Not specified'}  
**Status:** {t['Status']}  
**Enrollment:** {t['Enrollment']}  
**Sponsor:** {t['Sponsor']}  
**First Posted:** {t['PostDate']}  
"""
        )

        if t["Outcomes"]:
            for o in t["Outcomes"].get("primaryOutcomes", []):
                st.markdown(f"- **Primary:** {o.get('measure')} ({o.get('timeFrame')})")
            for o in t["Outcomes"].get("secondaryOutcomes", []):
                st.markdown(f"- **Secondary:** {o.get('measure')} ({o.get('timeFrame')})")

        st.markdown(
            f"[View on ClinicalTrials.gov]"
            f"(https://clinicaltrials.gov/study/{t['NCT']})"
        )
        st.divider()


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
