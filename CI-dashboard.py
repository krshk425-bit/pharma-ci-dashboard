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

with news_tab:
    st.header("Latest Alzheimer’s News")
    st.write("News source selector and headlines here")

with congress_tab:
    st.header("Upcoming Congresses (2026)")
    st.write("Location and date filters with event list")

