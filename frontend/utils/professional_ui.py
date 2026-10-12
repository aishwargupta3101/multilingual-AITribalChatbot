import streamlit as st

def apply_professional_ui():
    current_theme = st.session_state.get("theme", "Light")
    st.markdown("""
<style>
.main .block-container{max-width:1180px;padding:1rem 1rem 6rem}
.main .chat-header{display:flex;align-items:center;justify-content:space-between;background:linear-gradient(135deg,#f7fbf8,#fff);border:1px solid #d9e5dd;border-radius:18px;padding:15px 19px;margin-bottom:18px;box-shadow:0 4px 18px rgba(35,70,48,.05)}
.main .chat-title-area{display:flex;align-items:center;gap:11px}
.main .chat-title-icon{width:40px;height:40px;border-radius:12px;background:#eaf5ed;border:1px solid #d7e8dc;display:flex;align-items:center;justify-content:center;font-size:20px}
.main .chat-title{font-size:20px!important;font-weight:750!important;color:#193526!important;line-height:1.2}
.main .chat-subtitle{font-size:12px!important;color:#718078!important;margin-top:3px}
.main .chat-header-right{display:flex;align-items:center;gap:10px}
.main .chat-language{padding:6px 10px;border-radius:9px;background:#f7faf8;border:1px solid #d9e5dd;font-size:11px;color:#52645a}
.main .chat-status{display:flex;align-items:center;gap:6px;font-size:11px;color:#557062}
.main .chat-status-dot{width:7px;height:7px;border-radius:50%;background:#49a46a;box-shadow:0 0 0 3px rgba(73,164,106,.12)}
.main .chat-welcome{padding:30px;border:1px solid #d9e5dd;border-radius:20px;background:linear-gradient(145deg,#f5faf6,#fff);box-shadow:0 5px 22px rgba(35,70,48,.05);margin:8px 0 20px}
.main .chat-welcome-icon{width:48px;height:48px;border-radius:14px;background:#eaf5ed;border:1px solid #d5e7da;display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:13px}
.main .chat-welcome-title{font-size:25px;font-weight:750;color:#193526;line-height:1.25}
.main .chat-welcome-text{font-size:14px;line-height:1.7;color:#69786f;margin-top:7px;max-width:760px}
.main .chat-row{display:flex;width:100%;margin-bottom:20px;align-items:flex-start}
.main .assistant-row{justify-content:flex-start;gap:10px}
.main .user-row{justify-content:flex-end;gap:9px}
.main .ai-avatar,.main .user-avatar{width:35px;height:35px;min-width:35px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-size:15px}
.main .ai-avatar{background:#edf6f0;border:1px solid #d2e4d7;box-shadow:0 2px 7px rgba(35,70,48,.06)}
.main .user-avatar{background:#f2f5f3;border:1px solid #dfe7e2}
.main .assistant-message-wrapper{max-width:82%;min-width:0}
.main .user-message-wrapper{max-width:70%;min-width:0}
.main .ai-label,.main .user-label{font-size:11px;font-weight:700;margin-bottom:5px;color:#52645a}
.main .ai-label{display:flex;align-items:center;gap:6px}
.main .ai-online-dot{width:6px;height:6px;border-radius:50%;background:#4fa56d;display:inline-block}
.main .assistant-message,.main .user-message{word-wrap:break-word;overflow-wrap:anywhere}
.main .assistant-message{padding:17px 19px;border-radius:5px 17px 17px 17px;background:#fff;border:1px solid #dce7df;color:#24352c;font-size:15px;line-height:1.75;box-shadow:0 3px 12px rgba(31,61,43,.045)}
.main .user-message{padding:13px 17px;border-radius:17px 5px 17px 17px;background:#edf6f0;border:1px solid #d4e6da;color:#263a2e;font-size:14px;line-height:1.65}
.main .message-info{margin-left:45px;margin-top:-9px;margin-bottom:18px;font-size:10px;color:#8a9790}
.main .assistant-message h1,.main .assistant-message h2,.main .assistant-message h3{color:#193526;margin-top:15px;margin-bottom:7px}
.main .assistant-message h1{font-size:21px}
.main .assistant-message h2{font-size:18px}
.main .assistant-message h3{font-size:16px}
.main .assistant-message p{margin:6px 0 10px}
.main .assistant-message ul,.main .assistant-message ol{margin:7px 0 11px;padding-left:22px}
.main .assistant-message li{margin:4px 0}
.main .assistant-message strong{color:#234634}
.main .assistant-message code{padding:2px 5px;border-radius:5px;background:#f0f5f2;color:#315b43;font-size:13px}
.main .assistant-message pre{padding:13px 15px;margin:10px 0;border-radius:10px;background:#f5f7f6;border:1px solid #dce5df;overflow-x:auto}
.main .assistant-message blockquote{margin:10px 0;padding:8px 13px;border-left:3px solid #75a486;background:#f5faf6;color:#5e7066}
.main .chat-toolbar-label{font-size:13px;font-weight:700;color:#52645a;padding:7px 0}
.main .stButton>button,.main .stDownloadButton>button{border:1px solid #d5e3da!important;border-radius:10px!important;background:#fff!important;color:#31533f!important;font-size:12px!important;font-weight:600!important;min-height:36px!important;box-shadow:0 2px 8px rgba(31,61,43,.04)!important;transition:all .15s ease!important}
.main .stButton>button:hover,.main .stDownloadButton>button:hover{border-color:#9fc2aa!important;background:#f5faf7!important;box-shadow:0 4px 12px rgba(31,61,43,.08)!important;transform:translateY(-1px)}
.main .stTextInput>div>div,.main .stSelectbox>div>div,.main .stTextArea>div>div{border-radius:11px!important;border-color:#d5e3da!important}
.main .stTextInput input,.main .stTextArea textarea{font-size:14px!important;color:#263a2e!important}
.main .stCaption{font-size:11px!important;color:#7b8981!important}
.main [data-testid="stExpander"]{border:1px solid #dce7df!important;border-radius:12px!important;background:#fff!important;box-shadow:0 2px 10px rgba(31,61,43,.035)!important}
.main [data-testid="stExpander"] summary{font-size:13px!important;font-weight:650!important;color:#31533f!important}
.main [data-testid="stMetric"]{background:#fff!important;border:1px solid #dce7df!important;border-radius:14px!important;padding:14px!important;box-shadow:0 3px 12px rgba(31,61,43,.04)!important}
.main [data-testid="stMetricLabel"]{font-size:11px!important;color:#718078!important}
.main [data-testid="stMetricValue"]{font-size:24px!important;color:#193526!important;font-weight:750!important}
.main .stAlert{border-radius:12px!important;border:1px solid #dce7df!important}
.main hr{border:none!important;border-top:1px solid #e3ebe6!important;margin:18px 0!important}
.main .stChatInputContainer{padding-bottom:14px!important;max-width:900px!important;margin:0 auto!important}
.main .stChatInputContainer>div{min-height:54px!important;border:1px solid #cfded4!important;border-radius:16px!important;background:#fff!important;box-shadow:0 5px 20px rgba(30,65,44,.08)!important}
.main .stChatInputContainer textarea{font-size:15px!important;color:#263a2e!important;padding-top:14px!important;padding-bottom:14px!important}
.main .stChatInputContainer textarea::placeholder{color:#8a9890!important}
.main .stChatInputContainer button{border-radius:10px!important}
.main ::-webkit-scrollbar{width:7px;height:7px}
.main ::-webkit-scrollbar-track{background:#f4f7f5}
.main ::-webkit-scrollbar-thumb{background:#cbd9d0;border-radius:10px}
.main ::-webkit-scrollbar-thumb:hover{background:#aebfb4}

/* SETTINGS */
.main .settings-page-header{padding:10px 0 18px!important;border-bottom:1px solid #dfe8e2;margin-bottom:16px!important}
.main .settings-header-icon{width:52px;height:52px;border-radius:15px;background:linear-gradient(145deg,#e8f4ec,#f5faf7);border:1px solid #d5e6da;box-shadow:0 4px 14px rgba(31,61,43,.06)}
.main .settings-header-title{font-size:27px!important;font-weight:750!important;color:#193526!important;line-height:1.2;letter-spacing:-.2px}
.main .settings-header-subtitle{font-size:13px!important;color:#718078!important;line-height:1.5;margin-top:3px}
.main .settings-section{margin-top:18px!important;margin-bottom:7px!important}
.main .settings-section-title{font-size:17px!important;font-weight:750!important;color:#193526!important;margin-bottom:1px!important}
.main .settings-section-description{font-size:12px!important;color:#7b8981!important;line-height:1.6;margin-top:2px!important;margin-bottom:8px!important}
.main .settings-info-card,.main .settings-model-card,.main .settings-about-card{border:1px solid #dce7df!important;border-radius:14px!important;background:#fff!important;box-shadow:0 3px 14px rgba(31,61,43,.045)!important;transition:all .18s ease}
.main .settings-info-card:hover,.main .settings-model-card:hover,.main .settings-about-card:hover{border-color:#bfd5c6!important;box-shadow:0 6px 18px rgba(31,61,43,.07)!important;transform:translateY(-1px)}
.main .settings-info-card{padding:17px 19px!important;margin-top:4px!important}
.main .settings-info-icon{width:42px!important;height:42px!important;border-radius:11px!important;background:#edf6f0!important;border:1px solid #d9e9dd!important}
.main .settings-info-label,.main .settings-model-label{font-size:11px!important;color:#7b8981!important;font-weight:600!important}
.main .settings-info-value,.main .settings-model-value{font-size:15px!important;color:#193526!important;font-weight:700!important}
.main .settings-model-card{padding:17px 19px!important;min-height:76px!important;display:flex!important;flex-direction:column!important;justify-content:center!important}
.main .settings-about-card{padding:18px 20px!important;margin-top:5px!important;margin-bottom:30px!important}
.main .settings-about-card p{font-size:13px!important;line-height:1.7!important;color:#52645a!important;margin:3px 0!important}
.main .settings-about-card strong{color:#31533f!important}
.main .settings-section .stButton>button{min-height:40px!important}
.main .settings-section .stSelectbox>div>div{background:#fff!important;border:1px solid #d5e3da!important}
.main .settings-section .stSelectbox label,.main .settings-section .stTextInput label,.main .settings-section .stTextArea label{font-size:12px!important;font-weight:650!important;color:#52645a!important}
.main .settings-section [data-testid="stCheckbox"] label{font-size:13px!important;color:#52645a!important}
.main .settings-section [data-testid="stCheckbox"] label p{color:#52645a!important}
.main .settings-section .stCheckbox{margin-top:0!important;margin-bottom:2px!important}
.main .settings-section .stSelectbox{margin-top:0!important;margin-bottom:6px!important}
.main .settings-section .stSelectbox>div>div{min-height:48px!important}

/* MOBILE */
@media(max-width:768px){
.main .block-container{padding:1.1rem .7rem 4rem}
.main .chat-header{padding:13px 14px}
.main .chat-header-right{display:none}
.main .assistant-message-wrapper{max-width:88%}
.main .user-message-wrapper{max-width:84%}
.main .assistant-message{font-size:14px;padding:14px 15px}
.main .user-message{font-size:13px;padding:12px 14px}
.main .chat-row{margin-bottom:16px}
.main .chat-welcome{padding:22px 18px}
.main .chat-welcome-title{font-size:21px}
.main .chat-welcome-text{font-size:13px}
.main .stChatInputContainer{max-width:100%!important}
.main [data-testid="stMetric"]{padding:11px!important}
.main .settings-page-header{padding:8px 0 16px!important;margin-bottom:14px!important}
.main .settings-header-icon{width:44px;height:44px}
.main .settings-header-title{font-size:23px!important}
.main .settings-header-subtitle{font-size:12px!important}
.main .settings-section{margin-top:16px!important}
.main .settings-section-title{font-size:16px!important}
.main .settings-model-card{min-height:70px!important}
.main .settings-about-card{margin-bottom:32px!important}
}
</style>
""",unsafe_allow_html=True)

    if current_theme == "Dark":
        st.markdown("""
<style>
.stApp{background:#101714!important;color:#e8f1eb!important}
[data-testid="stAppViewContainer"]{background:#101714!important}
[data-testid="stHeader"]{background:#101714!important}
[data-testid="stMain"]{background:#101714!important}
.main{background:#101714!important;color:#e8f1eb!important}
.main .block-container{background:#101714!important}

/* HEADINGS */
.main .chat-title,.main .chat-welcome-title,.main .settings-header-title,.main .settings-section-title{color:#edf6f0!important}
.main .chat-subtitle,.main .chat-welcome-text,.main .settings-header-subtitle,.main .settings-section-description{color:#aabbb0!important}

/* CHAT */
.main .chat-header{background:linear-gradient(135deg,#18241e,#141c18)!important;border-color:#2d4034!important}
.main .chat-welcome{background:linear-gradient(145deg,#17231d,#131b17)!important;border-color:#2d4034!important}
.main .chat-title-icon,.main .chat-welcome-icon,.main .settings-header-icon,.main .settings-info-icon{background:#1d3025!important;border-color:#34513f!important}
.main .assistant-message{background:#17211c!important;border-color:#2c4034!important;color:#e2ece5!important;box-shadow:0 4px 14px rgba(0,0,0,.18)!important}
.main .user-message{background:#20372a!important;border-color:#345542!important;color:#e6f0e9!important}
.main .ai-label,.main .user-label{color:#aebfb5!important}
.main .assistant-message h1,.main .assistant-message h2,.main .assistant-message h3{color:#e7f3eb!important}
.main .assistant-message strong{color:#b9dfc4!important}
.main .assistant-message code{background:#202f27!important;color:#b9d9c2!important}
.main .assistant-message pre{background:#121b16!important;border-color:#2e4035!important}
.main .assistant-message blockquote{background:#1b2b22!important;border-left-color:#6d9f7d!important;color:#aebfb5!important}

/* SETTINGS */
.main .settings-info-card,.main .settings-model-card,.main .settings-about-card{background:#17211c!important;border-color:#2d4034!important;box-shadow:0 4px 16px rgba(0,0,0,.16)!important}
.main .settings-info-card:hover,.main .settings-model-card:hover,.main .settings-about-card:hover{border-color:#496b55!important;box-shadow:0 7px 20px rgba(0,0,0,.22)!important}
.main .settings-info-label,.main .settings-model-label{color:#9dada3!important}
.main .settings-info-value,.main .settings-model-value,.main .settings-about-title{color:#edf6f0!important}
.main .settings-about-text{color:#adbbb2!important}

/* INPUTS */
.main .stSelectbox>div>div,.main .stTextInput>div>div,.main .stTextArea>div>div{background:#17211c!important;border-color:#365041!important}
.main .stSelectbox label,.main .stTextInput label,.main .stTextArea label{color:#b8c8be!important}
.main input,.main textarea{background:#17211c!important;color:#e8f1eb!important}
.main input::placeholder,.main textarea::placeholder{color:#82958a!important}

/* CHAT INPUT */
.main .stChatInputContainer>div{background:#17211c!important;border-color:#365041!important;box-shadow:0 5px 20px rgba(0,0,0,.2)!important}
.main .stChatInputContainer textarea{background:#17211c!important;color:#e8f1eb!important}
.main .stChatInputContainer textarea::placeholder{color:#82958a!important}

/* BUTTONS */
.main .stButton>button,.main .stDownloadButton>button{background:#17211c!important;border-color:#365041!important;color:#c9dbcf!important}
.main .stButton>button:hover,.main .stDownloadButton>button:hover{background:#213328!important;border-color:#54755f!important;color:#edf6f0!important}

/* OTHER COMPONENTS */
.main [data-testid="stExpander"]{background:#17211c!important;border-color:#2d4034!important}
.main [data-testid="stExpander"] summary{color:#c6d7cc!important}
.main [data-testid="stMetric"]{background:#17211c!important;border-color:#2d4034!important}
.main [data-testid="stMetricLabel"]{color:#9dada3!important}
.main [data-testid="stMetricValue"]{color:#edf6f0!important}
.main .stCaption{color:#899b90!important}
.main hr{border-top-color:#2b3b32!important}
.main .stAlert{background:#18251e!important;border-color:#304438!important;color:#dce9df!important}

/* SCROLLBAR */
.main ::-webkit-scrollbar-track{background:#101714!important}
.main ::-webkit-scrollbar-thumb{background:#34483b!important}
</style>
""",unsafe_allow_html=True)