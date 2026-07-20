import streamlit as st
from api.client import APIClient
from api.endpoints import UPLOAD_ENDPOINT


def show_upload():
    st.subheader("📂 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:
        st.success(f"Selected: {uploaded_file.name}")
        st.write(f"Size: {uploaded_file.size/1024:.2f} KB")

        if st.button("Upload"):
            with st.spinner("Uploading..."):
                try:
                    response = APIClient.upload(
                        UPLOAD_ENDPOINT,
                        uploaded_file,
                        st.session_state.session_id
                    )
                    st.write("Backend Response")
                    st.json(response)

                except Exception as e:
                    st.exception(e)