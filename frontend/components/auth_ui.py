import os
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st

_COOKIE_MANAGER = None


def _api_base() -> str:
    base = (
        os.getenv("BACKEND_URL")
        or os.getenv("TRIBAL_API_BASE_URL")
        or "http://localhost:8000"
    )
    return base.rstrip("/")


def _request(
    path: str,
    payload: dict | None = None,
    token: str | None = None,
    method: str = "POST",
):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.request(
            method,
            f"{_api_base()}{path}",
            json=payload if method.upper() != "GET" else None,
            headers=headers,
            timeout=25,
        )
        data = response.json() if response.content else {}
        if not response.ok:
            detail = data.get("detail", "Authentication request failed")
            if response.status_code in (401, 403):
                return None
            st.error(detail)
            return None
        return data
    except requests.RequestException:
        st.error("Cannot reach Tribal AI backend. Please try again shortly.")
        return None


def _cookie_manager():
    """Create the encrypted browser-cookie manager for this Streamlit session."""
    global _COOKIE_MANAGER
    try:
        from streamlit_cookies_manager import EncryptedCookieManager
    except ImportError:
        st.error(
            "Persistent sign-in needs streamlit-cookies-manager. "
            "Install it using: pip install streamlit-cookies-manager"
        )
        st.stop()

    cookie_password = (
        os.getenv("COOKIE_PASSWORD")
        or os.getenv("AUTH_SECRET_KEY")
        or ""
    )
    if len(cookie_password) < 16:
        st.error(
            "Set COOKIE_PASSWORD (at least 16 characters) or a strong "
            "AUTH_SECRET_KEY in your .env file."
        )
        st.stop()

    manager = EncryptedCookieManager(
        prefix="tribal_ai/",
        password=cookie_password,
    )
    if not manager.ready():
        st.info("Preparing your secure sign-in session…")
        st.stop()

    _COOKIE_MANAGER = manager
    return manager


def _persist_token(token: str):
    if _COOKIE_MANAGER is not None:
        _COOKIE_MANAGER["auth_token"] = token
        _COOKIE_MANAGER.save()


def _clear_persisted_token():
    """Persist an empty token so a fast rerun cannot restore the old session."""
    if _COOKIE_MANAGER is not None:
        try:
            # Setting an empty value is more robust than deleting the key while
            # the browser cookie component is syncing its updated cookie state.
            _COOKIE_MANAGER["auth_token"] = ""
            _COOKIE_MANAGER.save()
        except Exception:
            pass


def _set_session(data: dict):
    token = data.get("access_token")
    user = data.get("user")
    if not token or not user:
        st.error("The authentication server returned an incomplete response.")
        return
    st.session_state["auth_token"] = token
    st.session_state["auth_user"] = user
    st.session_state["authenticated"] = True
    _persist_token(token)
    st.rerun()


def _restore_session(cookies) -> bool:
    """Restore a browser-persisted token and validate it against FastAPI."""
    token = cookies.get("auth_token")
    if not token:
        return False

    result = _request("/api/v1/auth/me", token=token, method="GET")
    if not result or not result.get("user"):
        _clear_persisted_token()
        return False

    st.session_state["auth_token"] = token
    st.session_state["auth_user"] = result["user"]
    st.session_state["authenticated"] = True
    return True


