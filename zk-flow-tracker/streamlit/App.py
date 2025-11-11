import os
import time
import requests
import streamlit as st

API_BASE = os.getenv("ZKFLOW_API_BASE", "http://localhost:8000/api")

st.set_page_config(page_title="ZK Flow Tracker", layout="wide")
st.title("ZK Flow Tracker — Internal Dashboard (MVP)")

with st.sidebar:
    st.header("Filters")
    min_usd = st.number_input("Min USD value", min_value=0, value=0, step=1000000)
    limit = st.slider("Rows", min_value=10, max_value=500, value=100, step=10)
    refresh = st.button("Refresh")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Recent Flows")
    try:
        r = requests.get(f"{API_BASE}/flows", params={"limit": limit}, timeout=8)
        flows = r.json()
        if isinstance(flows, list) and min_usd > 0:
            flows = [f for f in flows if float(f.get("usd_value", 0)) >= min_usd]
        st.dataframe(flows, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load flows: {e}")

with col2:
    st.subheader("Recent Transfers")
    try:
        r = requests.get(f"{API_BASE}/events/transfers", params={"limit": limit}, timeout=8)
        txs = r.json()
        if isinstance(txs, list) and min_usd > 0:
            txs = [t for t in txs if float(t.get("amount_usd", 0)) >= min_usd]
        st.dataframe(txs, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load transfers: {e}")

if refresh:
    st.experimental_rerun()
