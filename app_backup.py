
import streamlit as st
import os
import pandas as pd

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="KALI VISION AI | Bengal",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --gold: #E5BC70;
    --cream: #F9EBD1;
    --red: #A32638;
    --muted: #C3B1AC;
}

.stApp {
    background:
    radial-gradient(ellipse at 75% 20%, #451321 0%, transparent 45%),
    linear-gradient(130deg, #090609, #190B12 55%, #080609);
    color: var(--cream);
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p {
    color: var(--cream);
}

/* NAVIGATION */

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 25px;
    border: 1px solid rgba(229,188,112,.3);
    border-radius: 15px;
    background: rgba(25,10,17,.8);
    margin-bottom: 30px;
}

.brand {
    color: var(--gold);
    font-family: 'Cormorant Garamond', serif;
    font-size: 27px;
    font-weight: 700;
    letter-spacing: 3px;
}

/* HERO */

.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(42px, 5vw, 76px);
    line-height: 1.05;
    color: var(--gold);
    font-weight: 600;
}

.hero-subtitle {
    font-family: 'Cormorant Garamond', serif;
    font-size: 29px;
    color: #F4D7A1;
    font-style: italic;
}

.eyebrow {
    color: var(--gold);
    letter-spacing: 5px;
    font-size: 11px;
    text-transform: uppercase;
}

.description {
    color: var(--muted);
    line-height: 1.9;
    font-size: 15px;
}

.hero-image {
    border: 1px solid rgba(229,188,112,.4);
    border-radius: 20px;
    overflow: hidden;
}

.hero-image img {
    border-radius: 20px;
}

/* SECTION */

.section-label {
    color: var(--gold);
    font-size: 11px;
    letter-spacing: 4px;
    margin-top: 55px;
    text-transform: uppercase;
}

.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 39px;
    color: var(--cream);
}

/* METRICS */

.metric-box {
    background: linear-gradient(145deg,
    rgba(130,45,60,.2),
    rgba(255,255,255,.025));
    border: 1px solid rgba(229,188,112,.22);
    border-radius: 15px;
    padding: 22px;
    text-align: center;
}

.metric-value {
    color: var(--gold);
    font-size: 32px;
    font-family: 'Cormorant Garamond', serif;
}

.metric-caption {
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 2px;
}

/* FEATURE CARDS */

.feature-card {
    background: linear-gradient(145deg,
    rgba(100,30,48,.28),
    rgba(255,255,255,.025));
    border: 1px solid rgba(229,188,112,.25);
    border-radius: 18px;
    padding: 25px;
    min-height: 205px;
}

.feature-icon {
    font-size: 34px;
}

.feature-card h3 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 25px;
    color: var(--gold);
}

.feature-card p {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.8;
}

/* BUTTONS */

