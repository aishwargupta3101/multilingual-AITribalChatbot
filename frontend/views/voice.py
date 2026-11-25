"""
Tribal AI — Voice Studio
A redesigned Streamlit voice translation page.

The existing speech/translation API calls and language codes are intentionally
preserved. Styling is additive and local to the voice page.
"""
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from api.client import APIClient

# Make the project root importable when Streamlit is launched from frontend/.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.translation.meitei_script_converter import convert_bengali_to_meitei

SUPPORTED_LANGUAGES = {
    "English": "english",
    "Hindi": "hindi",
    "Manipuri": "manipuri",
    "Assamese": "assamese",
    "Bengali": "bengali",
    "Gujarati": "gujarati",
    "Kannada": "kannada",
    "Malayalam": "malayalam",
    "Marathi": "marathi",
    "Nepali": "nepali",
    "Punjabi": "punjabi",
    "Sanskrit": "sanskrit",
    "Tamil": "tamil",
    "Telugu": "telugu",
    "Urdu": "urdu",
}


def _voice_styles() -> None:
    """Inject page-specific styling without replacing the app's global theme."""
    st.markdown(
        """
        <style>
        :root {
            --voice-bg: #ffffff;
            --voice-panel: #ffffff;
            --voice-panel-2: #f4faf6;
            --voice-border: #d8e9dd;
            --voice-green: #16834a;
            --voice-green-bright: #20a65c;
            --voice-text: #173b28;
            --voice-muted: #627568;
        }

        /* Page width and typography */
        .main .block-container {
            max-width: 1280px !important;
            padding-top: 1.45rem !important;
            padding-bottom: 2.8rem !important;
        }
        .voice-page-title {
            color: var(--voice-text);
            font-size: clamp(28px, 3.4vw, 42px);
            font-weight: 820;
            line-height: 1.12;
            letter-spacing: -1.3px;
            margin: 0 0 9px 0;
        }
        .voice-page-title span { color: var(--voice-green); }
        .voice-page-subtitle {
            color: var(--voice-muted);
            font-size: 14px;
            line-height: 1.75;
            max-width: 700px;
            margin: 0;
        }
        .voice-eyebrow {
            color: var(--voice-green-bright);
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 2px;
            font-weight: 850;
            margin-bottom: 12px;
        }
        .voice-hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--voice-border);
            border-radius: 22px;
            padding: clamp(22px, 3.6vw, 38px);
            margin: 0 0 22px 0;
            background:
                radial-gradient(ellipse at 82% 0%, rgba(54, 190, 103, .18), transparent 42%),
                linear-gradient(135deg, #111d14 0%, #0b100c 76%);
            box-shadow: 0 16px 40px rgba(0,0,0,.12);
        }
        .voice-hero-mark {
            display: inline-flex;
            width: 46px; height: 46px;
            align-items: center; justify-content: center;
            border-radius: 14px;
            background: #153521;
            border: 1px solid #2f6841;
            color: #80eea2;
            font-size: 24px;
            margin-bottom: 17px;
        }
        .voice-section-title {
            color: #edf6ef;
            font-size: 18px;
            font-weight: 760;
            letter-spacing: -.35px;
            margin: 0 0 5px 0;
        }
        .voice-section-subtitle {
            color: #a8b9ac;
            font-size: 12px;
            line-height: 1.65;
            margin: 0 0 14px 0;
        }
        .voice-card {
            height: 100%;
            min-height: 104px;
            padding: 16px;
            background: linear-gradient(145deg, #121d15, #0d130f);
            border: 1px solid #2b4331;
            border-radius: 15px;
        }
        .voice-card-icon {
            width: 34px; height: 34px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 11px;
            background: #153521;
            border: 1px solid #2e6942;
            color: #67e997;
            font-size: 17px;
            margin-bottom: 11px;
        }
        .voice-card-title { color: #eef6ef; font-size: 13px; font-weight: 750; margin-bottom: 5px; }
        .voice-card-text { color: #a8b9ac; font-size: 11px; line-height: 1.65; }
        .voice-kicker {
            color: #77d997;
            font-size: 10px;
            font-weight: 850;
            letter-spacing: 1.7px;
            text-transform: uppercase;
            margin: 5px 0 10px;
        }
        .voice-status {
            display: inline-flex; align-items: center; gap: 7px;
            padding: 7px 11px; border-radius: 999px;
            border: 1px solid #2d4c36; background: #101b13;
            color: #c8ddce; font-size: 11px; font-weight: 650;
        }
        .voice-status-dot {
            width: 7px; height: 7px; border-radius: 50%;
            display: inline-block; background: #49d982;
            box-shadow: 0 0 11px rgba(73,217,130,.55);
        }
        .voice-result-card {
            background: linear-gradient(145deg, #111b14, #0c120e);
            border: 1px solid #2b4432;
            border-radius: 16px;
            padding: 17px;
            height: 100%;
        }
        .voice-result-label {
            display: flex; align-items: center; gap: 8px;
            color: #79e59a; font-size: 10px; font-weight: 850;
            letter-spacing: 1.25px; text-transform: uppercase;
            margin-bottom: 12px;
        }
        .voice-result-copy { color: #e9f2eb; font-size: 14px; line-height: 1.8; overflow-wrap: anywhere; }
        .voice-divider { border: 0; border-top: 1px solid #263b2b; margin: 22px 0; }
        .voice-footnote { color: #84988a; font-size: 10px; line-height: 1.7; }
        .voice-empty {
            text-align: center;
            border: 1px dashed #365640;
            border-radius: 16px;
            background: rgba(17, 29, 20, .72);
            padding: 17px;
            color: #a8b9ac;
            font-size: 12px;
        }

        /* Voice recorder component buttons */
        .main [data-testid="stAudioInput"],
        .main [data-testid="stAudio"] {
            border-radius: 14px !important;
        }
        .main .stButton > button,
        .main .stDownloadButton > button {
            min-height: 43px !important;
            border-radius: 11px !important;
            border: 1px solid #35533d !important;
            background: #142219 !important;
            color: #edf7ef !important;
            font-weight: 700 !important;
            transition: transform .16s ease, border-color .16s ease, background .16s ease !important;
        }
        .main .stButton > button:hover,
        .main .stDownloadButton > button:hover {
            background: #1b3423 !important;
            border-color: #4ca568 !important;
            color: #ffffff !important;
            transform: translateY(-1px);
        }
        .main .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2eaf62, #168247) !important;
            border-color: #38c370 !important;
            color: #ffffff !important;
            box-shadow: 0 6px 18px rgba(30,151,76,.17) !important;
        }
        .main .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #3acb75, #1d9952) !important;
        }

        /* Select boxes and their labels */
        .main [data-testid="stWidgetLabel"] p,
        .main label { color: #dce9df !important; font-weight: 650 !important; }
        .main [data-baseweb="select"] > div {
            background: #111b14 !important;
            border: 1px solid #35523d !important;
            border-radius: 11px !important;
            min-height: 43px;
        }
        .main [data-baseweb="select"] input,
        .main [data-baseweb="select"] div,
        .main [data-baseweb="select"] span { color: #edf6ef !important; }
        div[data-baseweb="popover"] { z-index: 999999 !important; }
        div[data-baseweb="popover"] [role="option"] { color: #183b26 !important; }

        /* Audio playback: rounded frame; native browser controls stay functional */
        .main audio { width: 100%; border-radius: 12px; }
        .main [data-testid="stAudio"] { margin-top: 6px; margin-bottom: 8px; }

        /* Status messages remain legible on dark surfaces */
        .main [data-testid="stAlert"] {
            border-radius: 12px !important;
            background: #111d14 !important;
            color: #e9f4eb !important;
            border-color: #355b3e !important;
        }
        @media (max-width: 700px) {
            .main .block-container { padding: 1rem .8rem 2rem !important; }
            .voice-hero { padding: 22px 18px; border-radius: 17px; }
            .voice-page-title { font-size: 29px; }
            .voice-card { min-height: auto; }
        }

        /* ===== Tribal AI Voice Studio: bright 3D motion layer ===== */
        .main .block-container {
            background: #ffffff !important;
            color: #20372a !important;
        }
        .voice-hero {
            color: #173b28 !important;
            background:
                radial-gradient(circle at 83% 18%, rgba(82,205,126,.17), transparent 27%),
                radial-gradient(circle at 10% 100%, rgba(104,213,145,.12), transparent 34%),
                linear-gradient(135deg,#f0fbf3 0%,#ffffff 58%,#f5fcf7 100%) !important;
            border: 1px solid #cfe5d5 !important;
            box-shadow: 0 16px 42px rgba(25,105,55,.08), inset 0 1px 0 #fff !important;
            animation: voiceHeroIn .75s cubic-bezier(.2,.75,.25,1) both;
        }
        .voice-page-title, .voice-section-title { color: #173b28 !important; }
        .voice-page-subtitle, .voice-section-subtitle,
        .voice-card-text, .voice-footnote { color: #617568 !important; }
        .voice-eyebrow, .voice-kicker { color: #16834a !important; }

        .voice-hero::after {
            content: "";
            position: absolute;
            width: 220px; height: 220px;
            right: 5%; top: -105px;
            border-radius: 50%;
            border: 1px solid rgba(39,164,83,.20);
            box-shadow: 0 0 0 14px rgba(39,164,83,.035),
                        0 0 0 30px rgba(39,164,83,.025);
            animation: voiceOrbit 16s linear infinite;
            pointer-events: none;
        }
        .voice-hero-mark {
            position: relative;
            background: linear-gradient(145deg,#ffffff,#dff5e6) !important;
            border: 1px solid #b9dfc5 !important;
            color: #16834a !important;
            box-shadow: 0 8px 0 #d9eee0, 0 15px 28px rgba(22,131,74,.14),
                        inset 0 2px 5px rgba(255,255,255,.95) !important;
            animation: voiceMarkFloat 3.8s ease-in-out infinite;
        }
        .voice-status {
            background: #ffffff !important;
            border-color: #cfe5d5 !important;
            color: #315b40 !important;
            box-shadow: 0 5px 16px rgba(22,131,74,.06);
        }
        .voice-status-dot { animation: voicePulse 1.8s ease-in-out infinite; }

        .voice-card {
            position: relative;
            overflow: hidden;
            background: linear-gradient(145deg,#ffffff,#f4faf6) !important;
            border: 1px solid #d8e9dd !important;
            border-radius: 17px !important;
            box-shadow: 0 5px 0 #e6f1e9, 0 12px 24px rgba(28,92,49,.055) !important;
            transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease !important;
            animation: voiceCardIn .65s both;
        }
        .voice-card:hover {
            transform: translateY(-6px) perspective(850px) rotateX(2deg) !important;
            border-color: #8fcba0 !important;
            box-shadow: 0 8px 0 #d8ecde, 0 20px 34px rgba(22,131,74,.13) !important;
        }
        .voice-card-icon {
            background: linear-gradient(145deg,#f0fff4,#d7f3df) !important;
            border-color: #bde2c7 !important;
            color: #16834a !important;
            box-shadow: 0 4px 0 #dcefe1, 0 7px 13px rgba(22,131,74,.08);
        }

        .voice-result-card {
            background: linear-gradient(145deg,#ffffff,#f6fbf7) !important;
            border: 1px solid #d8e9dd !important;
            box-shadow: 0 8px 22px rgba(22,91,48,.06) !important;
            animation: voiceCardIn .5s both;
        }
        .voice-result-label { color: #16834a !important; }
        .voice-result-copy { color: #263d2e !important; }
        .voice-empty {
            color: #617568 !important;
            background: linear-gradient(145deg,#ffffff,#f5fbf7) !important;
            border: 1px dashed #a9d4b5 !important;
            box-shadow: inset 0 1px 0 #fff;
        }
        .voice-divider { border-top-color: #e2eee5 !important; }

        .main .stButton > button,
        .main .stDownloadButton > button {
            color: #245438 !important;
            background: linear-gradient(145deg,#ffffff,#f2faf4) !important;
            border: 1px solid #cfe3d4 !important;
            box-shadow: 0 4px 0 #e5f0e8, 0 7px 16px rgba(22,131,74,.045) !important;
            transition: transform .2s ease, box-shadow .2s ease, background .2s ease !important;
        }
        .main .stButton > button:hover,
        .main .stDownloadButton > button:hover {
            color: #145c32 !important;
            background: #effaf2 !important;
            border-color: #86c99a !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 0 #dcefe1, 0 12px 22px rgba(22,131,74,.11) !important;
        }
        .main .stButton > button[kind="primary"] {
            background: linear-gradient(110deg,#16834a,#2caf66,#16834a) !important;
            background-size: 200% 100% !important;
            color: #ffffff !important;
            border: 1px solid #16834a !important;
            box-shadow: 0 6px 0 #d4eadb, 0 12px 23px rgba(22,131,74,.16) !important;
            animation: voiceButtonShimmer 5s linear infinite;
        }
        .main .stButton > button[kind="primary"]:hover {
            background-position: 100% 0 !important;
            transform: translateY(-3px) !important;
        }

        .main [data-testid="stWidgetLabel"] p,
        .main label { color: #315640 !important; }
        .main [data-baseweb="select"] > div {
            background: #ffffff !important;
            border: 1px solid #d4e5d9 !important;
            border-radius: 11px !important;
            box-shadow: 0 3px 10px rgba(22,91,48,.035);
        }
        .main [data-baseweb="select"] input,
        .main [data-baseweb="select"] div,
        .main [data-baseweb="select"] span { color: #294735 !important; }
        .main [data-testid="stAlert"] {
            background: #f3faf5 !important;
            color: #294735 !important;
            border: 1px solid #d5e9da !important;
        }
        .main audio { width: 100%; border-radius: 13px; }

        /* Decorative animated equalizer: visual only, does not affect recording. */
        .voice-equalizer {
            display:flex; align-items:center; justify-content:center; gap:5px;
            height:54px; margin:17px 0 2px;
        }
        .voice-equalizer span {
            display:block; width:5px; height:13px; border-radius:8px;
            background:linear-gradient(180deg,#62d98b,#16834a);
            transform-origin:center;
            animation: voiceWave 1.05s ease-in-out infinite;
            box-shadow:0 0 10px rgba(35,165,83,.18);
        }
        .voice-equalizer span:nth-child(2n) { animation-delay:.13s; }
        .voice-equalizer span:nth-child(3n) { animation-delay:.27s; }
        .voice-equalizer span:nth-child(4n) { animation-delay:.39s; }

        @keyframes voiceHeroIn {
            from { opacity:0; transform:translateY(14px); }
            to { opacity:1; transform:translateY(0); }
        }
        @keyframes voiceMarkFloat {
            0%,100% { transform:translateY(0) rotate(-3deg); }
            50% { transform:translateY(-7px) rotate(3deg); }
        }
        @keyframes voiceOrbit { to { transform:rotate(360deg); } }
        @keyframes voicePulse {
            0%,100% { box-shadow:0 0 0 0 rgba(73,190,111,.24),0 0 10px rgba(73,190,111,.35); }
            50% { box-shadow:0 0 0 7px rgba(73,190,111,0),0 0 15px rgba(73,190,111,.55); }
        }
        @keyframes voiceCardIn {
            from { opacity:0; transform:translateY(10px); }
            to { opacity:1; transform:translateY(0); }
        }
        @keyframes voiceWave {
            0%,100% { height:9px; opacity:.55; }
            50% { height:42px; opacity:1; }
        }
        @keyframes voiceButtonShimmer {
            0% { background-position:0% 50%; }
            100% { background-position:200% 50%; }
        }
        @media (prefers-reduced-motion: reduce) {
            .voice-hero, .voice-hero-mark, .voice-status-dot, .voice-card,
            .voice-equalizer span, .main .stButton > button[kind="primary"] {
                animation:none !important; transition:none !important;
            }
        }


        /* ===== Extra dimensional Voice Studio layer ===== */
        .voice-hero {
            min-height: 265px;
            transform-style: preserve-3d;
            perspective: 1000px;
            background:
                radial-gradient(circle at 50% 115%, rgba(65,196,111,.13), transparent 38%),
                radial-gradient(circle at 88% 12%, rgba(117,226,151,.24), transparent 29%),
                linear-gradient(125deg,#effbf2 0%,#ffffff 48%,#f1faf4 100%) !important;
            box-shadow:
                0 2px 0 #e0f0e4,
                0 16px 38px rgba(22,108,57,.09),
                0 28px 65px rgba(22,108,57,.045),
                inset 0 1px 0 #ffffff !important;
        }
        .voice-hero-mark {
            width: 64px !important;
            height: 64px !important;
            border-radius: 20px !important;
            font-size: 31px !important;
            transform-style: preserve-3d;
            box-shadow:
                0 7px 0 #cce8d3,
                0 13px 20px rgba(22,131,74,.17),
                inset 0 2px 5px #ffffff !important;
            animation: voiceMark3D 4s ease-in-out infinite !important;
        }
        .voice-hero-mark::after {
            content: "";
            position: absolute;
            inset: -8px;
            border: 1px solid rgba(35,160,81,.28);
            border-radius: 25px;
            transform: rotate(45deg);
            animation: voiceMarkHalo 8s linear infinite;
            pointer-events: none;
        }
        .voice-hero::before {
            content: "✦";
            position: absolute;
            right: 13%;
            top: 23%;
            color: #39b96c;
            font-size: 22px;
            text-shadow: 0 0 12px rgba(53,185,103,.55);
            animation: voiceSparkle 3.2s ease-in-out infinite;
            pointer-events: none;
        }
        .voice-hero::after {
            width: 270px !important;
            height: 270px !important;
            right: 4% !important;
            top: -125px !important;
            border: 1px solid rgba(39,164,83,.24) !important;
            box-shadow:
                0 0 0 12px rgba(39,164,83,.035),
                0 0 0 27px rgba(39,164,83,.025),
                inset 0 0 25px rgba(39,164,83,.045) !important;
            animation: voiceOrbit3D 18s linear infinite !important;
        }

        .voice-card {
            transform-style: preserve-3d;
            perspective: 900px;
            box-shadow:
                0 4px 0 #e1efe5,
                0 11px 24px rgba(28,92,49,.065),
                inset 0 1px 0 #fff !important;
        }
        .voice-card:hover {
            transform: translateY(-8px) rotateX(4deg) rotateY(-2deg) !important;
            box-shadow:
                0 8px 0 #d5eadb,
                0 23px 38px rgba(22,131,74,.15),
                inset 0 1px 0 #fff !important;
        }
        .voice-card-icon {
            width: 42px !important;
            height: 42px !important;
            border-radius: 14px !important;
            font-size: 20px !important;
            box-shadow:
                0 4px 0 #d7eddd,
                0 8px 15px rgba(22,131,74,.12) !important;
            transition: transform .3s ease !important;
        }
        .voice-card:hover .voice-card-icon {
            transform: translateY(-3px) rotate(-8deg) scale(1.08);
        }

        /* Deep layered sound stage around the decorative equalizer */
        .voice-equalizer {
            position: relative;
            height: 82px !important;
            max-width: 460px;
            margin: 19px auto 0 !important;
            padding: 0 24px;
            border: 1px solid rgba(57,166,91,.16);
            border-radius: 24px;
            background: linear-gradient(180deg,rgba(255,255,255,.65),rgba(235,249,239,.55));
            box-shadow: inset 0 2px 8px rgba(255,255,255,.9),
                        0 9px 20px rgba(27,112,58,.055);
            gap: 6px !important;
        }
        .voice-equalizer::before,
        .voice-equalizer::after {
            content: "";
            position: absolute;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #37b96a;
            box-shadow: 0 0 0 5px rgba(55,185,106,.09), 0 0 18px rgba(55,185,106,.45);
            animation: voicePulse 2s ease-in-out infinite;
        }
        .voice-equalizer::before { left: 13px; }
        .voice-equalizer::after { right: 13px; animation-delay: .8s; }
        .voice-equalizer span {
            width: 6px !important;
            border-radius: 10px !important;
            background: linear-gradient(180deg,#8ce6a7 0%,#35b96b 48%,#16834a 100%) !important;
            box-shadow: 0 0 12px rgba(35,165,83,.2), 0 3px 5px rgba(20,107,54,.12) !important;
            animation: voiceWave3D 1.15s cubic-bezier(.45,0,.55,1) infinite !important;
        }

        .voice-result-card {
            position: relative;
            overflow: hidden;
            transform-style: preserve-3d;
            box-shadow: 0 5px 0 #e5f0e8, 0 14px 28px rgba(22,91,48,.07) !important;
            transition: transform .25s ease, box-shadow .25s ease !important;
        }
        .voice-result-card:hover {
            transform: translateY(-4px) perspective(900px) rotateX(2deg);
            box-shadow: 0 8px 0 #d9ecdf, 0 20px 34px rgba(22,91,48,.12) !important;
        }
        .voice-result-card::after {
            content: "";
            position: absolute;
            top: -60%;
            left: -70%;
            width: 45%;
            height: 220%;
            transform: rotate(25deg);
            background: linear-gradient(90deg,transparent,rgba(255,255,255,.65),transparent);
            animation: voiceShine 7s ease-in-out infinite;
            pointer-events: none;
        }

        .main [data-testid="stAudioInput"] {
            border: 1px solid #cfe5d5 !important;
            border-radius: 18px !important;
            padding: 8px !important;
            background: linear-gradient(145deg,#ffffff,#f1faf4) !important;
            box-shadow: 0 5px 0 #e3f0e6, 0 12px 24px rgba(22,131,74,.07) !important;
        }
        .main .stButton > button[kind="primary"] {
            position: relative;
            overflow: hidden;
            transform: translateZ(0);
            box-shadow: 0 6px 0 #cfe8d6, 0 14px 25px rgba(22,131,74,.18) !important;
        }
        .main .stButton > button[kind="primary"]::after {
            content: "";
            position: absolute;
            top: -50%;
            left: -80%;
            width: 40%;
            height: 200%;
            background: linear-gradient(90deg,transparent,rgba(255,255,255,.35),transparent);
            transform: rotate(22deg);
            animation: voiceButtonSweep 4.5s ease-in-out infinite;
            pointer-events: none;
        }
        .main .stButton > button:active {
            transform: translateY(2px) !important;
            box-shadow: 0 2px 0 #cfe8d6 !important;
        }

        @keyframes voiceMark3D {
            0%,100% { transform: translateY(0) rotateY(-10deg) rotateX(5deg); }
            50% { transform: translateY(-9px) rotateY(12deg) rotateX(-4deg); }
        }
        @keyframes voiceMarkHalo {
            from { transform: rotate(0deg) scale(.96); }
            to { transform: rotate(360deg) scale(.96); }
        }
        @keyframes voiceOrbit3D {
            from { transform: rotate(0deg) rotateX(58deg); }
            to { transform: rotate(360deg) rotateX(58deg); }
        }
        @keyframes voiceSparkle {
            0%,100% { opacity:.35; transform:translateY(4px) scale(.75) rotate(0deg); }
            50% { opacity:1; transform:translateY(-8px) scale(1.25) rotate(35deg); }
        }
        @keyframes voiceWave3D {
            0%,100% { height:10px; filter:brightness(.92); transform:scaleY(.75); }
            50% { height:53px; filter:brightness(1.12); transform:scaleY(1); }
        }
        @keyframes voiceShine {
            0%,65% { left:-70%; }
            100% { left:140%; }
        }
        @keyframes voiceButtonSweep {
            0%,72% { left:-80%; }
            100% { left:145%; }
        }
        @media (prefers-reduced-motion: reduce) {
            .voice-hero::before, .voice-hero::after, .voice-hero-mark,
            .voice-hero-mark::after, .voice-equalizer span,
            .voice-result-card::after, .main .stButton > button[kind="primary"]::after {
                animation:none !important;
            }
        }


        /* ===== Force a fully white Voice page canvas ===== */
        html, body, .stApp,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        section.main,
        section.main > div,
        .main .block-container {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
        }
        [data-testid="stHeader"] {
            background: rgba(255,255,255,.98) !important;
        }
        [data-testid="stMain"] {
            color: #20372A !important;
        }
        .voice-hero {
            background:
                radial-gradient(circle at 83% 18%, rgba(82,205,126,.15), transparent 27%),
                radial-gradient(circle at 10% 100%, rgba(104,213,145,.10), transparent 34%),
                linear-gradient(135deg,#F0FBF3 0%,#FFFFFF 58%,#F5FCF7 100%) !important;
        }
        .voice-section-title,
        .voice-card-title,
        .voice-result-copy,
        .voice-page-title {
            color: #173B28 !important;
        }
        .voice-section-subtitle,
        .voice-card-text,
        .voice-page-subtitle,
        .voice-footnote {
            color: #627568 !important;
        }
        .voice-card {
            background: linear-gradient(145deg,#FFFFFF 0%,#F5FBF7 100%) !important;
            border-color: #D8E9DD !important;
        }
        .voice-result-card,
        .voice-empty {
            background: linear-gradient(145deg,#FFFFFF,#F6FBF7) !important;
        }
        [data-testid="stVerticalBlock"] > div {
            color: inherit;
        }


        /* Reference-matched Voice Studio layout */
        html, body, .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"],
        [data-testid="stHeader"], [data-testid="stMain"], [data-testid="stMainBlockContainer"],
        section.main, section.main > div, .main .block-container {
            background:#FFFFFF !important; background-color:#FFFFFF !important;
            color:#173B28 !important;
        }
        [data-testid="stHeader"] { background:#FFFFFF !important; }
        .main .block-container { max-width:1500px !important; padding:1.1rem 2.4rem 2.6rem !important; }
        .voice-brand-row { display:flex; align-items:center; gap:12px; margin:2px 0 18px; color:#102F20; }
        .voice-brand-icon { width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(145deg,#f5fff7,#bdeecb);border:1px solid #b8e4c5;box-shadow:0 5px 0 #d9f0df,0 9px 18px #16834a20;font-size:25px; }
        .voice-brand-name { font-size:25px;font-weight:850;letter-spacing:-.8px; }
        .voice-brand-divider { height:30px;border-left:2px solid #b9d8c2;margin:0 5px; }
        .voice-brand-product { font-size:19px;font-weight:650;color:#315d40; }
        .voice-hero-new { position:relative;display:grid;grid-template-columns:1.2fr .8fr;align-items:center;min-height:225px;padding:20px 28px 24px;margin:0 0 20px;border:0;border-radius:22px;overflow:hidden;background:radial-gradient(ellipse at 78% 45%,#d8f8e2 0%,#f4fff7 34%,transparent 65%),linear-gradient(120deg,#ffffff,#f7fcf8); }
        .voice-hero-copy { position:relative;z-index:2; }
        .voice-eyebrow { color:#16834a;font-size:10px;font-weight:900;letter-spacing:2px;margin-bottom:16px; }
        .voice-page-title { color:#102d1e !important;font-size:clamp(32px,3.4vw,48px);font-weight:900;letter-spacing:-1.6px;line-height:1.08;margin:0 0 10px; }
        .voice-page-title span { color:#159447 !important; }
        .voice-page-subtitle { color:#405f4b !important;font-size:16px;line-height:1.6;max-width:720px;margin:0 0 16px; }
        .voice-status { display:inline-flex;align-items:center;gap:8px;padding:8px 13px;border:1px solid #d2edda;border-radius:999px;background:#f4fff7;color:#28563a;font-size:11px;font-weight:750;box-shadow:0 4px 12px #16834a12; }
        .voice-status-dot { width:8px;height:8px;border-radius:50%;background:#27c66a;box-shadow:0 0 0 5px #27c66a20,0 0 12px #27c66a; }
        .voice-mic-stage { position:relative;height:215px;display:grid;place-items:center;perspective:900px; }
        .voice-mic-globe { position:relative;z-index:3;width:132px;height:132px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 30% 23%,#ffffff 0 5%,#baf8ce 12%,#54d987 32%,#12a94e 65%,#08733b 100%);border:2px solid #b5f3c8;box-shadow:inset -15px -18px 25px #00552d55,inset 8px 8px 18px #ffffffcc,0 15px 0 #d6f1de,0 24px 35px #07843c40,0 0 42px #5de58c65;animation:voiceGlobeFloat 4s ease-in-out infinite; }
        .voice-mic-globe span { color:#fff;font-size:54px;filter:drop-shadow(0 3px 3px #006b35aa); }
        .voice-mic-platform { position:absolute;z-index:2;bottom:14px;width:235px;height:35px;border-radius:50%;background:linear-gradient(180deg,#ffffff,#c9e8d2 60%,#a9d9b8);border:1px solid #c6e6cf;box-shadow:0 8px 0 #e4f3e8,0 15px 22px #16834a25; }
        .voice-orbit { position:absolute;width:255px;height:92px;border:2px solid #76d99b80;border-radius:50%;transform:rotate(-17deg);animation:voiceOrbitSpin 11s linear infinite; }
        .voice-orbit-two { width:265px;height:102px;transform:rotate(24deg);border-color:#a4e9b980;animation-duration:14s;animation-direction:reverse; }
        .voice-orbit-dot { position:absolute;z-index:4;width:13px;height:13px;border-radius:50%;background:radial-gradient(circle at 30% 25%,#fff,#35e86f 45%,#0b9a45);box-shadow:0 0 14px #42dc78; }
        .voice-dot-one { top:27px;left:25%; }.voice-dot-two { top:55px;right:19%; }
        .voice-side-wave { position:absolute;display:flex;align-items:center;gap:5px;height:90px; }
        .voice-side-left { left:0; }.voice-side-right { right:0; }
        .voice-side-wave i { display:block;width:6px;height:18px;border-radius:8px;background:linear-gradient(#8cf4ad,#18ad50);animation:voiceSideWave 1.1s ease-in-out infinite; }
        .voice-side-wave i:nth-child(2n){animation-delay:.18s}.voice-side-wave i:nth-child(3n){animation-delay:.34s}.voice-side-wave i:nth-child(4n){animation-delay:.48s}
        .voice-language-panel { margin:0 0 12px;padding:16px 22px 8px;border:1px solid #cdebd5;border-radius:20px 20px 0 0;background:linear-gradient(110deg,#f2fff5,#fff 55%,#f0fcf3); }
        .voice-step-label { display:flex;align-items:center;gap:10px;margin:0 0 8px;color:#126b37;font-size:11px;font-weight:900;letter-spacing:1.7px; }
        .voice-step-label b { display:inline-grid;place-items:center;min-width:42px;height:28px;padding:0 10px;border-radius:999px;background:linear-gradient(145deg,#21bd5e,#087b39);color:#fff;font-size:14px;letter-spacing:0;box-shadow:0 4px 0 #d5f0dc; }
        .voice-language-panel h2,.voice-capture-heading h2,.voice-results-heading h2 { color:#123923;font-size:27px;font-weight:850;letter-spacing:-.6px;margin:0 0 3px; }
        .voice-language-panel p,.voice-capture-heading p { color:#496653;font-size:14px;margin:0 0 8px; }
        .voice-select-label { color:#155d34;font-weight:800;font-size:14px;margin:0 0 5px; }
        .main [data-baseweb="select"] > div { background:#fff !important;border:1px solid #bfe4ca !important;border-radius:14px !important;min-height:54px !important;box-shadow:0 5px 0 #e3f3e7,0 9px 18px #16834a12 !important; }
        .main [data-baseweb="select"] input,.main [data-baseweb="select"] div,.main [data-baseweb="select"] span { color:#153d27 !important; }
        .main [data-testid="stWidgetLabel"] p,.main label { color:#315640 !important; }
        .voice-capture-heading { margin:24px 0 14px;padding-left:2px; }
        .voice-capture-heading .voice-step-label { margin-bottom:7px; }
        .voice-recorder-shell { min-height:128px;padding:23px 18px 14px;border:1px solid #ccebd5;border-radius:22px;background:linear-gradient(145deg,#ffffff,#f0fbf3);box-shadow:0 5px 0 #e3f1e7,0 13px 26px #16834a10; }
        .voice-recorder-shell [data-testid="stButton"] button,.voice-recorder-shell button { min-height:56px !important;border-radius:999px !important;background:linear-gradient(110deg,#12a84d,#087436) !important;color:#fff !important;border:1px solid #42d778 !important;box-shadow:0 6px 0 #cfead7,0 12px 25px #0c9a4a35 !important;font-weight:850 !important; }
        .voice-tip-panel { display:flex;align-items:center;gap:18px;min-height:128px;padding:18px;border:1px solid #ccebd5;border-radius:22px;background:linear-gradient(130deg,#fff,#e9faee);box-shadow:0 5px 0 #e2f1e6,0 13px 24px #16834a12; }
        .voice-tip-illustration { flex:0 0 90px;height:90px;display:grid;place-items:center;border-right:1px solid #bfe2c8;font-size:49px;filter:drop-shadow(0 8px 8px #16834a25); }
        .voice-tip-copy h3 { color:#123923;font-size:20px;font-weight:850;margin:0 0 7px; }
        .voice-tip-copy p { color:#45634e;font-size:13px;line-height:1.6;margin:0; }
        .voice-preview-empty { display:flex;align-items:center;gap:14px;min-height:76px;margin:18px 0 22px;padding:12px 20px;border:1px solid #bde8ca;border-radius:20px;background:linear-gradient(100deg,#fff,#effbf3);box-shadow:0 5px 0 #e3f2e7,0 11px 22px #16834a12; }
        .voice-preview-play { width:42px;height:42px;display:grid;place-items:center;border-radius:50%;color:#0c9b47;background:linear-gradient(145deg,#fff,#dff6e6);border:1px solid #bce6c8;box-shadow:0 4px 0 #d7efde,0 7px 13px #16834a20; }
        .voice-preview-empty strong { color:#173d28;white-space:nowrap; }
        .voice-preview-wave { flex:1;display:flex;align-items:center;justify-content:center;gap:4px;height:48px;overflow:hidden; }
        .voice-preview-wave i { width:4px;height:7px;border-radius:8px;background:#19b653;animation:voicePreviewWave 1.15s ease-in-out infinite; }
        .voice-preview-wave i:nth-child(3n){animation-delay:.18s}.voice-preview-wave i:nth-child(4n){animation-delay:.32s}.voice-preview-wave i:nth-child(5n){animation-delay:.48s}
        .voice-preview-time { color:#183e29;font-size:13px;white-space:nowrap;font-weight:700; }
        .voice-preview-panel { color:#17472b;font-weight:800;margin:18px 0 6px; }
        .voice-results-heading { margin-top:26px; }
        .voice-footnote { color:#6c8373 !important;border-top:1px solid #e4eee6;padding-top:16px;margin-top:25px; }
        .main .stButton > button,.main .stDownloadButton > button { background:linear-gradient(145deg,#fff,#f0faf3) !important;color:#1b5633 !important;border:1px solid #cde5d3 !important;border-radius:12px !important;box-shadow:0 4px 0 #e4f0e7,0 8px 16px #16834a0c !important; }
        .main .stButton > button[kind="primary"] { background:linear-gradient(110deg,#159b4b,#08743a) !important;color:#fff !important; }
        .main [data-testid="stAlert"] { background:#f3faf5 !important;color:#294735 !important;border:1px solid #d5e9da !important; }
        @keyframes voiceGlobeFloat {0%,100%{transform:translateY(0) rotateY(-7deg)}50%{transform:translateY(-10px) rotateY(8deg)}}
        @keyframes voiceOrbitSpin {from{rotate:0deg}to{rotate:360deg}}
        @keyframes voiceSideWave {0%,100%{height:14px;opacity:.55}50%{height:70px;opacity:1}}
        @keyframes voicePreviewWave {0%,100%{height:6px;opacity:.55}50%{height:39px;opacity:1}}
        @media(max-width:850px){.main .block-container{padding:1rem .8rem 2rem!important}.voice-hero-new{grid-template-columns:1fr;min-height:auto}.voice-mic-stage{height:175px}.voice-brand-product{font-size:14px}.voice-page-title{font-size:34px}.voice-preview-empty{flex-wrap:wrap}.voice-preview-wave{flex-basis:100%;order:3}}
        @media(prefers-reduced-motion:reduce){.voice-globe,.voice-orbit,.voice-side-wave i,.voice-preview-wave i{animation:none!important}}

        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_feature_cards() -> None:
    cols = st.columns(3, gap="medium")
    items = [
        ("↗", "Speak naturally", "Record a voice message in your chosen input language."),
        ("文", "Understand clearly", "Review the recognized words and their translation."),
        ("♫", "Listen back", "Generate and play translated speech when supported."),
    ]
    for col, (icon, title, description) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="voice-card">
                    <div class="voice-card-icon">{icon}</div>
                    <div class="voice-card-title">{title}</div>
                    <div class="voice-card-text">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_result_card(label: str, icon: str, text: str) -> None:
    # Escape transcript text before placing it inside HTML.
    import html

    st.markdown(
        f"""
        <div class="voice-result-card">
            <div class="voice-result-label"><span>{icon}</span>{label}</div>
            <div class="voice-result-copy">{html.escape(text) if text else "No text returned."}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _process_recording(audio_bytes: bytes, input_language: str, response_language: str, response_label: str) -> None:
    """Run the existing audio translation endpoint and persist its result."""
    audio_path = None
    st.session_state["voice_processing"] = True
    try:
        audio_dir = PROJECT_ROOT / "data" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=".wav",
                dir=str(audio_dir),
                delete=False,
        ) as temp_audio:
            temp_audio.write(audio_bytes)
            audio_path = temp_audio.name

        progress = st.progress(8, text="Preparing your recording…")
        try:
            progress.progress(24, text="Sending audio for speech recognition…")
            response = APIClient.translate_audio(
                audio_path=audio_path,
                input_language=input_language,
                response_language=response_language,
            )
            progress.progress(100, text="Finishing translation…")
        finally:
            # Remove the temporary progress widget after the operation.
            progress.empty()

        if not isinstance(response, dict):
            st.error("The speech service returned an unexpected response.")
            st.session_state["voice_last_status"] = "error"
            return

        if not response.get("success"):
            st.error(response.get("error", "Voice translation failed."))
            st.session_state["voice_last_status"] = "error"
            return

        transcription = str(response.get("transcription") or "").strip()
        translated_text = str(response.get("translated_text") or "").strip()

        if not transcription:
            st.warning("No speech could be recognized. Try recording a little closer to the microphone.")
            st.session_state["voice_last_status"] = "empty"
            return

        st.session_state["voice_transcription"] = transcription
        st.session_state["voice_translated_text"] = translated_text
        # Keep the original widget key separate from the processed result.
        st.session_state["voice_processed_response_language"] = response_language
        st.session_state["voice_response_label"] = response_label
        st.session_state["voice_processed_input_label"] = st.session_state.get(
            "voice_input_language", "English"
        )
        st.session_state["voice_last_status"] = "success"
        st.success("Voice translated successfully. Review the result below.")
    except Exception as exc:
        st.session_state["voice_last_status"] = "error"
        st.error(f"Voice translation failed: {exc}")
    finally:
        st.session_state["voice_processing"] = False
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass


