
import streamlit as st
import requests
from pathlib import Path

API_URL = "http://127.0.0.1:8001/experimental/voice/tts"

st.set_page_config(page_title="Manipuri Voice Assistant", page_icon="🎙️", layout="centered")

st.title("🎙️ Manipuri Voice Assistant")
st.caption("Experimental GPU-powered text-to-speech")

script = st.selectbox(
    "Select Manipuri Script",
    ["bengali", "meitei_mayek"],
    format_func=lambda x: "Bengali Script" if x == "bengali" else "Meitei Mayek"
)

if script == "bengali":
    placeholder = "Enter Manipuri text in Bengali script..."
else:
    placeholder = "Enter Manipuri text in Meitei Mayek..."

text = st.text_area("Enter your text", placeholder=placeholder, height=180)

if st.button("Generate Speech", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating speech using remote GPU..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"text": text, "script": script},
                    timeout=600
                )
                if response.status_code == 200:
                    output_dir = Path("experimental_outputs/manipuri_tts")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / f"streamlit_{script}.wav"
                    output_path.write_bytes(response.content)
                    st.success("Speech generated successfully!")
                    st.audio(response.content, format="audio/wav")
                    st.download_button(
                        "Download Audio",
                        data=response.content,
                        file_name=f"manipuri_{script}.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the experimental API: {e}")