def _google_sign_in():
    """
    Always render the Google sign-in button on the login screen.
    The explicit click starts OIDC; a returned ID token is then exchanged
    with FastAPI for a Tribal AI session.
    """
    if st.button(
        "🌐  Continue with Google",
        key="tribal_google_login",
        use_container_width=True,
    ):
        # A new explicit login attempt must not be suppressed by the previous
        # Google token's processed marker.
        st.session_state.pop("_google_id_token_processed", None)
        try:
            st.login()
        except Exception as exc:
            st.error(
                "Google sign-in could not start. Check the [auth] settings "
                f"in .streamlit/secrets.toml. Details: {exc}"
            )
        return

    try:
        google_logged_in = bool(st.user.is_logged_in)
    except Exception:
        google_logged_in = False

    if not google_logged_in:
        return

    try:
        id_token = st.user.tokens["id"]
    except Exception:
        id_token = None

    if not id_token:
        st.error(
            'Google sign-in succeeded, but the ID token is unavailable. '
            'Check expose_tokens = "id" in .streamlit/secrets.toml.'
        )
        return

    # Do not exchange the same Google identity repeatedly on ordinary reruns.
    if st.session_state.get("_google_id_token_processed") == id_token:
        return

    result = _request("/api/v1/auth/google", {"id_token": id_token})
    if result:
        st.session_state["_google_id_token_processed"] = id_token
        _set_session(result)


