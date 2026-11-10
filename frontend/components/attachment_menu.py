
"""
Tribal AI Chatbot - Compact Plus Tools Menu.

Design:
- Soft sage-green plus button
- Dark forest-green plus symbol
- Compact floating Tools popup
- Two-column tool layout
- Existing workspace navigation preserved
"""

import streamlit as st


def _navigate(page_name: str) -> None:
    """Navigate to an existing Tribal AI workspace."""
    st.session_state.selected_page = page_name
    st.session_state.sidebar_navigation = "💬 Chat"


def render_plus_menu() -> None:
    """Render the compact floating Tools menu."""

    st.markdown(
        """
        <style>
        /* PLUS TRIGGER: scoped to this menu only.
           Use descendant selectors because Streamlit may add wrapper
           elements between the popover container and its trigger button. */
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button {
            background: #DCEFE2 !important;
            background-color: #DCEFE2 !important;
            background-image: none !important;
            color: #245B3B !important;
            border: 1px solid #A9CEB5 !important;
            border-radius: 11px !important;
            width: 48px !important;
            min-width: 48px !important;
            height: 42px !important;
            min-height: 42px !important;
            padding: 0 !important;
            opacity: 1 !important;
            box-shadow: 0 2px 6px rgba(36, 91, 59, 0.08) !important;
            filter: none !important;
        }

        /* Dark forest-green plus and chevron */
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button,
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button p,
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button span,
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button svg,
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button svg path {
            color: #245B3B !important;
            fill: #245B3B !important;
            stroke: #245B3B !important;
            -webkit-text-fill-color: #245B3B !important;
            opacity: 1 !important;
        }

        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button p,
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button span {
            font-size: 21px !important;
            font-weight: 700 !important;
        }

        /* Gentle hover */
        div[class*="st-key-tribal_plus_menu"] [data-testid="stPopover"] button:hover {
            background: #CDE6D5 !important;
            background-color: #CDE6D5 !important;
            border-color: #8FBE9D !important;
            box-shadow: 0 3px 8px rgba(36, 91, 59, 0.12) !important;
        }

        div[data-testid="stPopoverBody"] {
            width: 340px !important;
            max-width: min(340px, calc(100vw - 30px)) !important;

            padding: 16px !important;

            background: #ffffff !important;

            border: 1px solid #d6e5da !important;
            border-radius: 16px !important;

            box-shadow: 0 10px 32px rgba(0, 0, 0, 0.12) !important;
        }
        div[data-testid="stPopoverBody"] .tools-heading {
            color: #173e29 !important;

            font-size: 17px !important;
            font-weight: 750 !important;

            margin: 0 0 3px 0 !important;
        }

        div[data-testid="stPopoverBody"] .tools-subheading {
            color: #607568 !important;

            font-size: 12px !important;
            margin-bottom: 12px !important;
        }


        /* =====================================
           TOOL BUTTONS
           ===================================== */

        div[data-testid="stPopoverBody"]
        div[data-testid="stButton"] button {
            width: 100% !important;
            min-height: 46px !important;

            background: #F7FBF8 !important;
            color: #173E29 !important;

            border: 1px solid #D7E5DB !important;
            border-radius: 11px !important;

            box-shadow: none !important;
            opacity: 1 !important;

            font-size: 13px !important;
            font-weight: 600 !important;
        }

        /* Keep tool names readable */

        div[data-testid="stPopoverBody"]
        div[data-testid="stButton"] button p,
        div[data-testid="stPopoverBody"]
        div[data-testid="stButton"] button span {
            color: #173E29 !important;

            -webkit-text-fill-color: #173E29 !important;

            opacity: 1 !important;
            font-size: 13px !important;
            white-space: normal !important;
        }

        /* Tool hover */

        div[data-testid="stPopoverBody"]
        div[data-testid="stButton"] button:hover {
            background: #EAF5ED !important;
            border-color: #80B491 !important;
        }

        /* Column spacing */

        div[data-testid="stPopoverBody"]
        [data-testid="stHorizontalBlock"] {
            gap: 10px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="tribal_plus_menu"):

        with st.popover(
            "＋",
            help="Open Tribal AI tools",
            use_container_width=False,
        ):

            st.markdown(
                """
                <div class="tools-heading">🧰 Tools</div>
                <div class="tools-subheading">
                    Choose a workspace
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2, gap="small")

            with col1:
                st.button(
                    "📄 Documents",
                    key="plus_open_documents",
                    use_container_width=True,
                    on_click=_navigate,
                    args=("📄 Documents",),
                )

            with col2:
                st.button(
                    "🎤 Voice",
                    key="plus_open_voice",
                    use_container_width=True,
                    on_click=_navigate,
                    args=("🎤 Voice",),
                )
            col1, col2 = st.columns(2, gap="small")

            with col1:
                st.button(
                    "🎓 Video Learning",
                    key="plus_open_video_learning",
                    use_container_width=True,
                    on_click=_navigate,
                    args=("🎓 Video Learning",),
                )

            with col2:
                st.button(
                    "🌿 Education",
                    key="plus_open_education",
                    use_container_width=True,
                    on_click=_navigate,
                    args=("🌿 Education Assistant",),
                )
            st.button(
                "📊 Presentation Generator",
                key="plus_open_presentation",
                use_container_width=True,
                on_click=_navigate,
                args=("📊 Presentation Generator",),
            )
