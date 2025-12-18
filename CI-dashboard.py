import streamlit as st

st.set_page_config(page_title="Pharma CI Dashboard", layout="wide")

st.title("Pharma CI Dashboard")
st.write("Welcome! This dashboard tracks pipeline, congress, and competitor insights.")
import streamlit as st

st.set_page_config(page_title="Pharma CI Dashboard", layout="wide")

st.title("Pharma CI Dashboard")
st.write("Welcome! This dashboard tracks pipeline, congress, and competitor insights.")

# Tabs
pipeline_tab, news_tab, congress_tab = st.tabs(["Pipeline", "News", "Congress Planner"])

with pipeline_tab:
    st.header("Alzheimer's Disease Pipeline")
    st.write("Trial phase filter and pipeline summary here")

    import feedparser
    rss_url = "https://clinicaltrials.gov/api/rss?cond=Alzheimer+Disease&dateField=StudyFirstPostDate"
    feed = feedparser.parse(rss_url)

    st.subheader("Latest Alzheimer's Trials from ClinicalTrials.gov")
    for entry in feed.entries[:5]:  # Show top 5
        st.markdown(f"- [{entry.title}]({entry.link})")

with news_tab:
    st.header("Latest Alzheimer’s News")
    st.write("News source selector and headlines here")
    st.subheader("Alzheimer’s News Sources")
news_sources = {
    "Alzheimer's Association": "https://www.alz.org/news",
    "Alzheimer's Disease International": "https://www.alzint.org/news-events/news/?filter_news_type=420&btn_filter_news=Search",
    "Global Alzheimer’s Platform": "https://globalalzplatform.org/category/in-the-news/",
    "Dementias Platform UK": "https://www.dementiasplatform.uk/news-and-media/latest-news"
}

for name, url in news_sources.items():
    st.markdown(f"- [{name}]({url})")

    

with congress_tab:
    st.header("Upcoming Congresses (2026)")
    st.write("Location and date filters with event list")
    import pandas as pd

congress_data = [
    ["AAIC 2026", "July 12–15, 2026", "London, UK", "https://aaic.alz.org/abstracts/overview.asp"],
    ["ADI 2026", "April 14–16, 2026", "Lyon, France", "https://www.alzint.org/news-events/events/the-37th-global-conference-of-alzheimers-disease-international/"],
    ["AD/PD 2026", "March 5–9, 2026", "Copenhagen, Denmark", "https://adpd.kenes.com/"],
    ["ISAD 2026", "Sept 7–8, 2026", "Paris, France", "https://alzheimers-dementia.org/"]
]

df = pd.DataFrame(congress_data, columns=["Congress Name", "Date", "Location", "Link"])
st.subheader("Upcoming Alzheimer’s Congresses")
st.dataframe(df)