def _render_speech_output(translated_text: str, saved_language: str, saved_label: str) -> None:
    """Preserve the current language-specific TTS behavior."""
    if not translated_text or not saved_language:
        st.info("Audio generation will be available when a translated response is returned.")
        return

    if saved_language == "manipuri":
        st.markdown('<div class="voice-kicker">Manipuri speech settings</div>', unsafe_allow_html=True)
        script_options = {
            "Bengali Script": "bengali",
            "Meitei Mayek": "meitei_mayek",
        }
        selected_script = st.selectbox(
            "Choose the output script",
            list(script_options.keys()),
            key="manipuri_tts_script",
        )

        if st.button(
                "♫  Generate Manipuri speech",
                type="primary",
                use_container_width=True,
                key="generate_manipuri_tts",
        ):
            tts_text = translated_text
            tts_script = script_options[selected_script]
            try:
                with st.spinner("Generating Manipuri speech. This may take several minutes on CPU…"):
                    if tts_script == "meitei_mayek":
                        tts_text = convert_bengali_to_meitei(translated_text)
                        if not tts_text:
                            st.error("Could not convert the translated text to Meitei Mayek.")
                            return

                    audio_bytes = APIClient.manipuri_text_to_speech(
                        text=tts_text,
                        script=tts_script,
                        speaker="female",
                    )

                if not audio_bytes:
                    st.error("Manipuri speech generation failed. Check the backend logs.")
                else:
                    st.session_state["voice_generated_audio"] = audio_bytes
                    st.session_state["voice_generated_audio_name"] = f"manipuri_{tts_script}.wav"
                    st.session_state["voice_generated_audio_mime"] = "audio/wav"
                    st.success("Manipuri speech is ready.")
            except Exception as exc:
                st.error(f"Manipuri speech generation failed: {exc}")

    else:
        if st.button(
                "♫  Generate translated speech",
                type="primary",
                use_container_width=True,
                key="generate_standard_voice",
        ):
            try:
                with st.spinner(f"Generating audio in {saved_label}…"):
                    audio_response = APIClient.text_to_speech(translated_text, saved_language)

                # The API client should return MP3 bytes. Avoid treating JSON error
                # bodies or arbitrary truthy values as playable audio.
                if isinstance(audio_response, (bytes, bytearray)) and len(audio_response) > 100:
                    audio_bytes_candidate = bytes(audio_response)
                    looks_like_mp3 = (
                            audio_bytes_candidate.startswith(b"ID3")
                            or (
                                    len(audio_bytes_candidate) > 1
                                    and audio_bytes_candidate[0] == 0xFF
                                    and (audio_bytes_candidate[1] & 0xE0) == 0xE0
                            )
                    )
                    if looks_like_mp3:
                        st.session_state["voice_generated_audio"] = audio_bytes_candidate
                        st.session_state["voice_generated_audio_name"] = f"{saved_language}_speech.mp3"
                        st.session_state["voice_generated_audio_mime"] = "audio/mpeg"
                        st.success(f"Audio generated in {saved_label}.")
                    else:
                        st.error(
                            "The TTS endpoint did not return valid MP3 audio. "
                            "Check the backend log for the provider error."
                        )
                elif isinstance(audio_response, dict):
                    st.error(audio_response.get("error", "TTS generation failed."))
                else:
                    st.error(
                        f"Audio generation failed for {saved_label}. "
                        "Check backend connectivity and the TTS provider."
                    )
            except Exception as exc:
                st.error(f"Audio generation failed: {exc}")

    audio_bytes = st.session_state.get("voice_generated_audio")
    if audio_bytes:
        st.markdown('<div class="voice-kicker">Audio player</div>', unsafe_allow_html=True)
        st.audio(
            audio_bytes,
            format=st.session_state.get("voice_generated_audio_mime", "audio/mpeg"),
        )
        st.download_button(
            "⬇  Download audio",
            data=audio_bytes,
            file_name=st.session_state.get("voice_generated_audio_name", "tribal_ai_voice.mp3"),
            mime=st.session_state.get("voice_generated_audio_mime", "audio/mpeg"),
            use_container_width=True,
            key="download_generated_voice_audio",
        )