def _auth_styles():
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        .stApp, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(ellipse at 15% 15%, rgba(34,197,94,.18), transparent 35%),
                radial-gradient(ellipse at 85% 82%, rgba(20,184,166,.15), transparent 34%),
                linear-gradient(135deg, #06130e 0%, #0a2118 48%, #071711 100%) !important;
            color: #effcf3 !important;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        .main .block-container {
            width: min(100% - 3rem, 1420px) !important;
            max-width: 1420px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 2.5rem 1.5rem 3rem !important;
            overflow-x: hidden !important;
            box-sizing: border-box !important;
        }
        [data-testid="stHorizontalBlock"] { gap: clamp(2rem, 5vw, 5rem) !important; }
        [data-testid="stColumn"] { min-width: 0 !important; }
        .main .block-container p, .main .block-container label { overflow-wrap: anywhere; }
        .ta-auth-shell { min-height: 82vh; display:flex; align-items:center; }
        .ta-auth-kicker {
            display:inline-flex; align-items:center; gap:8px;
            border:1px solid rgba(134,239,172,.25);
            background:rgba(20,83,45,.30); color:#a7f3c0;
            padding:7px 12px; border-radius:999px; font-size:12px;
            letter-spacing:.08em; text-transform:uppercase;
        }
        .ta-auth-title {
            color:#f0fdf4 !important; font-size:clamp(2.35rem,4.2vw,3.8rem) !important;
            line-height:1.08 !important; letter-spacing:-.045em !important;
            font-weight:850 !important; margin:.9rem 0 .8rem !important;
            max-width:100% !important; overflow-wrap:normal !important;
            word-break:normal !important; padding-left:2px !important;
        }
        .ta-auth-gradient {
            background:linear-gradient(90deg,#86efac,#5eead4 65%,#d9f99d);
            -webkit-background-clip:text; background-clip:text; color:transparent;
        }
        .ta-auth-copy { color:#a7bdb0 !important; font-size:1rem; line-height:1.7; max-width:480px; }
        .ta-auth-points { display:flex; flex-wrap:wrap; gap:9px; margin-top:22px; }
        .ta-auth-pill {
            border:1px solid rgba(167,243,208,.16); background:rgba(15,45,31,.55);
            color:#c8e8d3; padding:8px 11px; border-radius:10px; font-size:12px;
        }
        .ta-orb-stage {
            position:relative; height:340px; width:100%; display:flex;
            align-items:center; justify-content:center; perspective:900px;
            isolation:isolate; margin:8px 0 0;
        }
        .ta-orb-glow {
            position:absolute; width:230px; height:230px; border-radius:50%;
            background:radial-gradient(circle,rgba(74,222,128,.27),rgba(45,212,191,.08) 48%,transparent 72%);
            filter:blur(12px); animation:ta-breathe 4s ease-in-out infinite;
        }
        .ta-orb {
            position:relative; width:178px; height:178px; border-radius:50%;
            transform-style:preserve-3d; animation:ta-float 6s ease-in-out infinite;
            background:
                radial-gradient(circle at 30% 24%,rgba(236,253,245,.98) 0 2%,rgba(167,243,208,.9) 5%,transparent 18%),
                radial-gradient(circle at 36% 30%,#5eead4 0%,#22c55e 22%,#087f5b 49%,#064e3b 70%,#03251c 100%);
            box-shadow:inset -18px -22px 42px rgba(0,0,0,.55),
                       inset 12px 12px 26px rgba(236,253,245,.25),
                       0 0 38px rgba(34,197,94,.28),0 0 100px rgba(20,184,166,.13);
        }
        .ta-orb:before,.ta-orb:after {
            content:""; position:absolute; inset:-18px; border:1px solid rgba(167,243,208,.38);
            border-radius:50%; transform:rotateX(68deg) rotateZ(-22deg);
            box-shadow:0 0 18px rgba(94,234,212,.12);
        }
        .ta-orb:after { inset:-32px; transform:rotateY(67deg) rotateZ(24deg); border-color:rgba(134,239,172,.24); }
        .ta-orb-core {
            position:absolute; width:28px; height:28px; border-radius:50%;
            left:calc(50% - 14px); top:calc(50% - 14px);
            background:#ecfdf5; box-shadow:0 0 18px #a7f3d0,0 0 48px #34d399;
        }
        .ta-orb-node {
            position:absolute; width:11px; height:11px; border-radius:50%;
            background:#a7f3d0; box-shadow:0 0 18px #5eead4;
        }
        .ta-orb-node.n1 { top:13%; left:22%; animation:ta-pulse 2.8s infinite; }
        .ta-orb-node.n2 { right:12%; top:43%; animation:ta-pulse 3.4s .4s infinite; }
        .ta-orb-node.n3 { bottom:13%; left:35%; animation:ta-pulse 3s .8s infinite; }
        .ta-orb-caption {
            position:absolute; bottom:3px; color:#86a995; font-size:11px;
            letter-spacing:.22em; text-transform:uppercase;
        }
        @keyframes ta-float {
            0%,100% { transform:translateY(0) rotateX(-8deg) rotateY(12deg); }
            50% { transform:translateY(-16px) rotateX(8deg) rotateY(-12deg); }
        }
        @keyframes ta-breathe { 0%,100% { transform:scale(.9); opacity:.65; } 50% { transform:scale(1.12); opacity:1; } }
        @keyframes ta-pulse { 0%,100% { transform:scale(.75); opacity:.5; } 50% { transform:scale(1.35); opacity:1; } }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap:10px !important; border-bottom:1px solid rgba(167,243,208,.20) !important;
        }
        /* Authentication view switch buttons (Sign in / Create account). */
        div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
            color:#e5f7eb !important;
            -webkit-text-fill-color:#e5f7eb !important;
            background:#123323 !important;
            border:1px solid rgba(167,243,208,.28) !important;
            font-weight:800 !important;
            opacity:1 !important;
            border-radius:10px !important;
        }
        div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button *,
        div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button p {
            color:#e5f7eb !important;
            -webkit-text-fill-color:#e5f7eb !important;
            opacity:1 !important;
        }
        div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] {
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            background:linear-gradient(100deg,#15803d,#0f766e) !important;
            border:1px solid #4ade80 !important;
        }
        div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] *,
        div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] p {
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
        }
        div[data-testid="stForm"] {
            background:rgba(8,31,21,.88) !important;
            border:1px solid rgba(167,243,208,.24) !important;
            border-radius:18px !important; padding:22px !important;
            box-shadow:0 24px 70px rgba(0,0,0,.30),inset 0 1px rgba(255,255,255,.05) !important;
            backdrop-filter:blur(18px);
        }
        div[data-testid="stWidgetLabel"] p,
        div[data-testid="stTextInput"] label,
        div[data-testid="stForm"] label,
        .main label {
            color:#e5f7eb !important; opacity:1 !important;
            font-weight:600 !important;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stForm"] input,
        div[data-baseweb="input"] input,
        .main input {
            background:#102b1e !important;
            background-color:#102b1e !important;
            color:#f0fdf4 !important;
            -webkit-text-fill-color:#f0fdf4 !important;
            caret-color:#86efac !important;
            border:1px solid rgba(167,243,208,.34) !important;
            border-radius:10px !important;
            opacity:1 !important;
        }
        div[data-testid="stTextInput"] input::placeholder,
        div[data-baseweb="input"] input::placeholder {
            color:#a8c4b2 !important;
            -webkit-text-fill-color:#a8c4b2 !important;
            opacity:1 !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-baseweb="input"] input:focus {
            border-color:#4ade80 !important;
            box-shadow:0 0 0 1px #4ade80 !important;
        }
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stForm"] button[kind="primary"],
        div[data-testid="stForm"] button[kind="secondary"] {
            min-height:46px !important; border-radius:11px !important;
            border:1px solid #4ade80 !important;
            background:linear-gradient(100deg,#15803d,#0f766e) !important;
            background-color:#15803d !important;
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            font-weight:800 !important;
            opacity:1 !important;
            box-shadow:0 8px 24px rgba(22,163,74,.22) !important;
            transition:transform .2s ease,filter .2s ease;
        }
        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stForm"] button p {
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            font-weight:800 !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            transform:translateY(-2px); filter:brightness(1.12);
        }
        div[data-testid="stAlert"] p, .main [data-testid="stMarkdownContainer"] p {
            color:#d2e8da;
        }
        .ta-auth-foot { color:#a9c6b4 !important; text-align:center; font-size:11px; margin-top:18px; }
        @media(max-width:850px) {
            .ta-orb-stage { height:220px; }
            .ta-orb { width:125px; height:125px; }
            .ta-auth-title { font-size:2.5rem !important; }
        }
        /* High-contrast logout button only when rendered as the sidebar's primary button. */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background:linear-gradient(100deg,#22c55e,#0f9f75) !important;
            color:#052014 !important; border:1px solid #86efac !important;
            font-weight:800 !important; border-radius:10px !important;
            box-shadow:0 5px 18px rgba(34,197,94,.18) !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
            background:linear-gradient(100deg,#4ade80,#2dd4bf) !important;
            color:#052014 !important; transform:translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_auth_screen():
    _auth_styles()

    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown(
            """
            <div style="padding:2.2rem .5rem .5rem">
              <div class="ta-auth-kicker">🌿 &nbsp; MULTILINGUAL INTELLIGENCE</div>
              <h1 class="ta-auth-title">Welcome to<br><span class="ta-auth-gradient">Tribal AI.</span></h1>
              <p class="ta-auth-copy">
                One intelligent workspace for conversation, learning and
                knowledge — built to connect languages, people and ideas.
              </p>
              <div class="ta-auth-points">
                <span class="ta-auth-pill">✦ Multilingual AI</span>
                <span class="ta-auth-pill">◈ Knowledge assistant</span>
                <span class="ta-auth-pill">⌘ Learning workspace</span>
              </div>
            </div>
            <div class="ta-orb-stage" aria-hidden="true">
              <div class="ta-orb-glow"></div>
              <div class="ta-orb">
                <div class="ta-orb-core"></div>
                <i class="ta-orb-node n1"></i><i class="ta-orb-node n2"></i><i class="ta-orb-node n3"></i>
              </div>
              <div class="ta-orb-caption">Intelligence in every language</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div style="padding:.8rem 0 .7rem">
              <div style="color:#86efac;font-size:11px;letter-spacing:.18em;font-weight:800">YOUR AI WORKSPACE</div>
              <h2 style="color:#f0fdf4;font-size:1.8rem;margin:.45rem 0 .3rem">Sign in to continue</h2>
              <p style="color:#c4d8cb;font-size:13px;margin:0">Access your Tribal AI workspace securely.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Use ordinary Streamlit buttons instead of st.tabs. This avoids the
        # BaseWeb tab text styling that remained black in some Streamlit themes.
        if "auth_view" not in st.session_state:
            st.session_state["auth_view"] = "signin"

        tab_a, tab_b = st.columns(2, gap="small")
        with tab_a:
            if st.button(
                "Sign in",
                key="auth_view_signin",
                use_container_width=True,
                type="primary" if st.session_state["auth_view"] == "signin" else "secondary",
            ):
                st.session_state["auth_view"] = "signin"
                st.rerun()
        with tab_b:
            if st.button(
                "Create account",
                key="auth_view_register",
                use_container_width=True,
                type="primary" if st.session_state["auth_view"] == "register" else "secondary",
            ):
                st.session_state["auth_view"] = "register"
                st.rerun()

        if st.session_state["auth_view"] == "signin":
            with st.form("tribal_login_form", clear_on_submit=False):
                email = st.text_input("Email", key="auth_login_email")
                password = st.text_input("Password", type="password", key="auth_login_password")
                submitted = st.form_submit_button("Sign in to Tribal AI", use_container_width=True)
            if submitted:
                if not email.strip() or not password:
                    st.warning("Enter your email and password.")
                else:
                    result = _request(
                        "/api/v1/auth/login",
                        {"email": email.strip(), "password": password},
                    )
                    if result:
                        _set_session(result)
            st.markdown(
                "<div class='ta-auth-foot'>Protected workspace · Your session stays on this device</div>",
                unsafe_allow_html=True,
            )
            _google_sign_in()

        else:
            with st.form("tribal_register_form", clear_on_submit=False):
                name = st.text_input("Full name", key="auth_register_name")
                email = st.text_input("Email address", key="auth_register_email")
                password = st.text_input(
                    "Password (minimum 8 characters)",
                    type="password",
                    key="auth_register_password",
                )
                confirm = st.text_input(
                    "Confirm password",
                    type="password",
                    key="auth_register_confirm",
                )
                submitted = st.form_submit_button("Create your account", use_container_width=True)
            if submitted:
                if not name.strip() or not email.strip() or not password:
                    st.warning("Complete all fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")
                else:
                    result = _request(
                        "/api/v1/auth/register",
                        {"name": name.strip(), "email": email.strip(), "password": password},
                    )
                    if result:
                        _set_session(result)
            st.markdown(
                "<div class='ta-auth-foot'>Create one account to access your workspace</div>",
                unsafe_allow_html=True,
            )
            _google_sign_in()


def require_authentication() -> bool:
    cookies = _cookie_manager()

    # Skip one restoration attempt immediately after logout. This prevents
    # the cookie manager's stale in-memory value from re-authenticating the user.
    if st.session_state.pop("_skip_auth_restore_once", False):
        show_auth_screen()
        return False

    if st.session_state.get("authenticated") and st.session_state.get("auth_token"):
        return True

    if _restore_session(cookies):
        return True

    show_auth_screen()
    return False



def show_user_logout():
    user = st.session_state.get("auth_user") or {}
    if not user:
        return

    display_name = user.get("name") or user.get("email") or "User"
    st.sidebar.markdown(
        f"<div style='color:#b9d5c2;font-size:11px;padding:8px 2px 4px'>"
        f"Signed in as <strong style='color:#f0fdf4'>{display_name}</strong></div>",
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "↪  Log out",
        key="tribal_logout_button",
        type="primary",
        use_container_width=True,
    ):
        was_google_user = (user.get("auth_provider") == "google")

        _clear_persisted_token()
        for key in ("auth_token", "auth_user", "authenticated"):
            st.session_state.pop(key, None)

        st.session_state["_skip_auth_restore_once"] = True

        if was_google_user:
            try:
                st.logout()
            except Exception:
                st.rerun()
        else:
            st.rerun()
