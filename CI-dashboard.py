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
import pandas as pd
import datetime

with pipeline_tab:
    st.header("Alzheimer's Disease Pipeline")

    # ---------------- INPUT FILTERS ----------------
    col1, col2, col3 = st.columns(3)
    with col1:
        phase = st.selectbox("Phase", ["All", "Phase 1", "Phase 2", "Phase 3"])
    with col2:
        status = st.selectbox("Recruitment Status", ["All", "Recruiting", "Completed", "Not yet recruiting", "Terminated"])
    with col3:
        sponsor_type = st.selectbox("Sponsor Type", ["All", "University/Hospital", "Industry"])

    col4, col5 = st.columns(2)
    with col4:
        from_date = st.date_input("From Date", value=datetime.date(2020, 1, 1))
    with col5:
        to_date = st.date_input("To Date", value=datetime.date.today())

    # ---------------- FETCH TRIAL LIST ----------------
    base_url = "https://clinicaltrials.gov/api/v2/studies?query.term=Alzheimer%20Disease&pageSize=50"
    try:
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        trials = response.json()["studies"]
    except Exception as e:
        st.error(f"Failed to fetch trial list: {e}")
        st.stop()

    st.subheader("Filtered Alzheimer’s Trials")

    for trial in trials:
        try:
            title = trial.get("briefTitle", "N/A")
            nct_id = trial.get("nctId", "N/A")
            phase_val = trial.get("phase", "N/A")
            status_val = trial.get("status", "N/A")
            sponsor = trial.get("sponsor", {}).get("name", "N/A")
            start_date = trial.get("startDate", "N/A")
            pcd = trial.get("primaryCompletionDate", "N/A")
            scd = trial.get("completionDate", "N/A")
            link = f"https://clinicaltrials.gov/study/{nct_id}"

            # Convert start date
            try:
                post_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            except:
                post_date = None

            # Apply filters
            if (phase == "All" or phase_val == phase) and \
               (status == "All" or status_val == status) and \
               (post_date and from_date <= post_date <= to_date):

                # ---------------- FETCH OUTCOMES ----------------
                detail_url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
                try:
                    detail = requests.get(detail_url, timeout=10).json()
                    outcomes = []
                    if "outcomes" in detail:
                        if "primary" in detail["outcomes"]:
                            for o in detail["outcomes"]["primary"]:
                                outcomes.append(["Primary", o.get("measure", ""), o.get("timeFrame", "")])
                        if "secondary" in detail["outcomes"]:
                            for o in detail["outcomes"]["secondary"]:
                                outcomes.append(["Secondary", o.get("measure", ""), o.get("timeFrame", "")])
                except:
                    outcomes = []

                # ---------------- DISPLAY TRIAL CARD ----------------
                with st.expander(f"{title} ({phase_val}, {status_val})"):
                    st.markdown(f"**Trial Link:** [{nct_id}]({link})")
                    st.write(f"**Start Date (SSD):** {start_date}")
                    st.write(f"**Primary Completion Date (PCD):** {pcd}")
                    st.write(f"**Study Completion Date (SCD):** {scd}")
                    st.write(f"**Sponsor:** {sponsor}")
                    if outcomes:
                        df = pd.DataFrame(outcomes, columns=["Outcome Type", "Measure", "Time Frame"])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write("No outcomes reported.")
        except:
            continue

    # ---------------- RECENT TRIALS ----------------
    st.subheader("Trials Posted in Past 14 Days")
    cutoff = datetime.date.today() - datetime.timedelta(days=14)
    for trial in trials:
        try:
            title = trial.get("briefTitle", "N/A")
            nct_id = trial.get("nctId", "N/A")
            start_date = trial.get("startDate", None)
            post_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            if post_date >= cutoff:
                link = f"https://clinicaltrials.gov/study/{nct_id}"
                st.markdown(f"- [{title}]({link}) (Posted: {post_date.strftime('%d-%b-%Y')})")
        except:
            continue




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