def show_voice_page():
    """Render the redesigned Tribal AI Multilingual Voice Studio."""
    _voice_styles()

    # Keep language choices and processing state compatible with the existing workflow.
    input_label = st.session_state.get("voice_input_language", "English")
    response_label = st.session_state.get("voice_response_language", "Hindi")
    if input_label not in SUPPORTED_LANGUAGES:
        input_label = "English"
    if response_label not in SUPPORTED_LANGUAGES:
        response_label = "Hindi"

    st.markdown(
        """
        <div class="voice-brand-row">
            <div class="voice-brand-icon">🌿</div>
            <div class="voice-brand-name">Tribal AI</div>
            <div class="voice-brand-divider"></div>
            <div class="voice-brand-product">Multilingual Voice Studio</div>
        </div>
        <section class="voice-hero-new">
            <div class="voice-hero-copy">
                <div class="voice-eyebrow">TRIBAL AI · MULTILINGUAL VOICE STUDIO</div>
                <h1 class="voice-page-title">Your voice. <span>Your language.</span></h1>
                <p class="voice-page-subtitle">
                    Speak naturally, translate across supported languages, and listen to your message.
                </p>
                <div class="voice-status"><span class="voice-status-dot"></span> Voice assistant ready</div>
            </div>
            <div class="voice-mic-stage" aria-hidden="true">
                <div class="voice-orbit voice-orbit-one"></div>
                <div class="voice-orbit voice-orbit-two"></div>
                <div class="voice-orbit-dot voice-dot-one"></div>
                <div class="voice-orbit-dot voice-dot-two"></div>
                <div class="voice-mic-globe"><span>🎙</span></div>
                <div class="voice-mic-platform"></div>
                <div class="voice-side-wave voice-side-left">
                    <i></i><i></i><i></i><i></i><i></i><i></i><i></i>
                </div>
                <div class="voice-side-wave voice-side-right">
                    <i></i><i></i><i></i><i></i><i></i><i></i><i></i>
                </div>
            </div>
        </section>

        <section class="voice-language-panel">
            <div class="voice-step-label"><b>01</b><span>SET UP YOUR CONVERSATION</span></div>
            <h2>Choose your languages</h2>
            <p>Select the language you will speak and the language you want Tribal AI to respond in.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    language_col, response_col = st.columns(2, gap="large")
    with language_col:
        st.markdown('<div class="voice-select-label">🎙 &nbsp; Speak in</div>', unsafe_allow_html=True)
        input_label = st.selectbox(
            "Speak in",
            list(SUPPORTED_LANGUAGES.keys()),
            key="voice_input_language",
            label_visibility="collapsed",
        )
    with response_col:
        st.markdown('<div class="voice-select-label">文 &nbsp; Translate to</div>', unsafe_allow_html=True)
        response_label = st.selectbox(
            "Translate to",
            list(SUPPORTED_LANGUAGES.keys()),
            index=list(SUPPORTED_LANGUAGES.keys()).index("Hindi"),
            key="voice_response_language",
            label_visibility="collapsed",
        )

    input_language = SUPPORTED_LANGUAGES[input_label]
    response_language = SUPPORTED_LANGUAGES[response_label]

    st.markdown(
        """
        <div class="voice-capture-heading">
            <div class="voice-step-label"><b>02</b><span>VOICE CAPTURE</span></div>
            <h2>Speak when you’re ready</h2>
            <p>Allow microphone access, start recording, and stop when you have finished speaking.
            You can listen to the recording before translating it.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    recorder_col, guide_col = st.columns([1.6, 1], gap="large")
    with recorder_col:
        st.markdown('<div class="voice-recorder-shell">', unsafe_allow_html=True)
        audio = mic_recorder(
            start_prompt="🎙  Start recording",
            stop_prompt="⏹  Stop recording",
            just_once=False,
            use_container_width=True,
            format="wav",
            key="voice_component_recorder",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with guide_col:
        st.markdown(
            """
            <div class="voice-tip-panel">
                <div class="voice-tip-illustration">💡</div>
                <div class="voice-tip-copy">
                    <h3>A quick recording tip</h3>
                    <p>Speak clearly and keep your device close enough to capture your voice.
                    Reduce background noise for more reliable transcription.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    audio_bytes = audio.get("bytes") if isinstance(audio, dict) else None

    if audio_bytes:
        st.markdown(
            '<div class="voice-preview-panel"><div class="voice-preview-title">▶ &nbsp; Recording preview</div></div>',
            unsafe_allow_html=True,
        )
        st.audio(audio_bytes, format="audio/wav")
        st.caption(f"Ready to process · {input_label} → {response_label}")

        if st.button(
                "🌿  Translate my voice",
                type="primary",
                use_container_width=True,
                key="component_process_voice",
        ):
            _process_recording(
                audio_bytes=audio_bytes,
                input_language=input_language,
                response_language=response_language,
                response_label=response_label,
            )
    else:
        st.markdown(
            """
            <div class="voice-preview-empty">
                <span class="voice-preview-play">▶</span>
                <strong>Recording preview</strong>
                <div class="voice-preview-wave">
                    <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
                    <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
                    <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
                </div>
                <span class="voice-preview-time">00:00 / 00:00</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    transcription = st.session_state.get("voice_transcription", "")
    translated_text = st.session_state.get("voice_translated_text", "")
    saved_language = st.session_state.get("voice_processed_response_language", "")
    saved_label = st.session_state.get("voice_response_label", "")
    if transcription:
        st.markdown(
            '<div class="voice-results-heading"><div class="voice-step-label"><b>03</b><span>YOUR RESULTS</span></div><h2>Your voice, understood</h2></div>',
            unsafe_allow_html=True)
        st.markdown(
            '<p class="voice-section-subtitle">Review the recognized speech, compare the translation, and generate audio when the selected language is supported.</p>',
            unsafe_allow_html=True,
        )
        result_col, translated_col = st.columns(2, gap="medium")
        with result_col:
            _render_result_card("Original transcription", "✎", transcription)
        with translated_col:
            _render_result_card(f"Translated response · {saved_label or 'Target language'}", "文", translated_text)
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        _render_speech_output(translated_text, saved_language, saved_label)

    st.markdown(
        """
        <div class="voice-footnote">
            🌿 TRIBAL AI &nbsp;·&nbsp; PRESERVING KNOWLEDGE, CONNECTING CULTURES<br>
            Speech recognition, translation, and audio generation depend on the selected language
            and the capabilities configured in your backend.
        </div>
        """,
        unsafe_allow_html=True,
    )
