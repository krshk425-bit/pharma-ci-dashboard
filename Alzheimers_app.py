import streamlit as st

st.set_page_config(page_title="Neurology Pharma GPT", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to:", 
    ["Clinical Trials", "Regulatory", "Manufacturing", "Commercial"])

# Clinical Trials Tab
if section == "Clinical Trials":
    st.header("Clinical Trials")
    st.write("Summarize neurology trial protocols, endpoints, and recruitment strategies.")
    query = st.text_input("Ask about a trial (e.g., Lecanemab Phase 3):")
    if query:
        st.success(f"GPT response for: {query}")

# Regulatory Tab
elif section == "Regulatory":
    st.header("Regulatory")
    st.write("Interpret FDA/EMA guidelines, draft submissions, prepare Q&A.")
    query = st.text_input("Ask about regulatory guidance:")
    if query:
        st.success(f"GPT response for: {query}")

# Manufacturing Tab
elif section == "Manufacturing":
    st.header("Manufacturing & Quality")
    st.write("Generate GMP checklists, summarize deviations, support validation.")
    query = st.text_input("Ask about SOPs or GMP compliance:")
    if query:
        st.success(f"GPT response for: {query}")

# Commercial Tab
elif section == "Commercial":
    st.header("Commercial Rollout")
    st.write("Simulate payer negotiations, launch planning, stakeholder communication.")
    query = st.text_input("Ask about market access or launch strategy:")
    if query:
        st.success(f"GPT response for: {query}")
