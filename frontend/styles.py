
import streamlit as st


def apply_custom_css():
    st.markdown(
        """
        <style>
        * {
            box-sizing: border-box;
        }
        .stApp {
            background: #f7f9f8 !important;
            color: #243b2e !important;
        }
        .main .block-container {
            max-width: 1180px;
            padding-top: 1.5rem;
            padding-bottom: 6rem;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Sidebar width */
        section[data-testid="stSidebar"] {
            width: 285px !important;
            min-width: 285px !important;
            max-width: 285px !important;

            background: #10251b !important;

            border-right: 1px solid #294637;
        }
        /* Sidebar main container */
        section[data-testid="stSidebar"] > div {
            background: #10251b !important;

            padding: 0 !important;
        }    
        /* Sidebar inner content */
        section[data-testid="stSidebar"] .block-container {
            padding: 20px 16px 14px 16px !important;

            max-width: 100% !important;
        }


        /* Remove unnecessary Streamlit gaps */
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.35rem;
        }
        .brand-wrapper {
            display: flex;

            align-items: center;

            gap: 11px;

            padding: 4px 5px 17px 5px;

            border-bottom: 1px solid #294637;

            margin-bottom: 15px;
        }

        .brand-logo {
            width: 42px;
            height: 42px;

            display: flex;

            align-items: center;
            justify-content: center;

            border-radius: 12px;

            background: #e7f1ea;

            font-size: 22px;

            box-shadow:
                0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .brand-title {
            font-size: 17px;

            line-height: 1.2;

            font-weight: 750;

            color: #f3f8f4;

            letter-spacing: -0.2px;
        }

        .brand-subtitle {
            margin-top: 4px;

            font-size: 10px;

            line-height: 1.3;

            color: #9eb4a5;

            letter-spacing: 0.15px;
        }


        /* =========================================================
           STATUS
           ========================================================= */

        .sidebar-status {
            display: flex;

            align-items: center;

            gap: 7px;

            padding: 8px 10px;

            margin-bottom: 14px;

            border-radius: 8px;

            background: #172f23;

            border: 1px solid #294637;

            color: #abc0b1;

            font-size: 10px;

            font-weight: 500;
        }

        .sidebar-status-dot {
            width: 7px;
            height: 7px;

            flex-shrink: 0;

            border-radius: 50%;

            background: #72b987;

            box-shadow:
                0 0 0 3px rgba(114, 185, 135, 0.12);
        }


        /* =========================================================
           NEW CONVERSATION
           ========================================================= */

        section[data-testid="stSidebar"] button {
            font-family: inherit !important;
        }


        /* Streamlit button */
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;

            min-height: 40px;

            border-radius: 9px;

            border: 1px solid #527963 !important;

            background: #1d4932 !important;

            color: #f3f8f4 !important;

            font-size: 12px !important;

            font-weight: 650 !important;

            transition:
                background 0.18s ease,
                border-color 0.18s ease,
                transform 0.18s ease;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #265b3e !important;

            border-color: #6d9b7d !important;

            transform: translateY(-1px);
        }

        section[data-testid="stSidebar"] .stButton > button:active {
            transform: translateY(0);
        }


        /* =========================================================
           SECTION HEADINGS
           ========================================================= */

        .sidebar-section-title,
        .recent-chats-title,
        .conversation-language-title {
            margin-top: 18px;

            margin-bottom: 7px;

            padding-left: 3px;

            color: #718d7b;

            font-size: 9px;

            font-weight: 750;

            letter-spacing: 1.1px;

            text-transform: uppercase;
        }


        /* =========================================================
           NAVIGATION
           ========================================================= */

        /* Sidebar navigation buttons */
        section[data-testid="stSidebar"] .nav-button button {
            width: 100% !important;

            min-height: 36px !important;

            margin: 2px 0 !important;

            padding: 7px 10px !important;

            border: 1px solid transparent !important;

            border-radius: 8px !important;

            background: transparent !important;

            color: #b8c9bd !important;

            text-align: left !important;

            font-size: 12px !important;

            font-weight: 500 !important;
        }

        section[data-testid="stSidebar"] .nav-button button:hover {
            background: #173324 !important;

            color: #edf5ef !important;

            border-color: #294637 !important;
        }


        /* =========================================================
           RECENT CHATS
           ========================================================= */

        .recent-chat-item {
            display: flex;

            align-items: center;

            gap: 8px;

            width: 100%;

            padding: 8px 9px;

            margin-bottom: 3px;

            border-radius: 8px;

            background: transparent;

            border: 1px solid transparent;

            color: #aebfb4;

            font-size: 11px;

            line-height: 1.3;

            transition: all 0.18s ease;
        }

        .recent-chat-item:hover {
            background: #173324;

            border-color: #294637;

            color: #edf5ef;
        }

        .recent-chat-icon {
            width: 25px;
            height: 25px;

            flex-shrink: 0;

            display: flex;

            align-items: center;
            justify-content: center;

            border-radius: 7px;

            background: #193728;

            color: #89aa95;

            font-size: 12px;
        }

        .recent-chat-text {
            overflow: hidden;

            white-space: nowrap;

            text-overflow: ellipsis;
        }


        /* =========================================================
           LANGUAGE SECTION
           ========================================================= */

        .conversation-language-title {
            margin-top: 17px;
        }


        /* Selectbox wrapper */
        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div {
            min-height: 38px !important;

            border-radius: 9px !important;

            background: #172f23 !important;

            border: 1px solid #345442 !important;

            color: #edf5ef !important;

            box-shadow: none !important;
        }


        /* Selectbox text */
        section[data-testid="stSidebar"]
        div[data-baseweb="select"] span {
            color: #edf5ef !important;

            font-size: 12px !important;
        }


        /* Selectbox arrow */
        section[data-testid="stSidebar"]
        div[data-baseweb="select"] svg {
            fill: #91ab99 !important;
        }


        /* Selectbox hover */
        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div:hover {
            border-color: #5b8068 !important;

            background: #1a3627 !important;
        }


        /* =========================================================
           LANGUAGE MODE CARD
           ========================================================= */

        .language-mode-card {
            margin-top: 9px;

            padding: 12px;

            border-radius: 10px;

            background:
                linear-gradient(
                    145deg,
                    #173324,
                    #132c20
                );

            border: 1px solid #294637;
        }

        .language-mode-header {
            display: flex;

            align-items: center;

            gap: 8px;

            margin-bottom: 5px;
        }

        .language-mode-icon {
            width: 25px;
            height: 25px;

            display: flex;

            align-items: center;
            justify-content: center;

            border-radius: 7px;

            background: #224632;

            font-size: 12px;
        }

        .language-mode-title {
            color: #e6f0e8;

            font-size: 11px;

            font-weight: 700;
        }

        .language-mode-text {
            color: #91a99a;

            font-size: 9.5px;

            line-height: 1.45;

            padding-left: 33px;
        }


        /* =========================================================
           SIDEBAR FOOTER
           ========================================================= */

        .sidebar-footer {
            margin-top: 18px;

            padding: 11px 4px 2px 4px;

            border-top: 1px solid #294637;

            color: #718a79;

            font-size: 9px;

            line-height: 1.5;

            text-align: center;
        }

        .sidebar-footer strong {
            color: #9eb5a5;

            font-weight: 600;
        }


        /* =========================================================
           SIDEBAR SCROLLBAR
           ========================================================= */

        section[data-testid="stSidebar"] ::-webkit-scrollbar {
            width: 4px;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
            background: transparent;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
            background: #31523f;

            border-radius: 10px;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
            background: #496d56;
        }


        /* =========================================================
           MOBILE
           ========================================================= */

        @media (max-width: 768px) {

            section[data-testid="stSidebar"] {
                width: 270px !important;
                min-width: 270px !important;
            }

            section[data-testid="stSidebar"] .block-container {
                padding: 17px 13px 12px 13px !important;
            }

            .brand-wrapper {
                padding-bottom: 14px;
                margin-bottom: 12px;
            }
        }

        /* =========================================================
           HOME
           ========================================================= */

        .hero-section {
            position: relative;

            overflow: hidden;

            padding: 45px 6px 40px 6px;
        }

        .hero-badge {
            display: inline-flex;

            align-items: center;

            padding: 6px 11px;

            border-radius: 20px;

            background: #e8f2ec;

            color: #315c46;

            font-size: 12px;

            font-weight: 600;
        }

        .hero-title {
            max-width: 760px;

            margin-top: 14px;

            font-size: 44px;

            line-height: 1.1;

            font-weight: 750;

            color: #173d2b;

            letter-spacing: -1px;
        }

        .hero-title span {
            color: #4d7d60;
        }

        .hero-description {
            max-width: 700px;

            margin-top: 17px;

            font-size: 15px;

            line-height: 1.7;

            color: #66756d;
        }

        .hero-language {
            margin-top: 18px;

            font-size: 12px;

            color: #527061;
        }

        .hero-glow {
            position: absolute;

            border-radius: 50%;

            pointer-events: none;

            opacity: 0.25;
        }

        .hero-glow-one {
            width: 230px;
            height: 230px;

            right: -90px;
            top: -60px;

            background: #dcece2;
        }

        .hero-glow-two {
            width: 150px;
            height: 150px;

            left: -70px;
            bottom: -60px;

            background: #e7efe9;
        }

        .section-heading {
            margin: 24px 0 17px 0;
        }

        .section-eyebrow {
            font-size: 11px;

            font-weight: 700;

            letter-spacing: 1px;

            text-transform: uppercase;

            color: #5b816a;
        }

        .section-title {
            margin-top: 4px;

            font-size: 25px;

            font-weight: 700;

            color: #173d2b;
        }

        .section-description {
            margin-top: 5px;

            font-size: 13px;

            color: #718078;
        }

        .feature-card {
            min-height: 160px;

            padding: 20px;

            border: 1px solid #dce7df;

            border-radius: 13px;

            background: #ffffff;
        }

        .feature-icon {
            width: 37px;
            height: 37px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 9px;

            background: #edf5ef;

            font-size: 18px;

            margin-bottom: 13px;
        }

        .feature-title {
            font-size: 15px;

            font-weight: 700;

            color: #254735;
        }

        .feature-text {
            margin-top: 6px;

            font-size: 12px;

            line-height: 1.6;

            color: #718078;
        }

        .home-cta {
            display: flex;

            align-items: center;

            gap: 14px;

            margin-top: 28px;

            padding: 18px 20px;

            border-radius: 12px;

            background: #eaf3ed;

            border: 1px solid #d7e5dc;
        }

        .home-cta-icon {
            font-size: 21px;
        }

        .home-cta-content {
            flex: 1;
        }

        .home-cta-title {
            font-size: 15px;

            font-weight: 700;

            color: #234634;
        }

        .home-cta-text {
            margin-top: 3px;

            font-size: 12px;

            color: #6c7b73;
        }

        .home-cta-arrow {
            font-size: 19px;

            color: #527b61;
        }

        .home-footer {
            margin-top: 40px;

            padding-top: 17px;

            border-top: 1px solid #dfe7e2;

            text-align: center;

            font-size: 11px;

            color: #87928c;
        }


        /* =========================================================
           CHAT
           ========================================================= */

        .chat-header {
            display: flex;

            align-items: center;

            justify-content: space-between;

            gap: 20px;

            padding: 10px 4px 17px 4px;

            border-bottom: 1px solid #dfe8e2;

            margin-bottom: 20px;
        }

        .chat-title-area {
            display: flex;

            align-items: center;

            gap: 12px;

            min-width: 0;
        }

        .chat-title-icon {
            width: 44px;
            height: 44px;

            flex-shrink: 0;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 11px;

            background: #e8f2ec;

            font-size: 21px;
        }

        .chat-title {
            font-size: 24px;

            font-weight: 700;

            line-height: 1.2;

            color: #173d2b;
        }

        .chat-subtitle {
            margin-top: 3px;

            font-size: 12px;

            color: #718078;
        }

        .chat-header-right {
            display: flex;

            align-items: center;

            gap: 11px;
        }

        .chat-language {
            padding: 6px 10px;

            border-radius: 8px;

            background: #eef5f1;

            color: #315c46;

            font-size: 12px;

            font-weight: 600;
        }

        .chat-status {
            display: flex;

            align-items: center;

            gap: 6px;

            font-size: 12px;

            color: #627169;
        }

        .chat-status-dot {
            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: #4f9b68;
        }

        .chat-welcome {
            display: flex;

            align-items: flex-start;

            gap: 15px;

            padding: 21px;

            border: 1px solid #dce7df;

            border-radius: 14px;

            background: #ffffff;

            margin-bottom: 21px;
        }

        .chat-welcome-icon {
            width: 42px;
            height: 42px;

            flex-shrink: 0;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 10px;

            background: #edf5ef;

            font-size: 20px;
        }

        .chat-welcome-title {
            font-size: 20px;

            font-weight: 700;

            color: #173d2b;

            margin-bottom: 6px;
        }

        .chat-welcome-text {
            max-width: 760px;

            font-size: 13px;

            line-height: 1.6;

            color: #66756d;
        }

        .chat-suggestions-header {
            margin: 4px 0 11px 2px;
        }

        .chat-suggestions-title {
            font-size: 15px;

            font-weight: 700;

            color: #254735;
        }

        .chat-suggestions-subtitle {
            margin-top: 2px;

            font-size: 12px;

            color: #7a8780;
        }

        .chat-suggestion-card {
            min-height: 105px;

            padding: 16px;

            border: 1px solid #dce7df;

            border-radius: 12px;

            background: #ffffff;
        }

        .chat-suggestion-card:hover {
            border-color: #a9c3b2;
        }

        .chat-suggestion-icon {
            width: 30px;
            height: 30px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 8px;

            background: #edf5ef;

            font-size: 15px;

            margin-bottom: 9px;
        }

        .chat-suggestion-title {
            font-size: 13px;

            font-weight: 700;

            color: #234634;
        }

        .chat-suggestion-text {
            margin-top: 3px;

            font-size: 11px;

            line-height: 1.45;

            color: #728078;
        }

        .chat-conversation-heading {
            display: flex;

            align-items: center;

            gap: 12px;

            margin: 24px 2px 12px 2px;
        }

        .chat-conversation-title {
            flex-shrink: 0;

            font-size: 14px;

            font-weight: 700;

            color: #31523f;
        }

        .chat-conversation-line {
            height: 1px;

            flex: 1;

            background: #e1e8e3;
        }


        /* =========================================================
           CHAT INPUT
           ========================================================= */

        div[data-testid="stChatInput"] {
            padding-top: 8px;
        }

        div[data-testid="stChatInput"] textarea {
            border: 1px solid #cfdcd4 !important;

            border-radius: 12px !important;

            background: #ffffff !important;

            color: #243b2e !important;

            font-size: 14px !important;
        }

        div[data-testid="stChatInput"] textarea:focus {
            border-color: #719c80 !important;

            box-shadow: 0 0 0 1px #719c80 !important;
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: #89958e !important;
        }

        .chat-toolbar-label {
            padding: 7px 0;

            font-size: 12px;

            font-weight: 600;

            color: #718078;
        }


        /* =========================================================
           CHAT ACTION BUTTONS
           ========================================================= */

        div[data-testid="stDownloadButton"] button {
            min-height: 32px !important;

            padding: 5px 10px !important;

            border-radius: 7px !important;

            border: 1px solid #d4e0d8 !important;

            background: #ffffff !important;

            color: #527061 !important;

            font-size: 11px !important;

            font-weight: 600 !important;

            box-shadow: none !important;
        }

        div[data-testid="stDownloadButton"] button:hover {
            background: #edf5ef !important;

            border-color: #9dbba8 !important;
        }


        .chat-toolbar-label + div {
            margin-top: 0 !important;
        }


        /* Regenerate button */

        button[kind="secondary"] {
            min-height: 32px !important;

            border-radius: 7px !important;
        }


        /* =========================================================
           CHAT ACTION AREA
           ========================================================= */

        .chat-message-actions {
            display: flex;

            align-items: center;

            gap: 8px;

            margin-top: 6px;

            margin-bottom: 10px;
        }


        /* =========================================================
           CHAT ERROR
           ========================================================= */

        .chat-error-card {
            display: flex;

            align-items: center;

            gap: 10px;

            margin-top: 12px;

            padding: 13px 15px;

            border: 1px solid #eadada;

            border-radius: 10px;

            background: #fffafa;
        }

        .chat-error-icon {
            font-size: 18px;
        }

        .chat-error-text {
            font-size: 12px;

            color: #704545;
        }
        .chat-row {
            width: 100%;
            display: flex;
            margin-bottom: 18px;
            align-items: flex-start;
        }


        /* =========================================================
           USER MESSAGE
           ========================================================= */

        .user-row {
            justify-content: flex-end;
            gap: 10px;
        }

        .user-message-wrapper {
            max-width: 72%;
        }

        .user-label {
            text-align: right;

            margin-bottom: 6px;

            font-size: 12px;
            font-weight: 700;

            color: #53645a;
        }

        .user-message {
            padding: 13px 17px;

            border-radius: 16px 4px 16px 16px;

            background: #e8f2ec;

            border: 1px solid #d3e4d9;

            color: #243b2d;

            font-size: 14px;
            line-height: 1.65;

            box-shadow: 0 2px 7px rgba(30, 60, 40, 0.05);

            word-wrap: break-word;
        }

        .user-avatar {
            width: 34px;
            height: 34px;

            flex-shrink: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background: #edf3ef;

            border: 1px solid #d8e4dc;

            font-size: 16px;
        }


        /* =========================================================
           AI MESSAGE
           ========================================================= */

        .assistant-row {
            justify-content: flex-start;
            gap: 10px;
        }

        .ai-avatar {
            width: 34px;
            height: 34px;

            flex-shrink: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background: #edf5ef;

            border: 1px solid #d6e6da;

            font-size: 17px;
        }

        .assistant-message-wrapper {
            max-width: 78%;
        }

        .ai-label {
            display: flex;
            align-items: center;

            gap: 6px;

            margin-bottom: 6px;

            font-size: 12px;
            font-weight: 700;

            color: #53645a;
        }

        .ai-online-dot {
            width: 6px;
            height: 6px;

            border-radius: 50%;

            background: #5d9b70;

            display: inline-block;
        }

        .assistant-message {
            padding: 16px 18px;

            border-radius: 4px 16px 16px 16px;

            background: #ffffff;

            border: 1px solid #dce6df;

            color: #263a2e;

            font-size: 14px;
            line-height: 1.75;

            box-shadow: 0 3px 10px rgba(30, 60, 40, 0.055);

            word-wrap: break-word;
        }


        /* =========================================================
           MESSAGE INFORMATION
           ========================================================= */

        .message-info {
            margin-left: 44px;

            margin-top: -10px;

            margin-bottom: 18px;

            font-size: 10px;

            color: #8a968e;
        }


        /* =========================================================
           MOBILE
           ========================================================= */

        @media (max-width: 768px) {

            .user-message-wrapper {
                max-width: 82%;
            }

            .assistant-message-wrapper {
                max-width: 84%;
            }

            .user-message,
            .assistant-message {
                font-size: 13px;
                padding: 12px 14px;
            }

            .chat-row {
                margin-bottom: 14px;
            }

            .message-info {
                margin-left: 42px;
            }
        }
        .image-gallery-header {
            display: flex;

            align-items: center;

            gap: 11px;

            margin-top: 22px;

            margin-bottom: 13px;

            padding-top: 17px;

            border-top: 1px solid #dfe8e2;
        }

        .image-gallery-icon {
            width: 36px;
            height: 36px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 9px;

            background: #e8f2ec;

            font-size: 17px;
        }

        .image-gallery-title {
            font-size: 17px;

            font-weight: 700;

            color: #254735;
        }

        .image-gallery-subtitle {
            margin-top: 2px;

            font-size: 11px;

            color: #7a8780;
        }


        /* =========================================================
           IMAGE CARD
           ========================================================= */

        .image-card-title {
            margin-top: 8px;

            font-size: 12px;

            line-height: 1.4;

            font-weight: 600;

            color: #40584a;

            overflow: hidden;

            display: -webkit-box;

            -webkit-line-clamp: 2;

            -webkit-box-orient: vertical;
        }

        .image-source-link {
            display: inline-block;

            margin-top: 5px;

            font-size: 10px;

            color: #527b61 !important;

            text-decoration: none !important;
        }

        .image-source-link:hover {
            color: #315c46 !important;

            text-decoration: underline !important;
        }


        /* =========================================================
           EMPTY STATE
           ========================================================= */

        .image-gallery-empty {
            display: flex;

            align-items: center;

            gap: 12px;

            padding: 15px;

            margin-top: 10px;

            border: 1px solid #dce7df;

            border-radius: 10px;

            background: #ffffff;
        }

        .image-gallery-empty-icon {
            font-size: 20px;
        }

        .image-gallery-empty-title {
            font-size: 13px;

            font-weight: 600;

            color: #40584a;
        }

        .image-gallery-empty-text {
            margin-top: 2px;

            font-size: 11px;

            color: #7a8780;
        }
        /* =========================================================
           DOCUMENTS
           ========================================================= */

        .documents-page-header {
            display: flex;

            align-items: center;

            justify-content: space-between;

            gap: 16px;

            padding: 10px 4px 20px 4px;

            border-bottom: 1px solid #dfe8e2;

            margin-bottom: 22px;
        }

        .documents-header-content {
            display: flex;

            align-items: center;

            gap: 14px;

            flex: 1;
        }

        .documents-header-icon {
            width: 46px;
            height: 46px;

            flex-shrink: 0;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 11px;

            background: #e8f2ec;

            font-size: 21px;
        }

        .documents-header-title {
            font-size: 26px;

            font-weight: 700;

            line-height: 1.2;

            color: #173d2b;
        }

        .documents-header-subtitle {
            margin-top: 4px;

            font-size: 13px;

            line-height: 1.5;

            color: #718078;
        }

        .documents-header-language {
            padding: 7px 11px;

            border-radius: 8px;

            background: #eef5f1;

            color: #315c46;

            font-size: 12px;

            font-weight: 600;
        }

        .documents-intro {
            margin-bottom: 18px;
        }

        .documents-intro-title {
            font-size: 17px;

            font-weight: 700;

            color: #254735;
        }

        .documents-intro-text {
            max-width: 720px;

            margin-top: 5px;

            font-size: 13px;

            line-height: 1.6;

            color: #718078;
        }

        .upload-card {
            padding: 24px;

            border: 1px solid #dce7df;

            border-radius: 14px;

            background: #ffffff;

            box-shadow: 0 2px 8px rgba(31, 61, 45, 0.04);
        }

        .upload-card-header {
            display: flex;

            align-items: center;

            gap: 13px;

            margin-bottom: 18px;
        }

        .upload-card-icon {
            width: 40px;
            height: 40px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 10px;

            background: #edf5ef;

            font-size: 18px;
        }

        .upload-card-title {
            font-size: 16px;

            font-weight: 700;

            color: #234634;
        }

        .upload-card-subtitle {
            margin-top: 3px;

            font-size: 12px;

            color: #7a8780;
        }

        /* File uploader */

        div[data-testid="stFileUploader"] {
            width: 100%;
        }

        div[data-testid="stFileUploader"] section {
            padding: 25px 20px !important;

            border: 1.5px dashed #b8cfc0 !important;

            border-radius: 12px !important;

            background: #f8fbf9 !important;
        }

        div[data-testid="stFileUploader"] section:hover {
            border-color: #719c80 !important;

            background: #f4f9f5 !important;
        }

        div[data-testid="stFileUploader"] label p {
            color: #31523f !important;

            font-size: 13px !important;
        }

        div[data-testid="stFileUploader"] button {
            border: 1px solid #c9dacf !important;

            border-radius: 8px !important;

            background: #ffffff !important;

            color: #315c46 !important;

            font-weight: 600 !important;
        }

        div[data-testid="stFileUploader"] button:hover {
            border-color: #719c80 !important;

            background: #edf5ef !important;
        }

        .document-selected-file {
            display: flex;

            align-items: center;

            gap: 12px;

            margin-top: 15px;

            padding: 13px 15px;

            border: 1px solid #d8e6dc;

            border-radius: 10px;

            background: #f7faf8;
        }

        .document-file-icon {
            width: 34px;
            height: 34px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 8px;

            background: #e8f2ec;

            font-size: 16px;
        }

        .document-file-info {
            flex: 1;

            min-width: 0;
        }

        .document-file-name {
            font-size: 13px;

            font-weight: 600;

            color: #294a37;

            overflow: hidden;

            text-overflow: ellipsis;

            white-space: nowrap;
        }

        .document-file-size {
            margin-top: 2px;

            font-size: 11px;

            color: #7b8881;
        }

        .document-info-card {
            min-height: 105px;

            padding: 16px;

            border: 1px solid #dce7df;

            border-radius: 12px;

            background: #ffffff;
        }

        .document-info-icon {
            font-size: 18px;

            margin-bottom: 8px;
        }

        .document-info-title {
            font-size: 13px;

            font-weight: 700;

            color: #31523f;
        }

        .document-info-text {
            margin-top: 4px;

            font-size: 11px;

            line-height: 1.5;

            color: #77847d;
        }

        .document-success-card {
            display: flex;

            align-items: center;

            gap: 11px;

            margin-top: 16px;

            padding: 13px 15px;

            border: 1px solid #d3e6d8;

            border-radius: 10px;

            background: #edf7ef;
        }

        .document-success-icon {
            font-size: 19px;

            color: #4d805a;
        }

        .document-success-title {
            font-size: 13px;

            font-weight: 700;

            color: #315c3f;
        }

        .document-success-text {
            margin-top: 2px;

            font-size: 11px;

            color: #6d7c72;
        }

        .document-error-card {
            padding: 13px 15px;

            margin-top: 15px;

            border: 1px solid #eadada;

            border-radius: 10px;

            background: #fffafa;
        }

        .document-error-title {
            font-size: 13px;

            font-weight: 700;

            color: #704545;
        }

        .document-error-text {
            margin-top: 3px;

            font-size: 11px;

            color: #806969;
        }

        .documents-footer {
            margin-top: 30px;

            padding-top: 16px;

            border-top: 1px solid #e0e7e2;

            text-align: center;

            font-size: 11px;

            color: #849088;
        }


        /* =========================================================
           VOICE
           ========================================================= */

        .voice-page-header {
            display: flex;

            align-items: center;

            gap: 14px;

            padding: 10px 0 22px 0;
        }

        .voice-header-icon {
            width: 46px;
            height: 46px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 11px;

            background: #e8f2ec;

            font-size: 21px;
        }

        .voice-header-content {
            flex: 1;
        }

        .voice-header-title {
            font-size: 26px;

            font-weight: 700;

            color: #173d2b;
        }

        .voice-header-subtitle {
            margin-top: 4px;

            font-size: 13px;

            color: #718078;
        }

        .voice-header-language {
            padding: 7px 11px;

            border-radius: 8px;

            background: #eef5f1;

            color: #315c46;

            font-size: 12px;

            font-weight: 600;
        }

        .voice-language-card,
        .voice-record-card,
        .voice-recorded-card,
        .voice-success-card,
        .voice-result-card,
        .voice-ai-card,
        .voice-empty-card,
        .voice-error-card {
            border: 1px solid #dce7df;

            border-radius: 13px;

            background: #ffffff;
        }

        .voice-language-card {
            display: flex;

            align-items: center;

            gap: 14px;

            padding: 17px;

            margin-bottom: 18px;
        }

        .voice-language-icon,
        .voice-record-icon {
            font-size: 22px;
        }

        .voice-language-content {
            flex: 1;
        }

        .voice-language-title,
        .voice-record-title,
        .voice-recorded-title {
            font-size: 15px;

            font-weight: 700;

            color: #234634;
        }

        .voice-language-text,
        .voice-record-text,
        .voice-recorded-text {
            margin-top: 4px;

            font-size: 12px;

            color: #718078;
        }

        .voice-language-badge,
        .voice-ready-badge {
            padding: 5px 9px;

            border-radius: 7px;

            background: #edf5ef;

            color: #3f7252;

            font-size: 10px;

            font-weight: 700;
        }

        .voice-record-card {
            padding: 22px;

            text-align: center;
        }

        .voice-record-icon {
            margin-bottom: 8px;
        }

        .voice-recorded-card {
            display: flex;

            align-items: center;

            gap: 13px;

            padding: 15px;

            margin-top: 15px;
        }

        .voice-recorded-content {
            flex: 1;
        }

        .voice-success-card {
            display: flex;

            align-items: center;

            gap: 12px;

            padding: 15px;

            margin-top: 15px;

            background: #edf6ef;

            border-color: #d6e8d9;
        }

        .voice-success-icon {
            font-size: 20px;

            color: #4b805b;
        }

        .voice-success-title {
            font-size: 14px;

            font-weight: 700;

            color: #315c3f;
        }

        .voice-success-text {
            margin-top: 3px;

            font-size: 12px;

            color: #68786e;
        }

        .voice-result-card {
            padding: 17px;

            margin-top: 15px;
        }

        .voice-result-label {
            font-size: 10px;

            font-weight: 700;

            letter-spacing: 0.8px;

            color: #718078;
        }

        .voice-result-text {
            margin-top: 8px;

            font-size: 14px;

            line-height: 1.6;

            color: #294434;
        }

        .voice-ai-card {
            padding: 18px;

            margin-top: 15px;
        }

        .voice-ai-header {
            display: flex;

            align-items: center;

            gap: 10px;
        }

        .voice-ai-icon {
            font-size: 20px;
        }

        .voice-ai-title {
            font-size: 14px;

            font-weight: 700;

            color: #234634;
        }

        .voice-ai-language {
            margin-top: 2px;

            font-size: 10px;

            color: #7a8780;
        }

        .voice-ai-response {
            margin-top: 13px;

            padding-top: 13px;

            border-top: 1px solid #e5ebe7;

            font-size: 14px;

            line-height: 1.65;

            color: #2e4437;
        }

        .voice-empty-card {
            padding: 30px;

            text-align: center;

            margin-top: 15px;
        }

        .voice-empty-icon {
            font-size: 28px;
        }

        .voice-empty-title {
            margin-top: 8px;

            font-size: 15px;

            font-weight: 700;

            color: #31523f;
        }

        .voice-empty-text {
            margin-top: 5px;

            font-size: 12px;

            color: #718078;
        }

        .voice-error-card {
            display: flex;

            gap: 12px;

            padding: 15px;

            margin-top: 15px;

            background: #fffafa;

            border-color: #eadada;
        }

        .voice-error-icon {
            font-size: 20px;
        }

        .voice-error-title {
            font-size: 14px;

            font-weight: 700;

            color: #704545;
        }

        .voice-error-text {
            margin-top: 3px;

            font-size: 12px;

            color: #806969;
        }

        .voice-footer-info {
            margin-top: 25px;

            padding-top: 15px;

            border-top: 1px solid #e0e7e2;

            text-align: center;

            font-size: 11px;

            color: #849088;
        }


        /* =========================================================
           HISTORY
           ========================================================= */

        .history-page-header {
            display: flex;

            align-items: center;

            gap: 14px;

            padding: 10px 0 22px 0;
        }

        .history-header-icon {
            width: 46px;
            height: 46px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 11px;

            background: #e8f2ec;

            font-size: 21px;
        }

        .history-header-content {
            flex: 1;
        }

        .history-header-title {
            font-size: 26px;

            font-weight: 700;

            color: #173d2b;
        }

        .history-header-subtitle {
            margin-top: 4px;

            font-size: 13px;

            color: #718078;
        }

        .history-header-language {
            padding: 7px 11px;

            border-radius: 8px;

            background: #eef5f1;

            color: #315c46;

            font-size: 12px;

            font-weight: 600;
        }

        .history-stat-card {
            min-height: 110px;

            padding: 18px;

            border: 1px solid #dce7df;

            border-radius: 13px;

            background: #ffffff;
        }

        .history-stat-icon {
            font-size: 17px;
        }

        .history-stat-number {
            margin-top: 8px;

            font-size: 24px;

            font-weight: 700;

            color: #234634;
        }

        .history-stat-label {
            margin-top: 2px;

            font-size: 11px;

            color: #78857e;
        }

        .history-section-header {
            margin: 27px 0 12px 0;
        }

        .history-section-title {
            font-size: 17px;

            font-weight: 700;

            color: #254735;
        }

        .history-section-subtitle {
            margin-top: 3px;

            font-size: 12px;

            color: #7a8780;
        }

        .history-message {
            padding: 16px 18px;

            margin: 10px 0;

            border-radius: 12px;

            border: 1px solid #dce7df;
        }

        .history-user-message {
            background: #edf5ef;
        }

        .history-ai-message {
            background: #ffffff;
        }

        .history-message-top {
            display: flex;

            align-items: center;

            gap: 8px;
        }

        .history-message-icon {
            font-size: 15px;
        }

        .history-message-role {
            font-size: 12px;

            font-weight: 700;

            color: #31523f;
        }

        .history-message-number {
            margin-left: auto;

            font-size: 10px;

            color: #89958e;
        }

        .history-message-content {
            margin-top: 9px;

            font-size: 13px;

            line-height: 1.65;

            color: #33473b;

            white-space: pre-wrap;
        }

        .history-empty-card {
            padding: 40px 20px;

            margin-top: 15px;

            text-align: center;

            border: 1px solid #dce7df;

            border-radius: 13px;

            background: #ffffff;
        }

        .history-empty-icon {
            font-size: 28px;
        }

        .history-empty-title {
            margin-top: 9px;

            font-size: 16px;

            font-weight: 700;

            color: #31523f;
        }

        .history-empty-text {
            max-width: 500px;

            margin: 5px auto 0 auto;

            font-size: 12px;

            line-height: 1.5;

            color: #718078;
        }

        .history-actions-title {
            margin-top: 25px;

            margin-bottom: 9px;

            font-size: 14px;

            font-weight: 700;

            color: #31523f;
        }


        /* =========================================================
           SETTINGS
           ========================================================= */

        .settings-page-header {
            display: flex;

            align-items: center;

            gap: 16px;

            padding: 10px 0 24px 0;

            border-bottom: 1px solid #dfe8e2;
        }

        .settings-header-icon {
            width: 48px;
            height: 48px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 12px;

            background: #e8f2ec;

            font-size: 22px;
        }

        .settings-header-content {
            flex: 1;
        }

        .settings-header-title {
            font-size: 28px;

            font-weight: 700;

            color: #173d2b;
        }

        .settings-header-subtitle {
            margin-top: 5px;

            font-size: 14px;

            color: #66756d;
        }

        .settings-section {
            margin-top: 24px;

            margin-bottom: 12px;
        }

        .settings-section-title {
            font-size: 18px;

            font-weight: 700;

            color: #173d2b;
        }

        .settings-section-description {
            margin-top: 4px;

            font-size: 13px;

            color: #718078;
        }

        .settings-info-card {
            display: flex;

            align-items: center;

            gap: 14px;

            padding: 15px 18px;

            border: 1px solid #dce6df;

            border-radius: 12px;

            background: #ffffff;
        }

        .settings-info-icon {
            width: 40px;
            height: 40px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 10px;

            background: #edf5ef;

            font-size: 18px;
        }

        .settings-info-content {
            flex: 1;
        }

        .settings-info-label {
            font-size: 12px;

            color: #7a8780;
        }

        .settings-info-value {
            margin-top: 2px;

            font-size: 16px;

            font-weight: 600;

            color: #173d2b;
        }

        .settings-model-card {
            padding: 16px 18px;

            border: 1px solid #dce6df;

            border-radius: 12px;

            background: #ffffff;
        }

        .settings-model-label {
            font-size: 12px;

            color: #7a8780;
        }

        .settings-model-value {
            margin-top: 5px;

            font-size: 17px;

            font-weight: 600;

            color: #173d2b;
        }

        .settings-about-card {
            display: flex;

            align-items: flex-start;

            gap: 15px;

            padding: 18px;

            border: 1px solid #dce6df;

            border-radius: 12px;

            background: #ffffff;
        }

        .settings-about-icon {
            font-size: 25px;
        }

        .settings-about-content {
            flex: 1;
        }

        .settings-about-title {
            font-size: 16px;

            font-weight: 700;

            color: #173d2b;
        }

        .settings-about-text {
            margin-top: 6px;

            font-size: 13px;

            line-height: 1.6;

            color: #68766e;
        }

        div[data-testid="stCheckbox"] label p {
            color: #30483a !important;
        }

        div[data-testid="stSelectbox"] label p {
            color: #30483a !important;
        }


        /* =========================================================
           GENERAL BUTTONS
           ========================================================= */

        .stButton > button {
            border-radius: 9px !important;

            border: 1px solid #cfdcd4 !important;

            color: #31523f !important;

            background: #ffffff !important;

            font-weight: 600 !important;

            box-shadow: none !important;
        }

        .stButton > button:hover {
            border-color: #719c80 !important;

            color: #234634 !important;
        }


        /* =========================================================
           DOWNLOAD BUTTON
           ========================================================= */

        button[data-testid="stDownloadButton"] {
            border-radius: 9px !important;

            border: 1px solid #cfdcd4 !important;

            background: #ffffff !important;

            color: #31523f !important;
        }


        /* =========================================================
           GENERAL INPUT
           ========================================================= */

        input,
        textarea {
            color: #243b2e !important;
        }


        /* =========================================================
           MOBILE
           ========================================================= */

        @media (max-width: 768px) {

            .main .block-container {
                padding-left: 1rem;

                padding-right: 1rem;

                padding-top: 1rem;
            }

            .hero-section {
                padding: 30px 4px;
            }

            .hero-title {
                font-size: 34px;
            }

            .hero-description {
                font-size: 14px;
            }

            .chat-header {
                align-items: flex-start;
            }

            .chat-header-right {
                flex-direction: column;

                align-items: flex-end;

                gap: 5px;
            }

            .chat-title {
                font-size: 21px;
            }

            .chat-subtitle {
                font-size: 11px;
            }

            .chat-welcome {
                padding: 17px;
            }

            .chat-welcome-title {
                font-size: 18px;
            }

            .chat-suggestion-card {
                margin-bottom: 8px;
            }

            .documents-page-header,
            .voice-page-header,
            .history-page-header,
            .settings-page-header {
                align-items: flex-start;
            }

            .documents-header-title,
            .voice-header-title,
            .history-header-title {
                font-size: 22px;
            }

            .settings-header-title {
                font-size: 24px;
            }

            .documents-header-language,
            .voice-header-language,
            .history-header-language {
                display: none;
            }

            .upload-card {
                padding: 18px;
            }

            .settings-model-card {
                margin-bottom: 10px;
            }
        }
        div[data-testid="stFileUploader"] {
            margin-top: -2px;
            margin-bottom: 4px;
        }

        div[data-testid="stFileUploader"] section {
            min-height: 110px !important;
        }


        /* Hide unnecessary uploader instruction clutter */
        div[data-testid="stFileUploader"] small {
            color: #7a8780 !important;
        }


        /* File uploader drag/drop area */
        div[data-testid="stFileUploader"] section {
            display: flex;
            align-items: center;
            justify-content: center;
        } 
        section[data-testid="stSidebar"] .brand-title {
            color: #f3f8f4 !important;
        }

        section[data-testid="stSidebar"] .brand-subtitle {
            color: #9eb4a5 !important;
        }


        /* Status */
        section[data-testid="stSidebar"] .sidebar-status {
            color: #abc0b1 !important;
        }

        section[data-testid="stSidebar"] .sidebar-status span,
        section[data-testid="stSidebar"] .sidebar-status div {
            color: #abc0b1 !important;
        }


        /* Section headings */
        section[data-testid="stSidebar"] .sidebar-section-title,
        section[data-testid="stSidebar"] .recent-chats-title,
        section[data-testid="stSidebar"] .conversation-language-title {
            color: #7fa58b !important;
        }


        /* =========================================================
           STREAMLIT RADIO / NAVIGATION
           ========================================================= */

        section[data-testid="stSidebar"] .stRadio label {
            color: #dce9df !important;
        }

        section[data-testid="stSidebar"] .stRadio label p {
            color: #dce9df !important;
        }

        section[data-testid="stSidebar"] .stRadio label span {
            color: #dce9df !important;
        }


        /* Radio circle */
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {
            background: transparent !important;
        }


        /* Radio hover */
        section[data-testid="stSidebar"] .stRadio label:hover {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] .stRadio label:hover p {
            color: #ffffff !important;
        }


        /* Selected radio */
        section[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] .stRadio label[data-checked="true"] p {
            color: #ffffff !important;
        }


        /* =========================================================
           SIDEBAR BUTTON TEXT
           ========================================================= */

        section[data-testid="stSidebar"] .stButton > button {
            color: #f3f8f4 !important;
        }

        section[data-testid="stSidebar"] .stButton > button p {
            color: #f3f8f4 !important;
        }


        /* =========================================================
           RECENT CHAT TEXT
           ========================================================= */

        section[data-testid="stSidebar"] .recent-chat-item {
            color: #d5e3d9 !important;
        }

        section[data-testid="stSidebar"] .recent-chat-item * {
            color: inherit !important;
        }


        /* =========================================================
           LANGUAGE SELECTBOX
           ========================================================= */

        section[data-testid="stSidebar"] div[data-baseweb="select"] {
            color: #edf5ef !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] span {
            color: #edf5ef !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] input {
            color: #edf5ef !important;
        }


        /* =========================================================
           LANGUAGE MODE CARD
           ========================================================= */

        section[data-testid="stSidebar"] .language-mode-title {
            color: #e6f0e8 !important;
        }

        section[data-testid="stSidebar"] .language-mode-text {
            color: #91a99a !important;
        }


        /* =========================================================
           FOOTER
           ========================================================= */

        section[data-testid="stSidebar"] .sidebar-footer {
            color: #819889 !important;
        }

        section[data-testid="stSidebar"] .sidebar-footer strong {
            color: #a9bdaf !important;
        }
        /* Everything inside sidebar */
        section[data-testid="stSidebar"] {
            color: #e8f1eb !important;
        }


        /* Normal markdown text */
        section[data-testid="stSidebar"] p {
            color: #c9d8ce !important;
        }


        /* Headings */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] h5,
        section[data-testid="stSidebar"] h6 {
            color: #f1f7f3 !important;
        }


        /* Brand */
        section[data-testid="stSidebar"] .brand-title {
            color: #f1f7f3 !important;
        }

        section[data-testid="stSidebar"] .brand-subtitle {
            color: #9eb7a6 !important;
        }


        /* Status */
        section[data-testid="stSidebar"] .sidebar-status {
            color: #b9cdbf !important;
        }


        /* Section headings */
        section[data-testid="stSidebar"] .sidebar-section-title,
        section[data-testid="stSidebar"] .recent-chats-title,
        section[data-testid="stSidebar"] .conversation-language-title {
            color: #7fa88c !important;
        }


        /* Navigation */
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stRadio label p,
        section[data-testid="stSidebar"] .stRadio label span {
            color: #d9e6dd !important;
        }


        /* Selected navigation */
        section[data-testid="stSidebar"] .stRadio label[data-checked="true"],
        section[data-testid="stSidebar"] .stRadio label[data-checked="true"] p,
        section[data-testid="stSidebar"] .stRadio label[data-checked="true"] span {
            color: #ffffff !important;
        }


        /* Buttons */
        section[data-testid="stSidebar"] .stButton button,
        section[data-testid="stSidebar"] .stButton button p {
            color: #f4faf6 !important;
        }


        /* Recent chats */
        section[data-testid="stSidebar"] .recent-chat-item,
        section[data-testid="stSidebar"] .recent-chat-item p,
        section[data-testid="stSidebar"] .recent-chat-item span {
            color: #d5e2d9 !important;
        }


        /* Language select */
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] div[data-baseweb="select"] span,
        section[data-testid="stSidebar"] div[data-baseweb="select"] input {
            color: #edf5ef !important;
        }


        /* Language mode */
        section[data-testid="stSidebar"] .language-mode-title {
            color: #e6f0e9 !important;
        }

        section[data-testid="stSidebar"] .language-mode-text {
            color: #9fb5a6 !important;
        }


        /* Footer */
        section[data-testid="stSidebar"] .sidebar-footer {
            color: #8da493 !important;
        }

        section[data-testid="stSidebar"] .sidebar-footer strong {
            color: #b3c7b9 !important;
        }


        /* Streamlit captions */
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #8fa697 !important;
        }


        /* Any remaining markdown text */
        section[data-testid="stSidebar"] .element-container p {
            color: #c9d8ce !important;
        }


        /* Don't affect buttons */
        section[data-testid="stSidebar"] .stButton .element-container p {
            color: inherit !important;
        }

        section[data-testid="stSidebar"] {
            background: #0d241a !important;
        }

        section[data-testid="stSidebar"] .block-container {
            padding: 18px 14px 12px 14px !important;
        }


        /* ---------------------------------------------------------
           BRAND
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .brand-wrapper {
            padding: 2px 2px 14px 2px !important;
            margin-bottom: 10px !important;

            border-bottom: 1px solid #284536 !important;
        }

        section[data-testid="stSidebar"] .brand-logo {
            width: 38px !important;
            height: 38px !important;

            border-radius: 10px !important;

            background: #e8f2eb !important;

            font-size: 20px !important;
        }

        section[data-testid="stSidebar"] .brand-title {
            color: #f4f8f5 !important;

            font-size: 17px !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"] .brand-subtitle {
            color: #91aa99 !important;

            font-size: 9px !important;

            margin-top: 3px !important;
        }


        /* ---------------------------------------------------------
           ONLINE STATUS
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .sidebar-status {
            display: flex !important;

            align-items: center !important;

            margin: 7px 0 11px 0 !important;

            padding: 5px 3px !important;

            background: transparent !important;

            border: none !important;

            color: #8fa999 !important;

            font-size: 9px !important;

            line-height: 1.2 !important;
        }

        section[data-testid="stSidebar"] .sidebar-status-dot {
            width: 6px !important;
            height: 6px !important;

            background: #72c28a !important;

            box-shadow:
                0 0 0 3px rgba(114,194,138,0.10) !important;
        }


        /* ---------------------------------------------------------
           NEW CONVERSATION
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .stButton > button {
            min-height: 38px !important;

            height: 38px !important;

            padding: 6px 10px !important;

            border-radius: 9px !important;

            background: #1b4c34 !important;

            border: 1px solid #48775c !important;

            color: #f5faf6 !important;

            font-size: 12px !important;

            font-weight: 650 !important;

            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #235b3e !important;

            border-color: #659077 !important;
        }


        /* ---------------------------------------------------------
           SECTION HEADINGS
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .sidebar-section-title,
        section[data-testid="stSidebar"] .recent-chats-title,
        section[data-testid="stSidebar"] .conversation-language-title {
            margin-top: 15px !important;

            margin-bottom: 5px !important;

            padding-left: 2px !important;

            color: #78a487 !important;

            font-size: 9px !important;

            font-weight: 750 !important;

            letter-spacing: 1.2px !important;
        }


        /* ---------------------------------------------------------
           NAVIGATION
           --------------------------------------------------------- */

        /* Reduce radio container spacing */
        section[data-testid="stSidebar"] .stRadio {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        section[data-testid="stSidebar"] .stRadio > div {
            gap: 1px !important;
        }


        /* Each navigation item */
        section[data-testid="stSidebar"] .stRadio label {
            min-height: 32px !important;

            padding: 5px 7px !important;

            margin: 1px 0 !important;

            border-radius: 7px !important;

            color: #c9d8ce !important;

            font-size: 12px !important;

            transition: all 0.15s ease !important;
        }

        section[data-testid="stSidebar"] .stRadio label:hover {
            background: #163425 !important;

            color: #ffffff !important;
        }


        /* Navigation text */
        section[data-testid="stSidebar"] .stRadio label p {
            color: #c9d8ce !important;

            font-size: 12px !important;

            margin: 0 !important;
        }


        /* ---------------------------------------------------------
           REMOVE UGLY RADIO CIRCLES
           --------------------------------------------------------- */

        /* Hide Streamlit radio indicator */
        section[data-testid="stSidebar"]
        .stRadio label > div:first-child {
            display: none !important;
        }


        /* Give navigation more left alignment */
        section[data-testid="stSidebar"] .stRadio label {
            padding-left: 9px !important;
        }


        /* Selected navigation */
        section[data-testid="stSidebar"]
        .stRadio label:has(input:checked) {
            background: #1b4932 !important;

            border: 1px solid #315e45 !important;

            color: #ffffff !important;
        }

        section[data-testid="stSidebar"]
        .stRadio label:has(input:checked) p {
            color: #ffffff !important;

            font-weight: 650 !important;
        }


        /* ---------------------------------------------------------
           RECENT CHATS
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .recent-chat-item {
            min-height: 34px !important;

            padding: 7px 9px !important;

            margin: 2px 0 !important;

            border-radius: 8px !important;

            background: #173b29 !important;

            border: 1px solid #315c45 !important;

            color: #d9e7dd !important;

            font-size: 11px !important;

            line-height: 1.2 !important;
        }

        section[data-testid="stSidebar"] .recent-chat-item:hover {
            background: #1d4b34 !important;

            border-color: #4c795e !important;

            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] .recent-chat-icon {
            width: 22px !important;
            height: 22px !important;

            background: #204732 !important;

            border-radius: 6px !important;

            font-size: 11px !important;
        }


        /* ---------------------------------------------------------
           LANGUAGE SELECTOR
           --------------------------------------------------------- */

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div {
            min-height: 36px !important;

            border-radius: 8px !important;

            background: #173526 !important;

            border: 1px solid #345943 !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] span {
            color: #e4eee7 !important;

            font-size: 11px !important;
        }


        /* ---------------------------------------------------------
           LANGUAGE MODE CARD
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .language-mode-card {
            margin-top: 7px !important;

            padding: 10px !important;

            border-radius: 9px !important;

            background: #142f22 !important;

            border: 1px solid #2b4d3a !important;
        }

        section[data-testid="stSidebar"] .language-mode-title {
            color: #e7f1e9 !important;

            font-size: 11px !important;

            font-weight: 650 !important;
        }

        section[data-testid="stSidebar"] .language-mode-text {
            color: #91aa99 !important;

            font-size: 9px !important;

            line-height: 1.4 !important;
        }


        /* ---------------------------------------------------------
           FOOTER
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .sidebar-footer {
            margin-top: 12px !important;

            padding: 10px 3px 3px 3px !important;

            border-top: 1px solid #284536 !important;

            color: #7f9989 !important;

            font-size: 9px !important;

            line-height: 1.45 !important;

            text-align: center !important;
        }

        section[data-testid="stSidebar"] .sidebar-footer strong {
            color: #a8bcad !important;
        }


        /* ---------------------------------------------------------
           GENERAL SIDEBAR TEXT
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] p {
            color: #c9d8ce !important;
        }

        section[data-testid="stSidebar"] .element-container {
            color: #c9d8ce !important;
        }


        /* ---------------------------------------------------------
           SCROLLBAR
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] ::-webkit-scrollbar {
            width: 4px;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
            background: transparent;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
            background: #315440;

            border-radius: 10px;
        }
        section[data-testid="stSidebar"] {
            width: 285px !important;
            min-width: 285px !important;
            max-width: 285px !important;

            background: #0d241a !important;

            border-right: 1px solid #203e2f !important;
        }

        section[data-testid="stSidebar"] > div {
            background: #0d241a !important;
        }

        section[data-testid="stSidebar"] .block-container {
            padding: 16px 12px 12px 12px !important;
        }


        /* Remove excessive Streamlit spacing */

        section[data-testid="stSidebar"]
        [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        section[data-testid="stSidebar"]
        [data-testid="stVerticalBlockBorderWrapper"] {
            gap: 0 !important;
        }


        /* ---------------------------------------------------------
           BRAND
           --------------------------------------------------------- */

        .tribal-brand {
            padding: 2px 4px 12px 4px !important;

            margin-bottom: 8px !important;

            border-bottom: 1px solid #294637 !important;
        }

        .brand-symbol {
            width: 38px;
            height: 38px;

            display: flex;
            align-items: center;
            justify-content: center;

            margin-bottom: 6px;

            border-radius: 10px;

            background: #e8f2eb;

            font-size: 20px;

            box-shadow: 0 3px 10px rgba(0,0,0,0.12);
        }

        .brand-name {
            color: #f3f8f5 !important;

            font-size: 18px !important;

            font-weight: 700 !important;

            line-height: 1.2;

            letter-spacing: -0.2px;
        }

        .brand-subtitle {
            margin-top: 3px;

            color: #91aa99 !important;

            font-size: 9px !important;

            line-height: 1.3;
        }


        /* ---------------------------------------------------------
           ONLINE BADGE
           --------------------------------------------------------- */

        .online-badge {
            display: flex;

            align-items: center;

            gap: 6px;

            margin-top: 7px;

            color: #82a58e !important;

            font-size: 8px !important;

            font-weight: 650;

            letter-spacing: 0.8px;
        }

        .online-dot {
            width: 6px;
            height: 6px;

            display: inline-block;

            border-radius: 50%;

            background: #6fc387;

            box-shadow:
                0 0 0 3px rgba(111,195,135,0.10);
        }


        /* ---------------------------------------------------------
           NEW CONVERSATION BUTTON
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .stButton {
            margin: 0 !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100% !important;

            min-height: 38px !important;
            height: 38px !important;

            margin: 0 !important;

            padding: 5px 10px !important;

            border-radius: 9px !important;

            background: #1b4b33 !important;

            border: 1px solid #4b795e !important;

            color: #f4faf6 !important;

            font-size: 12px !important;

            font-weight: 650 !important;

            box-shadow: none !important;

            transition: all 0.15s ease !important;
        }

        section[data-testid="stSidebar"] .stButton > button p {
            color: #f4faf6 !important;

            font-size: 12px !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #225b3d !important;

            border-color: #659178 !important;

            transform: translateY(-1px);
        }


        /* ---------------------------------------------------------
           SMALL SPACER
           --------------------------------------------------------- */

        .sidebar-space-small {
            height: 9px !important;
        }


        /* ---------------------------------------------------------
           SECTION TITLES
           --------------------------------------------------------- */

        .sidebar-section-title {
            margin: 9px 2px 4px 2px !important;

            padding: 0 !important;

            color: #79a488 !important;

            font-size: 9px !important;

            font-weight: 750 !important;

            letter-spacing: 1.2px !important;

            line-height: 1.2 !important;
        }


        /* ---------------------------------------------------------
           DIVIDER
           --------------------------------------------------------- */

        .sidebar-divider {
            height: 1px !important;

            margin: 8px 2px !important;

            background: #203e2f !important;
        }


        /* ---------------------------------------------------------
           NAVIGATION RADIO
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] .stRadio {
            margin: 0 !important;

            padding: 0 !important;
        }

        section[data-testid="stSidebar"] .stRadio > div {
            gap: 1px !important;

            margin: 0 !important;

            padding: 0 !important;
        }


        /* Each navigation item */

        section[data-testid="stSidebar"] .stRadio label {
            min-height: 31px !important;

            height: 31px !important;

            display: flex !important;

            align-items: center !important;

            margin: 1px 0 !important;

            padding: 4px 8px !important;

            border-radius: 7px !important;

            color: #cbd9cf !important;

            font-size: 12px !important;

            line-height: 1 !important;

            cursor: pointer !important;

            transition: background 0.15s ease !important;
        }


        /* Text inside navigation */

        section[data-testid="stSidebar"] .stRadio label p {
            margin: 0 !important;

            padding: 0 !important;

            color: #cbd9cf !important;

            font-size: 12px !important;

            line-height: 1 !important;
        }


        /* Hover */

        section[data-testid="stSidebar"] .stRadio label:hover {
            background: #153425 !important;

            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] .stRadio label:hover p {
            color: #ffffff !important;
        }


        /* ---------------------------------------------------------
           HIDE RADIO CIRCLES
           --------------------------------------------------------- */

        section[data-testid="stSidebar"]
        .stRadio label > div:first-child {
            display: none !important;
        }


        /* Selected item */

        section[data-testid="stSidebar"]
        .stRadio label:has(input:checked) {
            background: #1a4931 !important;

            border: 1px solid #315d46 !important;

            color: #ffffff !important;
        }

        section[data-testid="stSidebar"]
        .stRadio label:has(input:checked) p {
            color: #ffffff !important;

            font-weight: 650 !important;
        }


        /* ---------------------------------------------------------
           RECENT CHATS
           --------------------------------------------------------- */

        .no-chats {
            padding: 8px 4px;

            color: #71897a !important;

            font-size: 10px;
        }


        /* Recent chat buttons */

        section[data-testid="stSidebar"]
        button[kind="secondary"] {
            font-size: 11px !important;
        }


        /*
           Only style the recent chat buttons.
           New conversation remains controlled above.
        */

        section[data-testid="stSidebar"]
        .stButton > button {
            overflow: hidden !important;
        }


        /* ---------------------------------------------------------
           LANGUAGE
           --------------------------------------------------------- */

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] {
            margin-top: 2px !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div {
            min-height: 36px !important;

            height: 36px !important;

            border-radius: 8px !important;

            background: #f4f7f5 !important;

            border: 1px solid #cbd9d0 !important;

            box-shadow: none !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] span {
            color: #263d30 !important;

            font-size: 11px !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] svg {
            fill: #263d30 !important;
        }
        
                section[data-testid="stSidebar"] {
            height: 100vh !important;
            overflow: hidden !important;
        }
        
        section[data-testid="stSidebar"] > div {
            height: 100vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }
        
        section[data-testid="stSidebar"] .block-container {
            overflow: visible !important;
        }
        
        section[data-testid="stSidebar"] div[data-baseweb="select"] {
            position: relative !important;
            z-index: 10000 !important;
        }
        

        /* ---------------------------------------------------------
           LANGUAGE MODE
           --------------------------------------------------------- */

        .language-mode,
        .language-mode.tai-mode {
            display: flex;

            align-items: center;

            gap: 9px;

            margin-top: 8px;

            padding: 9px 10px;

            border-radius: 9px;

            background: #132f22;

            border: 1px solid #2a4d3a;
        }

        .mode-icon {
            width: 27px;
            height: 27px;

            flex-shrink: 0;

            display: flex;

            align-items: center;
            justify-content: center;

            border-radius: 7px;

            background: #1d4932;

            font-size: 13px;
        }

        .mode-content {
            min-width: 0;

            flex: 1;
        }

        .mode-title {
            color: #e6f0e8 !important;

            font-size: 10.5px !important;

            font-weight: 650 !important;

            line-height: 1.2;
        }

        .mode-description {
            margin-top: 3px;

            color: #8fa99a !important;

            font-size: 8.5px !important;

            line-height: 1.25;
        }

        .mode-status {
            color: #70bd84 !important;

            font-size: 10px !important;
        }


        /* ---------------------------------------------------------
           BOTTOM AREA
           --------------------------------------------------------- */

        .sidebar-bottom {
            margin-top: 10px !important;

            padding: 10px 3px 2px 3px !important;

            border-top: 1px solid #203e2f !important;
        }

        .bottom-title {
            color: #b2c7b8 !important;

            font-size: 10px !important;

            font-weight: 650 !important;

            line-height: 1.3;
        }

        .bottom-text {
            margin-top: 3px;

            color: #718a7b !important;

            font-size: 8.5px !important;

            line-height: 1.4;
        }

        .version {
            margin-top: 5px;

            color: #526b5b !important;

            font-size: 8px !important;

            letter-spacing: 0.4px;
        }


        /* ---------------------------------------------------------
           GENERAL SIDEBAR TEXT OVERRIDE
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] p {
            color: #cbd9cf !important;
        }

        section[data-testid="stSidebar"] .element-container {
            color: #cbd9cf;
        }


        /* ---------------------------------------------------------
           SCROLLBAR
           --------------------------------------------------------- */

        section[data-testid="stSidebar"] ::-webkit-scrollbar {
            width: 4px;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
            background: transparent;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
            background: #315440;

            border-radius: 10px;
        }

        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
            background: #486d56;
        }
        /* Keep the opened language menu above everything */
        div[data-baseweb="popover"] {
            z-index: 999999 !important;
        }
        
        /* Allow the language list to contain all options */
        div[data-baseweb="popover"] div[data-baseweb="menu"] {
            max-height: 70vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }
        
        /* BaseWeb listbox */
        div[data-baseweb="popover"] [role="listbox"] {
            max-height: 70vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }
        
        /* Individual language options */
        div[data-baseweb="popover"] [role="option"] {
            min-height: 38px !important;
            white-space: nowrap !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
