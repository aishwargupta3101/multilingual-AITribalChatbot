import streamlit as st
from html import escape


def _navigate(page: str) -> None:
    """Keep the existing Streamlit page router and sidebar state in sync."""
    st.session_state["main_navigation"] = page
    st.session_state["selected_page"] = page


def _open_chat() -> None:
    _navigate("💬 Chat")


def _open_voice() -> None:
    _navigate("🎤 Voice")


def _open_chapter_learning() -> None:
    _navigate("📘 Chapter Learning")


def show_home() -> None:
    """Tribal AI landing page inspired by the supplied emerald dashboard reference."""
    language = escape(
        str(st.session_state.get("language", "english"))
        .replace("_", " ")
        .title()
    )

    st.markdown(
        r"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

        /* Everything is scoped to this page; the app's native sidebar is untouched. */
        .tribal-ref-home {
            --mint: #72f5a4;
            --mint2: #36df7e;
            --line: rgba(78, 218, 131, .42);
            color: #effff3;
            font-family: 'DM Sans', sans-serif;
            position: relative;
            isolation: isolate;
            padding: 8px 0 22px;
        }
        .tribal-ref-home * { box-sizing: border-box; }

        @keyframes tr-aurora {
            0% { transform: translate3d(-2%, 0, 0) scale(1); opacity: .48; }
            100% { transform: translate3d(3%, 2%, 0) scale(1.08); opacity: .82; }
        }
        @keyframes tr-twinkle {
            0%,100% { opacity: .18; transform: scale(.72); }
            50% { opacity: .95; transform: scale(1.25); }
        }
        @keyframes tr-float {
            0%,100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        @keyframes tr-beam {
            0% { transform: translateX(-125%) skewX(-18deg); opacity: 0; }
            20% { opacity: .65; }
            75% { opacity: .4; }
            100% { transform: translateX(230%) skewX(-18deg); opacity: 0; }
        }
        @keyframes tr-rise {
            from { opacity: 0; transform: translateY(18px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes tr-pulse {
            0%,100% { box-shadow: 0 0 12px rgba(55,235,129,.16); }
            50% { box-shadow: 0 0 30px rgba(55,235,129,.42); }
        }
        @keyframes tr-wave {
            0%,100% { transform: scaleY(.72); opacity: .58; }
            50% { transform: scaleY(1.08); opacity: 1; }
        }

        .tr-hero {
            max-width: 1240px;
            min-height: 390px;
            margin: 2px auto 30px;
            position: relative;
            isolation: isolate;
            overflow: hidden;
            border: 1px solid rgba(75, 226, 132, .56);
            border-radius: 28px;
            padding: 24px 24px 26px;
            text-align: center;
            background:
                radial-gradient(ellipse at 50% 8%, rgba(22, 115, 56, .36), transparent 53%),
                linear-gradient(115deg, #06180e 0%, #082416 48%, #04130b 100%);
            box-shadow: 0 18px 70px rgba(0,0,0,.32), inset 0 1px 0 rgba(220,255,229,.08);
            animation: tr-rise .8s ease both;
        }
        .tr-hero::before {
            content: '';
            position: absolute;
            z-index: -1;
            inset: -30%;
            pointer-events: none;
            background:
                radial-gradient(ellipse at 18% 48%, rgba(30, 230, 112, .22), transparent 26%),
                radial-gradient(ellipse at 85% 40%, rgba(0, 193, 135, .19), transparent 27%),
                radial-gradient(ellipse at 50% 100%, rgba(48, 218, 116, .13), transparent 34%);
            filter: blur(24px);
            animation: tr-aurora 11s ease-in-out infinite alternate;
        }
        .tr-hero::after {
            content: '';
            position: absolute;
            z-index: 2;
            top: 0;
            bottom: 0;
            left: -40%;
            width: 30%;
            pointer-events: none;
            background: linear-gradient(90deg, transparent, rgba(122,255,169,.12), transparent);
            transform: skewX(-18deg);
            animation: tr-beam 9s ease-in-out 1s infinite;
        }
        .tr-stars { position:absolute; inset:0; z-index:0; pointer-events:none; }
        .tr-star { position:absolute; width:4px; height:4px; border-radius:50%; background:#70ff9e; box-shadow:0 0 13px #36ef83; animation:tr-twinkle 3s ease-in-out infinite; }
        .tr-star.a { top:13%; left:21%; }
        .tr-star.b { top:22%; right:18%; animation-delay:-1.2s; }
        .tr-star.c { top:58%; left:12%; animation-delay:-2.1s; }
        .tr-star.d { top:69%; right:14%; animation-delay:-.5s; }
        .tr-star.e { top:8%; right:39%; width:3px;height:3px; animation-delay:-1.7s; }

        .tr-landscape {
            position:absolute;
            z-index:0;
            pointer-events:none;
            left:0; right:0; bottom:0;
            height:175px;
            opacity:.95;
        }
        .tr-art-left {
            position:absolute;
            left:0; bottom:0;
            width:34%;
            height:100%;
            opacity:.96;
        }
        .tr-art-right {
            position:absolute;
            right:0; bottom:0;
            width:35%;
            height:100%;
            opacity:.9;
        }
        .tr-light-ribbon {
            position:absolute;
            z-index:1;
            left:-4%; right:-4%; bottom:31px;
            height:2px;
            background:linear-gradient(90deg,transparent,#27df77 18%,#9affb7 48%,#21d875 78%,transparent);
            box-shadow:0 0 12px #35e981, 0 0 28px rgba(46,235,125,.8);
            transform:rotate(-2deg);
            opacity:.78;
        }
        .tr-light-ribbon.r2 {
            bottom:57px; left:5%; right:-10%;
            height:1px; opacity:.36; transform:rotate(2deg);
            filter:blur(1px);
        }
        .tr-hero-content { position:relative; z-index:3; }
        .tr-eyebrow {
            display:flex; justify-content:center; align-items:center; gap:10px;
            color:#a7e9ba; font-size:10px; font-weight:800; letter-spacing:.25em;
            text-transform:uppercase; margin:0 auto 15px;
        }
        .tr-live-dot { width:8px;height:8px;border-radius:50%;background:#37ed87;box-shadow:0 0 14px #37ed87;display:inline-block; }
        .tr-logo {
            display:grid; place-items:center;
            width:70px;height:70px;margin:0 auto 8px;
            border:1px solid rgba(81,238,139,.66);border-radius:21px;
            background:linear-gradient(145deg,rgba(22,119,58,.72),rgba(3,30,15,.94));
            font-size:35px; animation:tr-float 5s ease-in-out infinite,tr-pulse 3s ease-in-out infinite;
        }
        .tr-brand { color:#e1ffea;font-size:10px;font-weight:800;letter-spacing:.34em;margin:0 0 20px; }
        .tr-title {
            margin:0 auto 14px;
            color:#f4fff7;
            font-family:'Space Grotesk','DM Sans',sans-serif;
            font-size:clamp(36px,5vw,66px);
            line-height:1.06;letter-spacing:-.055em;font-weight:700;
            text-shadow:0 4px 28px rgba(0,0,0,.3);
        }
        .tr-title span { color:#43e985; font-style:italic; text-shadow:0 0 27px rgba(45,232,124,.32); }
        .tr-subtitle { max-width:690px;margin:0 auto 20px;color:#d0e5d6;font-size:15px;line-height:1.8; }
        .tr-language {
            display:inline-flex;align-items:center;gap:9px;
            padding:10px 18px;border-radius:999px;
            border:1px solid rgba(86,214,129,.48);
            background:rgba(6,42,22,.84);color:#d9f5e1;font-size:12px;
            box-shadow:0 0 24px rgba(44,209,110,.12);
        }
        .tr-language strong { color:#80f6a7; }

        .tr-section {
            display:flex;align-items:center;justify-content:center;gap:15px;
            margin:0 auto 19px;color:#d9f8e2;
            font-size:12px;font-weight:800;letter-spacing:.28em;
            animation:tr-rise .9s .12s both;
        }
        .tr-section::before,.tr-section::after {
            content:'';width:48px;height:1px;
            background:linear-gradient(90deg,transparent,#45e889);
            box-shadow:0 0 8px rgba(61,238,133,.6);
        }
        .tr-section::after { background:linear-gradient(90deg,#45e889,transparent); }
        .tr-leaf { color:#86f6a5;font-size:18px; }

        .tr-card {
            position:relative;overflow:hidden;min-height:244px;
            padding:20px 20px 18px;border-radius:22px;
            border:1px solid rgba(76,208,123,.54);
            background:linear-gradient(145deg,rgba(12,48,27,.96),rgba(3,20,11,.98));
            box-shadow:0 14px 38px rgba(0,0,0,.24),inset 0 1px 0 rgba(223,255,230,.06);
            transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease;
            animation:tr-rise .75s both;
        }
        .tr-card::before {
            content:'';position:absolute;inset:0;pointer-events:none;
            background:radial-gradient(circle at 90% 12%,rgba(50,215,112,.14),transparent 34%);
        }
        .tr-card:hover {
            transform:translateY(-7px);
            border-color:#5bf09a;
            box-shadow:0 22px 48px rgba(0,0,0,.34),0 0 30px rgba(41,220,115,.16);
        }
        .tr-card-icon {
            width:48px;height:48px;display:grid;place-items:center;
            border-radius:15px;border:1px solid rgba(78,226,132,.66);
            background:rgba(14,88,43,.5);color:#7cf4a3;
            font-size:24px;margin-bottom:16px;
            box-shadow:0 0 20px rgba(49,220,116,.13);
        }
        .tr-card h3 { margin:0 0 8px;color:#f3fff6;font-size:19px;font-weight:800; }
        .tr-card p { min-height:50px;margin:0 0 13px;color:#c5ddcc;font-size:13px;line-height:1.65; }
        .tr-tag {
            display:inline-block;padding:6px 11px;border-radius:999px;
            color:#8df3aa;background:rgba(16,105,49,.4);
            border:1px solid rgba(63,213,119,.25);
            font-size:9px;font-weight:800;letter-spacing:.17em;
        }
        .tr-card-art { position:absolute;right:16px;top:14px;color:rgba(73,221,124,.13);font-size:60px; }
        .tr-footer {
            display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;
            margin-top:34px;padding:18px 6px 4px;
            border-top:1px solid rgba(86,197,122,.36);
            color:#b5d3be;font-size:11px;letter-spacing:.12em;
        }
        .tr-footer-brand { color:#e3f9e9;font-weight:800;letter-spacing:.24em; }
        .tr-ready { color:#83efa3;font-weight:800;display:flex;align-items:center;gap:8px; }

        /* Native Streamlit buttons stay functional and match the reference. */
        div[class*="st-key-tr_home_explore"] button,
        div[class*="st-key-tr_home_chat"] button,
        div[class*="st-key-tr_home_voice"] button {
            min-height:46px !important;border-radius:12px !important;
            border:1px solid rgba(105,232,149,.58) !important;
            background:linear-gradient(100deg,#e4ffe9,#bdf3ce) !important;
            color:#0a351b !important;font-weight:800 !important;
            box-shadow:0 5px 18px rgba(34,191,93,.12) !important;
            transition:transform .2s ease,box-shadow .2s ease !important;
        }
        div[class*="st-key-tr_home_explore"] button:hover,
        div[class*="st-key-tr_home_chat"] button:hover,
        div[class*="st-key-tr_home_voice"] button:hover {
            transform:translateY(-2px);box-shadow:0 10px 25px rgba(34,220,105,.24) !important;
        }
        @media(max-width:900px) {
            .tr-hero { min-height:410px;padding-left:16px;padding-right:16px; }
            .tr-art-left { width:27%;opacity:.5; }
            .tr-art-right { width:28%;opacity:.5; }
            .tr-card { min-height:220px; }
        }
        @media(max-width:640px) {
            .tr-hero { padding-top:24px;min-height:420px;border-radius:20px; }
            .tr-eyebrow { font-size:8px;letter-spacing:.14em; }
            .tr-title { font-size:36px; }
            .tr-subtitle { font-size:13px; }
            .tr-art-left,.tr-art-right { opacity:.25; }
            .tr-footer { justify-content:center;text-align:center; }
        }
        @media(prefers-reduced-motion:reduce) {
            .tribal-ref-home *, .tribal-ref-home *::before, .tribal-ref-home *::after {
                animation-duration:.01ms !important;animation-iteration-count:1 !important;transition-duration:.01ms !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Decorative vector scene: stylized person on the left, village on the right.
    # It is inline SVG, so no separate image assets or Node.js installation are needed.
    hero_html = f"""
    <div class="tribal-ref-home">
      <section class="tr-hero">
        <div class="tr-stars">
          <i class="tr-star a"></i><i class="tr-star b"></i><i class="tr-star c"></i>
          <i class="tr-star d"></i><i class="tr-star e"></i>
        </div>
        <div class="tr-landscape">
          <svg class="tr-art-left" viewBox="0 0 360 190" preserveAspectRatio="xMinYMax meet" aria-hidden="true">
            <defs>
              <linearGradient id="womanCloth" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stop-color="#e04b43"/><stop offset="1" stop-color="#792a32"/>
              </linearGradient>
              <linearGradient id="womanSkin" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stop-color="#e8aa78"/><stop offset="1" stop-color="#9c583c"/>
              </linearGradient>
              <filter id="softGlow"><feGaussianBlur stdDeviation="5"/></filter>
            </defs>
            <path d="M0 170 Q60 95 132 150 T300 142 L360 190 H0Z" fill="#0c5a31" opacity=".62"/>
            <path d="M0 183 Q70 135 145 168 T360 160" fill="none" stroke="#37e982" stroke-width="2" opacity=".6"/>
            <!-- leaves / feathered head ornament -->
            <path d="M160 70 Q120 18 104 4 Q119 47 160 78" fill="#3eaa58" stroke="#9cf4a8" stroke-width="1"/>
            <path d="M166 67 Q166 17 187 0 Q187 43 166 76" fill="#1c8749" stroke="#8deba0" stroke-width="1"/>
            <path d="M151 70 Q105 44 91 32 Q116 72 156 81" fill="#8bbd4b" stroke="#c9f58b" stroke-width="1"/>
            <!-- hair silhouette -->
            <path d="M113 93 Q105 42 156 38 Q204 40 205 92 Q204 134 178 150 L115 143 Q94 119 113 93Z" fill="#101a13"/>
            <!-- neck and face -->
            <path d="M143 108 L146 145 L178 145 L170 104Z" fill="url(#womanSkin)"/>
            <path d="M124 71 Q145 47 181 64 Q205 81 189 119 Q178 139 153 132 Q125 119 124 71Z" fill="url(#womanSkin)" stroke="#6f3c2b" stroke-width="2"/>
            <path d="M124 79 Q127 46 166 49 Q199 54 199 85 Q183 66 162 69 Q144 72 124 91Z" fill="#101a13"/>
            <path d="M180 92 Q191 96 188 104" fill="none" stroke="#7b422e" stroke-width="2" stroke-linecap="round"/>
            <path d="M162 112 Q173 119 184 111" fill="none" stroke="#713b2b" stroke-width="2" stroke-linecap="round"/>
            <circle cx="174" cy="88" r="2.5" fill="#1b2118"/>
            <circle cx="194" cy="111" r="5" fill="none" stroke="#e7c46b" stroke-width="2"/>
            <circle cx="194" cy="111" r="2" fill="#f7dc83"/>
            <!-- shoulders and traditional-inspired garment (generic decorative illustration) -->
            <path d="M83 190 Q93 140 137 135 L161 145 L190 134 Q237 146 259 190Z" fill="url(#womanCloth)" stroke="#d89c53" stroke-width="2"/>
            <path d="M137 139 L158 187 M185 139 L165 187" stroke="#f4ce7b" stroke-width="4"/>
            <path d="M98 159 Q164 178 242 157" fill="none" stroke="#f6d27b" stroke-width="3"/>
            <path d="M107 174 Q164 192 233 173" fill="none" stroke="#e7b65c" stroke-width="2" stroke-dasharray="4 5"/>
            <!-- jewelry -->
            <path d="M139 143 Q163 177 186 143" fill="none" stroke="#f7d989" stroke-width="3"/>
            <circle cx="163" cy="171" r="5" fill="#f4d27d"/>
            <path d="M126 118 Q112 130 126 141" fill="none" stroke="#edca76" stroke-width="3"/>
            <circle cx="125" cy="143" r="5" fill="none" stroke="#f2d47e" stroke-width="2"/>
            <path d="M0 150 Q65 122 102 156" fill="none" stroke="#3fe985" stroke-width="3" opacity=".8" filter="url(#softGlow)"/>
          </svg>
          <svg class="tr-art-right" viewBox="0 0 420 190" preserveAspectRatio="xMaxYMax meet" aria-hidden="true">
            <defs>
              <linearGradient id="hutRoof" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stop-color="#d5a45b"/><stop offset="1" stop-color="#76512d"/>
              </linearGradient>
            </defs>
            <path d="M0 164 Q90 112 180 149 T420 130 L420 190 H0Z" fill="#0a4c2b" opacity=".8"/>
            <path d="M20 178 Q115 140 210 170 T420 158" fill="none" stroke="#2bbd68" stroke-width="2"/>
            <!-- trees -->
            <g fill="#0d6337" stroke="#247c45" stroke-width="2">
              <path d="M300 150 L310 58 L320 150Z"/><path d="M282 115 Q310 42 338 115Z"/>
              <path d="M347 153 L356 83 L366 153Z"/><path d="M333 120 Q357 60 379 120Z"/>
              <path d="M55 162 L63 94 L71 162Z"/><path d="M43 128 Q63 72 83 128Z"/>
            </g>
            <!-- huts -->
            <g>
              <path d="M118 132 L174 86 L230 132Z" fill="url(#hutRoof)" stroke="#e0b66d" stroke-width="2"/>
              <rect x="132" y="130" width="85" height="50" rx="2" fill="#98653b" stroke="#d0a264" stroke-width="2"/>
              <path d="M163 180 V146 Q175 133 188 146 V180Z" fill="#281d15"/>
              <path d="M125 133 H224" stroke="#f2d08b" stroke-width="3"/>
              <path d="M240 145 L283 110 L326 145Z" fill="#9c7040" stroke="#e0b66d" stroke-width="2"/>
              <rect x="251" y="144" width="64" height="38" fill="#875b35" stroke="#d0a264" stroke-width="2"/>
              <path d="M274 182 V155 Q283 145 293 155 V182Z" fill="#261b13"/>
            </g>
            <!-- warm windows -->
            <rect x="143" y="144" width="12" height="12" fill="#ffd47a" opacity=".8"/>
            <rect x="299" y="153" width="9" height="10" fill="#ffd47a" opacity=".8"/>
            <path d="M0 179 Q115 153 206 179 T420 170" fill="none" stroke="#57ed91" stroke-width="2" opacity=".6"/>
          </svg>
          <div class="tr-light-ribbon"></div><div class="tr-light-ribbon r2"></div>
        </div>
        <div class="tr-hero-content">
          <div class="tr-eyebrow"><span class="tr-live-dot"></span> INTELLIGENT&nbsp; · &nbsp;MULTILINGUAL&nbsp; · &nbsp;CULTURAL</div>
          <div class="tr-logo">🌿</div>
          <p class="tr-brand">TRIBAL AI</p>
          <h1 class="tr-title">How can I help you <span>today?</span></h1>
          <p class="tr-subtitle">Your multilingual knowledge assistant for community stories, culture,<br>
          traditions, learning, and everyday questions.</p>
          <div class="tr-language">🌐 &nbsp; Current language <strong>{language}</strong></div>
        </div>
      </section>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="tr-section"><span class="tr-leaf">🌿</span> START EXPLORING</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(3, gap="medium")
    card_data = [
        ("▣", "Explore knowledge",
         "Discover tribal culture, traditions, community stories, and local knowledge.",
         "LEARN & DISCOVER", "✧"),
        ("✧", "Ask a question",
         "Get helpful answers in your selected language with a simple conversation.",
         "CHAT ASSISTANT", "☷"),
        ("◉", "Use your voice",
         "Speak naturally and explore voice-based multilingual assistance.",
         "VOICE ASSISTANT", "〰"),
    ]

    for idx, (col, item) in enumerate(zip(columns, card_data)):
        icon, title, description, tag, art = item
        with col:
            st.markdown(
                f"""
                <article class="tr-card" style="animation-delay:{idx * .12:.2f}s">
                    <div class="tr-card-art">{art}</div>
                    <div class="tr-card-icon">{icon}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <span class="tr-tag">{tag}</span>
                </article>
                """,
                unsafe_allow_html=True,
            )
            if idx == 0:
                st.button(
                    "Explore with Tribal AI ↗",
                    key="tr_home_explore",
                    use_container_width=True,
                    on_click=_open_chat,
                )
            elif idx == 1:
                st.button(
                    "Start a conversation ↗",
                    key="tr_home_chat",
                    use_container_width=True,
                    on_click=_open_chat,
                )
            else:
                st.button(
                    "Open voice assistant ↗",
                    key="tr_home_voice",
                    use_container_width=True,
                    on_click=_open_voice,
                )

    st.markdown(
        """
        <footer class="tr-footer">
            <span class="tr-footer-brand">🌿 &nbsp; TRIBAL AI</span>
            <span>Preserving knowledge · Connecting cultures</span>
            <span class="tr-ready"><span class="tr-live-dot"></span> SYSTEM READY</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    show_home()
