import streamlit as st
from api.client import APIClient

def show_voice_recorder():
    st.subheader("🎤 Voice Chat")
    if "messages" not in st.session_state:
        st.session_state.messages =[]
    audio = st.audio_input("Record your question")
    if audio is not None:
        st.audio(audio)
        if st.button("Convert Speech to Text"):
            with st.spinner("Transcribing..."):
                result = APIClient.speech_to_text(
                    audio.getvalue()
                )
            if result["success"]:
                st.success("Speech converted successfully!")
                st.session_state.voice_text = result["text"]

                st.markdown("### 🎤 You Said")
                st.info(result["text"])
                with st.spinner("Generating response..."):

                    chat_result = APIClient.chat(
                        question=result["text"],
                        session_id=st.session_state.session_id,
                        language=st.session_state.language
                    )
                answer= chat_result["data"]["answer"]
                print(chat_result)
                st.session_state.voice_response = answer
                st.session_state.messages.append({
                    "role":"user",
                    "content":result["text"]
                })
                st.session_state.messages.append({
                    "role":"assistant",
                    "content":answer
                })
                st.markdown("### 🤖 AI Response")
                st.success(answer)
                with st.spinner("Generating Voice..."):
                    audio_bytes = APIClient.text_to_speech(
                        text=answer,
                        language=st.session_state.language
                    )
                st.subheader("###🔊 AI Voice")
                st.audio(
                    audio_bytes,
                    format="audio/wav"
                )
            else:
                st.error("Speech recognition failed.")