.stButton > button {
    background: linear-gradient(120deg,#EBC77F,#C48A39);
    color: #180B0C;
    border: none;
    border-radius: 30px;
    font-weight: 600;
    padding: 12px 25px;
    transition: .3s;
}

.stButton > button:hover {
    background: #FFE0A0;
    color: #180B0C;
    transform: translateY(-2px);
    border: none;
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea {
    background: #21121A;
    color: white;
    border: 1px solid #76503D;
    border-radius: 10px;
}

/* FOOTER */

.footer {
    text-align: center;
    color: #A58A79;
    padding: 45px 10px;
    letter-spacing: 3px;
    font-size: 11px;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# NAVIGATION
# =====================================

st.markdown("""
<div class="navbar">
    <div class="brand">✦ KALI VISION AI</div>
    <div style="color:#E5BC70;font-size:12px;">
        BENGAL · CULTURE · INTELLIGENCE
    </div>
</div>
""", unsafe_allow_html=True)

page = st.radio(
    "Navigation",
    ["Home", "AI Assistant", "Gallery", "Kolkata Explorer", "About"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# =====================================
# HOME PAGE
# =====================================

if page == "Home":

    left, right = st.columns([1.05, 1.15], gap="large")

    with left:

        st.markdown("""
        <div style="padding-top:35px;">

        <div class="eyebrow">
        ✦ A JOURNEY THROUGH DIVINE BENGAL
        </div>

        <h1 class="hero-title">
        KALI VISION AI
        </h1>

        <div class="hero-subtitle">
        The Divine Intelligence of Bengal
        </div>

        <p class="description">
        Discover the spiritual beauty of Kolkata's Kali Puja
        through Artificial Intelligence, Deep Learning,
        Computer Vision and Cultural Intelligence.
        </p>

        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        metrics = [
            ("03", "AI MODULES"),
            ("BENGAL", "REGION"),
            ("2026", "EDITION")
        ]

        for col, (value, label) in zip([c1,c2,c3], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{value}</div>
                    <div class="metric-caption">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.write("")

        if st.button("Explore The Experience →"):
            st.session_state.explore = True
            st.rerun()

    with right:

        image_path = "assets/maa_kali_hero.jpg"

        if os.path.exists(image_path):
            st.image(
                image_path,
                use_container_width=True
            )
        else:
            st.warning(
                "Add your Maa Kali image at "
                "assets/maa_kali_hero.jpg"
            )

    st.markdown("""
    <div class="section-label">
    POWERED BY ARTIFICIAL INTELLIGENCE
    </div>

    <div class="section-title">
    Explore AI Features
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3, gap="medium")

    features = [
        (
            "🤖",
            "Maa Kali AI Assistant",
            "A Bengali and English conversational "
            "AI assistant powered by RAG and LLMs."
        ),
        (
            "🧠",
            "Deep Learning Vision",
            "Explore idol images using Computer "
            "Vision and image embeddings."
        ),
        (
            "📍",
            "Smart Kolkata Explorer",
            "Explore famous Kali Puja destinations "
            "and intelligent location recommendations."
        )
    ]

    for col, (icon, title, desc) in zip([a,b,c], features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)


# =====================================
# AI ASSISTANT PAGE
# =====================================

elif page == "AI Assistant":

    st.markdown(
        '<div class="section-title">🤖 Maa Kali AI Assistant</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Ask questions about Kali Puja, Bengali culture "
        "and famous Kali temples."
    )

    question = st.text_input(
        "Ask your question",
        placeholder="Tell me about Fata Kesto Kali..."
    )

    language = st.selectbox(
        "Choose Language",
        ["English", "বাংলা", "Both"]
    )

    if st.button("Ask AI"):

        if question.strip():
            st.info(
                "AI assistant interface is ready. "
                "RAG and LLM integration will be added "
                "in the next development phase."
            )
        else:
            st.warning("Please enter a question.")


# =====================================
# GALLERY PAGE
# =====================================

elif page == "Gallery":

    st.markdown(
        '<div class="section-title">✦ Divine Gallery</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Explore Maa Kali idols and upload images "
        "for the upcoming Computer Vision module."
    )

    uploaded_file = st.file_uploader(
        "Upload a Maa Kali idol image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:

        st.image(
            uploaded_file,
            caption="Uploaded image",
            use_container_width=True
        )

        st.info(
            "Image upload successful. "
            "CLIP-based image analysis will be integrated next."
        )


# =====================================
# KOLKATA EXPLORER
# =====================================

elif page == "Kolkata Explorer":

    st.markdown(
        '<div class="section-title">📍 Kolkata Kali Puja Explorer</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Explore selected cultural destinations "
        "around Kolkata."
    )

    destinations = {
        "Fata Kesto Kali Puja": "Kolkata",
        "Kalighat Kali Temple": "Kalighat",
        "Dakshineswar Kali Temple": "Dakshineswar"
    }

    selected = st.selectbox(
        "Select Destination",
        list(destinations.keys())
    )

    st.success(
        f"Selected destination: {selected}"
    )

    st.info(
        "Interactive map, metro connectivity and "
        "route intelligence will be added in the next phase. "
        "This is currently a destination-selection demo."
    )


# =====================================
# ABOUT PAGE
# =====================================

elif page == "About":

    st.markdown(
        '<div class="section-title">About KALI VISION AI</div>',
        unsafe_allow_html=True
    )

    st.write("""
    KALI VISION AI is an AI-powered cultural exploration
    platform celebrating the spiritual heritage of Bengal.

    Our engineering focus:

    - Deep Learning
    - Computer Vision
    - Generative AI
    - Retrieval Augmented Generation
    - Data Analytics
    - Intelligent Recommendation Systems
    """)

    st.caption(
        "Built with Python, Streamlit and Artificial Intelligence."
    )


# =====================================
# FOOTER
# =====================================

st.markdown("""
<div class="footer">
    ✦ BUILT WITH INTELLIGENCE · INSPIRED BY DIVINITY ✦
    <br><br>
    JAI MAA KALI
    <br><br>
    KALI VISION AI © 2026
</div>
""", unsafe_allow_html=True)
