import streamlit as st
from api.client import APIClient
from api.endpoints import HEALTH_ENDPOINT

def show_backend_status():
    response = APIClient.get(HEALTH_ENDPOINT)
    st.subheader("Backend Status")
    if isinstance(response, dict) and "application" in response:
        st.success("✅ Backend Connected")
        st.json(response)
    else:
        st.error("❌ Backend Not Reachable")
        st.json(response)