import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image, ImageStat
from urllib.parse import quote
import plotly.express as px

# =====================================================
# KALI VISION AI | HYBRID CINEMATIC EDITION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="KALI VISION AI | Bengal",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# CSS DESIGN SYSTEM
# =====================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --gold: #E5BC70;
    --cream: #F8ECDD;
    --muted: #B9A7A4;
    --wine: #761F35;
}

.stApp {
    background:
        radial-gradient(ellipse at 80% 10%, #491426 0%, transparent 42%),
        linear-gradient(135deg, #080609, #190B13 60%, #090609);
    color: var(--cream);
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 1450px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p { color: var(--cream); }

[data-testid="stMarkdownContainer"] p {
    color: var(--muted);
    line-height: 1.8;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 17px 23px;
    border: 1px solid rgba(229,188,112,.25);
    border-radius: 15px;
    background: rgba(20,9,15,.86);
    margin-bottom: 22px;
}

.brand {
    font-family: 'Cormorant Garamond', serif;
    color: var(--gold);
    font-size: 27px;
    font-weight: 700;
    letter-spacing: 3px;
}

.nav-sub {
    color: #D5BDA7;
    font-size: 10px;
    letter-spacing: 2px;
}

.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(43px, 6vw, 79px);
    color: var(--gold);
    line-height: 1.03;
}

.hero-subtitle {
    font-family: 'Cormorant Garamond', serif;
    font-size: 28px;
    color: #F4D7A1;
    font-style: italic;
}

.eyebrow {
    color: var(--gold);
    font-size: 10px;
    letter-spacing: 4px;
}

.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 38px;
    color: var(--cream);
}

.section-label {
    color: var(--gold);
    letter-spacing: 4px;
    font-size: 10px;
    margin-top: 35px;
}

.hero-frame {
    border: 1px solid rgba(229,188,112,.4);
    border-radius: 19px;
    padding: 7px;
    background: rgba(255,255,255,.025);
}

.metric-box, .feature-card, .gallery-card, .info-panel {
    background: linear-gradient(145deg, rgba(110,34,53,.23), rgba(255,255,255,.025));
    border: 1px solid rgba(229,188,112,.22);
    border-radius: 15px;
    padding: 20px;
    transition: .3s;
}

.metric-box:hover, .feature-card:hover, .gallery-card:hover {
    border-color: var(--gold);
    transform: translateY(-3px);
}

.metric-value {
    color: var(--gold);
    font-family: 'Cormorant Garamond', serif;
    font-size: 29px;
    text-align: center;
}

.metric-caption {
    color: var(--muted);
    font-size: 9px;
    letter-spacing: 2px;
    text-align: center;
}

.feature-card { min-height: 175px; }
.feature-icon { font-size: 29px; }

.feature-card h3 {
    color: var(--gold);
    font-family: 'Cormorant Garamond', serif;
}

.gallery-card { padding: 12px; margin-bottom: 12px; }

.gallery-name {
    color: var(--gold);
    font-family: 'Cormorant Garamond', serif;
    font-size: 23px;
}

.gallery-location {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1px;
}

.stButton > button {
    background: linear-gradient(120deg, #EBC77F, #C48A39);
    color: #180B0C;
    border: none;
    border-radius: 30px;
    font-weight: 600;
    transition: .3s;
}

.stButton > button:hover {
    background: #FFE0A0;
    color: #180B0C;
    transform: translateY(-2px);
}

.stTextInput input, .stTextArea textarea {
    background: #21121A;
    color: white;
    border: 1px solid #76503D;
}

.footer {
    text-align: center;
    color: #A58A79;
    padding: 40px;
    letter-spacing: 3px;
    font-size: 10px;
}

[data-testid="stImage"] img { border-radius: 11px; }

@media (max-width: 700px) {
    .brand { font-size: 19px; }
    .nav-sub { font-size: 8px; }
    .hero-title { font-size: 43px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# IMAGE DATASET
# =====================================================

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Music files are intentionally local: add only recordings whose licence
# explicitly permits your intended website use. See assets/music/README.txt.
MUSIC_DIR = ASSET_DIR / "music"
MUSIC_TRACKS = [
    {"title": "Maa Kali Aarti", "artist": "Devotional collection", "file": "maa-kali-aarti.mp3", "mood": "Aarti"},
    {"title": "Shyama Sangeet", "artist": "Bengali devotional", "file": "shyama-sangeet.mp3", "mood": "Shyama Sangeet"},
    {"title": "Mahakali Stotram", "artist": "Devotional collection", "file": "mahakali-stotram.mp3", "mood": "Stotram"},
    {"title": "Bengali Devotional Instrumental", "artist": "Instrumental collection", "file": "bengali-devotional.mp3", "mood": "Instrumental"},
]

def available_music_tracks():
    """Return configured tracks whose audio files exist and are non-empty."""
    return [track for track in MUSIC_TRACKS
            if (MUSIC_DIR / track["file"]).is_file()
            and (MUSIC_DIR / track["file"]).stat().st_size > 0]


def get_images():
    """Return valid image files from the assets directory."""
    if not ASSET_DIR.exists():
        return []

    image_files = []

    for path in ASSET_DIR.iterdir():
        if (
            path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
            and path.stat().st_size > 0
            and "collage" not in path.name.lower()
        ):
            try:
                with Image.open(path) as img:
                    img.verify()
                image_files.append(path)
            except Exception:
                print(f"Skipping invalid image: {path.name}")

    return sorted(image_files, key=lambda item: item.name.lower())


def image_title(path):
    name = Path(path).stem
    return name.replace("_", " ").replace("-", " ").replace(".", " ").title()


def image_category(filename):
    # Accept either a pathlib.Path object or a plain filename string.
    name = Path(str(filename)).name.lower()

    if "dakshineswar" in name or "kalighat" in name:
        return "Temples"
    if "fata" in name or "kesto" in name:
        return "Kali Puja"
    if "club" in name or "pandal" in name or "chokhudan" in name:
        return "Pandals"
    if "maa" in name or "kali" in name:
        return "Maa Kali"

    return "Cultural Collection"


def get_image_stats(file):
    """Return basic image dimensions and RGB statistics."""
    with Image.open(file) as img:
        rgb = img.convert("RGB")
        stat = ImageStat.Stat(rgb)

        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "brightness": round(sum(stat.mean) / 3, 2),
            "red": round(stat.mean[0], 2),
            "green": round(stat.mean[1], 2),
            "blue": round(stat.mean[2], 2),
            "aspect_ratio": round(img.width / img.height, 2),
        }


# =====================================================
# NAVIGATION
# =====================================================

st.markdown(
    """
<div class="navbar">
    <div class="brand">✦ KALI VISION AI</div>
    <div class="nav-sub">BENGAL · CULTURE · INTELLIGENCE</div>
</div>
""",
    unsafe_allow_html=True,
)

pages = [
    "Home",
    "AI Assistant",
    "Gallery",
    "Music Lounge",
    "Vision Lab",
    "Kolkata Explorer",
    "Analytics",
    "About",
]

# Use a separate state value to avoid modifying the radio widget
# after it has been instantiated.
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

if "navigation_request" in st.session_state:
    requested_page = st.session_state.pop("navigation_request")
    if requested_page in pages:
        st.session_state.selected_page = requested_page

page = st.radio(
    "Navigation",
    pages,
    horizontal=True,
    label_visibility="collapsed",
    key="selected_page",
)

st.divider()

images = get_images()

# =====================================================
# HOME
# =====================================================

if page == "Home":
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown(
            """
<div style="padding-top:35px">
    <div class="eyebrow">✦ A JOURNEY THROUGH DIVINE BENGAL</div>
    <h1 class="hero-title">KALI VISION AI</h1>
    <div class="hero-subtitle">The Divine Intelligence of Bengal</div>
    <p>
    Discover Bengal's spiritual heritage through Artificial
    Intelligence, Deep Learning, Computer Vision and Data Analytics.
    Explore the temples, traditions and visual beauty of Kali Puja.
    </p>
</div>
""",
            unsafe_allow_html=True,
        )

        col_a, col_b, col_c = st.columns(3)
        metrics = [
            (str(len(images)), "IMAGES"),
            ("07", "MODULES"),
            ("2026", "EDITION"),
        ]

        for metric_col, (value, label) in zip(
            [col_a, col_b, col_c], metrics
        ):
            with metric_col:
                st.markdown(
                    f"""
<div class="metric-box">
    <div class="metric-value">{value}</div>
    <div class="metric-caption">{label}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

        st.write("")
        if st.button("Explore Divine Bengal →"):
            st.session_state.navigation_request = "Gallery"
            st.rerun()

    with right:
        st.markdown(
            '<div class="hero-frame">', unsafe_allow_html=True
        )
        hero = ASSET_DIR / "maa_kali_hero.png"

        if not hero.exists():
            hero = ASSET_DIR / "maa_kali_hero.jpg"

        if hero.exists() and hero.stat().st_size > 0:
            try:
                st.image(str(hero), use_container_width=True)
            except Exception:
                st.warning("The hero image could not be opened.")
        else:
            st.warning(
                "Add a valid Maa Kali hero image to "
                "assets/maa_kali_hero.png"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
<div class="section-label">THE EXPERIENCE</div>
<div class="section-title">Where Tradition Meets Intelligence</div>
""",
        unsafe_allow_html=True,
    )

    features = [
        ("🤖", "AI Assistant", "Explore Bengali cultural knowledge."),
        ("🧠", "Vision Intelligence", "Analyze uploaded devotional images."),
        ("📍", "Kolkata Explorer", "Discover temples and puja destinations."),
        ("📸", "Divine Gallery", "Explore the visual heritage of Bengal."),
        ("📊", "Festival Analytics", "Understand your image collection."),
        ("🌺", "Cultural Discovery", "Learn about traditions and rituals."),
    ]

    for index in range(0, len(features), 3):
        feature_cols = st.columns(3)
        for feature_col, item in zip(
            feature_cols, features[index : index + 3]
        ):
            with feature_col:
                st.markdown(
                    f"""
<div class="feature-card">
    <div class="feature-icon">{item[0]}</div>
    <h3>{item[1]}</h3>
    <p>{item[2]}</p>
</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown(
        '<div class="section-label">SOUND OF DEVOTION</div>'
        '<div class="section-title">A Divine Musical Experience</div>',
        unsafe_allow_html=True,
    )
    home_tracks = available_music_tracks()
    if home_tracks:
        chosen_home_track = st.selectbox(
            "Choose a devotional track",
            home_tracks,
            format_func=lambda track: f"{track['title']} · {track['mood']}",
            key="home_music_track",
        )
        home_audio = MUSIC_DIR / chosen_home_track["file"]
        st.audio(str(home_audio), format="audio/mp3", autoplay=False)
        st.caption("Press play to begin. Browsers generally block sound autoplay until the visitor interacts with the page.")
        if st.button("Open Music Lounge →", key="open_music_lounge"):
            st.session_state.navigation_request = "Music Lounge"
            st.rerun()
    else:
        st.info("Your music library is ready for royalty-free recordings. Add licensed MP3 files to assets/music/ to activate the player.")
        if st.button("Set up Divine Music Lounge →", key="open_music_lounge_empty"):
            st.session_state.navigation_request = "Music Lounge"
            st.rerun()

# =====================================================
# GALLERY
# =====================================================

elif page == "Gallery":
    st.markdown(
        '<div class="section-label">VISUAL HERITAGE OF BENGAL</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-title">✦ Divine Bengal Gallery</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "A curated visual collection of Kali Puja, temples "
        "and Bengal's cultural heritage."
    )

    if not images:
        st.info(
            "No valid images found. Add JPG, PNG or WEBP files "
            "to your assets folder."
        )
    else:
        category_options = ["All"] + sorted(
            {image_category(path.name) for path in images}
        )
        category = st.selectbox(
            "Explore collection", category_options
        )

        filtered = [
            path
            for path in images
            if category == "All"
            or image_category(path.name) == category
        ]

        st.caption(f"{len(filtered)} images in this collection")

        for start in range(0, len(filtered), 3):
            cols = st.columns(3, gap="medium")

            for col, path in zip(cols, filtered[start : start + 3]):
                with col:
                    st.markdown(
                        '<div class="gallery-card">',
                        unsafe_allow_html=True,
                    )

                    try:
                        st.image(
                            str(path),
                            use_container_width=True,
                        )
                    except Exception:
                        st.warning(
                            f"Unable to load image: {path.name}"
                        )

                    st.markdown(
                        f'<div class="gallery-name">'
                        f'{image_title(path)}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="gallery-location">'
                        f'{image_category(path.name)}</div>',
                        unsafe_allow_html=True,
                    )

                    with st.expander("Explore this image"):
                        st.write("**File:**", path.name)
                        st.write(
                            "**Collection:**",
                            image_category(path.name),
                        )
                        st.write("**Image information:**")

                        try:
                            info = get_image_stats(path)
                            st.write(
                                f"Resolution: {info['width']} × "
                                f"{info['height']}"
                            )
                            st.write(f"Format: {info['format']}")
                        except Exception:
                            st.warning(
                                "Could not read image metadata."
                            )

                    st.markdown(
                        "</div>", unsafe_allow_html=True
                    )

# =====================================================
# AI ASSISTANT
# =====================================================

elif page == "AI Assistant":
    st.markdown(
        '<div class="section-title">🤖 Maa Kali AI Assistant</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Ask questions about Kali Puja, temples and Bengali traditions."
    )

    language = st.selectbox(
        "Response language", ["English", "বাংলা", "Both"]
    )
    question = st.text_input(
        "Your question",
        placeholder="Tell me about Dakshineswar Kali Temple...",
    )

    if st.button("Ask Assistant"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            st.info(
                "The conversational interface is ready. Connect an LLM "
                "and a verified Bengali cultural knowledge base to enable "
                "generated answers."
            )

    st.caption(
        "LLM and RAG integration: planned development module."
    )

# =====================================================
# VISION LAB
# =====================================================

elif page == "Vision Lab":
    st.markdown(
        '<div class="section-title">🧠 Vision Intelligence Lab</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Upload a devotional image to explore its visual properties. "
        "This baseline uses image processing, not a trained "
        "deep-learning classifier."
    )

    upload = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp"],
    )

    if upload is not None:
        try:
            img = Image.open(upload).convert("RGB")
            info = get_image_stats(upload)

            left, right = st.columns([1, 1], gap="large")

            with left:
                st.image(img, use_container_width=True)

            with right:
                st.markdown("### Image Intelligence Report")
                st.metric("Image width", f"{info['width']} px")
                st.metric("Image height", f"{info['height']} px")
                st.metric(
                    "Average brightness", info["brightness"]
                )
                st.metric("Aspect ratio", info["aspect_ratio"])

                color_df = pd.DataFrame(
                    {
                        "Color": ["Red", "Green", "Blue"],
                        "Mean intensity": [
                            info["red"],
                            info["green"],
                            info["blue"],
                        ],
                    }
                )

                fig = px.bar(
                    color_df,
                    x="Color",
                    y="Mean intensity",
                    title="RGB Channel Analysis",
                )
                st.plotly_chart(fig, use_container_width=True)
                st.success("Image processing completed.")

        except Exception as error:
            st.error(f"Unable to process this image: {error}")

# =====================================================
# KOLKATA EXPLORER
# =====================================================

elif page == "Kolkata Explorer":
    st.markdown(
        '<div class="section-title">📍 Smart Kolkata Explorer</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Discover important Kali temples and selected puja destinations."
    )

    places = {
        "Dakshineswar Kali Temple": "Dakshineswar Kali Temple, Kolkata",
        "Kalighat Kali Temple": "Kalighat Kali Temple, Kolkata",
        "Fata Kesto Kali Puja": "Fata Kesto Kali Puja, Kolkata",
    }

    selected = st.selectbox(
        "Choose a destination", list(places.keys())
    )
    location = places[selected]

    st.markdown(
        f"""
<div class="info-panel">
    <h3 style="color:#E5BC70">{selected}</h3>
    <p>{location}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    map_url = (
        "https://www.google.com/maps/search/?api=1&query="
        + quote(location)
    )
    st.link_button(
        "Open destination in Google Maps ↗", map_url
    )
    st.caption(
        "Map search is provided through Google Maps. Verify current "
        "opening times, access and event information before visiting."
    )

# =====================================================
# MUSIC LOUNGE
# =====================================================

elif page == "Music Lounge":
    st.markdown(
        '<div class="section-label">THE SOUND OF DIVINE BENGAL</div>'
        '<div class="section-title">🪔 Divine Music Lounge</div>',
        unsafe_allow_html=True,
    )
    st.write("Listen to Bengali Shyama Sangeet, Maa Kali devotional songs and spiritual instrumentals.")

    tracks = available_music_tracks()
    if not tracks:
        st.info("No audio files have been added yet. Place your licensed MP3 recordings in the assets/music/ folder using the filenames below.")
        st.markdown("""
        **Music slots**
        - `maa-kali-aarti.mp3` — Maa Kali Aarti
        - `shyama-sangeet.mp3` — Bengali Shyama Sangeet
        - `mahakali-stotram.mp3` — Mahakali Stotram
        - `bengali-devotional.mp3` — Bengali devotional instrumental
        """)
    else:
        track_names = [f"{track['title']} · {track['mood']}" for track in tracks]
        selected_index = st.selectbox(
            "Select your devotional music",
            range(len(tracks)),
            format_func=lambda index: track_names[index],
            key="music_lounge_track_index",
        )
        selected_track = tracks[selected_index]
        audio_path = MUSIC_DIR / selected_track["file"]

        music_left, music_right = st.columns([1, 2], gap="large")
        with music_left:
            music_cover = ASSET_DIR / "maa_kali_hero.png"
            if not music_cover.exists():
                music_cover = ASSET_DIR / "maa_kali_hero.jpg"
            if music_cover.exists():
                st.image(str(music_cover), use_container_width=True)
            else:
                st.markdown("### 🪔 JAI MAA KALI")
        with music_right:
            st.markdown(f"### {selected_track['title']}")
            st.caption(f"{selected_track['artist']} · {selected_track['mood']}")
            st.audio(str(audio_path), format="audio/mp3", autoplay=False)
            st.caption("Playback starts when the visitor presses Play. Browsers normally prevent audible autoplay on a first visit.")

        st.markdown("### Your devotional playlist")
        for index, track in enumerate(tracks, start=1):
            st.markdown(f"**{index:02d}. {track['title']}**  ·  {track['mood']}")

    st.divider()
    st.caption("Copyright reminder: use only recordings with a licence that permits website streaming and your intended commercial/non-commercial use. Keep the creator, source URL and licence details in music_credits.json.")

# =====================================================
# ANALYTICS
# =====================================================

elif page == "Analytics":
    st.markdown(
        '<div class="section-title">📊 Cultural Data Analytics</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Explore the composition of your local image dataset."
    )

    if images:
        df = pd.DataFrame(
            [
                {
                    "Image": path.name,
                    "Category": image_category(path.name),
                    "Size KB": round(path.stat().st_size / 1024, 2),
                }
                for path in images
            ]
        )

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total images", len(df))
        col_b.metric("Categories", df["Category"].nunique())
        col_c.metric(
            "Dataset size",
            f"{df['Size KB'].sum() / 1024:.2f} MB",
        )

        counts = df["Category"].value_counts().reset_index()
        counts.columns = ["Category", "Images"]

        fig = px.pie(
            counts,
            names="Category",
            values="Images",
            hole=0.55,
            title="Image Category Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(
            counts,
            x="Category",
            y="Images",
            title="Collection by Category",
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Dataset Inventory")
        st.dataframe(
            df, use_container_width=True, hide_index=True
        )

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download dataset report",
            data=csv_data,
            file_name="kali_vision_dataset.csv",
            mime="text/csv",
        )
    else:
        st.info(
            "Add images to your assets folder to generate analytics."
        )

# =====================================================
# ABOUT
# =====================================================

elif page == "About":
    st.markdown(
        '<div class="section-title">About KALI VISION AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="info-panel">
    <h3 style="color:#E5BC70">The Divine Intelligence of Bengal</h3>
    <p>
    KALI VISION AI is a cultural technology project exploring
    Bengal's devotional heritage through Artificial Intelligence,
    Computer Vision and Data Analytics.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Technology Stack")

    tech = pd.DataFrame(
        {
            "Layer": [
                "Frontend",
                "Programming",
                "Data Processing",
                "Visualization",
                "Computer Vision",
                "Generative AI",
            ],
            "Technology": [
                "Streamlit",
                "Python",
                "Pandas, NumPy",
                "Plotly",
                "Pillow, PyTorch (planned)",
                "LLM + RAG (planned)",
            ],
        }
    )

    st.dataframe(
        tech, use_container_width=True, hide_index=True
    )

    st.markdown("### Project Modules")
    st.write(
        """
- Cinematic cultural interface
- Image dataset exploration
- Image processing and visual analytics
- Conversational AI integration roadmap
- Geospatial discovery roadmap
"""
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    """
<div class="footer">
    ✦ BUILT WITH INTELLIGENCE · INSPIRED BY DIVINITY ✦
    <br><br>
    JAI MAA KALI
    <br><br>
    KALI VISION AI © 2026
</div>
""",
    unsafe_allow_html=True,
)
