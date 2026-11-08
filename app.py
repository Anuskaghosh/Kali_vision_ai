
import streamlit as st
import streamlit.components.v1 as components
import os
import json
import shutil
import subprocess
import ssl
import urllib.error
import urllib.request
from datetime import datetime
from html import escape as html_escape
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _SSL_CTX = ssl.create_default_context()

# =====================================================
# KALI VISION AI | HYBRID CINEMATIC EDITION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="KALI VISION AI | Bengal",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CSS DESIGN SYSTEM
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Cinzel+Decorative:wght@700;900&family=Great+Vibes&family=Inter:wght@300;400;500;600;700&family=Tiro+Bangla&display=swap');

:root {
    --gold:#E5BC70;
    --gold-bright:#FFD98E;
    --cream:#F8ECDD;
    --muted:#B9A7A4;
    --wine:#761F35;
    --hibiscus:#D6336C;
    --ember:#FF7A3D;
}

/* ---------- ANIMATIONS ---------- */
@keyframes fadeUp {
    from {opacity:0;transform:translateY(26px);}
    to {opacity:1;transform:translateY(0);}
}
@keyframes fadeDown {
    from {opacity:0;transform:translateY(-18px);}
    to {opacity:1;transform:translateY(0);}
}
@keyframes scaleIn {
    from {opacity:0;transform:scale(.93);}
    to {opacity:1;transform:scale(1);}
}
@keyframes flicker {
    0%,100% {opacity:1;filter:drop-shadow(0 0 6px rgba(255,160,70,.85));}
    22% {opacity:.8;filter:drop-shadow(0 0 14px rgba(255,110,40,.95));}
    48% {opacity:.95;filter:drop-shadow(0 0 9px rgba(255,180,90,.8));}
    71% {opacity:.72;filter:drop-shadow(0 0 18px rgba(255,90,30,1));}
}
@keyframes glowPulse {
    0%,100% {box-shadow:0 0 24px rgba(229,188,112,.16),inset 0 0 32px rgba(118,31,53,.28);}
    50% {box-shadow:0 0 52px rgba(229,188,112,.38),inset 0 0 48px rgba(214,51,108,.3);}
}
@keyframes shimmer {
    0% {background-position:-200% center;}
    100% {background-position:200% center;}
}
@keyframes emberRise {
    0% {transform:translateY(0) translateX(0) scale(1);opacity:0;}
    12% {opacity:.95;}
    85% {opacity:.5;}
    100% {transform:translateY(-108vh) translateX(3vw) scale(.25);opacity:0;}
}
@keyframes floatY {
    0%,100% {transform:translateY(0);}
    50% {transform:translateY(-8px);}
}
@keyframes marqueeScroll {
    from {transform:translateX(0);}
    to {transform:translateX(-50%);}
}

/* ---------- BASE ---------- */
.stApp {
    background:
    radial-gradient(ellipse at 82% 6%,rgba(118,31,53,.6) 0%,transparent 46%),
    radial-gradient(ellipse at 10% 94%,rgba(214,51,108,.16) 0%,transparent 44%),
    linear-gradient(160deg,#070408 0%,#150810 45%,#1D0A14 78%,#080509);
    color:var(--cream);
    font-family:'Inter',sans-serif;
}

header[data-testid="stHeader"] {background:transparent;}
#MainMenu, footer {visibility:hidden;}
/* The running/stop control is Streamlit's "script still going" icon.
   It sits in the top bar for the whole run; the page itself is the loading state. */
div[data-testid="stStatusWidget"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"] {
    display:none !important;
    visibility:hidden !important;
    pointer-events:none !important;
}

.block-container {
    max-width:1500px;
    padding-top:1.2rem;
    padding-bottom:3rem;
    animation:fadeUp .75s ease both;
}

/* Zero-size components.html / hook hosts — Streamlit still leaves flex-gap
   space for height="0px" element containers. Pull them out of flow.
   Do NOT target height="1" — Metro's live map mounts at 1px then pins fullscreen. */
[data-testid="stElementContainer"][height="0px"],
[data-testid="stElementContainer"][width="0px"][height="0px"],
[data-testid="stElementContainer"]:has(iframe[height="0"]),
[data-testid="stLayoutWrapper"]:has(> [data-testid="stElementContainer"][height="0px"]:only-child) {
    position:fixed !important;
    left:-10000px !important;
    top:0 !important;
    width:0 !important;
    height:0 !important;
    min-width:0 !important;
    min-height:0 !important;
    max-width:0 !important;
    max-height:0 !important;
    margin:0 !important;
    padding:0 !important;
    overflow:hidden !important;
    border:none !important;
    opacity:0 !important;
    pointer-events:none !important;
    flex:0 0 0 !important;
}
/* Style-only markdown blocks (CSS/JS injectors) leave empty layout slots */
[data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] > style:only-child),
[data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] > script:only-child) {
    position:fixed !important;
    left:-10000px !important;
    top:0 !important;
    width:0 !important;
    height:0 !important;
    margin:0 !important;
    padding:0 !important;
    overflow:hidden !important;
    opacity:0 !important;
    pointer-events:none !important;
}

h1,h2,h3,p {color:var(--cream);}

[data-testid="stMarkdownContainer"] p {
    color:var(--muted);
    line-height:1.8;
}

/* ---------- EMBER PARTICLES ---------- */
.embers {
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:0;
    overflow:hidden;
}
.embers span {
    position:absolute;
    left:var(--x);
    bottom:-12px;
    width:var(--s);
    height:var(--s);
    border-radius:50%;
    background:radial-gradient(circle,#FFE0A0 0%,var(--ember) 55%,transparent 100%);
    box-shadow:0 0 9px 2px rgba(255,140,60,.5);
    opacity:0;
    animation:emberRise var(--t) linear infinite;
    animation-delay:var(--d);
}

/* ---------- ALPANA BORDER ---------- */
.alpana {
    height:13px;
    margin:0 0 20px;
    background:
        radial-gradient(circle at 8px 6.5px,var(--gold) 2.1px,transparent 2.7px) 0 0/30px 13px repeat-x,
        radial-gradient(circle at 23px 6.5px,var(--hibiscus) 2.1px,transparent 2.7px) 0 0/30px 13px repeat-x;
    opacity:.65;
    animation:fadeDown .9s ease both;
}

/* ---------- NAVBAR ---------- */
.navbar {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:17px 23px;
    border:1px solid rgba(229,188,112,.3);
    border-radius:15px;
    background:rgba(22,9,16,.88);
    margin-bottom:14px;
    box-shadow:0 4px 30px rgba(0,0,0,.45);
    animation:fadeDown .7s ease both;
}

.brand {
    font-family:'Cinzel Decorative',serif;
    font-size:25px;
    font-weight:900;
    letter-spacing:3px;
    background:linear-gradient(90deg,#B97E2E,var(--gold-bright),var(--gold),#B97E2E);
    background-size:220% auto;
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
    animation:shimmer 7s linear infinite;
}

.nav-sub {
    color:#D5BDA7;
    font-size:10px;
    letter-spacing:2px;
}
.nav-clock {
    position:fixed;
    top:14px;
    right:18px;
    z-index:1000003;
    color:var(--gold);
    font-family:'Cinzel',serif;
    font-size:28px;
    font-weight:600;
    letter-spacing:1.6px;
    line-height:1;
    white-space:nowrap;
    pointer-events:none;
    text-shadow:0 2px 14px rgba(0,0,0,.55);
}

/* ---------- HERO ---------- */
.hero-title {
    font-family:'Cinzel Decorative',serif;
    font-size:clamp(28px,3.2vw,49px);
    font-weight:900;
    line-height:1.05;
    background:linear-gradient(90deg,#C48A39,#FFE9BE,var(--gold-bright),#C48A39);
    background-size:220% auto;
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
    animation:shimmer 8s linear infinite,fadeUp .9s ease both;
}

.hero-subtitle {
    font-family:'Cormorant Garamond',serif;
    font-size:29px;
    color:#F4D7A1;
    font-style:italic;
    animation:fadeUp .9s .15s ease both;
}

.bengali-blessing {
    font-family:'Tiro Bangla',serif;
    color:var(--hibiscus);
    font-size:19px;
    letter-spacing:1px;
    margin:6px 0 4px;
    animation:fadeUp .9s .25s ease both;
}

.eyebrow {
    color:var(--gold);
    font-size:10px;
    letter-spacing:4px;
    animation:fadeUp .8s ease both;
}

.hero-shell {
    max-width:820px;
    padding:36px 8px 18px;
    animation:fadeUp .9s ease both;
}
.hero-shell p {
    max-width:62ch;
    line-height:1.65;
}
.hero-metrics {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:14px;
    margin:18px 0 8px;
    max-width:640px;
}
.hero-cta {
    margin-top:6px;
}
.hero-frame {
    border:1px solid rgba(229,188,112,.55);
    border-radius:21px;
    padding:9px;
    background:linear-gradient(145deg,rgba(118,31,53,.18),rgba(255,255,255,.03));
    animation:glowPulse 4.6s ease-in-out infinite,scaleIn .9s ease both;
}
.hero-frame [data-testid="stImage"] img {
    transition:transform .55s ease;
}
.hero-frame [data-testid="stImage"]:hover img {
    transform:scale(1.015);
}

/* ---------- EXPERIENCE SECTION ---------- */
.experience {
    position:relative;
    margin:8px 0 28px;
    padding:8px 4px 28px;
    overflow:hidden;
    animation:fadeUp .9s ease both;
}
.experience::before,
.experience::after {
    content:"";
    position:absolute;
    width:180px;
    height:180px;
    border-radius:50%;
    pointer-events:none;
    z-index:0;
    filter:blur(2px);
}
.experience::before {
    left:-20px;
    bottom:-40px;
    background:radial-gradient(circle,rgba(255,140,50,.55) 0%,rgba(255,100,30,.18) 42%,transparent 70%);
}
.experience::after {
    right:40px;
    bottom:-50px;
    background:radial-gradient(circle,rgba(255,160,60,.45) 0%,rgba(214,51,108,.12) 45%,transparent 72%);
}
.experience-header {
    position:relative;
    z-index:1;
    display:grid;
    grid-template-columns:minmax(0,1.05fr) minmax(220px,.95fr);
    gap:28px;
    align-items:end;
    margin-bottom:28px;
}
.experience-copy {max-width:560px;padding-bottom:12px;}
.experience-kicker {
    display:flex;
    align-items:center;
    gap:14px;
    color:var(--gold);
    font-size:11px;
    letter-spacing:3.5px;
    font-weight:600;
    margin-bottom:14px;
}
.experience-kicker::after {
    content:"";
    flex:1;
    max-width:120px;
    height:1px;
    background:linear-gradient(90deg,rgba(229,188,112,.85),transparent);
}
.experience-title {
    font-family:'Cormorant Garamond',serif;
    font-size:clamp(40px,5.2vw,64px);
    line-height:1.05;
    color:#F7F0E6;
    font-weight:500;
    margin:0 0 18px;
}
.experience-title .script {
    display:inline-block;
    font-family:'Great Vibes',cursive;
    font-size:1.18em;
    color:var(--gold-bright);
    font-style:normal;
    font-weight:400;
    line-height:1;
    position:relative;
    padding:0 4px 8px 0;
}
.experience-title .script::after {
    content:"";
    position:absolute;
    left:0;
    right:8%;
    bottom:2px;
    height:10px;
    background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 20' fill='none'%3E%3Cpath d='M2 14 C40 4, 80 18, 120 8 S180 4, 198 12' stroke='%23C6284C' stroke-width='3' stroke-linecap='round'/%3E%3C/svg%3E") center / 100% 100% no-repeat;
}
.experience-lede {
    display:flex;
    gap:14px;
    align-items:stretch;
    max-width:420px;
}
.experience-lede-bar {
    width:2px;
    flex:0 0 2px;
    background:linear-gradient(180deg,#C6284C,#D6336C);
    border-radius:2px;
}
.experience-lede p {
    margin:0;
    color:#D9CBC3;
    font-size:14px;
    line-height:1.65;
    font-weight:400;
}
.experience-portrait {
    position:relative;
    justify-self:end;
    width:min(100%,420px);
    aspect-ratio:4/5;
    max-height:420px;
    border-radius:8px;
    overflow:hidden;
    mask-image:linear-gradient(180deg,#000 55%,transparent 100%);
    -webkit-mask-image:linear-gradient(180deg,#000 68%,transparent 100%);
}
.experience-portrait img {
    width:100%;
    height:100%;
    object-fit:cover;
    object-position:center 18%;
    display:block;
    filter:saturate(1.05) contrast(1.05);
}
.experience-bento {
    position:relative;
    z-index:1;
    display:grid;
    grid-template-columns:1.4fr 1fr 1fr;
    grid-template-rows:minmax(160px,1fr) minmax(160px,1fr);
    gap:14px;
    align-items:stretch;
}
.exp-card {
    border:1px solid rgba(229,188,112,.32);
    border-radius:16px;
    background:linear-gradient(160deg,rgba(28,12,18,.88),rgba(18,8,12,.78));
    backdrop-filter:blur(8px);
    box-shadow:0 10px 28px rgba(0,0,0,.28);
    transition:border-color .25s,transform .25s,box-shadow .25s;
    overflow:hidden;
    position:relative;
}
.exp-card:hover {
    border-color:rgba(229,188,112,.55);
    transform:translateY(-2px);
    box-shadow:0 14px 32px rgba(0,0,0,.35),0 0 18px rgba(229,188,112,.08);
}
.exp-card-bg {
    position:absolute;
    inset:0;
    background-size:cover;
    background-position:center;
    opacity:.72;
    filter:sepia(.18) saturate(1.05) brightness(.88);
}
.exp-card-bg::after {
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(165deg,rgba(12,6,10,.55) 0%,rgba(18,8,12,.48) 48%,rgba(12,6,10,.68) 100%);
}
.exp-card-01 {
    grid-column:1;
    grid-row:1 / 3;
    min-height:100%;
    display:flex;
    flex-direction:column;
    justify-content:flex-end;
}
.exp-card-01 .exp-card-bg {
    opacity:.78;
    background-position:center 40%;
    filter:sepia(.2) saturate(1.08) brightness(.92);
}
.exp-card-01 .exp-card-bg::after {
    background:
        linear-gradient(90deg,rgba(12,6,10,.82) 0%,rgba(12,6,10,.45) 46%,rgba(12,6,10,.18) 100%),
        linear-gradient(180deg,rgba(12,6,10,.08) 0%,rgba(12,6,10,.42) 100%);
}
.exp-card-01-content {
    position:relative;
    z-index:1;
    padding:26px 24px 24px;
    max-width:72%;
}
.exp-num {
    color:rgba(229,188,112,.7);
    font-size:11px;
    letter-spacing:2px;
    margin-bottom:8px;
}
.exp-card-01 h3 {
    margin:0 0 8px;
    color:#F7F0E6;
    font-family:'Cormorant Garamond',serif;
    font-size:34px;
    font-weight:600;
    line-height:1.1;
}
.exp-card-01 p {
    margin:0 0 18px;
    color:#C9B6AE;
    font-size:13px;
    line-height:1.55;
}
.exp-pill {
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:10px 22px;
    border-radius:999px;
    background:linear-gradient(120deg,#F0CD85,#C48A39);
    color:#180B0C !important;
    font-size:13px;
    font-weight:600;
    letter-spacing:.02em;
    text-decoration:none !important;
    border:1px solid rgba(255,233,190,.35);
    box-shadow:0 8px 24px rgba(229,188,112,.35);
    transition:background .3s,transform .3s,box-shadow .3s;
}
.exp-pill:hover {
    background:#FFE0A0;
    color:#180B0C !important;
    transform:translateY(-2px);
    box-shadow:0 10px 28px rgba(229,188,112,.48);
}
.exp-pill-sm {
    padding:7px 14px;
    font-size:11px;
    align-self:flex-start;
    margin-top:4px;
}
.exp-mini {
    padding:20px 16px 16px;
    min-height:0;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    gap:12px;
}
.exp-mini-body {
    position:relative;
    z-index:1;
    display:flex;
    flex-direction:column;
    gap:10px;
    margin-top:auto;
}
.exp-mini-top {
    position:relative;
    z-index:1;
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:10px;
}
.exp-mini-icon {
    width:28px;
    height:28px;
    color:var(--gold);
    flex:0 0 auto;
    filter:drop-shadow(0 2px 6px rgba(0,0,0,.55));
}
.exp-mini-icon svg {
    width:100%;
    height:100%;
    stroke:currentColor;
    fill:none;
    stroke-width:1.6;
    stroke-linecap:round;
    stroke-linejoin:round;
}
.exp-mini .exp-num {
    margin:0;
    font-size:12px;
    color:rgba(229,188,112,.75);
    text-shadow:0 2px 8px rgba(0,0,0,.55);
}
.exp-mini h4 {
    margin:0;
    color:#F0E2D4;
    font-family:'Cormorant Garamond',serif;
    font-size:20px;
    font-weight:600;
    line-height:1.2;
    text-shadow:0 2px 10px rgba(0,0,0,.55);
}
.exp-mini .exp-pill {box-shadow:0 6px 16px rgba(229,188,112,.28);}
.exp-card-02 {grid-column:2;grid-row:1;}
.exp-card-03 {grid-column:3;grid-row:1;}
.exp-card-04 {grid-column:2;grid-row:2;}
.exp-card-05 {grid-column:3;grid-row:2;}
@media (max-width:1100px) {
    .experience-bento {
        grid-template-columns:1.2fr 1fr 1fr;
        grid-template-rows:auto auto;
    }
    .exp-card-01 {grid-column:1;grid-row:1 / 3;min-height:280px;}
    .exp-card-02 {grid-column:2;grid-row:1;}
    .exp-card-03 {grid-column:3;grid-row:1;}
    .exp-card-04 {grid-column:2;grid-row:2;}
    .exp-card-05 {grid-column:3;grid-row:2;}
}
@media (max-width:980px) {
    .experience-header {grid-template-columns:1fr;gap:18px;}
    .experience-portrait {justify-self:center;width:min(100%,340px);max-height:300px;}
    .experience-copy {max-width:100%;}
    .experience-bento {
        grid-template-columns:1fr 1fr;
        grid-template-rows:none;
    }
    .exp-card-01 {
        grid-column:1 / -1;
        grid-row:auto;
        min-height:240px;
    }
    .exp-card-02,.exp-card-03,.exp-card-04,.exp-card-05 {
        grid-column:auto;grid-row:auto;
        min-height:150px;
    }
    .exp-card-01-content {max-width:78%;}
}
@media (max-width:620px) {
    .experience {padding:4px 0 20px;margin-bottom:18px;}
    .experience::before,.experience::after {width:120px;height:120px;}
    .experience-title {font-size:clamp(32px,9vw,42px);}
    .experience-portrait {max-height:240px;aspect-ratio:3/4;}
    .experience-bento {grid-template-columns:1fr;gap:12px;}
    .exp-card-01 {min-height:220px;}
    .exp-card-01-content {max-width:100%;padding:20px 18px 18px;}
    .exp-card-01 h3 {font-size:28px;}
    .exp-mini {padding:16px 14px 14px;min-height:132px;}
    .exp-pill {width:100%;justify-content:center;}
    .exp-pill-sm {width:auto;}
}

/* ---------- SECTIONS ---------- */
.section-title {
    font-family:'Cormorant Garamond',serif;
    font-size:40px;
    color:var(--cream);
    animation:fadeUp .8s .1s ease both;
}

.section-label {
    color:var(--gold);
    letter-spacing:4px;
    font-size:10px;
    margin-top:35px;
    animation:fadeUp .8s ease both;
}
.section-label::before {
    content:"◆ ";
    color:var(--hibiscus);
}

/* ---------- DIYA DIVIDER ---------- */
.diya-divider {
    display:flex;
    align-items:center;
    gap:20px;
    margin:36px 0 6px;
}
.dd-line {
    flex:1;
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(229,188,112,.55),transparent);
}
.dd-flame {
    font-size:27px;
    display:inline-block;
    animation:flicker 2.5s ease-in-out infinite;
}

/* ---------- MARQUEE ---------- */
.marquee {
    overflow:hidden;
    white-space:nowrap;
    border-top:1px solid rgba(229,188,112,.18);
    border-bottom:1px solid rgba(229,188,112,.18);
    padding:9px 0;
    margin:26px 0 4px;
    -webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);
    mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);
}
.marquee-inner {
    display:inline-block;
    animation:marqueeScroll 26s linear infinite;
    font-family:'Cormorant Garamond',serif;
    color:var(--gold);
    font-size:16px;
    letter-spacing:5px;
}
.marquee-inner .red {color:var(--hibiscus);}

/* ---------- CARDS ---------- */
.metric-box,.feature-card,.info-panel {
    background:linear-gradient(145deg,rgb(221 154 171 / 15%),rgba(255,255,255,.025));
    border:1px solid rgba(229,188,112,.22);
    border-radius:15px;
    padding:20px;
    transition:border-color .3s,transform .3s,box-shadow .3s;
    animation:fadeUp .85s ease both;
}

.metric-box:hover,.feature-card:hover {
    border-color:var(--gold);
    transform:translateY(-4px);
    box-shadow:0 10px 28px rgba(214,51,108,.16),0 0 18px rgba(229,188,112,.14);
}

.metric-value {
    color:var(--gold);
    font-family:'Cormorant Garamond',serif;
    font-size:30px;
    text-align:center;
}

.metric-caption {
    color:var(--muted);
    font-size:9px;
    letter-spacing:2px;
    text-align:center;
}

.feature-card {min-height:175px;}
.feature-icon {
    display:inline-block;
    margin-bottom:6px;
    color:var(--gold);
    font-family:'Cinzel Decorative',serif;
    font-size:12px;
    letter-spacing:3px;
    font-weight:700;
}
.feature-card h3 {
    color:var(--gold);
    font-family:'Cormorant Garamond',serif;
}

/* ---------- GALLERY ---------- */
.gallery-grid {
    column-count:3;
    column-gap:18px;
    margin-top:16px;
}
.gcard {
    break-inside:avoid;
    display:block;
    position:relative;
    margin:0 0 18px;
    border:1px solid rgba(229,188,112,.28);
    border-radius:16px;
    overflow:hidden;
    background:rgba(20,9,15,.6);
    box-shadow:0 6px 22px rgba(0,0,0,.45);
    transition:transform .35s ease,border-color .35s ease,box-shadow .35s ease;
}
.gcard img {
    width:100%;
    height:auto;
    display:block;
    background:#14090f;
    transition:transform .6s ease;
}
.gcard:hover {
    transform:translateY(-5px);
    border-color:var(--gold);
    box-shadow:0 16px 42px rgba(0,0,0,.55),0 0 26px rgba(229,188,112,.18);
}
.gcard:hover img {transform:scale(1.05);}
.gcard-overlay {
    position:absolute;
    left:0;right:0;bottom:0;
    padding:46px 15px 13px;
    background:linear-gradient(to top,rgba(9,4,8,.95) 28%,rgba(9,4,8,.55) 68%,transparent);
    pointer-events:none;
}
.gcard-name {
    font-family:'Cormorant Garamond',serif;
    color:var(--gold);
    font-size:21px;
    line-height:1.2;
}
.gcard-meta {
    color:var(--muted);
    font-size:9px;
    letter-spacing:1.5px;
    margin-top:5px;
}
.gcard-cat {
    display:inline-block;
    color:var(--hibiscus);
    border:1px solid rgba(214,51,108,.55);
    border-radius:20px;
    padding:1px 9px;
    margin-right:7px;
    font-size:8px;
    letter-spacing:2px;
}
@media(max-width:1100px){.gallery-grid{column-count:2;}}
@media(max-width:620px){.gallery-grid{column-count:1;}}

/* ---------- AI ASSISTANT ---------- */
.assistant-header {
    margin:6px 0 22px;
    max-width:720px;
    animation:fadeUp .85s ease both;
}
.assistant-kicker {
    display:flex;
    align-items:center;
    gap:14px;
    color:var(--gold);
    font-size:11px;
    letter-spacing:3.5px;
    font-weight:600;
    margin-bottom:12px;
}
.assistant-kicker::after {
    content:"";
    flex:1;
    max-width:140px;
    height:1px;
    background:linear-gradient(90deg,rgba(229,188,112,.85),transparent);
}
.assistant-title {
    margin:0 0 14px;
    font-family:'Cormorant Garamond',serif;
    font-size:clamp(34px,4.5vw,52px);
    line-height:1.08;
    color:#F8ECDD;
    font-weight:600;
}
.assistant-lede {
    display:flex;
    gap:14px;
    align-items:stretch;
    max-width:540px;
}
.assistant-lede-bar {
    width:2px;
    flex:0 0 2px;
    border-radius:2px;
    background:linear-gradient(180deg,#C6284C,#D6336C);
}
.assistant-lede p {
    margin:0;
    color:#E8D8C8;
    font-size:15px;
    line-height:1.65;
}
.assistant-label {
    color:var(--gold);
    font-size:10px;
    letter-spacing:2.5px;
    font-weight:600;
    margin:4px 0 8px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-label) {
    background:linear-gradient(145deg,rgba(48,18,28,.92),rgba(28,12,18,.9)) !important;
    border:1px solid rgba(229,188,112,.38) !important;
    border-radius:16px !important;
    padding:14px 16px 10px !important;
    box-shadow:0 12px 32px rgba(0,0,0,.35);
    animation:fadeUp .85s .08s ease both;
    backdrop-filter:blur(10px);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-stage-mark) {
    background:linear-gradient(160deg,rgba(26,12,18,.94),rgba(16,8,14,.92)) !important;
    border:1px solid rgba(229,188,112,.36) !important;
    border-radius:18px !important;
    padding:14px 12px 12px !important;
    min-height:280px;
    box-shadow:inset 0 0 0 1px rgba(255,255,255,.03),0 14px 36px rgba(0,0,0,.38);
    animation:fadeUp .85s .12s ease both;
    backdrop-filter:blur(10px);
}
.assistant-stage-mark {display:none;}
.assistant-footnote {
    margin:12px 0 88px;
    padding:11px 14px;
    border:1px solid rgba(229,188,112,.22);
    border-radius:12px;
    background:rgba(20,10,16,.75);
    color:#E8D8C8;
    font-size:12px;
    letter-spacing:.3px;
    line-height:1.5;
}
.assistant-footnote b {color:var(--gold);font-weight:600;}

/* ---------- VISION LAB ---------- */
.vision-header {
    margin:6px 0 22px;
    max-width:720px;
    animation:fadeUp .85s ease both;
}
.vision-kicker {
    display:flex;
    align-items:center;
    gap:14px;
    color:var(--gold);
    font-size:11px;
    letter-spacing:3.5px;
    font-weight:600;
    margin-bottom:12px;
}
.vision-kicker::after {
    content:"";
    flex:1;
    max-width:140px;
    height:1px;
    background:linear-gradient(90deg,rgba(229,188,112,.85),transparent);
}
.vision-title {
    margin:0 0 14px;
    font-family:'Cormorant Garamond',serif;
    font-size:clamp(34px,4.5vw,52px);
    line-height:1.08;
    color:#F8ECDD;
    font-weight:600;
}
.vision-lede {
    display:flex;
    gap:14px;
    align-items:stretch;
    max-width:560px;
}
.vision-lede-bar {
    width:2px;
    flex:0 0 2px;
    border-radius:2px;
    background:linear-gradient(180deg,#C6284C,#D6336C);
}
.vision-lede p {
    margin:0;
    color:#E8D8C8;
    font-size:15px;
    line-height:1.65;
}
.vision-label {
    color:var(--gold);
    font-size:10px;
    letter-spacing:2.5px;
    font-weight:600;
    margin:4px 0 8px;
}
.vision-empty {
    margin:8px 0 24px;
    padding:28px 22px;
    border:1px dashed rgba(229,188,112,.35);
    border-radius:16px;
    background:rgba(20,10,16,.55);
    text-align:center;
    animation:fadeUp .85s .1s ease both;
}
.vision-empty h3 {
    margin:0 0 8px;
    font-family:'Cormorant Garamond',serif;
    color:#F4D7A1;
    font-size:26px;
    font-weight:600;
}
.vision-empty p {
    margin:0 auto;
    max-width:420px;
    color:#E8D8C8;
    font-size:14px;
    line-height:1.6;
}
.vision-frame {
    border:1px solid rgba(229,188,112,.36);
    border-radius:16px;
    overflow:hidden;
    background:rgba(16,8,14,.88);
    box-shadow:0 14px 36px rgba(0,0,0,.4);
    animation:fadeUp .85s .1s ease both;
}
.vision-frame img {display:block;width:100%;}
.vision-report-title {
    margin:0 0 14px;
    font-family:'Cormorant Garamond',serif;
    color:#F8ECDD;
    font-size:28px;
    font-weight:600;
}
.vision-note {
    margin:14px 0 8px;
    padding:11px 14px;
    border:1px solid rgba(229,188,112,.22);
    border-radius:12px;
    background:rgba(20,10,16,.75);
    color:#E8D8C8;
    font-size:12px;
    line-height:1.5;
}
.vision-note b {color:var(--gold);font-weight:600;}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-label) {
    background:linear-gradient(145deg,rgba(48,18,28,.92),rgba(28,12,18,.9)) !important;
    border:1px solid rgba(229,188,112,.38) !important;
    border-radius:16px !important;
    padding:14px 16px 12px !important;
    box-shadow:0 12px 32px rgba(0,0,0,.35);
    animation:fadeUp .85s .08s ease both;
    backdrop-filter:blur(10px);
}
/* File uploader — strip Streamlit chrome, match wine/gold */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploader"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploader"] section,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploader"] > div {
    background:transparent !important;
    background-color:transparent !important;
    color:#E8D8C8 !important;
    border:none !important;
    box-shadow:none !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] > div {
    background:linear-gradient(145deg,rgba(28,12,18,.55),rgba(18,8,14,.4)) !important;
    background-color:transparent !important;
    border:1px dashed rgba(229,188,112,.42) !important;
    border-radius:14px !important;
    color:#E8D8C8 !important;
    box-shadow:inset 0 0 0 1px rgba(229,188,112,.06) !important;
    min-height:88px;
    padding:18px 16px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"]:hover {
    border-color:rgba(229,188,112,.72) !important;
    background:linear-gradient(145deg,rgba(42,16,24,.62),rgba(22,10,16,.5)) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] * {
    color:#E8D8C8 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] small,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] span,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] p {
    color:rgba(232,216,200,.72) !important;
    font-family:'Inter',sans-serif !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] svg {
    display:none !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] button,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploader"] button {
    background:linear-gradient(120deg,#F0CD85,#C48A39) !important;
    color:#180B0C !important;
    border:none !important;
    border-radius:999px !important;
    font-weight:600 !important;
    letter-spacing:.4px !important;
    box-shadow:0 6px 18px rgba(0,0,0,.28) !important;
    padding:0.45rem 1.1rem !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderDropzone"] button:hover,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploader"] button:hover {
    filter:brightness(1.06);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderFileName"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderFile"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-upload-mark) [data-testid="stFileUploaderFileData"] {
    background:rgba(18,9,14,.65) !important;
    border:1px solid rgba(229,188,112,.28) !important;
    border-radius:10px !important;
    color:#F3E6D8 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.vision-stage-mark) {
    background:linear-gradient(160deg,rgba(26,12,18,.94),rgba(16,8,14,.92)) !important;
    border:1px solid rgba(229,188,112,.36) !important;
    border-radius:18px !important;
    padding:16px 14px 14px !important;
    box-shadow:inset 0 0 0 1px rgba(255,255,255,.03),0 14px 36px rgba(0,0,0,.38);
    animation:fadeUp .85s .12s ease both;
    backdrop-filter:blur(10px);
}
.vision-upload-mark,
.vision-stage-mark {display:none;}

/* ---------- KOLKATA EXPLORER ---------- */
.explorer-header {
    margin:6px 0 22px;
    max-width:720px;
    animation:fadeUp .85s ease both;
}
.explorer-kicker {
    display:flex;
    align-items:center;
    gap:14px;
    color:var(--gold);
    font-size:11px;
    letter-spacing:3.5px;
    font-weight:600;
    margin-bottom:12px;
}
.explorer-kicker::after {
    content:"";
    flex:1;
    max-width:140px;
    height:1px;
    background:linear-gradient(90deg,rgba(229,188,112,.85),transparent);
}
.explorer-title {
    margin:0 0 14px;
    font-family:'Cormorant Garamond',serif;
    font-size:clamp(34px,4.5vw,52px);
    line-height:1.08;
    color:#F8ECDD;
    font-weight:600;
}
.explorer-lede {
    display:flex;
    gap:14px;
    align-items:stretch;
    max-width:560px;
}
.explorer-lede-bar {
    width:2px;
    flex:0 0 2px;
    border-radius:2px;
    background:linear-gradient(180deg,#C6284C,#D6336C);
}
.explorer-lede p {
    margin:0;
    color:#E8D8C8;
    font-size:15px;
    line-height:1.65;
}
.explorer-label {
    color:var(--gold);
    font-size:10px;
    letter-spacing:2.5px;
    font-weight:600;
    margin:4px 0 8px;
}
.explorer-place-name {
    margin:0 0 6px;
    font-family:'Cormorant Garamond',serif;
    color:#F8ECDD;
    font-size:28px;
    font-weight:600;
    line-height:1.15;
}
.explorer-place-meta {
    margin:0 0 14px;
    color:var(--gold);
    font-size:11px;
    letter-spacing:2px;
    font-weight:600;
}
.explorer-place-body {
    margin:0 0 12px;
    color:#E8D8C8;
    font-size:14px;
    line-height:1.65;
}
.explorer-place-bn {
    margin:0 0 16px;
    font-family:'Tiro Bangla',serif;
    color:#F4D7A1;
    font-size:16px;
    line-height:1.55;
}
.explorer-coords {
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin:0 0 14px;
}
.explorer-chip {
    padding:6px 10px;
    border:1px solid rgba(229,188,112,.28);
    border-radius:999px;
    background:rgba(18,9,14,.55);
    color:#E8D8C8;
    font-size:11px;
    letter-spacing:.4px;
}
.explorer-note {
    margin:12px 0 8px;
    padding:11px 14px;
    border:1px solid rgba(229,188,112,.22);
    border-radius:12px;
    background:rgba(20,10,16,.75);
    color:#E8D8C8;
    font-size:12px;
    line-height:1.5;
}
.explorer-note b {color:var(--gold);font-weight:600;}
.explorer-map-shell {
    border:1px solid rgba(229,188,112,.36);
    border-radius:16px;
    overflow:hidden;
    background:rgba(16,8,14,.9);
    box-shadow:0 14px 36px rgba(0,0,0,.4);
}
.explorer-map-shell iframe {display:block;width:100%;border:0;}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-label) {
    background:linear-gradient(145deg,rgba(48,18,28,.92),rgba(28,12,18,.9)) !important;
    border:1px solid rgba(229,188,112,.38) !important;
    border-radius:16px !important;
    padding:14px 16px 12px !important;
    box-shadow:0 12px 32px rgba(0,0,0,.35);
    animation:fadeUp .85s .08s ease both;
    backdrop-filter:blur(10px);
}
/* Keep Destination + Map panels equal height in the explorer row */
div[data-testid="stHorizontalBlock"]:has(.explorer-stage-mark) {
    align-items:stretch !important;
}
div[data-testid="stHorizontalBlock"]:has(.explorer-stage-mark) > div[data-testid="stColumn"] {
    display:flex !important;
    flex-direction:column !important;
}
div[data-testid="stHorizontalBlock"]:has(.explorer-stage-mark) > div[data-testid="stColumn"] > div {
    flex:1 1 auto !important;
    height:100% !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-stage-mark) {
    background:linear-gradient(160deg,rgba(26,12,18,.94),rgba(16,8,14,.92)) !important;
    border:1px solid rgba(229,188,112,.36) !important;
    border-radius:18px !important;
    padding:16px 14px 14px !important;
    box-shadow:inset 0 0 0 1px rgba(255,255,255,.03),0 14px 36px rgba(0,0,0,.38);
    animation:fadeUp .85s .12s ease both;
    backdrop-filter:blur(10px);
    min-height:600px !important;
    height:100% !important;
    box-sizing:border-box !important;
    display:flex !important;
    flex-direction:column !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-stage-mark) > div {
    flex:1 1 auto !important;
    display:flex !important;
    flex-direction:column !important;
    height:100% !important;
}
.explorer-spacer {
    flex:1 1 auto;
    min-height:48px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-label) [data-testid="stPills"] button,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-label) button[kind="pills"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-label) [data-testid="stBaseButton-pills"] {
    color:#F3E6D8 !important;
    border-color:rgba(229,188,112,.35) !important;
    background:rgba(24,12,18,.55) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-label) [data-testid="stPills"] button[aria-checked="true"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-label) button[kind="pillsActive"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.explorer-label) [data-testid="stBaseButton-pillsActive"] {
    color:#180B0C !important;
    border-color:rgba(229,188,112,.75) !important;
    background:linear-gradient(120deg,#F0CD85,#C48A39) !important;
}
.explorer-stage-mark {display:none;}

/* ---------- ANALYTICS INVENTORY ---------- */
.inventory-panel {
    margin:4px 0 14px;
    padding:4px 0 2px;
    border:1px solid rgba(229,188,112,.36);
    border-radius:18px;
    background:linear-gradient(160deg,rgba(26,12,18,.94),rgba(16,8,14,.92));
    box-shadow:inset 0 0 0 1px rgba(255,255,255,.03),0 14px 36px rgba(0,0,0,.38);
    overflow:hidden;
    animation:fadeUp .85s .1s ease both;
    backdrop-filter:blur(10px);
}
.inventory-scroll {
    max-height:420px;
    overflow:auto;
    padding:0;
}
.inventory-table {
    width:100%;
    border-collapse:collapse;
    font-family:'Inter',sans-serif;
    font-size:13px;
}
.inventory-table thead th {
    position:sticky;
    top:0;
    z-index:1;
    padding:12px 14px;
    text-align:left;
    color:var(--gold);
    font-size:10px;
    letter-spacing:2px;
    font-weight:600;
    background:rgba(32,14,20,.98);
    border-bottom:1px solid rgba(229,188,112,.32);
    white-space:nowrap;
}
.inventory-table tbody td {
    padding:11px 14px;
    color:#E8D8C8;
    border-bottom:1px solid rgba(229,188,112,.12);
    vertical-align:middle;
}
.inventory-table tbody tr:nth-child(even) td {
    background:rgba(229,188,112,.04);
}
.inventory-table tbody tr:hover td {
    background:rgba(214,51,108,.12);
}
.inventory-table .inv-name {
    color:#F8ECDD;
    font-family:'Cormorant Garamond',serif;
    font-size:15px;
}
.inventory-table .inv-cat {
    display:inline-block;
    padding:3px 9px;
    border:1px solid rgba(229,188,112,.28);
    border-radius:999px;
    background:rgba(18,9,14,.55);
    color:#F4D7A1;
    font-size:11px;
    letter-spacing:.4px;
}
.inventory-table .inv-num {
    color:#F4D7A1;
    font-variant-numeric:tabular-nums;
}
.inventory-foot {
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:12px;
    padding:10px 14px;
    border-top:1px solid rgba(229,188,112,.2);
    color:rgba(232,216,200,.7);
    font-size:12px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.inventory-actions-mark) {
    background:transparent !important;
    border:none !important;
    box-shadow:none !important;
    padding:0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.inventory-actions-mark) [data-testid="stDownloadButton"] button,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.inventory-actions-mark) button {
    background:linear-gradient(120deg,#F0CD85,#C48A39) !important;
    color:#180B0C !important;
    border:none !important;
    border-radius:999px !important;
    font-weight:600 !important;
    letter-spacing:.4px !important;
    box-shadow:0 6px 18px rgba(0,0,0,.28) !important;
}
.inventory-actions-mark {display:none;}

/* Pills contrast inside assistant toolbar */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-label) [data-testid="stPills"] button,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-label) button[kind="pills"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-label) [data-testid="stBaseButton-pills"] {
    color:#F3E6D8 !important;
    border-color:rgba(229,188,112,.35) !important;
    background:rgba(24,12,18,.55) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-label) [data-testid="stPills"] button[aria-checked="true"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-label) button[kind="pillsActive"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.assistant-label) [data-testid="stBaseButton-pillsActive"] {
    color:#1A0F0C !important;
    background:linear-gradient(120deg,#F0CD85,#C48A39) !important;
    border-color:rgba(255,233,190,.45) !important;
}

/* ---------- CHAT ---------- */
[data-testid="stChatMessage"] {
    background:linear-gradient(145deg,rgba(90,28,48,.55),rgba(30,14,22,.72));
    border:1px solid rgba(229,188,112,.28);
    border-left:3px solid rgba(229,188,112,.55);
    border-radius:16px;
    padding:14px 18px;
    margin-bottom:10px;
    color:#F3E6D8 !important;
}
[data-testid="stChatMessage"]:hover {border-color:rgba(229,188,112,.5);}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color:#F3E6D8 !important;
}
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] b {
    color:#FFD98E !important;
}
[data-testid="stChatMessage"] em {
    color:#F4D7A1 !important;
}
[data-testid="stChatMessage"] a {
    color:var(--gold-bright) !important;
}
[data-testid="stChatMessage"] hr {
    border-color:rgba(229,188,112,.25) !important;
}
[data-testid="stChatMessageContent"] {
    color:#F3E6D8 !important;
}
/* Sticky bottom chat bar — dock and the input surface stay clear */
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] [data-baseweb],
[data-testid="stChatInputTextArea"],
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background:transparent !important;
    background-color:transparent !important;
    background-image:none !important;
    box-shadow:none !important;
}
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    border-top:none !important;
    padding-bottom:10px !important;
}
[data-testid="stChatInput"] {
    border:1px solid rgba(229,188,112,.42) !important;
    border-radius:999px !important;
    max-width:100%;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    color:#F8ECDD !important;
    caret-color:var(--gold);
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color:rgba(232,216,200,.55) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color:rgba(229,188,112,.75) !important;
    box-shadow:none !important;
    background:transparent !important;
}
[data-testid="stChatInput"] button {
    background:linear-gradient(120deg,#F0CD85,#C48A39) !important;
    color:#180B0C !important;
    border:none !important;
}

/* ---------- VERSE ---------- */
.verse {
    border-left:3px solid var(--hibiscus);
    padding:4px 0 4px 22px;
    margin:22px 0;
}
.verse-bn {
    font-family:'Tiro Bangla',serif;
    color:var(--gold);
    font-size:22px;
    line-height:1.6;
}
.verse-en {
    font-family:'Cormorant Garamond',serif;
    color:var(--muted);
    font-style:italic;
    font-size:17px;
    margin-top:4px;
}

/* ---------- ROADMAP LIST ---------- */
.road-list {list-style:none;padding:0;margin:10px 0 0;}
.road-list li {
    padding:9px 0 9px 30px;
    position:relative;
    color:var(--muted);
    border-bottom:1px solid rgba(229,188,112,.12);
}
.road-list li:last-child {border-bottom:none;}
.road-list li::before {
    content:"✦";
    position:absolute;
    left:4px;
    color:var(--gold);
}
.road-list li.done::before {color:var(--hibiscus);}

/* ---------- WIDGETS ---------- */
.stButton>button,
.stButton>button p,
.stButton>button span,
[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] button p,
[data-testid="stDownloadButton"] button span,
[data-testid="stLinkButton"] a,
[data-testid="stLinkButton"] a p,
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button p {
    background:linear-gradient(120deg,#F0CD85,#C48A39);
    color:#180B0C !important;
    border:none;
    border-radius:30px;
    font-weight:600;
    transition:.3s;
}
.stButton>button:hover,
[data-testid="stDownloadButton"] button:hover,
[data-testid="stLinkButton"] a:hover {
    background:#FFE0A0;
    color:#180B0C !important;
    transform:translateY(-2px);
    box-shadow:0 8px 24px rgba(229,188,112,.42);
}

.stTextInput input,.stTextArea textarea {
    background:#21121A;
    color:white;
    border:1px solid #76503D;
}
.stTextInput input:focus,.stTextArea textarea:focus {
    border-color:var(--gold);
    box-shadow:0 0 12px rgba(229,188,112,.25);
}

[data-testid="stImage"] img {border-radius:11px;}

/* ---------- MUSIC PLAYER ---------- */
.music-player {
    position:fixed;
    bottom:18px;
    right:18px;
    z-index:2147483000; /* above Streamlit chrome so controls stay clickable */
    width:min(380px,calc(100vw - 36px));
    padding:14px 16px 12px;
    border:1px solid rgba(229,188,112,.38);
    border-radius:16px;
    background:rgba(17,8,14,.97);
    backdrop-filter:blur(12px);
    box-shadow:0 10px 36px rgba(0,0,0,.6),0 0 24px rgba(229,188,112,.12);
    animation:fadeUp .9s .3s ease both;
    font-family:'Inter',sans-serif;
    pointer-events:auto;
    isolation:isolate;
    touch-action:manipulation;
}
.music-player button,
.music-player input {
    pointer-events:auto;
    touch-action:manipulation;
}
/* Lift music player when sticky chat bar is on screen (AI Assistant) */
body:has([data-testid="stChatInput"]) .music-player {
    bottom:92px;
}
.mp-top {
    display:flex;
    align-items:center;
    gap:12px;
    margin-bottom:12px;
}
.mp-diya {
    font-size:26px;
    flex:0 0 auto;
    line-height:1;
}
.mp-diya.is-playing {animation:flicker 2.6s ease-in-out infinite;}
.mp-meta {flex:1;min-width:0;}
.mp-label {
    color:var(--gold);
    font-size:9px;
    letter-spacing:2.5px;
    font-weight:600;
    margin-bottom:2px;
}
.mp-track {
    color:#F4D7A1;
    font-family:'Cormorant Garamond',serif;
    font-size:17px;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
    line-height:1.2;
}
.mp-status {
    flex:0 0 auto;
    font-size:10px;
    letter-spacing:1.2px;
    text-transform:uppercase;
    padding:4px 10px;
    border-radius:999px;
    border:1px solid rgba(229,188,112,.28);
    color:#C9A57A;
    background:rgba(229,188,112,.06);
}
.mp-status.playing {
    color:#1a0f0c;
    background:var(--gold);
    border-color:var(--gold);
}
.mp-status.paused {color:#F4D7A1;border-color:rgba(244,215,161,.4);}
.mp-controls {
    display:flex;
    align-items:center;
    gap:10px;
}
.mp-btn {
    appearance:none;
    border:1px solid rgba(229,188,112,.45);
    background:rgba(229,188,112,.1);
    color:#F4D7A1;
    border-radius:10px;
    width:40px;
    height:40px;
    font-size:14px;
    cursor:pointer;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    transition:background .2s,border-color .2s,transform .15s;
    flex:0 0 auto;
    padding:0;
    line-height:1;
}
.mp-btn:hover {
    background:rgba(229,188,112,.22);
    border-color:var(--gold);
}
.mp-btn:active {transform:scale(.96);}
.mp-btn.primary {
    background:var(--gold);
    color:#1a0f0c;
    border-color:var(--gold);
    font-weight:700;
}
.mp-btn.primary:hover {filter:brightness(1.08);}
.mp-vol {
    flex:1;
    display:flex;
    align-items:center;
    gap:8px;
    min-width:0;
}
.mp-vol-icon {
    color:#C9A57A;
    font-size:13px;
    flex:0 0 auto;
    width:18px;
    text-align:center;
}
.mp-vol input[type=range] {
    -webkit-appearance:none;
    appearance:none;
    flex:1;
    height:4px;
    border-radius:999px;
    background:rgba(229,188,112,.25);
    outline:none;
    cursor:pointer;
    min-width:0;
}
.mp-vol input[type=range]::-webkit-slider-thumb {
    -webkit-appearance:none;
    appearance:none;
    width:14px;
    height:14px;
    border-radius:50%;
    background:var(--gold);
    border:none;
    box-shadow:0 0 8px rgba(229,188,112,.45);
    cursor:pointer;
}
.mp-vol input[type=range]::-moz-range-thumb {
    width:14px;
    height:14px;
    border-radius:50%;
    background:var(--gold);
    border:none;
    cursor:pointer;
}
.mp-vol-pct {
    color:#C9A57A;
    font-size:11px;
    letter-spacing:.5px;
    width:34px;
    text-align:right;
    flex:0 0 auto;
}
.mp-track-btn {
    appearance:none;
    border:none;
    background:transparent;
    padding:0;
    margin:0;
    width:100%;
    text-align:left;
    cursor:pointer;
    color:inherit;
    font:inherit;
}
.mp-track-btn:hover .mp-track {color:#FFE9BE;}
.mp-list-panel {
    display:none;
    margin-top:10px;
    padding:6px;
    border:1px solid rgba(229,188,112,.28);
    border-radius:12px;
    background:rgba(12,6,10,.92);
    max-height:168px;
    overflow:auto;
}
.music-player.mp-list-open .mp-list-panel {display:block;}
.mp-list-item {
    appearance:none;
    width:100%;
    display:flex;
    align-items:center;
    gap:8px;
    text-align:left;
    border:none;
    background:transparent;
    color:#E8D8C8;
    font-family:'Inter',sans-serif;
    font-size:12px;
    padding:8px 10px;
    border-radius:8px;
    cursor:pointer;
}
.mp-list-item:hover {background:rgba(229,188,112,.12);color:#F8ECDD;}
.mp-list-item.is-active {
    background:rgba(229,188,112,.18);
    color:#F0CD85;
    font-weight:600;
}
.mp-list-idx {
    color:rgba(229,188,112,.7);
    font-size:10px;
    letter-spacing:1px;
    flex:0 0 18px;
}
.mp-list-title {
    flex:1;
    min-width:0;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
    font-family:'Cormorant Garamond',serif;
    font-size:14px;
}
@media (max-width:520px) {
    .music-player {bottom:12px;right:12px;left:12px;width:auto;}
    body:has([data-testid="stChatInput"]) .music-player {bottom:96px;left:12px;right:12px;width:auto;}
    .mp-track {font-size:15px;}
}

/* ---------- FOOTER ---------- */
.footer {
    text-align:center;
    color:#A58A79;
    padding:40px;
    letter-spacing:3px;
    font-size:10px;
}
.footer-diyas {
    font-size:22px;
    letter-spacing:14px;
    margin-bottom:14px;
}
.footer-diyas span {
    display:inline-block;
    animation:flicker 2.8s ease-in-out infinite;
}
.footer-diyas span:nth-child(2) {animation-delay:.6s;}
.footer-diyas span:nth-child(3) {animation-delay:1.2s;}

/* ---------- GLOBAL PILL NAVBAR (centred in document flow) ---------- */
/* In-flow so it never covers the brand header / alpana / hero.
   Streamlit's host is stElementContainer and shrinks to the pill, which
   pins the bar to the left of the page. Stretch that host, then centre. */
div[data-testid="element-container"]:has(div[data-testid="stRadio"]),
div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
    display:flex !important;
    justify-content:center !important;
    align-items:center !important;
    align-self:stretch !important;
    width:100% !important;
    max-width:100% !important;
    margin:0 !important;
    padding:0 !important;
    height:auto !important;
    min-height:0 !important;
    position:relative !important;
    z-index:5 !important;
}
div[data-testid="stRadio"] {
    position:relative !important;
    top:auto !important;
    left:auto !important;
    right:auto !important;
    transform:none !important;
    width:max-content !important;
    max-width:calc(100vw - 24px) !important;
    margin:0 auto !important;
    z-index:5 !important;
    display:flex !important;
    justify-content:center !important;
    pointer-events:auto !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"],
div[data-testid="stRadio"] > div {
    display:inline-flex !important;
    justify-content:center !important;
    align-items:center !important;
    flex-wrap:wrap !important;
    gap:2px !important;
    margin:0 !important;
    padding:5px 7px !important;
    background:linear-gradient(180deg,rgba(52,16,26,.96),rgba(18,7,12,.94)) !important;
    border:1px solid rgba(229,188,112,.4) !important;
    border-radius:999px !important;
    box-shadow:0 14px 40px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.05) !important;
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
    pointer-events:auto !important;
}
/* Visually hide radio circles WITHOUT display:none (keeps Streamlit click wiring) */
div[data-testid="stRadio"] label {
    position:relative !important;
    margin:0 !important;
    padding:6px 10px !important;
    border-radius:999px !important;
    background:transparent !important;
    border:1px solid transparent !important;
    transition:background .18s ease, border-color .18s ease, color .18s ease !important;
    cursor:pointer !important;
    pointer-events:auto !important;
    flex:0 0 auto !important;
}
div[data-testid="stRadio"] label > div:first-child {
    position:absolute !important;
    width:1px !important;
    height:1px !important;
    padding:0 !important;
    margin:-1px !important;
    overflow:hidden !important;
    clip:rect(0,0,0,0) !important;
    white-space:nowrap !important;
    border:0 !important;
    opacity:0 !important;
}
div[data-testid="stRadio"] label input[type="radio"] {
    position:absolute !important;
    opacity:0 !important;
    width:1px !important;
    height:1px !important;
    pointer-events:auto !important;
}
div[data-testid="stRadio"] label p {
    font-family:'Inter',sans-serif !important;
    font-size:11.5px !important;
    font-weight:500 !important;
    letter-spacing:.25px !important;
    color:#E8D5C8 !important;
    margin:0 !important;
    white-space:nowrap !important;
    pointer-events:none !important; /* clicks fall through to label */
}
@media (min-width:1100px) {
    div[data-testid="stRadio"] > div[role="radiogroup"],
    div[data-testid="stRadio"] > div {
        flex-wrap:nowrap !important;
    }
}
div[data-testid="stRadio"] label:hover {
    background:rgba(118,31,53,.42) !important;
    border-color:rgba(229,188,112,.22) !important;
}
div[data-testid="stRadio"] label:hover p { color:#F8ECDD !important; }
/* Active item */
div[data-testid="stRadio"] label:has(input:checked),
div[data-testid="stRadio"] label[data-checked="true"] {
    background:rgba(118,31,53,.85) !important;
    border-color:rgba(229,188,112,.55) !important;
    box-shadow:0 0 0 1px rgba(229,188,112,.18), 0 6px 18px rgba(118,31,53,.35) !important;
}
div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stRadio"] label[data-checked="true"] p {
    color:#F0CD85 !important;
    font-weight:600 !important;
}

@media (max-width:900px) {
    .block-container {
        padding-left:1rem !important;
        padding-right:1rem !important;
        padding-top:0.9rem;
    }
    .navbar {
        flex-wrap:wrap;
        gap:8px 16px;
        padding:14px 16px;
    }
    .hero-shell {padding:24px 4px 12px;}
    .hero-subtitle {font-size:clamp(20px,4.5vw,26px);}
    .bengali-blessing {font-size:16px;}
    .marquee-inner {font-size:14px;letter-spacing:3px;}
}

@media (max-width:700px) {
    .brand {font-size:clamp(14px,4.2vw,17px);letter-spacing:2px;}
    .nav-sub {font-size:8px;letter-spacing:1.5px;width:100%;}
    .nav-clock {font-size:20px; top:10px; right:12px;}
    .navbar {padding:12px 14px;}
    .hero-title {font-size:clamp(28px,8vw,40px) !important;}
    .hero-shell {padding:18px 0 8px;max-width:100%;}
    .hero-shell p {font-size:14px;max-width:100%;}
    .hero-metrics {
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:8px;
        max-width:100%;
    }
    .metric-box,.feature-card,.info-panel {padding:14px 10px;}
    .metric-value {font-size:22px;}
    .metric-caption {font-size:8px;letter-spacing:1.2px;}
    .footer {padding:28px 12px;letter-spacing:2px;}
    .footer-diyas {letter-spacing:8px;}
    .section-title {font-size:clamp(28px,7vw,36px);}
    /* iOS/mobile: fixed backgrounds jank — scroll instead */
    .stApp {
        background-attachment:scroll !important;
    }
}

@media (max-width:480px) {
    .block-container {
        padding-left:0.7rem !important;
        padding-right:0.7rem !important;
        padding-bottom:5.5rem;
    }
    .hero-metrics {grid-template-columns:1fr;gap:10px;}
    .hero-metrics .metric-box {padding:16px 14px;}
    .eyebrow {letter-spacing:2.5px;font-size:9px;}
    .embers {opacity:.55;}
    div[data-testid="stRadio"] {
        max-width:calc(100vw - 12px) !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"],
    div[data-testid="stRadio"] > div {
        border-radius:22px !important;
        padding:4px 5px !important;
        gap:1px !important;
        max-width:calc(100vw - 12px);
        overflow-x:auto;
        flex-wrap:nowrap !important;
        justify-content:flex-start !important;
        -webkit-overflow-scrolling:touch;
    }
    div[data-testid="stRadio"] label { padding:6px 10px !important; flex:0 0 auto; }
    div[data-testid="stRadio"] label p {font-size:11px !important;}
}
</style>

<div class="embers">
    <span style="--x:4%;  --d:0s;    --t:15s;  --s:5px"></span>
    <span style="--x:11%; --d:4s;    --t:18s;  --s:4px"></span>
    <span style="--x:18%; --d:8s;    --t:13s;  --s:6px"></span>
    <span style="--x:26%; --d:2.5s;  --t:19s;  --s:4px"></span>
    <span style="--x:34%; --d:7s;    --t:16s;  --s:5px"></span>
    <span style="--x:43%; --d:1s;    --t:14s;  --s:4px"></span>
    <span style="--x:52%; --d:9s;    --t:20s;  --s:6px"></span>
    <span style="--x:60%; --d:5s;    --t:15s;  --s:4px"></span>
    <span style="--x:68%; --d:11s;   --t:17s;  --s:5px"></span>
    <span style="--x:76%; --d:3s;    --t:13.5s;--s:4px"></span>
    <span style="--x:84%; --d:6.5s;  --t:18.5s;--s:6px"></span>
    <span style="--x:92%; --d:10s;   --t:16s;  --s:4px"></span>
    <span style="--x:97%; --d:2s;    --t:21s;  --s:5px"></span>
</div>
""", unsafe_allow_html=True)


# =====================================================
# IMAGE DATASET
# =====================================================

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

def get_images():
    if not ASSET_DIR.exists():
        return []
    return sorted([
        p for p in ASSET_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        and p.stat().st_size > 0
    ])

def image_title(path):
    name = path.stem
    return name.replace("_", " ").replace("-", " ").replace(".", " ").title()

def music_display_title(path):
    """Human-facing track titles (overrides awkward filenames)."""
    stem = Path(path).stem.lower()
    if "osama" in stem:
        return "Oshyama Oshyama"
    return image_title(path)

def image_category(filename):
    name = str(filename).lower()
    if "kishori" in name:
        return "Kishori Kali"
    if "dakshineswar" in name:
        return "Temples"
    if "kalighat" in name:
        return "Temples"
    if "fata" in name or "kesto" in name:
        return "Kali Puja"
    if "club" in name or "pandal" in name:
        return "Pandals"
    if "maa" in name or "kali" in name:
        return "Maa Kali"
    return "Cultural Collection"

def build_analytics_pdf(df, counts, weight, total_mb, largest_row):
    """Build a themed PDF dataset report (bytes)."""
    import pandas as pd
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    gold = colors.HexColor("#C48A39")
    wine = colors.HexColor("#761F35")
    hibiscus = colors.HexColor("#D6336C")
    cream = colors.HexColor("#F8ECDD")
    ink = colors.HexColor("#1A0C12")
    muted = colors.HexColor("#5C4A48")
    row_alt = colors.HexColor("#F7EFE4")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="KALI VISION AI — Dataset Report",
        author="KALI VISION AI",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "KaliTitle",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=22,
        textColor=wine,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "KaliSub",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=11,
        textColor=gold,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "KaliSection",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=13,
        textColor=wine,
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "KaliBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=ink,
        leading=12,
    )
    small_style = ParagraphStyle(
        "KaliSmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=muted,
        alignment=TA_CENTER,
    )
    cell_style = ParagraphStyle(
        "KaliCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        textColor=ink,
        leading=9,
    )

    story = []
    story.append(Paragraph("KALI VISION AI", title_style))
    story.append(Paragraph("Cultural Dataset Report · Bengal Archive", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=8))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%d %B %Y, %H:%M')} · "
        f"{len(df)} sacred frames · {total_mb:.2f} MB of heritage",
        small_style,
    ))
    story.append(Spacer(1, 8))

    # Summary metrics
    story.append(Paragraph("Archive summary", section_style))
    summary_data = [[
        Paragraph(f"<b>{len(df)}</b><br/>Sacred frames", body_style),
        Paragraph(f"<b>{df['Category'].nunique()}</b><br/>Collections", body_style),
        Paragraph(f"<b>{total_mb:.1f} MB</b><br/>Heritage weight", body_style),
        Paragraph(
            f"<b>{largest_row['Size KB']/1024:.2f} MB</b><br/>Largest · {html_escape(str(largest_row['Image'])[:42])}",
            body_style,
        ),
    ]]
    summary = Table(summary_data, colWidths=[60 * mm, 55 * mm, 55 * mm, 80 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cream),
        ("BOX", (0, 0), (-1, -1), 1, gold),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5D2B0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(summary)
    story.append(Spacer(1, 8))

    # Category breakdown
    story.append(Paragraph("Composition by collection", section_style))
    cat_rows = [[Paragraph("<b>Category</b>", cell_style),
                 Paragraph("<b>Frames</b>", cell_style),
                 Paragraph("<b>Weight (MB)</b>", cell_style)]]
    weight_map = {r["Category"]: r["Size MB"] for _, r in weight.iterrows()}
    for _, r in counts.iterrows():
        cat_rows.append([
            Paragraph(html_escape(str(r["Category"])), cell_style),
            Paragraph(str(int(r["Images"])), cell_style),
            Paragraph(f"{weight_map.get(r['Category'], 0):.2f}", cell_style),
        ])
    cat_table = Table(cat_rows, colWidths=[90 * mm, 35 * mm, 40 * mm])
    cat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), wine),
        ("TEXTCOLOR", (0, 0), (-1, 0), cream),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, row_alt]),
        ("BOX", (0, 0), (-1, -1), 0.8, gold),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0CFA8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 10))

    # Inventory ledger
    story.append(Paragraph("Dataset inventory", section_style))
    inv = df[["Image", "Category", "Width", "Height", "Orientation", "Size KB"]].copy()
    inv = inv.sort_values(["Category", "Image"]).reset_index(drop=True)
    header = [
        Paragraph("<b>Image</b>", cell_style),
        Paragraph("<b>Category</b>", cell_style),
        Paragraph("<b>W</b>", cell_style),
        Paragraph("<b>H</b>", cell_style),
        Paragraph("<b>Orientation</b>", cell_style),
        Paragraph("<b>Size KB</b>", cell_style),
    ]
    inv_rows = [header]
    for _, row in inv.iterrows():
        w = "—" if pd.isna(row["Width"]) else str(int(row["Width"]))
        h = "—" if pd.isna(row["Height"]) else str(int(row["Height"]))
        name = str(row["Image"])
        if len(name) > 48:
            name = name[:45] + "…"
        inv_rows.append([
            Paragraph(html_escape(name), cell_style),
            Paragraph(html_escape(str(row["Category"])), cell_style),
            Paragraph(w, cell_style),
            Paragraph(h, cell_style),
            Paragraph(html_escape(str(row["Orientation"])), cell_style),
            Paragraph(f'{row["Size KB"]:.2f}', cell_style),
        ])

    inv_table = Table(
        inv_rows,
        colWidths=[95 * mm, 42 * mm, 22 * mm, 22 * mm, 32 * mm, 28 * mm],
        repeatRows=1,
    )
    inv_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), wine),
        ("TEXTCOLOR", (0, 0), (-1, 0), cream),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, row_alt]),
        ("BOX", (0, 0), (-1, -1), 0.8, gold),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E0CFA8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, 0), 1, hibiscus),
    ]))
    story.append(inv_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.6, color=gold, spaceAfter=6))
    story.append(Paragraph(
        "✦ Built with intelligence · Inspired by divinity · Jai Maa Kali ✦",
        small_style,
    ))

    doc.build(story)
    return buf.getvalue()

STATIC_IMG_DIR = BASE_DIR / "static" / "assets"
WEB_IMG_DIR = STATIC_IMG_DIR / "web"

def sync_static_assets(files, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for p in files:
        d = dest_dir / p.name
        if not d.exists() or d.stat().st_size != p.stat().st_size:
            shutil.copy2(p, d)

def web_image(src: Path, max_edge: int = 1200, quality: int = 72):
    """Small JPEG used on screen. The file in assets/ stays the original."""
    WEB_IMG_DIR.mkdir(parents=True, exist_ok=True)
    dest = WEB_IMG_DIR / f"{src.stem}-{max_edge}.jpg"
    meta_path = dest.with_suffix(".meta")
    # Trust a copy already on disk. A mtime check re-encodes every photo
    # after deploy, because git gives the files a new checkout time.
    fresh = dest.exists() and dest.stat().st_size > 0
    if not fresh:
        from PIL import Image
        with Image.open(src) as im:
            im = im.convert("RGB")
            im.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
            width, height = im.size
            im.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
        meta_path.write_text(f"{width} {height}")
    width = height = ""
    try:
        width, height = meta_path.read_text().split()
    except Exception:
        pass
    url = "/app/static/assets/web/" + quote(dest.name)
    kb = round(dest.stat().st_size / 1024) if dest.exists() else 0
    label = f"{width} × {height} · {kb} KB" if width and height else f"{kb} KB"
    return url, label, width, height


def original_image_size(path: Path):
    """Width and height without reopening the original on every Analytics run."""
    key = f"{path.name}|{path.stat().st_size}"
    cache_path = WEB_IMG_DIR / "original-sizes.json"
    data = {}
    try:
        data = json.loads(cache_path.read_text())
    except Exception:
        data = {}
    hit = data.get(key)
    if isinstance(hit, list) and len(hit) == 2:
        return int(hit[0]), int(hit[1])
    from PIL import Image
    with Image.open(path) as im:
        width, height = im.size
    data[key] = [width, height]
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data))
    except Exception:
        pass
    return width, height


# =====================================================
# BENGALI WELCOME GATE — full-screen first paint
# =====================================================

def _metro_deep_link_active() -> bool:
    qp = st.query_params
    return bool(
        qp.get("metro_dest")
        or qp.get("metro_olat")
        or qp.get("metro_geo_err")
        or qp.get("metro_reset")
        or qp.get("metro_near_me")
    )


def _render_bengali_welcome() -> None:
    """Full-viewport Bengali welcome; Continue dismisses into the site.

    Rendered as a pinned components iframe so Streamlit layout cannot clip it.
    """
    _idol = ASSET_DIR / "kali_garland_idol.webp"
    if _idol.exists():
        sync_static_assets([_idol], STATIC_IMG_DIR)
    st.markdown(
        """
<style>
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu, footer, header { display:none !important; }
.block-container {
  padding:0 !important;
  max-width:100% !important;
  margin:0 !important;
}
section.main > div { padding-top:0 !important; }
/* Welcome gate: collapse hook wrappers; keep the pinned scroll iframe */
[data-testid="stVerticalBlock"] { gap:0 !important; }
[data-testid="stElementContainer"][height="0px"],
[data-testid="stElementContainer"][width="0px"][height="0px"],
[data-testid="stElementContainer"]:has(iframe[height="0"]),
[data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] > style:only-child),
[data-testid="stForm"]:has(.kali-welcome-restore) {
  position:fixed !important;
  left:-10000px !important;
  top:0 !important;
  width:0 !important;
  height:0 !important;
  margin:0 !important;
  padding:0 !important;
  overflow:hidden !important;
  opacity:0 !important;
  pointer-events:none !important;
}
/* Prefer the marked welcome frame once pinFrame runs */
iframe[data-kali-welcome-frame="1"] {
  position:fixed !important;
  inset:0 !important;
  width:100vw !important;
  height:100vh !important;
  height:100dvh !important;
  z-index:2147483000 !important;
  border:0 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cormorant+Garamond:wght@500;600&family=Inter:wght@400;600&family=Tiro+Bangla&display=swap" rel="stylesheet" />
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #070408;
  }
  @keyframes flicker {
    0%, 100% { opacity: 1; filter: drop-shadow(0 0 6px rgba(255,170,60,.9)); transform: scale(1); }
    18% { opacity: .78; filter: drop-shadow(0 0 14px rgba(255,120,40,1)); transform: scale(1.04); }
    42% { opacity: .95; filter: drop-shadow(0 0 8px rgba(255,190,90,.85)); transform: scale(.98); }
    67% { opacity: .7; filter: drop-shadow(0 0 18px rgba(255,100,30,1)); transform: scale(1.06); }
  }
  @keyframes floatDiya {
    0%, 100% { transform: translateY(0) translateX(0) rotate(-2deg); }
    50% { transform: translateY(-14px) translateX(6px) rotate(2deg); }
  }
  @keyframes scrollUnfurl {
    from { opacity: 0; transform: translateY(28px) scale(.96); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }
  @keyframes glowPulse {
    0%, 100% { box-shadow: 0 18px 50px rgba(0,0,0,.45), 0 0 0 1px rgba(180,120,50,.25); }
    50% { box-shadow: 0 22px 60px rgba(0,0,0,.5), 0 0 40px rgba(229,188,112,.18); }
  }
  .wrap {
    position: relative;
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: clamp(20px, 4vh, 40px) clamp(14px, 4vw, 40px);
    text-align: center;
    background:
      radial-gradient(ellipse at 50% 0%, rgba(118,31,53,.55) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 100%, rgba(214,51,108,.18) 0%, transparent 45%),
      linear-gradient(165deg, #070408 0%, #12070e 40%, #1a0a12 75%, #080509 100%);
    color: #3a2418;
    overflow: hidden;
  }
  .wrap::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 20% 30%, rgba(229,188,112,.06), transparent 40%),
      radial-gradient(circle at 80% 70%, rgba(255,140,60,.05), transparent 35%);
    pointer-events: none;
  }

  /* Floating diyas */
  .diyas { position: absolute; inset: 0; pointer-events: none; z-index: 2; }
  .diya {
    position: absolute;
    width: 28px;
    height: 42px;
    animation: floatDiya var(--float, 4.5s) ease-in-out infinite;
    animation-delay: var(--delay, 0s);
  }
  .diya .bowl {
    position: absolute;
    left: 50%;
    bottom: 0;
    width: 22px;
    height: 10px;
    transform: translateX(-50%);
    border-radius: 0 0 12px 12px;
    background: linear-gradient(180deg, #C9A24A 0%, #8B6914 55%, #5C3D0E 100%);
    box-shadow: 0 2px 6px rgba(0,0,0,.45);
  }
  .diya .bowl::before {
    content: "";
    position: absolute;
    left: 2px; right: 2px; top: -3px;
    height: 5px;
    border-radius: 999px;
    background: linear-gradient(180deg, #E8C86A, #A67C1A);
  }
  .diya .flame {
    position: absolute;
    left: 50%;
    bottom: 10px;
    width: 10px;
    height: 18px;
    transform: translateX(-50%);
    border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
    background: radial-gradient(circle at 50% 70%, #FFF4C2 0%, #FFB347 35%, #FF6A1A 70%, transparent 100%);
    animation: flicker var(--flick, 2.4s) ease-in-out infinite;
    animation-delay: var(--delay, 0s);
  }
  .diya .flame::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: 2px;
    width: 4px;
    height: 8px;
    transform: translateX(-50%);
    border-radius: 50%;
    background: #FFF8E0;
    opacity: .9;
  }
  .d1 { top: 8%; left: 8%; --float: 5.2s; --flick: 2.1s; --delay: 0s; }
  .d2 { top: 14%; right: 10%; --float: 4.6s; --flick: 2.8s; --delay: .4s; }
  .d3 { top: 42%; left: 4%; --float: 5.8s; --flick: 2.3s; --delay: .9s; }
  .d4 { top: 48%; right: 5%; --float: 4.9s; --flick: 2.6s; --delay: .2s; }
  .d5 { bottom: 16%; left: 11%; --float: 5.4s; --flick: 2.0s; --delay: 1.1s; }
  .d6 { bottom: 12%; right: 12%; --float: 4.3s; --flick: 2.7s; --delay: .6s; }
  .d7 { top: 22%; left: 22%; --float: 6s; --flick: 2.4s; --delay: 1.4s; width: 24px; height: 36px; }
  .d8 { top: 28%; right: 20%; --float: 5.1s; --flick: 2.2s; --delay: .8s; width: 24px; height: 36px; }
  .d9 { bottom: 28%; left: 18%; --float: 4.7s; --flick: 2.9s; --delay: .3s; width: 20px; height: 32px; }
  .d10 { bottom: 32%; right: 16%; --float: 5.6s; --flick: 2.15s; --delay: 1.2s; width: 20px; height: 32px; }

  /* Royal scroll */
  .scroll {
    position: relative;
    z-index: 3;
    width: min(680px, 94vw);
    max-height: calc(100vh - 28px);
    max-height: calc(100dvh - 28px);
    display: flex;
    flex-direction: column;
    overflow: visible;
    animation: scrollUnfurl .95s ease both, glowPulse 4.5s ease-in-out infinite;
  }
  .scroll-bloom {
    position: absolute;
    inset: 0;
    z-index: 6;
    pointer-events: none;
    overflow: visible;
  }
  .hibiscus {
    position: absolute;
    left: 0;
    top: 0;
    width: 64px;
    height: 64px;
    opacity: 0;
    filter: drop-shadow(0 2px 2px rgba(70, 12, 24, .38));
    will-change: transform, opacity;
  }
  .hibiscus svg { display: block; width: 100%; height: 100%; }
  .garland-cord {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    overflow: visible;
    pointer-events: none;
  }
  .idol-slot {
    position: absolute;
    left: 50%;
    top: 50%;
    z-index: 2;
    width: min(460px, 78vw);
    transform: translate(-50%, -50%);
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    filter: drop-shadow(0 18px 36px rgba(0,0,0,.55));
  }
  .idol {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: transparent;
  }
  .garland-fall {
    position: absolute;
    inset: 0;
    z-index: 8;
    pointer-events: none;
    overflow: visible;
  }
  .wrap.is-leaving .scroll {
    animation: none !important;
  }
  .scroll-roll {
    height: 22px;
    border-radius: 999px;
    background:
      repeating-linear-gradient(90deg,
        #6B4423 0 8px, #8B5A2B 8px 14px, #A67C52 14px 18px, #5C3A1E 18px 22px);
    box-shadow:
      inset 0 2px 0 rgba(255,220,150,.25),
      inset 0 -3px 6px rgba(0,0,0,.35),
      0 4px 12px rgba(0,0,0,.4);
    position: relative;
    z-index: 2;
  }
  .scroll-roll::before,
  .scroll-roll::after {
    content: "";
    position: absolute;
    top: 50%;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #E8C86A, #8B6914 60%, #4A3008);
    box-shadow: 0 0 0 2px rgba(90,55,20,.5);
    transform: translateY(-50%);
  }
  .scroll-roll::before { left: -6px; }
  .scroll-roll::after { right: -6px; }
  .scroll-body {
    position: relative;
    margin: -6px 10px;
    padding: clamp(18px, 3vh, 28px) clamp(22px, 4vw, 36px) clamp(16px, 2.4vh, 22px);
    overflow-y: auto;
    min-height: 0;
    background:
      linear-gradient(180deg, rgba(255,248,230,.2), transparent 18%),
      radial-gradient(ellipse at 50% 0%, rgba(180,120,50,.12), transparent 55%),
      linear-gradient(165deg, #F3E2C0 0%, #E8D0A4 38%, #DFC28E 72%, #D4B57A 100%);
    border-left: 1px solid rgba(140,95,40,.35);
    border-right: 1px solid rgba(140,95,40,.35);
    box-shadow:
      inset 0 0 40px rgba(120,70,20,.12),
      inset 18px 0 28px rgba(90,50,15,.08),
      inset -18px 0 28px rgba(90,50,15,.08);
  }
  .scroll-body::before {
    content: "";
    position: absolute;
    inset: 10px;
    border: 1px solid rgba(150,100,40,.28);
    border-radius: 4px;
    pointer-events: none;
  }
  .ornament {
    font-size: 18px;
    letter-spacing: .35em;
    color: #8B5A2B;
    margin: 0 0 10px;
    opacity: .85;
  }
  .kicker {
    font-family: Inter, sans-serif;
    font-size: 10px;
    letter-spacing: .28em;
    text-transform: uppercase;
    color: #7A4E1E;
    margin: 0 0 14px;
  }
  .title {
    font-family: "Cinzel Decorative", serif;
    font-size: clamp(22px, 3.6vw, 32px);
    font-weight: 400;
    line-height: 1.25;
    margin: 0 0 8px;
    color: #4A1A24;
    text-shadow: 0 1px 0 rgba(255,245,220,.5);
  }
  .brand {
    font-family: "Tiro Bangla", "Cinzel", serif;
    font-size: clamp(16px, 2.4vw, 20px);
    letter-spacing: .04em;
    color: #6B1F32;
    margin: 0 0 12px;
    font-weight: 600;
  }
  .divider {
    width: min(220px, 60%);
    height: 1px;
    margin: 0 auto 18px;
    background: linear-gradient(90deg, transparent, #A67C2A, transparent);
  }
  .body {
    font-family: "Tiro Bangla", "Cormorant Garamond", serif;
    font-size: clamp(14px, 1.9vw, 16.5px);
    line-height: 1.65;
    color: #3F2A1C;
    margin: 0 0 12px;
  }
  .body strong {
    font-weight: 600;
    color: #4A1A24;
  }
  .signoff {
    margin: 4px 0 14px;
    font-family: "Tiro Bangla", "Cormorant Garamond", serif;
    font-size: clamp(13px, 1.8vw, 15px);
    line-height: 1.55;
    color: #5C3A1E;
  }
  .signoff strong {
    display: block;
    margin-top: 2px;
    font-family: "Cinzel", serif;
    font-size: clamp(13px, 1.8vw, 15px);
    letter-spacing: .08em;
    color: #6B1F32;
  }
  .go {
    appearance: none;
    border: 1px solid rgba(120,70,20,.45);
    border-radius: 999px;
    min-width: min(300px, 80%);
    min-height: 50px;
    padding: 12px 24px;
    cursor: pointer;
    font-family: "Tiro Bangla", Inter, sans-serif;
    font-size: clamp(15px, 2.2vw, 18px);
    font-weight: 600;
    letter-spacing: .03em;
    color: #F8ECDD;
    background: linear-gradient(135deg, #6B1F32 0%, #8B2A3E 45%, #A33A4E 100%);
    box-shadow: 0 10px 28px rgba(80,20,30,.35), inset 0 1px 0 rgba(255,220,180,.2);
  }
  .go:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
  }
  .mark {
    margin-top: 18px;
    font-family: Inter, sans-serif;
    font-size: 11px;
    letter-spacing: .18em;
    color: #7A4E1E;
  }
  @media (max-width: 700px) {
    .d7, .d8, .d9, .d10 { display: none; }
    .wrap { padding: 8px 10px 12px; }
    .scroll {
      width: min(420px, 88vw);
      max-height: min(74dvh, 620px);
    }
    .scroll-roll { height: 18px; }
    .scroll-body { padding: 14px 16px 12px; }
    .ornament { margin-bottom: 6px; font-size: 11px; }
    .title { font-size: 20px; letter-spacing: .03em; line-height: 1.2; }
    .brand { font-size: 15px; margin: 4px 0 6px; }
    .divider { margin: 8px auto 10px; }
    .body { font-size: 13.5px; line-height: 1.42; margin: 0 0 7px; }
    .signoff { font-size: 13px; margin-top: 6px; }
    .go {
      position: sticky;
      bottom: 0;
      z-index: 2;
      min-height: 44px;
      margin-top: 10px;
      padding: 10px 18px;
    }
    .hibiscus { width: 36px; height: 36px; }
  }
</style>
</head>
<body>
  <div class="wrap">
    <div class="diyas" aria-hidden="true">
      <div class="diya d1"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d2"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d3"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d4"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d5"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d6"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d7"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d8"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d9"><span class="flame"></span><span class="bowl"></span></div>
      <div class="diya d10"><span class="flame"></span><span class="bowl"></span></div>
    </div>

    <div class="scroll" role="dialog" aria-label="Bengali welcome scroll">
      <div class="scroll-roll" aria-hidden="true"></div>
      <div class="scroll-body">
        <div class="ornament">❖ ✦ ❖</div>
        <h1 class="title">Welcome to KALI VISION AI</h1>
        <p class="brand">জয় মা কালী! Jai Maa Kali!</p>
        <div class="divider" aria-hidden="true"></div>
        <p class="body">নমস্কার সবাইকে! ❤️</p>
        <p class="body">
          Welcome to KALI VISION AI! A small initiative to bring you closer to Maa Kali,
          her divine forms, Bengal's rich culture, sacred temples, and beautiful traditions.
        </p>
        <p class="body">
          চলুন, একসঙ্গে Maa Kali-র ইতিহাস, মহিমা ও আমাদের ঐতিহ্যকে জানি, আবিষ্কার করি এবং উদযাপন করি।
        </p>
        <p class="body">
          This is a humble effort, and I sincerely apologize if I have unintentionally made any mistakes.
          Your suggestions and corrections are always welcome.
        </p>
        <p class="body"><strong>Explore, learn and celebrate our heritage.</strong></p>
        <p class="body">May Maa Kali bless you all with strength and happiness.</p>
        <p class="body"><strong>জয় মা কালী!</strong> ❤️</p>
        <p class="signoff">Made with love and devotion by <strong>Anuska Ghosh</strong></p>
        <p class="signoff">নমস্কারান্তে, <strong>Anuska Ghosh</strong></p>
        <button class="go" id="kali-welcome-go" type="button">ওয়েবসাইটে প্রবেশ করুন</button>
      </div>
      <div class="scroll-roll" aria-hidden="true"></div>
      <div class="scroll-bloom" id="kali-scroll-bloom" aria-hidden="true"></div>
    </div>
    <div class="idol-slot" id="kali-idol-slot">
      <img class="idol" id="kali-idol" alt="মা কালি" />
    </div>
  </div>
  <script>
  (function () {
    function hibiscusPetal(deg, color) {
      return '<path d="M0,1 C9,-1 16,-12 8,-23 C4,-27 0,-25 -3,-20 C-13,-12 -9,-1 0,1Z" fill="'
        + color + '" stroke="#9A2E40" stroke-width="0.6" transform="rotate(' + deg + ')"/>';
    }
    var FLOWER = '<svg viewBox="0 0 64 64" aria-hidden="true">'
      + '<g transform="translate(32,36)">'
      + '<ellipse rx="5.2" ry="3.4" cy="9" fill="#4E7840" transform="rotate(16)"/>'
      + '<ellipse rx="5.2" ry="3.4" cy="9" fill="#3C6230" transform="rotate(78)"/>'
      + hibiscusPetal(0, "#C33848")
      + hibiscusPetal(72, "#B43244")
      + hibiscusPetal(144, "#C73E52")
      + hibiscusPetal(216, "#B43244")
      + hibiscusPetal(288, "#C33848")
      + '<circle r="5.8" fill="#8A1E34"/>'
      + '<circle r="2.9" fill="#5A1224"/>'
      + '<path d="M0,0 C1,-10 0,-20 1,-32" stroke="#E7C56B" stroke-width="2" fill="none" stroke-linecap="round"/>'
      + '<circle cx="-2.8" cy="-16" r="1.55" fill="#F4D78A"/>'
      + '<circle cx="3.1" cy="-21" r="1.45" fill="#E9C15C"/>'
      + '<circle cx="-1.3" cy="-26" r="1.4" fill="#F0CC72"/>'
      + '<circle cx="1" cy="-33" r="2.2" fill="#F8E3A4"/>'
      + '</g></svg>';
    var bloom = document.getElementById("kali-scroll-bloom");
    var scrollEl = bloom && bloom.parentElement;
    var falling = false;
    var wave = 0;
    var leaving = false;
    var settleGarland = function () {};
    var narrow = window.innerWidth <= 700;
    var SIZE = narrow ? 36 : 64;
    var GAP = narrow ? 32 : 56;
    function paint(node, x, y, rot, opacity) {
      node.style.opacity = String(opacity);
      node.style.transform = "translate(" + x.toFixed(2) + "px," + y.toFixed(2) + "px) rotate(" + rot.toFixed(2) + "deg)";
    }
    function smoothstep(p) {
      return p * p * p * (p * (p * 6 - 15) + 10);
    }
    function curvePoint(p0, p1, p2, p3, t) {
      var t2 = t * t;
      var t3 = t2 * t;
      return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3);
    }
    function buildPath(side, W, H) {
      var xSide = side === "left" ? -14 : (W - SIZE + 14);
      var yTop = 0;
      var yBot = H - SIZE + 4;
      var dir = side === "left" ? 1 : -1;
      var tilt = side === "left" ? -7 : 7;
      var pts = [];
      var y = yTop;
      var guard = 0;
      while (guard < 48) {
        pts.push({ x: xSide, y: y, rot: tilt });
        if (y >= yBot - 0.5) break;
        y = Math.min(yBot, y + GAP);
        guard += 1;
      }
      var x = xSide;
      var center = (W - SIZE) / 2;
      var limit = side === "left" ? center : center + GAP;
      guard = 0;
      while (guard < 40) {
        var next = x + dir * GAP;
        if (side === "left" && next > limit + 0.5) break;
        if (side === "right" && next < limit - 0.5) break;
        x = next;
        var along = Math.abs(x - xSide) / Math.max(1, Math.abs(limit - xSide));
        pts.push({ x: x, y: yBot, rot: tilt * (1 - along) });
        guard += 1;
      }
      return pts;
    }
    function arcLengths(pts) {
      var lens = [0];
      var prev = { x: pts[0].x, y: pts[0].y - GAP };
      for (var i = 0; i < pts.length; i++) {
        var dx = pts[i].x - prev.x;
        var dy = pts[i].y - prev.y;
        lens.push(lens[lens.length - 1] + Math.sqrt(dx * dx + dy * dy));
        prev = pts[i];
      }
      return lens;
    }
    function cordD(centers) {
      if (centers.length < 2) return "";
      var d = "M" + centers[0].cx.toFixed(1) + " " + centers[0].cy.toFixed(1);
      for (var i = 1; i < centers.length; i++) {
        var a = centers[i - 1];
        var b = centers[i];
        var mx = (a.cx + b.cx) / 2;
        var my = (a.cy + b.cy) / 2;
        d += " Q" + a.cx.toFixed(1) + " " + a.cy.toFixed(1) + " " + mx.toFixed(1) + " " + my.toFixed(1);
      }
      var end = centers[centers.length - 1];
      d += " L" + end.cx.toFixed(1) + " " + end.cy.toFixed(1);
      return d;
    }
    function runCascade() {
      if (!bloom || !scrollEl || falling) return;
      var W = scrollEl.clientWidth;
      var H = scrollEl.clientHeight;
      if (W < 40 || H < 40) {
        setTimeout(runCascade, 80);
        return;
      }
      falling = true;
      var runId = ++wave;
      bloom.innerHTML = "";
      bloom.style.transition = "";
      bloom.style.opacity = "1";
      var leftPts = buildPath("left", W, H);
      var rightPts = buildPath("right", W, H);
      var leftLens = arcLengths(leftPts);
      var rightLens = arcLengths(rightPts);
      var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "garland-cord");
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      function makeCord() {
        var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "#5C7A40");
        path.setAttribute("stroke-width", "2.4");
        path.setAttribute("stroke-linecap", "round");
        path.setAttribute("stroke-linejoin", "round");
        svg.appendChild(path);
        return path;
      }
      var cordL = makeCord();
      var cordR = makeCord();
      bloom.appendChild(svg);
      function makeNodes(pts) {
        var nodes = [];
        for (var i = 0; i < pts.length; i++) {
          var node = document.createElement("div");
          node.className = "hibiscus";
          node.innerHTML = FLOWER;
          bloom.appendChild(node);
          nodes.push(node);
        }
        return nodes;
      }
      var leftNodes = makeNodes(leftPts);
      var rightNodes = makeNodes(rightPts);
      var started = performance.now();
      var DURATION = 8600;
      function placeStrand(pts, nodes, lens, dist) {
        var centers = [];
        for (var i = 0; i < pts.length; i++) {
          var a = lens[i];
          var b = lens[i + 1];
          var node = nodes[i];
          if (dist <= a + 0.2) {
            node.style.opacity = "0";
            continue;
          }
          var from = i === 0
            ? { x: pts[0].x, y: pts[0].y - GAP * 0.65, rot: pts[0].rot }
            : pts[i - 1];
          var span = Math.max(1, b - a);
          var p = dist >= b ? 1 : (dist - a) / span;
          var prev = i <= 1 ? from : pts[i - 2];
          var next = i + 1 < pts.length ? pts[i + 1] : pts[i];
          var x = p >= 1 ? pts[i].x : curvePoint(prev.x, from.x, pts[i].x, next.x, p);
          var y = p >= 1 ? pts[i].y : curvePoint(prev.y, from.y, pts[i].y, next.y, p);
          var rot = from.rot + (pts[i].rot - from.rot) * p;
          var fade = p >= 1 ? 1 : Math.min(1, p / 0.4);
          paint(node, x, y, rot, fade);
          centers.push({ cx: x + SIZE / 2, cy: y + SIZE / 2 });
        }
        return centers;
      }
      settleGarland = function () {
        if (runId !== wave) return;
        cordL.setAttribute("d", cordD(placeStrand(leftPts, leftNodes, leftLens, leftLens[leftLens.length - 1])));
        cordR.setAttribute("d", cordD(placeStrand(rightPts, rightNodes, rightLens, rightLens[rightLens.length - 1])));
      };
      function tick(now) {
        if (runId !== wave || !bloom.isConnected) return;
        var t = Math.min(1, (now - started) / DURATION);
        var eased = smoothstep(t);
        cordL.setAttribute("d", cordD(placeStrand(leftPts, leftNodes, leftLens, eased * leftLens[leftLens.length - 1])));
        cordR.setAttribute("d", cordD(placeStrand(rightPts, rightNodes, rightLens, eased * rightLens[rightLens.length - 1])));
        if (t < 1) {
          requestAnimationFrame(tick);
          return;
        }
        setTimeout(function () {
          if (runId !== wave || !bloom.isConnected) return;
          bloom.style.transition = "opacity .7s ease";
          bloom.style.opacity = "0";
          setTimeout(function () {
            if (runId !== wave) return;
            bloom.innerHTML = "";
            bloom.style.transition = "";
            falling = false;
            runCascade();
          }, 760);
        }, 2800);
      }
      requestAnimationFrame(tick);
    }
    setTimeout(runCascade, 320);

    function pinFrame() {
      try {
        var frame = window.frameElement;
        if (!frame) return;
        frame.setAttribute("data-kali-welcome-frame", "1");
        frame.style.cssText = [
          "position:fixed",
          "inset:0",
          "top:0",
          "left:0",
          "right:0",
          "bottom:0",
          "width:100vw",
          "height:100vh",
          "max-width:100vw",
          "max-height:100vh",
          "z-index:2147483000",
          "border:0",
          "margin:0",
          "padding:0",
          "background:#070408",
          "display:block"
        ].join(";");
        if (frame.parentElement) {
          frame.parentElement.style.cssText =
            "margin:0;padding:0;height:0;overflow:visible;";
        }
      } catch (e) {}
    }
    pinFrame();
    setTimeout(pinFrame, 50);
    setTimeout(pinFrame, 250);

    var wrap = document.querySelector(".wrap");
    var idolSlot = document.getElementById("kali-idol-slot");
    var idol = document.getElementById("kali-idol");
    if (idol) {
      var origin = "";
      try { origin = window.parent.location.origin || ""; } catch (e) {}
      idol.src = origin + "/app/static/assets/kali_garland_idol.webp?v=3";
    }

    function enterSite() {
      // No localStorage/cookie writes — the scroll greets every visitor.
      // components.html iframes are sandboxed WITHOUT allow-top-navigation —
      // location.assign/reload below is blocked in Chrome. The hidden
      // kali-welcome-restore form only needs allow-forms (present), so dismiss
      // through it the same way the refresh-time restore probe does.
      try {
        var pdoc = window.parent.document;
        var form = pdoc.querySelector('[data-testid="stForm"]:has(.kali-welcome-restore)');
        var input = form && form.querySelector("input");
        var sbtn = form && form.querySelector("button");
        if (input && sbtn) {
          var proto = window.parent.HTMLInputElement.prototype;
          var desc = Object.getOwnPropertyDescriptor(proto, "value");
          if (desc && desc.set) desc.set.call(input, "1");
          else input.value = "1";
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.dispatchEvent(new Event("change", { bubbles: true }));
          sbtn.click();
          return;
        }
      } catch (eForm) {}
      try {
        var u = new URL(window.parent.location.href);
        u.searchParams.set("kali_welcome", "done");
        window.parent.location.assign(u.toString());
      } catch (e2) {
        try { window.parent.location.reload(); } catch (e3) {}
      }
    }

    var btn = document.getElementById("kali-welcome-go");
    if (!btn) return;
    btn.addEventListener("click", function () {
      if (leaving) return;
      leaving = true;
      btn.disabled = true;
      try { settleGarland(); } catch (e) {}
      wave += 1;

      var wRect = wrap.getBoundingClientRect();
      var sRect = scrollEl.getBoundingClientRect();
      var cx = sRect.left + sRect.width / 2;
      var bottomY = sRect.bottom - 90;

      var aspect = 820 / 1273;
      var maxH = window.innerHeight * 0.9;
      var maxW = Math.min(520, window.innerWidth * 0.84);
      var idolH = maxH;
      var idolW = idolH * aspect;
      if (idolW > maxW) {
        idolW = maxW;
        idolH = idolW / aspect;
      }
      idolSlot.style.width = Math.round(idolW) + "px";
      idolSlot.style.height = Math.round(idolH) + "px";
      idolSlot.style.left = "50%";
      idolSlot.style.top = "50%";
      idolSlot.style.visibility = "visible";
      idolSlot.style.opacity = "0";
      idolSlot.style.transform = "translate(-50%, -50%)";
      var iRect = idolSlot.getBoundingClientRect();
      idolSlot.style.transform = "translate(-50%, -42%)";

      var fall = document.createElement("div");
      fall.className = "garland-fall";
      wrap.appendChild(fall);
      var flowers = Array.prototype.slice.call(bloom.querySelectorAll(".hibiscus"));
      var kept = [];
      for (var i = 0; i < flowers.length; i++) {
        var node = flowers[i];
        if (parseFloat(node.style.opacity || "0") < 0.25) continue;
        var r = node.getBoundingClientRect();
        fall.appendChild(node);
        node.style.left = (r.left - wRect.left) + "px";
        node.style.top = (r.top - wRect.top) + "px";
        node.style.transform = "none";
        node.style.opacity = "1";
        kept.push(node);
      }
      kept.sort(function (a, b) {
        function key(el) {
          var box = el.getBoundingClientRect();
          var x = box.left + box.width / 2;
          var y = box.top + box.height / 2;
          if (y > bottomY) return 10000 + x;
          if (x < cx) return y;
          return 20000 + (sRect.bottom - y);
        }
        return key(a) - key(b);
      });
      var cord = bloom.querySelector(".garland-cord");
      if (cord) cord.style.opacity = "0";

      wrap.classList.add("is-leaving");
      scrollEl.style.animation = "none";
      var scrollUp = -(sRect.top + sRect.height + 28);
      var futureTop = iRect.top - wRect.top;
      var futureLeft = iRect.left - wRect.left;
      var futureW = iRect.width;
      var futureH = iRect.height || idolH;

      requestAnimationFrame(function () {
        scrollEl.style.transition = "transform 1.25s cubic-bezier(.55,.04,.28,1)";
        scrollEl.style.transform = "translateY(" + scrollUp + "px)";
        idolSlot.style.transition = "opacity 2.6s ease, transform 2.8s cubic-bezier(.16,.8,.24,1)";
        idolSlot.style.opacity = "1";
        idolSlot.style.transform = "translate(-50%, -50%)";
      });

      setTimeout(function () {
        function malaPoint(t) {
          var droop = Math.sin(t * Math.PI);
          return {
            x: futureLeft + futureW * (0.30 + 0.40 * t),
            y: futureTop + futureH * (0.25 + 0.20 * droop)
          };
        }
        var steps = 28;
        var curve = [];
        var lens = [0];
        for (var i = 0; i <= steps; i++) {
          curve.push(malaPoint(i / steps));
          if (i) {
            var dx = curve[i].x - curve[i - 1].x;
            var dy = curve[i].y - curve[i - 1].y;
            lens.push(lens[i - 1] + Math.sqrt(dx * dx + dy * dy));
          }
        }
        var length = lens[lens.length - 1];
        var spacing = SIZE * 0.86;
        var want = Math.max(5, Math.min(7, Math.round(length / spacing) + 1));
        function pointAlong(dist) {
          var d = Math.max(0, Math.min(length, dist));
          var i = 1;
          while (i < lens.length && lens[i] < d) i += 1;
          var a = curve[i - 1];
          var b = curve[Math.min(i, curve.length - 1)];
          var span = Math.max(1, lens[i] - lens[i - 1]);
          var p = (d - lens[i - 1]) / span;
          return { x: a.x + (b.x - a.x) * p, y: a.y + (b.y - a.y) * p };
        }
        var spots = [];
        for (var s = 0; s < want; s++) {
          spots.push(pointAlong(want === 1 ? length / 2 : (s / (want - 1)) * length));
        }
        var chosen = [];
        if (kept.length <= want) chosen = kept.slice();
        else {
          for (var c = 0; c < want; c++) {
            chosen.push(kept[Math.round(c * (kept.length - 1) / (want - 1))]);
          }
        }
        for (var j = 0; j < kept.length; j++) {
          if (chosen.indexOf(kept[j]) === -1) {
            kept[j].style.transition = "opacity .4s ease";
            kept[j].style.opacity = "0";
          }
        }
        var half = SIZE / 2;
        var motions = [];
        for (var k = 0; k < chosen.length; k++) {
          var spot = spots[Math.min(k, spots.length - 1)];
          var t = chosen.length === 1 ? 0.5 : k / (chosen.length - 1);
          var flower = chosen[k];
          flower.style.transition = "none";
          flower.style.zIndex = String(10 + k);
          motions.push({
            node: flower,
            sx: parseFloat(flower.style.left) || 0,
            sy: parseFloat(flower.style.top) || 0,
            ex: spot.x - half,
            ey: spot.y - half,
            rot: (t - 0.5) * 14,
            delay: k * 46
          });
        }
        var glideStart = performance.now();
        var GLIDE = 2800;
        function glide(now) {
          var pending = false;
          for (var m = 0; m < motions.length; m++) {
            var item = motions[m];
            var local = now - glideStart - item.delay;
            var p = local <= 0 ? 0 : Math.min(1, local / GLIDE);
            if (p < 1) pending = true;
            var e = smoothstep(p);
            var u = 1 - e;
            var mx = (item.sx + item.ex) / 2;
            var my = (item.sy + item.ey) / 2 + Math.min(48, Math.abs(item.ex - item.sx) * 0.08);
            var x = u * u * item.sx + 2 * u * e * mx + e * e * item.ex;
            var y = u * u * item.sy + 2 * u * e * my + e * e * item.ey;
            item.node.style.transform = "translate(" + (x - item.sx).toFixed(2) + "px," + (y - item.sy).toFixed(2) + "px) rotate(" + (item.rot * e).toFixed(2) + "deg)";
          }
          if (pending) requestAnimationFrame(glide);
        }
        requestAnimationFrame(glide);
      }, 520);

      setTimeout(enterSite, 5600);
    });
  })();
  </script>
</body>
</html>
        """,
        height=720,
        scrolling=False,
    )
    st.stop()


if "kali_welcome_dismissed" not in st.session_state:
    st.session_state.kali_welcome_dismissed = False
# Welcome scroll shows on EVERY fresh visit — no cookie/localStorage restore.

# Continue button on the welcome iframe lands here
if st.query_params.get("kali_welcome") == "done":
    st.session_state.kali_welcome_dismissed = True
    try:
        del st.query_params["kali_welcome"]
    except Exception:
        pass

# Restore "already continued" from localStorage via a hidden soft form
st.markdown(
    """
<style>
[data-testid="stForm"]:has(.kali-welcome-restore) {
  position:fixed !important;
  left:-9999px !important;
  top:0 !important;
  width:1px !important;
  height:1px !important;
  opacity:0 !important;
  overflow:hidden !important;
  pointer-events:none !important;
  z-index:-1 !important;
}
</style>
    """,
    unsafe_allow_html=True,
)
with st.form("kali_welcome_restore", border=False, clear_on_submit=True):
    st.markdown(
        '<div class="kali-welcome-restore" style="display:none" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    _welcome_restore_val = st.text_input(
        "kali_welcome_restore_val",
        key="kali_welcome_restore_payload",
        label_visibility="collapsed",
    )
    _welcome_restore_go = st.form_submit_button("restore welcome")
if _welcome_restore_go and str(_welcome_restore_val or "").strip() == "1":
    st.session_state.kali_welcome_dismissed = True
_nav_for_welcome = st.query_params.get("nav")
_metro_bridge_hit = _metro_deep_link_active()
_nav_skip_welcome = _nav_for_welcome in {
    "AI Assistant",
    "Gallery",
    "Kolkata Explorer",
    "Kolkata Metro",
    "Analytics",
    "About",
}

# Deep links / nav CTAs skip the welcome — and must STAMP dismissed,
# otherwise consuming metro_* query params on the next rerun re-opens the scroll.
if (_metro_bridge_hit or _nav_skip_welcome) and not st.session_state.kali_welcome_dismissed:
    st.session_state.kali_welcome_dismissed = True

_skip_welcome = (
    st.session_state.kali_welcome_dismissed
    or _metro_bridge_hit
    or _nav_skip_welcome
)
if not _skip_welcome:
    components.html(
        """
<script>
(function () {
  try {
    var win = window.parent;
    try { if (win.top && win.top.document) win = win.top; } catch (e0) {}
    var ls = null;
    try { ls = win.localStorage.getItem("kali_welcome_v1"); } catch (e) {}
    console.warn("[kali-welcome] SHOWING scroll", {
      href: String(win.location.href || ""),
      search: String(win.location.search || ""),
      localStorage: ls,
      stack: "welcome gate open — see [kali-welcome] gate in terminal"
    });
  } catch (e) {
    try { console.warn("[kali-welcome] SHOWING scroll (log failed)", String(e)); } catch (e2) {}
  }
})();
</script>
        """,
        height=0,
        width=0,
    )
    _render_bengali_welcome()


# =====================================================
# NAVIGATION (Streamlit radio — reliable page switching)
# Brand header stays in document flow above the pill nav.
# =====================================================

PAGES = [
    "Home", "AI Assistant", "Gallery",
    "Kolkata Explorer", "Kolkata Metro", "Analytics", "About"
]

if "page" not in st.session_state:
    st.session_state.page = "Home"

# Drop removed pages from stale session / bookmarks
if st.session_state.get("navigation") == "Vision Lab":
    st.session_state.navigation = "Home"
if st.session_state.get("navigation") not in (None, *PAGES):
    st.session_state.navigation = "Home"

# Deep-link CTAs from HTML (e.g. Experience "Explore Now").
# Never wipe metro_* bridges when clearing nav — GPS / pick handoff needs them.
_METRO_BRIDGE_KEYS = (
    "metro_dest",
    "metro_plat",
    "metro_plon",
    "metro_olat",
    "metro_olon",
    "metro_oacc",
    "metro_geo_err",
    "metro_near_me",
    "metro_reset",
)


def _clear_nav_query_keep_metro() -> None:
    kept = {k: st.query_params.get(k) for k in _METRO_BRIDGE_KEYS if st.query_params.get(k) is not None}
    try:
        del st.query_params["nav"]
    except Exception:
        pass
    for k, v in kept.items():
        if v is not None:
            st.query_params[k] = v


_nav_q = st.query_params.get("nav")
if _nav_q == "Vision Lab":
    _clear_nav_query_keep_metro()
elif _nav_q in PAGES:
    st.session_state.navigation = _nav_q
    _clear_nav_query_keep_metro()

# Metro bridges (destination pick / GPS / reset) must open the Metro page and
# leave their query params intact for modules.metro.metro_ui to consume.
if (
    st.query_params.get("metro_dest")
    or st.query_params.get("metro_olat")
    or st.query_params.get("metro_geo_err")
    or st.query_params.get("metro_reset")
    or st.query_params.get("metro_near_me")
):
    st.session_state.navigation = "Kolkata Metro"

# Brand + alpana for every page except Metro (map-first fullscreen)
_nav_preview = st.session_state.get("navigation", "Home")
if _nav_preview != "Kolkata Metro":
    st.markdown("""
<div class="nav-clock" id="kali-nav-clock"></div>
<div class="navbar">
    <div class="brand">✦ KALI VISION AI</div>
    <div class="nav-sub">BENGAL · CULTURE · INTELLIGENCE</div>
</div>
<div class="alpana"></div>
""", unsafe_allow_html=True)
    components.html(
        """
<script>
(function () {
  var win = window.parent;
  try { if (win.top && win.top.document) win = win.top; } catch (e) {}
  var doc = win.document;
  function tick() {
    var el = doc.getElementById("kali-nav-clock");
    if (!el) return;
    var text = new Date().toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit"
    });
    if (el.textContent !== text) el.textContent = text;
  }
  tick();
  if (win.__kaliNavClock) clearInterval(win.__kaliNavClock);
  win.__kaliNavClock = setInterval(tick, 1000);
})();
</script>
        """,
        height=0,
        width=0,
    )

page = st.radio(
    "Navigation",
    PAGES,
    horizontal=True,
    label_visibility="collapsed",
    key="navigation",
)

# Cover the previous page the instant Metro is chosen. Streamlit keeps the
# old charts on screen until the map script finishes, and they show through
# on the map-paper background for a couple of seconds.
_METRO_COVER_JS = r"""
window.__kaliMetroArm = function (show) {
  var d = document;
  function hideCharts() {
    d.querySelectorAll('[data-testid="stPlotlyChart"], .js-plotly-plot').forEach(function (node) {
      node.style.setProperty("visibility", "hidden", "important");
    });
  }
  function ensureStyle() {
    var style = d.getElementById("kali-metro-enter-style");
    if (!style) {
      style = d.createElement("style");
      style.id = "kali-metro-enter-style";
      d.head.appendChild(style);
    }
    style.textContent = "body.kali-metro-entering [data-testid='stMain'] canvas,body.kali-metro-entering .js-plotly-plot,body.kali-metro-entering [data-testid='stPlotlyChart'],body.kali-metro-entering .gallery-grid,body.kali-metro-entering .experience,body.kali-metro-entering .hero-shell,body.kali-metro-entering .gcard{visibility:hidden !important;}body.kali-metro-leaving .metro-dock-panel,body.kali-metro-leaving [data-metro-dock],body.kali-metro-leaving .metro-sheet-list,body.kali-metro-leaving .metro-sheet-row,body.kali-metro-leaving .metro-sheet-foot,body.kali-metro-leaving .metro-sheet-empty,body.kali-metro-leaving #metro-find-route,body.kali-metro-leaving [data-testid='stForm']:has(.metro-pick-bridge),body.kali-metro-leaving [data-testid='stForm']:has(.metro-route-bridge),body.kali-metro-leaving [data-testid='stForm']:has(.metro-page-geo-bridge),body.kali-metro-leaving [data-testid='stForm']:has(.site-geo-bridge),body.kali-metro-leaving [data-testid='stColumn']:has(.metro-near-me-btn),body.kali-metro-leaving [data-testid='stColumn']:has(.metro-sheet-search){display:none !important;visibility:hidden !important;}@keyframes kaliMetroPulse{0%,100%{opacity:.45;transform:scale(.9)}50%{opacity:1;transform:scale(1.08)}}";
  }
  function cover() {
    ensureStyle();
    d.body.classList.remove("kali-metro-leaving");
    d.body.classList.add("kali-metro-entering");
    var el = d.getElementById("kali-metro-enter-cover");
    if (!el) {
      el = d.createElement("div");
      el.id = "kali-metro-enter-cover";
      el.setAttribute("aria-hidden", "true");
      d.body.appendChild(el);
    }
    el.style.cssText = "position:fixed;inset:0;background:#dcd6cf;z-index:999990;pointer-events:none;transform:translateZ(0);";
    el.innerHTML = "<div style='position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:Cormorant Garamond,serif;color:#5A3A22'>"
      + "<div style='font-size:30px;letter-spacing:6px;animation:kaliMetroPulse 1.4s ease-in-out infinite'>✦</div>"
      + "<div style='font-size:16px;letter-spacing:4px;margin-top:12px;font-weight:600'>KOLKATA METRO</div>"
      + "<div style='font-size:10px;letter-spacing:2.4px;margin-top:8px;opacity:.65'>UNFURLING THE MAP…</div>"
      + "</div>";
    hideCharts();
  }
  function uncover() {
    d.body.classList.remove("kali-metro-entering");
    var el = d.getElementById("kali-metro-enter-cover");
    if (el) el.remove();
  }
  function mapCovers() {
    var frame = d.querySelector("iframe[data-metro-map-frame='1']");
    if (!frame) return false;
    var r = frame.getBoundingClientRect();
    var w = d.documentElement.clientWidth || window.innerWidth;
    var h = d.documentElement.clientHeight || window.innerHeight;
    return r.width > w * 0.8 && r.height > h * 0.8;
  }
  function hideMetro() {
    uncover();
    ensureStyle();
    d.body.classList.add("kali-metro-leaving");
    d.querySelectorAll("iframe[data-metro-map-frame]").forEach(function (frame) {
      frame.style.setProperty("opacity", "0", "important");
      frame.style.setProperty("visibility", "hidden", "important");
      frame.style.setProperty("pointer-events", "none", "important");
    });
    d.querySelectorAll(".metro-dock-panel, [data-metro-dock]").forEach(function (el) {
      if (el.querySelector && el.querySelector("[data-testid='stRadio']")) return;
      el.style.setProperty("opacity", "0", "important");
      el.style.setProperty("visibility", "hidden", "important");
      el.style.setProperty("pointer-events", "none", "important");
    });
    var chip = d.getElementById("metro-find-route");
    if (chip) chip.style.setProperty("display", "none", "important");
    [d.documentElement, d.body].concat([].slice.call(d.querySelectorAll(
      ".stApp, .block-container, [data-testid='stAppViewContainer'], [data-testid='stMain'], [data-testid='stMainBlockContainer']"
    ))).forEach(function (el) {
      if (!el || !el.style) return;
      el.style.setProperty("background", "#070408", "important");
      el.style.setProperty("background-image", "none", "important");
    });
  }
  if (window.__kaliMetroCoverTimer) {
    clearInterval(window.__kaliMetroCoverTimer);
    window.__kaliMetroCoverTimer = null;
  }
  if (!show) { hideMetro(); return; }
  cover();
  var tries = 0;
  window.__kaliMetroCoverTimer = setInterval(function () {
    tries += 1;
    hideCharts();
    if (mapCovers() || tries > 120) {
      clearInterval(window.__kaliMetroCoverTimer);
      window.__kaliMetroCoverTimer = null;
      uncover();
    }
  }, 100);
};
if (!window.__kaliMetroCoverClick) {
  window.__kaliMetroCoverClick = true;
  document.addEventListener("click", function (e) {
    var label = e.target && e.target.closest && e.target.closest('[data-testid="stRadio"] label');
    if (!label) return;
    var name = (label.textContent || "").replace(/\s+/g, " ").trim();
    window.__kaliMetroArm(name === "Kolkata Metro");
  }, true);
}
"""
components.html(
    f"""
<script>
(function () {{
  var doc = window.parent.document;
  if (doc.__kaliMetroCoverHook === 6) return;
  doc.__kaliMetroCoverHook = 6;
  var script = doc.createElement("script");
  script.textContent = {json.dumps(_METRO_COVER_JS)};
  doc.documentElement.appendChild(script);
  script.remove();
  [
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js",
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css",
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/images/marker-icon.png"
  ].forEach(function (h) {{
    var l = doc.createElement("link");
    l.rel = "prefetch"; l.href = h; doc.head.appendChild(l);
  }});
  var dns = doc.createElement("link");
  dns.rel = "dns-prefetch";
  dns.href = "https://tile.openstreetmap.org";
  doc.head.appendChild(dns);
}})();
</script>
    """,
    height=0,
    width=0,
)

# The Find route chip is appended to document.body from Metro, so it
# survives navigation unless we remove it on every other page.
if page != "Kolkata Metro":
    components.html(
        """
<script>
(function () {
  try {
    var doc = window.parent.document;
    var box = doc.getElementById("metro-find-route");
    if (box) box.remove();
  } catch (e) {}
})();
</script>
        """,
        height=0,
        width=0,
    )

# =====================================================
# SITE-WIDE LOCATION — ask the browser as soon as they enter
# (Browsers always show their own permission prompt; we cannot
# silently read GPS. Once allowed, coords are saved for Metro.)
# =====================================================
def _remember_geo_cookie() -> None:
    """Keep a saved fix without clicking the hidden form (that reruns the app)."""
    if (st.session_state.get("metro_origin") or {}).get("lat") is not None:
        return
    try:
        raw = (st.context.cookies.get("kali_geo") or "").strip()
    except Exception:
        return
    parts = raw.split("|")
    if len(parts) < 2:
        return
    try:
        lat = float(parts[0])
        lon = float(parts[1])
    except ValueError:
        return
    accuracy = None
    if len(parts) > 2 and parts[2]:
        try:
            accuracy = float(parts[2])
        except ValueError:
            accuracy = None
    st.session_state.metro_origin = {
        "lat": lat,
        "lon": lon,
        "label": "My Current Location",
        "source": "geolocation",
        "accuracy_m": accuracy,
        "kind": "user_gps",
    }


_remember_geo_cookie()
_has_saved_geo = bool(
    (st.session_state.get("metro_origin") or {}).get("lat") is not None
)
st.markdown(
    """
<style>
[data-testid="stForm"]:has(.site-geo-bridge) {
  position:fixed !important;
  left:-9999px !important;
  top:0 !important;
  width:1px !important;
  height:1px !important;
  opacity:0 !important;
  overflow:hidden !important;
  margin:0 !important;
  padding:0 !important;
  z-index:-1 !important;
}
/* The form is fixed, but its layout wrapper is still a flex item and
   leaves a blank band under the navbar. */
[data-testid="stLayoutWrapper"]:has(.site-geo-bridge) {
  position:absolute !important;
  width:0 !important;
  height:0 !important;
  min-height:0 !important;
  margin:0 !important;
  padding:0 !important;
  overflow:hidden !important;
}
</style>
    """,
    unsafe_allow_html=True,
)
with st.form("site_geo_bridge", border=False, clear_on_submit=True):
    st.markdown(
        '<div class="site-geo-bridge metro-geo-bridge" style="display:none" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    _site_geo_payload = st.text_input(
        "site_geo_payload",
        key="site_form_geo_payload",
        label_visibility="collapsed",
    )
    _site_geo_submitted = st.form_submit_button("Apply site geo")
if _site_geo_submitted:
    from modules.metro.metro_ui import apply_geo_payload
    apply_geo_payload(_site_geo_payload or "", arm_near_me=True)

components.html(
    f"""
<script>
(function () {{
  var win = window.parent;
  try {{ if (win.top && win.top.document) win = win.top; }} catch (e) {{}}
  var doc = win.document;
  var ON_METRO = {json.dumps(page == "Kolkata Metro")};
  var HAS_ORIGIN = {json.dumps(_has_saved_geo)};
  win.__kaliGeoShouldSubmit = ON_METRO && !HAS_ORIGIN;
  if (doc.__kaliSiteGeoBoot === 3) {{
    if (win.__kaliGeoShouldSubmit && !win.__kaliGeoSubmitted && win.__kaliSubmitSavedGeo) {{
      win.__kaliSubmitSavedGeo();
    }}
    return;
  }}
  doc.__kaliSiteGeoBoot = 3;

  function setNativeInput(input, value) {{
    var proto = win.HTMLInputElement.prototype;
    var desc = Object.getOwnPropertyDescriptor(proto, "value");
    if (desc && desc.set) desc.set.call(input, value);
    else input.value = value;
    if (input._valueTracker && input._valueTracker.setValue) {{
      try {{ input._valueTracker.setValue(value); }} catch (e) {{}}
    }}
    input.dispatchEvent(new Event("input", {{ bubbles: true }}));
    input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  }}

  function submitGeo(payload) {{
    var form = doc.querySelector('[data-testid="stForm"]:has(.site-geo-bridge)')
      || doc.querySelector('[data-testid="stForm"]:has(.metro-geo-bridge)');
    if (!form) return false;
    var input = form.querySelector("input");
    var btn = form.querySelector("button");
    if (!input || !btn) return false;
    setNativeInput(input, String(payload || ""));
    btn.click();
    return true;
  }}

  function saveLocal(lat, lon, acc) {{
    try {{
      win.localStorage.setItem("kali_user_geo", JSON.stringify({{
        lat: lat, lon: lon, acc: acc || null, ts: Date.now()
      }}));
    }} catch (e) {{}}
    try {{
      doc.cookie = "kali_geo=" + lat + "|" + lon + "|" + (acc || "") + "; path=/; max-age=2592000; SameSite=Lax";
    }} catch (e2) {{}}
  }}

  function submitSaved() {{
    if (!win.__kaliGeoShouldSubmit || win.__kaliGeoSubmitted) return;
    var raw = null;
    try {{ raw = win.localStorage.getItem("kali_user_geo"); }} catch (e) {{ return; }}
    if (!raw) return;
    try {{
      var o = JSON.parse(raw);
      if (!o || o.lat == null || o.lon == null) return;
      win.__kaliGeoSubmitted = true;
      submitGeo("ok|" + o.lat + "|" + o.lon + "|" + (o.acc || ""));
    }} catch (e2) {{}}
  }}
  win.__kaliSubmitSavedGeo = submitSaved;

  function requestLocation() {{
    if (win.__kaliGeoRequesting) return;
    win.__kaliGeoRequesting = true;
    if (!win.isSecureContext) {{
      win.__kaliGeoRequesting = false;
      return;
    }}
    if (!win.navigator || !win.navigator.geolocation) {{
      win.__kaliGeoRequesting = false;
      return;
    }}
    win.navigator.geolocation.getCurrentPosition(
      function (pos) {{
        win.__kaliGeoRequesting = false;
        win.__kaliGeoGot = true;
        var lat = pos.coords.latitude;
        var lon = pos.coords.longitude;
        var acc = (pos.coords.accuracy != null) ? String(pos.coords.accuracy) : "";
        saveLocal(lat, lon, acc);
        if (!win.__kaliGeoShouldSubmit || win.__kaliGeoSubmitted) return;
        win.__kaliGeoSubmitted = true;
        submitGeo("ok|" + lat + "|" + lon + "|" + acc);
      }},
      function () {{
        win.__kaliGeoRequesting = false;
      }},
      {{ enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 }}
    );
  }}

  // 1) Immediate request the moment they enter
  requestLocation();

  // 2) If the browser blocked load-time geo, retry on first interaction
  function interactionRetry() {{
    if (win.__kaliGeoGot) return;
    requestLocation();
  }}
  ["click", "touchstart", "keydown"].forEach(function (ev) {{
    doc.addEventListener(ev, interactionRetry, {{ once: true, capture: true }});
  }});

  // Saved coordinates are applied from the cookie on the next full load.
  // Only Metro, and only when Python does not already have a fix, may
  // click the form — that click reruns the whole site and holds the stop icon.
  submitSaved();
}})();
</script>
    """,
    height=0,
    width=0,
)

# Metro map is full-bleed — float the SAME Streamlit radio in a reserved top band.
# Critical: Streamlit's stHeader uses z-index ~999990 and was intercepting nav clicks.
# Other pages keep the pill in normal document flow under the brand header.
if page == "Kolkata Metro":
    st.markdown(
        """
<style>
/* Map-paper fill — never flash the dark divinity chrome while Leaflet mounts */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
    background: #dcd6cf !important;
    background-image: none !important;
}
.footer { display: none !important; }
/* Hide Streamlit chrome on Metro — it sat above the pill (z~999990) and stole clicks */
header[data-testid="stHeader"] {
    display: none !important;
}
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] {
    background: transparent !important;
    pointer-events: none !important;
}
/* Identity transforms still create a fixed containing block — clear them on Metro
   so position:fixed for nav/dock/map is viewport-relative again. */
[data-testid="stMainBlockContainer"],
[data-testid="stMain"],
.main .block-container {
    transform: none !important;
    filter: none !important;
    perspective: none !important;
    will-change: auto !important;
}
div[data-testid="element-container"]:has(div[data-testid="stRadio"]) {
    height:0 !important;
    min-height:0 !important;
    margin:0 !important;
    overflow:visible !important;
    pointer-events:none !important; /* host is zero-height; only the fixed pill receives events */
}
div[data-testid="stRadio"] {
    position:fixed !important;
    top:10px !important;
    left:50% !important;
    transform:translateX(-50%) !important;
    /* Above map (1), dock (~100), and Streamlit header (~999990) */
    z-index:1000001 !important;
    margin:0 !important;
    pointer-events:auto !important;
}
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] > div {
    pointer-events:auto !important;
}
@media (max-width:480px) {
    div[data-testid="stRadio"] { top:8px !important; }
}
</style>
        """,
        unsafe_allow_html=True,
    )
else:
    # Metro's map iframe used to paint transparent backgrounds onto the parent
    # document with inline !important styles. Those survive Streamlit reruns and
    # make every other page look broken until a hard refresh. Strip them here.
    components.html(
        """
<script>
(function () {
  var win = window.parent;
  var doc = win.document;
  var PROPS = [
    "position", "left", "right", "top", "bottom", "transform", "inset",
    "width", "max-width", "min-width", "min-height", "max-height", "height",
    "overflow", "overflow-x", "overflow-y", "z-index", "pointer-events",
    "background", "background-image", "background-color",
    "backdrop-filter", "-webkit-backdrop-filter", "flex", "border",
    "box-shadow", "border-radius", "padding", "margin", "display",
    "visibility", "opacity"
  ];
  function clearProps(el) {
    if (!el || !el.style) return;
    PROPS.forEach(function (prop) { el.style.removeProperty(prop); });
  }
  function isDock(el) {
    if (!el || !el.style) return false;
    if (el.classList && el.classList.contains("metro-dock-panel")) return true;
    if (el.getAttribute && el.getAttribute("data-metro-dock") === "1") return true;
    var bg = ((el.style.background || "") + (el.style.backgroundColor || "")).toLowerCase();
    var w = (el.style.maxWidth || "") + (el.style.width || "");
    if (bg.indexOf("21151d") >= 0 || bg.indexOf("33, 21, 29") >= 0) return true;
    if (w.indexOf("400px") >= 0 || w.indexOf("100vw - 4") >= 0 || w.indexOf("100vw - 2") >= 0) return true;
    return false;
  }
  function scrub() {
    try {
      var mapStillHere = !!doc.querySelector("iframe[data-metro-map-frame]");
      ["stApp", "stAppViewContainer", "stMain", "stMainBlockContainer"].forEach(function (id) {
        var el = doc.querySelector('[data-testid="' + id + '"]') || doc.querySelector("." + id);
        if (!el || !el.style) return;
        if (mapStillHere) {
          el.style.setProperty("background", "#070408", "important");
          el.style.setProperty("background-image", "none", "important");
        } else {
          el.style.removeProperty("background");
          el.style.removeProperty("background-image");
          el.style.removeProperty("background-color");
        }
      });
      [doc.documentElement, doc.body].forEach(function (el) {
        if (!el || !el.style) return;
        if (mapStillHere) {
          el.style.setProperty("background", "#070408", "important");
          el.style.setProperty("background-image", "none", "important");
        } else {
          el.style.removeProperty("background");
          el.style.removeProperty("background-image");
          el.style.removeProperty("background-color");
        }
        el.style.removeProperty("overflow");
      });
      var metroLeft = !!doc.querySelector(
        ".metro-sheet-row, .metro-sheet-list, .metro-dock-panel, [data-metro-dock], .metro-near-me-btn, .metro-sheet-search, .metro-dock-anchor, #metro-find-route, iframe[data-metro-map-frame]"
      );
      if (metroLeft) doc.body.classList.add("kali-metro-leaving");
      else doc.body.classList.remove("kali-metro-leaving");
      doc.querySelectorAll(
        ".metro-dock-panel, [data-metro-dock], [data-testid='stVerticalBlock'], [data-testid='stElementContainer'], [data-testid='stLayoutWrapper']"
      ).forEach(function (el) {
        if (!isDock(el)) return;
        if (el.classList) el.classList.remove("metro-dock-panel");
        if (el.removeAttribute) el.removeAttribute("data-metro-dock");
        clearProps(el);
      });
      doc.querySelectorAll("iframe[data-metro-map-frame]").forEach(function (frame) {
        frame.style.setProperty("opacity", "0", "important");
        frame.style.setProperty("visibility", "hidden", "important");
        frame.style.setProperty("pointer-events", "none", "important");
        var parent = frame.parentElement;
        if (parent && parent.style && (parent.style.pointerEvents === "none" || (parent.style.background || "").indexOf("dcd6cf") >= 0)) {
          clearProps(parent);
        }
      });
      var chip = doc.getElementById("metro-find-route");
      if (chip) chip.remove();
      doc.querySelectorAll(".music-player, #kali-music-player").forEach(function (el) {
        el.style.removeProperty("display");
        el.style.removeProperty("visibility");
        el.style.removeProperty("pointer-events");
      });
      win.dispatchEvent(new Event("resize"));
    } catch (e) {}
  }
  scrub();
  [80, 350, 1000].forEach(function (ms) { win.setTimeout(scrub, ms); });
})();
</script>
        """,
        height=0,
        width=0,
    )

def diya_divider():
    st.markdown("""
    <div class="diya-divider">
        <span class="dd-line"></span>
        <span class="dd-flame">✦</span>
        <span class="dd-line"></span>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# DIVINE MUSIC | SHYAMA SANGEET PLAYER
# =====================================================

MUSIC_DIR = ASSET_DIR / "music"
STATIC_MUSIC_DIR = BASE_DIR / "static" / "music"
LITE_MUSIC_DIR = STATIC_MUSIC_DIR / "lite"
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a"}

def _ffmpeg_exe():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
        exe = shutil.which("ffmpeg")
        if exe:
            return exe
    except Exception:
        pass
    return None


def _transcode_lite_audio(src: Path, dest: Path) -> None:
    try:
        subprocess.run(
            [
                "afconvert", "-f", "m4af", "-d", "aac",
                "-c", "1", "-b", "64000",
                str(src), str(dest),
            ],
            check=True,
            capture_output=True,
        )
        return
    except Exception:
        pass
    exe = _ffmpeg_exe()
    if not exe:
        return
    try:
        subprocess.run(
            [exe, "-y", "-i", str(src), "-c:a", "aac", "-b:a", "64k", str(dest)],
            check=True,
            capture_output=True,
        )
    except Exception:
        pass


def lite_music_url(src: Path) -> str:
    """Small background copy. The file in assets/music stays the original."""
    LITE_MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    dest = LITE_MUSIC_DIR / f"{src.stem}.m4a"
    if not (dest.exists() and dest.stat().st_size > 0):
        _transcode_lite_audio(src, dest)
    if dest.exists() and dest.stat().st_size > 0:
        return "/app/static/music/lite/" + quote(dest.name)
    return "/app/static/music/" + quote(src.name)
DEFAULT_MUSIC_VOLUME = 0.05

def get_music_tracks():
    if not MUSIC_DIR.exists():
        return []
    return [
        p for p in MUSIC_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
        and p.stat().st_size > 0
    ]

def order_music_playlist(tracks):
    """Prefer classic Shyama Sangeet first, then remaining tracks A–Z."""
    preferred, rest = [], []
    for p in tracks:
        n = p.name.lower()
        if "tumi" in n or "giri" in n or "shyama" in n:
            preferred.append(p)
        else:
            rest.append(p)
    preferred.sort(key=lambda p: p.name.lower())
    rest.sort(key=lambda p: p.name.lower())
    return preferred + rest

music_tracks = order_music_playlist(get_music_tracks())

# Metro is map-first — never show / inject the music player there
if page == "Kolkata Metro":
    components.html(
        """
<script>
(function () {
  try {
    var doc = window.parent.document;
    doc.querySelectorAll(".music-player, #kali-music-player").forEach(function (el) {
      try {
        var audio = el.querySelector("audio");
        if (audio) audio.pause();
        if (el._kaliAudio) el._kaliAudio.pause();
      } catch (e) {}
      el.style.setProperty("display", "none", "important");
      el.style.setProperty("visibility", "hidden", "important");
      el.style.setProperty("pointer-events", "none", "important");
    });
  } catch (e) {}
})();
</script>
        """,
        height=0,
        width=0,
    )
elif music_tracks:
    sync_static_assets(music_tracks, STATIC_MUSIC_DIR)
    playlist = [
        {
            "id": p.name,
            "src": lite_music_url(p),
            "title": music_display_title(p),
        }
        for p in music_tracks
    ]
    playlist_json = json.dumps(playlist, ensure_ascii=False)
    playlist_key = "|".join(item["id"] for item in playlist)
    vol_pct = int(DEFAULT_MUSIC_VOLUME * 100)
    # Inject into the parent page so controls / playlist survive Streamlit reruns.
    components.html(
        f"""
        <script>
        (async function () {{
          const doc = window.parent.document;
          const win = window.parent;
          const PLAYLIST = {playlist_json};
          const PLAYLIST_KEY = {playlist_key!r};
          const DEFAULT_VOL = {vol_pct};
          const PLAYER_VERSION = "v7-lite-aac";

          if (win.__kaliMusicBooting) return;
          let player = doc.getElementById("kali-music-player");
          if (
            player &&
            player.dataset.version === PLAYER_VERSION &&
            player._kaliPlaylistKey === PLAYLIST_KEY &&
            player._kaliReady
          ) {{
            return;
          }}

          win.__kaliMusicBooting = true;

          try {{
            if (player && (player.dataset.version !== PLAYER_VERSION || player._kaliPlaylistKey !== PLAYLIST_KEY)) {{
              try {{ if (player._kaliAudio) player._kaliAudio.pause(); }} catch (_) {{}}
              if (player._kaliBlobUrl) URL.revokeObjectURL(player._kaliBlobUrl);
              if (player._kaliAbort) {{ try {{ player._kaliAbort.abort(); }} catch (_) {{}} }}
              player.remove();
              player = null;
            }}

            if (!player) {{
              player = doc.createElement("div");
              player.id = "kali-music-player";
              player.className = "music-player";
              player.dataset.version = PLAYER_VERSION;
              player._kaliPlaylistKey = PLAYLIST_KEY;
              player._kaliPlaylist = PLAYLIST;
              player._kaliIndex = 0;
              player.innerHTML = `
                <div class="mp-top">
                  <span class="mp-diya" id="mp-diya">✦</span>
                  <div class="mp-meta">
                    <div class="mp-label">SHYAMA SANGEET · PLAYLIST</div>
                    <button type="button" class="mp-track-btn" id="mp-track-btn"
                            title="Show song list" aria-expanded="false">
                      <div class="mp-track" id="mp-track"></div>
                    </button>
        </div>
                  <span class="mp-status" id="mp-status">Loading</span>
    </div>
                <div class="mp-controls">
                  <button type="button" class="mp-btn" id="mp-prev"
                          aria-label="Previous song" title="Previous">⏮</button>
                  <button type="button" class="mp-btn primary" id="mp-play"
                          aria-label="Play or pause" title="Play / Pause">▶</button>
                  <button type="button" class="mp-btn" id="mp-next"
                          aria-label="Next song" title="Next">⏭</button>
                  <button type="button" class="mp-btn" id="mp-list"
                          aria-label="Song list" title="Song list">☰</button>
                  <div class="mp-vol">
                    <span class="mp-vol-icon" id="mp-vol-icon" aria-hidden="true">Vol</span>
                    <input type="range" id="mp-volume" min="0" max="100" step="1"
                           aria-label="Volume" title="Volume">
                    <span class="mp-vol-pct" id="mp-vol-pct"></span>
                  </div>
                </div>
                <div class="mp-list-panel" id="mp-list-panel" role="listbox" aria-label="Songs"></div>
                <audio id="mp-audio" preload="none" playsinline></audio>
              `;
              doc.body.appendChild(player);

              const audio = player.querySelector("#mp-audio");
              const playBtn = player.querySelector("#mp-play");
              const prevBtn = player.querySelector("#mp-prev");
              const nextBtn = player.querySelector("#mp-next");
              const listBtn = player.querySelector("#mp-list");
              const trackBtn = player.querySelector("#mp-track-btn");
              const listPanel = player.querySelector("#mp-list-panel");
              const statusEl = player.querySelector("#mp-status");
              const diyaEl = player.querySelector("#mp-diya");
              const trackEl = player.querySelector("#mp-track");
              const volInput = player.querySelector("#mp-volume");
              const volPctEl = player.querySelector("#mp-vol-pct");
              const volIcon = player.querySelector("#mp-vol-icon");

              player._kaliVolPct = DEFAULT_VOL;
              player._kaliBusy = false;
              player._kaliCache = Object.create(null);

              const applyVolume = (pct) => {{
                const n = Math.max(0, Math.min(100, Number(pct)));
                if (!Number.isFinite(n)) return;
                player._kaliVolPct = n;
                if (String(volInput.value) !== String(n)) volInput.value = String(n);
                audio.volume = n / 100;
                audio.muted = n === 0;
                volPctEl.textContent = Math.round(n) + "%";
                volIcon.textContent = n === 0 ? "Mute" : "Vol";
              }};

              const setUi = (state) => {{
                if (player._kaliReloading && (state === "Paused" || state === "Stopped")) return;
                statusEl.textContent = state;
                statusEl.classList.remove("playing", "paused");
                diyaEl.classList.remove("is-playing");
                if (state === "Playing") {{
                  statusEl.classList.add("playing");
                  diyaEl.classList.add("is-playing");
                  playBtn.textContent = "❚❚";
                  playBtn.title = "Pause";
                }} else if (state === "Paused") {{
                  statusEl.classList.add("paused");
                  playBtn.textContent = "▶";
                  playBtn.title = "Play";
                }} else {{
                  playBtn.textContent = "▶";
                  playBtn.title = "Play";
                }}
              }};

              const renderList = () => {{
                const idx = player._kaliIndex || 0;
                listPanel.innerHTML = player._kaliPlaylist.map((t, i) => `
                  <button type="button" class="mp-list-item${{i === idx ? " is-active" : ""}}"
                          data-index="${{i}}" role="option" aria-selected="${{i === idx}}">
                    <span class="mp-list-idx">${{String(i + 1).padStart(2, "0")}}</span>
                    <span class="mp-list-title">${{t.title.replace(/</g, "&lt;")}}</span>
                  </button>
                `).join("");
              }};

              const setListOpen = (open) => {{
                player.classList.toggle("mp-list-open", !!open);
                trackBtn.setAttribute("aria-expanded", open ? "true" : "false");
                if (open) renderList();
              }};

              const showTrackMeta = () => {{
                const t = player._kaliPlaylist[player._kaliIndex] || {{}};
                trackEl.textContent = t.title || "Untitled";
                trackEl.title = (t.title || "") + " — click for list";
                renderList();
              }};

              const loadIndex = async (index, {{ autoplay = false, isAdvance = false }} = {{}}) => {{
                const list = player._kaliPlaylist;
                if (!list.length) return;
                const idx = ((index % list.length) + list.length) % list.length;
                const track = list[idx];
                const gen = (player._kaliLoadGen || 0) + 1;
                player._kaliLoadGen = gen;
                player._kaliReloading = true;
                player._kaliReady = false;
                player._kaliIndex = idx;
                showTrackMeta();
                player._kaliSetUi("Loading");

                try {{
                  audio.preload = "none";
                  audio.src = track.src;
                  player._kaliSrc = track.src;
                  player._kaliApplyVolume(player._kaliVolPct || DEFAULT_VOL);
                  player._kaliReady = true;
                  player._kaliReloading = false;

                  if (autoplay || isAdvance) {{
                    player._kaliUserStopped = false;
                    try {{
                      await audio.play();
                      player._kaliAutostarted = true;
                      setUi("Playing");
                    }} catch (_) {{
                      try {{
                        audio.muted = true;
                        await audio.play();
                        applyVolume(player._kaliVolPct);
                        player._kaliAutostarted = true;
                        setUi("Playing");
                      }} catch (__) {{
                        setUi("Stopped");
                        statusEl.textContent = "Tap ▶";
                      }}
                    }}
                  }} else if (!player._kaliAutostarted) {{
                    const startLater = () => {{
                      if (!player._kaliAutostarted) player._kaliTryAutostart();
                    }};
                    if (win.requestIdleCallback) win.requestIdleCallback(startLater, {{ timeout: 4000 }});
                    else win.setTimeout(startLater, 2500);
                  }} else {{
                    setUi(audio.paused ? "Stopped" : "Playing");
                  }}
                }} catch (err) {{
                  if (err && err.name === "AbortError") return;
                  if (player._kaliLoadGen !== gen) return;
                  player._kaliReloading = false;
                  player._kaliReady = false;
                  setUi("Stopped");
                  statusEl.textContent = "Unavailable";
                }}
              }};

              const tryAutostart = async () => {{
                if (player._kaliAutostarted || player._kaliUserStopped || !player._kaliReady) return;
                player._kaliAutostarted = true;
                applyVolume(player._kaliVolPct);
                try {{
                  await audio.play();
                  setUi("Playing");
                  return;
                }} catch (_) {{}}
                try {{
                  audio.muted = true;
                  await audio.play();
                  applyVolume(player._kaliVolPct);
                  setUi("Playing");
                }} catch (_) {{
                  setUi("Stopped");
                  statusEl.textContent = "Tap ▶";
                }}
              }};

              const playNext = async () => {{
                if (player._kaliUserStopped) return;
                await loadIndex((player._kaliIndex || 0) + 1, {{ isAdvance: true }});
              }};

              playBtn.addEventListener("click", async (e) => {{
                e.preventDefault();
                e.stopPropagation();
                if (player._kaliBusy || player._kaliReloading || !player._kaliReady) return;
                player._kaliBusy = true;
                playBtn.disabled = true;
                try {{
                  if (audio.paused) {{
                    player._kaliUserStopped = false;
                    applyVolume(player._kaliVolPct);
                    await audio.play();
                    setUi("Playing");
                  }} else {{
                    audio.pause();
                    setUi("Paused");
                  }}
                }} catch (_) {{
                  setUi("Stopped");
                  statusEl.textContent = "Blocked";
                }} finally {{
                  player._kaliBusy = false;
                  playBtn.disabled = false;
                }}
              }});

              prevBtn.addEventListener("click", async (e) => {{
                e.preventDefault();
                e.stopPropagation();
                if (player._kaliBusy || player._kaliReloading) return;
                const restartCurrent = (audio.currentTime || 0) > 3;
                if (restartCurrent) {{
                  try {{ audio.currentTime = 0; }} catch (_) {{}}
                  return;
                }}
                await loadIndex((player._kaliIndex || 0) - 1, {{
                  autoplay: !audio.paused || !!player._kaliAutostarted,
                }});
              }});

              nextBtn.addEventListener("click", async (e) => {{
                e.preventDefault();
                e.stopPropagation();
                if (player._kaliBusy || player._kaliReloading) return;
                await loadIndex((player._kaliIndex || 0) + 1, {{
                  autoplay: !audio.paused || !!player._kaliAutostarted,
                }});
              }});

              const toggleList = (e) => {{
                e.preventDefault();
                e.stopPropagation();
                setListOpen(!player.classList.contains("mp-list-open"));
              }};
              listBtn.addEventListener("click", toggleList);
              trackBtn.addEventListener("click", toggleList);

              listPanel.addEventListener("click", async (e) => {{
                const btn = e.target.closest("[data-index]");
                if (!btn) return;
                e.preventDefault();
                e.stopPropagation();
                const i = Number(btn.getAttribute("data-index"));
                if (!Number.isFinite(i)) return;
                setListOpen(false);
                await loadIndex(i, {{ autoplay: true }});
              }});

              const onVol = (e) => {{
                e.stopPropagation();
                applyVolume(volInput.value);
              }};
              volInput.addEventListener("input", onVol);
              volInput.addEventListener("change", onVol);
              volInput.addEventListener("pointerdown", (e) => e.stopPropagation());
              volInput.addEventListener("pointermove", (e) => {{
                if (e.buttons) applyVolume(volInput.value);
              }});

              audio.addEventListener("play", () => setUi("Playing"));
              audio.addEventListener("pause", () => {{
                if (player._kaliReloading || player._kaliBusy) return;
                if (audio.ended) return;
                if (audio.currentTime === 0) setUi("Stopped");
                else setUi("Paused");
              }});
              audio.addEventListener("ended", () => {{
                // Advance through playlist; wrap to first after last.
                playNext();
              }});

              volInput.value = String(DEFAULT_VOL);
              applyVolume(DEFAULT_VOL);
              setUi("Loading");
              renderList();

              player._kaliAudio = audio;
              player._kaliTrack = trackEl;
              player._kaliSetUi = setUi;
              player._kaliTryAutostart = tryAutostart;
              player._kaliApplyVolume = applyVolume;
              player._kaliLoadIndex = loadIndex;
            }}

            await player._kaliLoadIndex(player._kaliIndex || 0, {{ autoplay: false }});
          }} finally {{
            win.__kaliMusicBooting = false;
          }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
else:
    st.caption(
        "Drop Shyama Sangeet tracks into assets/music/ "
        "to enable the music player."
    )

images = get_images()

# =====================================================
# AMBIENT WALLPAPER — shuffle Kali Ghat Temple / Kishori Kali every 5s
# (all pages except Kolkata Metro, which stays map-first)
# =====================================================

wallpaper_files = [
    ASSET_DIR / "kali ghat temple.jpg",
    ASSET_DIR / "kishori kali.png",
]
wallpaper_files = [
    p for p in wallpaper_files if p.exists() and p.stat().st_size > 0
]

if page == "Kolkata Metro":
    # Tear down wallpaper if user navigates onto the map page
    components.html(
        """
<script>
(function () {
  try {
    var doc = window.parent.document;
    var win = window.parent;
    if (win.__kaliWallpaperTimer) {
      clearInterval(win.__kaliWallpaperTimer);
      win.__kaliWallpaperTimer = null;
    }
    var root = doc.getElementById("kali-wallpaper");
    if (root) root.remove();
  } catch (e) {}
})();
</script>
        """,
        height=0,
        width=0,
    )
elif wallpaper_files:
    wallpaper_urls = [
        web_image(p, max_edge=960, quality=58)[0] for p in wallpaper_files
    ]
    wallpaper_json = json.dumps(wallpaper_urls, ensure_ascii=False)
    components.html(
        f"""
<script>
(function () {{
  const doc = window.parent.document;
  const win = window.parent;
  const SLIDES = {wallpaper_json};
  const INTERVAL_MS = 5000;
  const VERSION = "v3-lazy-wallpaper";

  if (!SLIDES.length) return;

  let root = doc.getElementById("kali-wallpaper");
  if (root && root.dataset.version === VERSION && root._kaliReady) {{
    return;
  }}

  if (win.__kaliWallpaperTimer) {{
    clearInterval(win.__kaliWallpaperTimer);
    win.__kaliWallpaperTimer = null;
  }}
  if (root) root.remove();

  root = doc.createElement("div");
  root.id = "kali-wallpaper";
  root.dataset.version = VERSION;
  root.setAttribute("aria-hidden", "true");
  root.innerHTML = `
    <style>
      #kali-wallpaper {{
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
        background: #070408;
      }}
      #kali-wallpaper .kali-wp-slide {{
        position: absolute;
        inset: 0;
        background-position: center 18%;
        background-size: cover;
        background-repeat: no-repeat;
        opacity: 0;
        transform: scale(1.04);
        transition: opacity 1.1s ease, transform 5s ease;
      }}
      #kali-wallpaper .kali-wp-slide.is-active {{
        opacity: 1;
        transform: scale(1);
      }}
      #kali-wallpaper .kali-wp-veil {{
        position: absolute;
        inset: 0;
        background:
            linear-gradient(165deg,
                rgba(9,4,8,.58) 0%,
                rgba(15,7,12,.74) 42%,
                rgba(9,4,8,.90) 72%,
                rgba(8,5,9,.97) 100%),
          radial-gradient(ellipse at 82% 6%,rgba(118,31,53,.45) 0%,transparent 46%),
          radial-gradient(ellipse at 10% 94%,rgba(214,51,108,.12) 0%,transparent 44%);
      }}
      [data-testid="stAppViewContainer"],
      [data-testid="stMain"],
      .stApp {{
        background: transparent !important;
        background-image: none !important;
      }}
      @media (max-width:700px) {{
        #kali-wallpaper .kali-wp-slide {{
          background-position: center 22%;
        }}
    }}
    </style>
    <div class="kali-wp-slides"></div>
    <div class="kali-wp-veil"></div>
  `;

  const host = doc.querySelector(".stApp") || doc.body;
  host.insertBefore(root, host.firstChild);

  const track = root.querySelector(".kali-wp-slides");
  SLIDES.forEach(function (src, i) {{
    const slide = doc.createElement("div");
    slide.className = "kali-wp-slide" + (i === 0 ? " is-active" : "");
    slide.dataset.src = src;
    if (i === 0) slide.style.backgroundImage = 'url("' + src + '")';
    track.appendChild(slide);
  }});

  function ensureSlide(slide) {{
    if (slide && slide.dataset.src && !slide.style.backgroundImage) {{
      slide.style.backgroundImage = 'url("' + slide.dataset.src + '")';
    }}
  }}

  let idx = 0;
  function shuffle() {{
    const slides = track.querySelectorAll(".kali-wp-slide");
    if (slides.length < 2) return;
    slides[idx].classList.remove("is-active");
    idx = (idx + 1) % slides.length;
    ensureSlide(slides[idx]);
    slides[idx].classList.add("is-active");
  }}
  if (win.requestIdleCallback) {{
    win.requestIdleCallback(function () {{
      ensureSlide(track.querySelectorAll(".kali-wp-slide")[1]);
    }}, {{ timeout: 4000 }});
  }}

  win.__kaliWallpaperTimer = win.setInterval(shuffle, INTERVAL_MS);
  root._kaliReady = true;
}})();
</script>
        """,
        height=0,
        width=0,
    )


# =====================================================
# HOME
# =====================================================

if page == "Home":

    metrics = [
        (str(len(images)), "IMAGES"),
        ("06", "MODULES"),
        ("2026", "EDITION"),
    ]
    metrics_html = "".join(
        f"""
        <div class="metric-box" style="animation-delay:{0.3 + i * 0.15}s">
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{label}</div>
        </div>
        """
        for i, (value, label) in enumerate(metrics)
    )

    st.html(f"""
<div class="hero-shell">
            <div class="eyebrow">✦ A JOURNEY THROUGH DIVINE BENGAL</div>
            <h1 class="hero-title">KALI VISION AI</h1>
            <div class="hero-subtitle">The Divine Intelligence of Bengal</div>
            <div class="bengali-blessing">শুভ কালী পূজা · জয় মা কালী</div>
            <p>
            On the darkest night of Deepavali, Bengal lights a million diyas
            for the Mother. Discover that living heritage through Artificial
            Intelligence, Computer Vision and Data Analytics — the temples,
            the pandals, the flames and the visual splendour of Kali Puja.
            </p>
  <div class="hero-metrics">
    {metrics_html}
        </div>
                </div>
""")

    if st.button("Explore Divine Bengal →", use_container_width=False):
            st.session_state.navigation = "Gallery"
            st.rerun()

    st.markdown("""
    <div class="marquee"><div class="marquee-inner">
        <span>জয় মা কালী &nbsp;✦&nbsp; JAI MAA KALI &nbsp;✦&nbsp; <span class="red">শুভ কালী পূজা</span> &nbsp;✦&nbsp; SHUBH KALI PUJA &nbsp;✦&nbsp; জয় মা কালী &nbsp;✦&nbsp; JAI MAA KALI &nbsp;✦&nbsp; <span class="red">শুভ দীপাবলি</span> &nbsp;✦&nbsp; </span><span>জয় মা কালী &nbsp;✦&nbsp; JAI MAA KALI &nbsp;✦&nbsp; <span class="red">শুভ কালী পূজা</span> &nbsp;✦&nbsp; SHUBH KALI PUJA &nbsp;✦&nbsp; জয় মা কালী &nbsp;✦&nbsp; JAI MAA KALI &nbsp;✦&nbsp; <span class="red">শুভ দীপাবলি</span> &nbsp;✦&nbsp; </span>
    </div></div>
    """,unsafe_allow_html=True)

    diya_divider()

    exp_kali = ASSET_DIR / "maa_kali_hero.webp"
    if not exp_kali.exists():
        exp_kali = ASSET_DIR / "maa_kali_hero.png"
    card_bgs = {
        "01": ASSET_DIR / "Dakshineswar Temple Aglow by Night.png",
        "02": ASSET_DIR / "kalighat_temple_kolkata.jpg",
        "03": ASSET_DIR / "kali_puja_pandal_kalighat_replica_behala.jpg",
        "04": ASSET_DIR / "kali_puja_pandal_kolkata_celebration_11.jpg",
        "05": ASSET_DIR / "kali_puja_pandal_pramanick_bari_kolkata.jpg",
    }
    # Fallbacks if a preferred file is missing
    fallbacks = {
        "01": ASSET_DIR / "dakshineswar_temple_real.jpg",
        "02": ASSET_DIR / "kalighat_temple.jpg",
        "03": ASSET_DIR / "kali_murti_kolkata_17.jpg",
        "04": ASSET_DIR / "kali_puja_pandal_behala_kolkata.jpg",
        "05": ASSET_DIR / "kali_puja_adi_kali_pandal.jpg",
    }
    for key, path in list(card_bgs.items()):
        if not path.exists() or path.stat().st_size == 0:
            card_bgs[key] = fallbacks[key]

    def _static_url(path):
        if path.exists() and path.stat().st_size > 0:
            return web_image(path, max_edge=720, quality=56)[0]
        return ""

    kali_url = _static_url(exp_kali)
    bg = {k: _static_url(p) for k, p in card_bgs.items()}

    # Use st.html (not markdown) so indented markup is not treated as a code block.
    st.html(f"""
<section class="experience">
  <div class="experience-header">
    <div class="experience-copy">
      <div class="experience-kicker">THE EXPERIENCE</div>
      <h2 class="experience-title">
        Where Tradition Meets
        <span class="script">Intelligence</span>
      </h2>
      <div class="experience-lede">
        <span class="experience-lede-bar" aria-hidden="true"></span>
        <p>A digital space that blends Bengal’s timeless traditions with the power of AI.</p>
                </div>
    </div>
    <div class="experience-portrait">
      {"<img src='" + kali_url + "' alt='Maa Kali'>" if kali_url else ""}
    </div>
  </div>

  <div class="experience-bento">
    <div class="exp-card exp-card-01">
      <div class="exp-card-bg" style="background-image:url('{bg['01']}')"></div>
      <div class="exp-card-01-content">
        <div class="exp-num">01</div>
        <h3>AI Assistant</h3>
        <p>Explore Bengali cultural knowledge through conversation.</p>
        <a class="exp-pill" href="?nav=AI+Assistant" target="_self">Explore Now →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-02">
      <div class="exp-card-bg" style="background-image:url('{bg['02']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11z"></path><circle cx="12" cy="10" r="2.4"></circle></svg>
        </span>
        <span class="exp-num">02</span>
      </div>
      <div class="exp-mini-body">
        <h4>Kolkata Explorer</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Kolkata+Explorer" target="_self">Explore →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-03">
      <div class="exp-card-bg" style="background-image:url('{bg['03']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><rect x="4" y="7" width="14" height="12" rx="1.5"></rect><path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h9A1.5 1.5 0 0 1 20 5.5V15"></path><path d="M4 11h14"></path></svg>
        </span>
        <span class="exp-num">03</span>
      </div>
      <div class="exp-mini-body">
        <h4>Divine Gallery</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Gallery" target="_self">Explore →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-04">
      <div class="exp-card-bg" style="background-image:url('{bg['04']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M4 19h16"></path><path d="M7 16V10"></path><path d="M12 16V6"></path><path d="M17 16v-7"></path></svg>
        </span>
        <span class="exp-num">04</span>
      </div>
      <div class="exp-mini-body">
        <h4>Festival Analytics</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Analytics" target="_self">Explore →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-05">
      <div class="exp-card-bg" style="background-image:url('{bg['05']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M3 17h18"></path><path d="M5 17V9l3 2 3-4 3 3 3-2 2 3v6"></path><circle cx="8" cy="17" r="1.2"></circle><circle cx="16" cy="17" r="1.2"></circle></svg>
        </span>
        <span class="exp-num">05</span>
      </div>
      <div class="exp-mini-body">
        <h4>Kolkata Metro</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Kolkata+Metro" target="_self">Explore →</a>
      </div>
    </div>
  </div>
</section>
""")


# =====================================================
# GALLERY
# =====================================================

elif page == "Gallery":

    st.markdown('<div class="section-label">VISUAL HERITAGE OF BENGAL</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">✦ Divine Bengal Gallery</div>',unsafe_allow_html=True)

    st.write("A curated collection of Kali Puja murtis, pandals and Bengal's sacred heritage — tap any frame to open it.")

    category_options = ["All"] + sorted(set(image_category(p.name) for p in images))
    category = st.pills(
        "Explore collection",
        category_options,
        default="All",
        label_visibility="collapsed"
    ) or "All"

    filtered = [
        p for p in images
        if category == "All" or image_category(p.name) == category
    ]

    st.caption(f"{len(filtered)} sacred frames in this collection")

    if not filtered:
        st.info("No images found. Add JPG, PNG or WEBP files to your assets folder.")
    else:
        cards = []
        for p in filtered:
            src, meta, width, height = web_image(p, max_edge=640, quality=52)
            title = html_escape(image_title(p))
            cat = html_escape(image_category(p.name).upper())
            dims = f' width="{width}" height="{height}"' if width and height else ""
            cards.append(f"""
            <figure class="gcard">
                <a href="{src}" target="_blank" rel="noopener">
                    <img src="{src}" alt="{title}" decoding="async"{dims}>
                </a>
                <figcaption class="gcard-overlay">
                    <div class="gcard-name">{title}</div>
                    <div class="gcard-meta"><span class="gcard-cat">{cat}</span>{html_escape(meta)}</div>
                </figcaption>
            </figure>""")

        st.markdown(
            f'<div class="gallery-grid">{"".join(cards)}</div>',
            unsafe_allow_html=True
        )


# =====================================================
# AI ASSISTANT
# =====================================================

elif page == "AI Assistant":

    st.html("""
<div class="assistant-header">
  <div class="assistant-kicker">SEEK HER WISDOM</div>
  <h2 class="assistant-title">Maa Kali AI Assistant</h2>
  <div class="assistant-lede">
    <span class="assistant-lede-bar" aria-hidden="true"></span>
    <p>Ask about Kali Puja, the great temples, murtis, rituals and Shyama Sangeet — answered from a curated devotional knowledge base.</p>
  </div>
</div>
""")

    KALI_KB = [
        {"keys":["kali puja","what is kali","diwali","deepavali","dipavali","festival","when"],
         "en":"**Kali Puja** is Bengal's great night of the Mother — celebrated on the new-moon night (Amavasya) of Kartik, the same night as Diwali. While the rest of India lights lamps for Lakshmi, Bengal worships the fierce, compassionate Kali. Pandals rise across Kolkata, diyas burn till dawn, and puja begins at midnight.",
         "bn":"কালীপূজা হলো বাংলার মায়ের মহা-রাত্রি — কার্তিক অমাবস্যায়, দীপাবলির রাতে মা কালীর আরাধনা। মাঝরাতে পূজা, ভোর পর্যন্ত প্রদীপের আলো।"},
        {"keys":["dakshineswar","rashmoni","ramakrishna","hooghly"],
         "en":"**Dakshineswar Kali Temple** (1855) was built by Rani Rashmoni on the east bank of the Hooghly. Its presiding deity is **Bhavatarini**, 'She who ferries souls across the ocean of existence'. Sri Ramakrishna Paramahamsa served here as priest — his room, the twelve Shiva temples and the nahabat are still places of pilgrimage.",
         "bn":"দক্ষিণেশ্বর কালীমন্দির (১৮৫৫) রানী রাসমণি নির্মিত — এখানে মা ভবতারিণী। শ্রীরামকৃষ্ণ এখানেই পূজারি ছিলেন।"},
        {"keys":["kalighat","peeth","shakti"],
         "en":"**Kalighat** is one of the 51 Shakti Peethas — where the toe of Sati's right foot is said to have fallen. The temple gave Kolkata (Kalikata) its name. The deity's fierce gold face, three eyes and long tongue are unique; her image is renewed annually with sacred rituals.",
         "bn":"কালীঘাট ৫১ শক্তিপীঠের একটি — কলকাতার নামই এখান থেকে। মায়ের স্বর্ণ-মুখ তিন নয়নে দীপ্ত।"},
        {"keys":["shyama","sangeet","song","music","ramprasad","pannalal","tumi naki","giri"],
         "en":"**Shyama Sangeet** is Bengal's devotional song tradition for the dark Mother — born of the 18th-century poet-saint **Ramprasad Sen**, and immortalised by singers like **Pannalal Bhattacharya** and **Anup Jalota**. 'Tumi Naki Giri Rajer Maiya' — the song filling this site — is among the most beloved. These songs see Kali not as terror but as mother.",
         "bn":"শ্যামা সঙ্গীত — কালীর উদ্দেশ্যে বাংলার ভক্তিগীতি। রামপ্রসাদ সেনের সৃষ্টি, পান্নালাল ভট্টাচার্যের কণ্ঠে অমর।"},
        {"keys":["fata","kesto","barowari","baroyari","community"],
         "en":"**Fata Kesto Kali Puja** is one of Kolkata's oldest community (Barowari) Kali pujas — running since the 19th century in central Kolkata. Legend ties it to a neighbourhood's vow to the Mother. Community Kali pujas like this turned worship into Bengal's greatest street festival of light.",
         "bn":"ফটা কেস্তো কালীপূজা — কলকাতার অন্যতম প্রাচীন বারোয়ারি পূজা, শত বছরের ঐতিহ্য।"},
        {"keys":["offer","jaba","hibiscus","bhog","flower","prasad","food","sacrifice"],
         "en":"**Offerings to Maa Kali**: red hibiscus (jaba) — her beloved flower, offered in counts of 108; bhog of khichuri, luchi and sweets; red sindoor; and lamps of mustard oil. Traditionally the puja happens after midnight, when devotees stay awake through the darkest hours.",
         "bn":"মায়ের প্রিয় লাল জবা — ১০৮টি ফুলের মালা, খিচুড়ি ভোগ, সিঁদুর আর সরষের তেলের প্রদীপ।"},
        {"keys":["visarjan","immersion","bisharjan","nimtala","ghat","farewell"],
         "en":"**Visarjan** is the tearful farewell — after puja, murtis are carried in procession to the Hooghly and immersed, often at **Nimtala Ghat**. Drums (dhak) thunder, devotees chant, and the Mother's image dissolves into the river — a reminder that all form returns to formlessness.",
         "bn":"বিসর্জন — মাকে হুগলি নদীতে বিদায়। ঢাকের আওয়াজে মূর্তি নদীর জলে মিশে যায়।"},
        {"keys":["kumartuli","kumortuli","idol maker","artisan","clay","sculpt"],
         "en":"**Kumartuli** is Kolkata's centuries-old potters' quarter where murtis are born. Clay from the Hooghly is layered over bamboo-and-straw frames, painted, dressed in shola pith crowns and real ornaments. The same hands build Durga in autumn and Kali at Deepavali.",
         "bn":"কুমারটুলি — কলকাতার কুমোরপাড়া, যেখানে প্রতিমা জন্ম নেয়। হুগলির মাটি, বাঁশ-খড়ের কাঠামো, শোলার মুকুট।"},
        {"keys":["tongue","black","form","icon","shiva","meaning","why","weapon","head"],
         "en":"**Her iconography**: Maa Kali's midnight form is time itself (kala). The outstretched tongue — a legend says she bit it in shame, stepping on Shiva; another sees it as devouring blood of demons. The garland of heads is the ego she severs; the skirt of arms, samsara she cuts. Shiva lies beneath her feet — stillness under power.",
         "bn":"মায়ের প্রকোষ্ঠ জিহ্বা, মুণ্ডমালা আর বাহুর স্কার্ট — অহংকার ও সংসার কর্তনের প্রতীক। পদতলে শিব — শক্তির নিচে প্রশান্তি।"},
        {"keys":["pandal","light","chandannagar","decoration","theme","lighting"],
         "en":"**Kali Puja pandals** are temporary temples of art — bamboo, cloth, thermocol and genius. Kolkata neighbourhoods compete in themes, and lights from **Chandannagar** (famous for its illumination craft) turn streets into rivers of fire. The best are open-air galleries visited by millions.",
         "bn":"প্যান্ডেল — বাঁশ, কাপড় আর কারিগরির সৃষ্ট অস্থায়ী মন্দির। চন্দননগরের আলোকসজ্জা রাস্তা ভরে দেয় আলোর নদীতে।"},
        {"keys":["hello","hi","jai","namaste","pranam","greet"],
         "en":"**জয় মা কালী!** Ask me about Kali Puja, the temples of Dakshineswar and Kalighat, murtis and their makers, offerings, Shyama Sangeet, or the immersion at Nimtala Ghat.",
         "bn":"জয় মা কালী! কালীপূজা, মন্দির, প্রতিমা, ভোগ বা শ্যামা সঙ্গীত — যা জানতে চান, জিজ্ঞাসা করুন।"},
    ]

    def divine_answer(q):
        ql = q.lower()
        best,score = None,0
        for e in KALI_KB:
            s = sum(1 for k in e["keys"] if k in ql)
            if s > score:
                best,score = e,s
        return best

    def compose(entry,lang):
        if not entry:
            return ("The Mother keeps that mystery veiled, my child. Ask me about **Kali Puja**, "
                    "**Dakshineswar**, **Kalighat**, **Shyama Sangeet**, **Fata Kesto**, "
                    "**Kumartuli**, **offerings**, **visarjan**, **pandals**, or Her sacred form.")
        en,bn = entry["en"],entry["bn"]
        if lang == "বাংলা": return bn
        if lang == "Both": return f"{en}\n\n---\n\n{bn}"
        return en

    with st.container(border=True):
        st.markdown('<div class="assistant-label">RESPONSE LANGUAGE</div>', unsafe_allow_html=True)
        lang = st.pills(
            "Response language",
            ["English", "বাংলা", "Both"],
            default="English",
            label_visibility="collapsed",
        ) or "English"

    suggestions = [
        "What is Kali Puja?", "Tell me about Dakshineswar",
        "What is Shyama Sangeet?", "Why is Maa Kali's tongue out?",
        "What happens at visarjan?", "Who makes the murtis?"
    ]
    st.markdown('<div class="assistant-label">SACRED QUESTIONS</div>', unsafe_allow_html=True)
    picked = st.pills("Sacred questions", suggestions, label_visibility="collapsed")

    if "chat" not in st.session_state:
        st.session_state.chat = [{
            "role": "assistant",
            "content": (
                "**জয় মা কালী** — I am the keeper of Bengal's devotional lore. "
                "Ask me anything about the Mother, her temples, her night."
            )
        }]
        st.session_state.last_suggestion = None

    # The bar stays pinned to the bottom even though it is read first.
    # Answer in this same run — a second rerun was redrawing the whole site.
    prompt = st.chat_input("Ask of the Mother…")
    if picked and picked != st.session_state.last_suggestion:
        prompt = picked
        st.session_state.last_suggestion = picked
    elif picked is None:
        st.session_state.last_suggestion = None

    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.session_state.chat.append({
            "role": "assistant",
            "content": compose(divine_answer(prompt), lang)
        })

    with st.container(border=True):
        st.markdown('<div class="assistant-stage-mark"></div>', unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])


# =====================================================
# KOLKATA EXPLORER
# =====================================================

elif page == "Kolkata Explorer":

    st.html("""
<div class="explorer-header">
  <div class="explorer-kicker">PATHS THROUGH THE CITY</div>
  <h2 class="explorer-title">Smart Kolkata Explorer</h2>
  <div class="explorer-lede">
    <span class="explorer-lede-bar" aria-hidden="true"></span>
    <p>Walk the Mother's city — temples, visarjan ghats and artisan quarters — on an interactive map of Kali destinations in and around Kolkata.</p>
  </div>
</div>
""")

    KOLKATA_PLACES = [
        {
            "name": "Dakshineswar Kali Temple",
            "area": "Dakshineswar · North Kolkata",
            "query": "Dakshineswar Kali Temple, Kolkata",
            "lat": 22.6551,
            "lon": 88.3579,
            "kind": "Temple",
            "en": "Built by Rani Rashmoni in 1855 on the east bank of the Hooghly. The presiding deity is Bhavatarini — She who ferries souls across existence. Sri Ramakrishna served here as priest.",
            "bn": "দক্ষিণেশ্বর — রানী রাসমণির নির্মিত মন্দির, মা ভবতারিণীর আরাধনা।",
        },
        {
            "name": "Kalighat Kali Temple",
            "area": "Kalighat · South Kolkata",
            "query": "Kalighat Kali Temple, Kolkata",
            "lat": 22.5200,
            "lon": 88.3420,
            "kind": "Shakti Peetha",
            "en": "One of the 51 Shakti Peethas — where Sati's right toe is said to have fallen. The temple gave Kalikata (Kolkata) its name; the fierce gold face of the Mother is renewed each year.",
            "bn": "কালীঘাট — ৫১ শক্তিপীঠের একটি, কলকাতার নামের উৎস।",
        },
        {
            "name": "Fata Kesto Kali Puja",
            "area": "Central Kolkata",
            "query": "Fata Kesto Kali Puja, Kolkata",
            "lat": 22.5836,
            "lon": 88.3639,
            "kind": "Barowari Puja",
            "en": "One of Kolkata's oldest community (Barowari) Kali pujas — a neighbourhood vow turned into a street festival of light, still burning through Kartik Amavasya.",
            "bn": "ফটা কেস্তো — কলকাতার প্রাচীন বারোয়ারি কালীপূজার অন্যতম।",
        },
        {
            "name": "Thanthania Kalibari",
            "area": "College Street · Central Kolkata",
            "query": "Thanthania Kalibari, Kolkata",
            "lat": 22.5755,
            "lon": 88.3632,
            "kind": "Temple",
            "en": "An 18th-century neighbourhood Kali shrine near College Street — intimate, continuous worship that predates many of the city's grand pandals.",
            "bn": "ঠনঠনিয়া কালীবাড়ি — কলেজ স্ট্রিটের কাছে পুরোনো পাড়ার মন্দির।",
        },
        {
            "name": "Kumartuli",
            "area": "Sovabazar · North Kolkata",
            "query": "Kumartuli, Kolkata",
            "lat": 22.6019,
            "lon": 88.3614,
            "kind": "Artisan Quarter",
            "en": "The potters' quarter where murtis are born — Hooghly clay over bamboo frames, painted and crowned before Durga and Kali seasons fill the lanes.",
            "bn": "কুমারটুলি — যেখানে প্রতিমা জন্ম নেয়।",
        },
        {
            "name": "Nimtala Ghat",
            "area": "Hooghly · North Kolkata",
            "query": "Nimtala Ghat, Kolkata",
            "lat": 22.5950,
            "lon": 88.3510,
            "kind": "Visarjan Ghat",
            "en": "A principal immersion ghat on the Hooghly — where processions bring the Mother's image to the river after puja, drums (dhak) answering the night.",
            "bn": "নিমতলা ঘাট — বিসর্জনের অন্যতম প্রধান ঘাট।",
        },
    ]

    place_names = [p["name"] for p in KOLKATA_PLACES]

    def geocode_kolkata(query):
        """Free Nominatim search, biased to the Kolkata region. No API key."""
        q = (query or "").strip()
        if not q:
            return []
        # Prefer Kolkata context without forcing bounded-only results
        search_q = q if "kolkata" in q.lower() or "calcutta" in q.lower() else f"{q}, Kolkata"
        url = (
            "https://nominatim.openstreetmap.org/search?"
            f"q={quote(search_q)}&format=json&limit=6&addressdetails=1"
            "&viewbox=88.15,22.35,88.60,22.80&bounded=0"
        )
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "KALI-VISION-AI/1.0 (cultural education; local app)"},
        )
        with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def place_from_nominatim(hit):
        display = hit.get("display_name") or "Unknown place"
        short = display.split(",")[0].strip()
        kind = (hit.get("type") or hit.get("class") or "Place").replace("_", " ").title()
        return {
            "name": short,
            "area": display,
            "query": display,
            "lat": float(hit["lat"]),
            "lon": float(hit["lon"]),
            "kind": kind,
            "en": f"Located via OpenStreetMap search — {display}.",
            "bn": "",
            "custom": True,
        }

    if "explorer_place" not in st.session_state:
        st.session_state.explorer_place = place_names[0]
    if "explorer_source" not in st.session_state:
        st.session_state.explorer_source = "curated"
    if "explorer_custom" not in st.session_state:
        st.session_state.explorer_custom = None
    if "explorer_hits" not in st.session_state:
        st.session_state.explorer_hits = []

    with st.container(border=True):
        st.markdown('<div class="explorer-label">SACRED DESTINATIONS</div>', unsafe_allow_html=True)
        picked = st.pills(
            "Sacred destinations",
            place_names,
            default=st.session_state.explorer_place if st.session_state.explorer_place in place_names else place_names[0],
            label_visibility="collapsed",
            key="explorer_pills",
        )
        if picked and picked != st.session_state.get("_explorer_last_pill"):
            # Switching curated pill clears free-search selection
            st.session_state.explorer_source = "curated"
            st.session_state.explorer_custom = None
            st.session_state.explorer_hits = []
            st.session_state.explorer_place = picked
            st.session_state._explorer_last_pill = picked
        elif picked and st.session_state.explorer_source != "search":
            st.session_state.explorer_place = picked
            st.session_state._explorer_last_pill = picked

        st.markdown('<div class="explorer-label" style="margin-top:14px">SEARCH YOUR OWN</div>', unsafe_allow_html=True)
        s1, s2 = st.columns([3.2, 1])
        with s1:
            search_q = st.text_input(
                "Search destination",
                placeholder="e.g. Belur Math, Adyapith, Lake Kalibari…",
                label_visibility="collapsed",
                key="explorer_search_q",
            )
        with s2:
            do_search = st.button("Search", use_container_width=True, key="explorer_search_btn")

        if do_search:
            if not (search_q or "").strip():
                st.warning("Enter a place name to search.")
            else:
                try:
                    hits = geocode_kolkata(search_q)
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError) as e:
                    hits = []
                    st.error(f"Search could not complete right now: {e}")
                st.session_state.explorer_hits = hits or []
                if hits:
                    st.session_state.explorer_custom = place_from_nominatim(hits[0])
                    st.session_state.explorer_source = "search"
                else:
                    st.session_state.explorer_custom = None
                    st.warning("No matching place found. Try adding “Kolkata” or a fuller name.")

        if st.session_state.explorer_hits:
            hit_labels = [h.get("display_name", "Result") for h in st.session_state.explorer_hits]
            choice = st.selectbox(
                "Search results",
                hit_labels,
                label_visibility="collapsed",
                key="explorer_hit_choice",
            )
            chosen = next(
                (h for h in st.session_state.explorer_hits if h.get("display_name") == choice),
                st.session_state.explorer_hits[0],
            )
            st.session_state.explorer_custom = place_from_nominatim(chosen)
            st.session_state.explorer_source = "search"

    if st.session_state.explorer_source == "search" and st.session_state.explorer_custom:
        place = st.session_state.explorer_custom
        selected_name = place["name"]
    else:
        selected_name = st.session_state.explorer_place
        place = next(p for p in KOLKATA_PLACES if p["name"] == selected_name)

    maps_url = "https://www.google.com/maps/search/?api=1&query=" + quote(place["query"])
    osm_url = (
        f"https://www.openstreetmap.org/?mlat={place['lat']}&mlon={place['lon']}"
        f"#map=16/{place['lat']}/{place['lon']}"
    )

    left, right = st.columns([0.95, 1.15], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="explorer-stage-mark"></div>', unsafe_allow_html=True)
            st.markdown('<div class="explorer-label">DESTINATION</div>', unsafe_allow_html=True)
            st.markdown(f'<h3 class="explorer-place-name">{place["name"]}</h3>', unsafe_allow_html=True)
            area_line = place["area"] if len(place["area"]) < 90 else place["area"][:87] + "…"
            st.markdown(
                f'<div class="explorer-place-meta">{place["kind"].upper()} · {area_line.upper()}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<p class="explorer-place-body">{place["en"]}</p>', unsafe_allow_html=True)
            if place.get("bn"):
                st.markdown(f'<p class="explorer-place-bn">{place["bn"]}</p>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="explorer-coords">
                  <span class="explorer-chip">{place["lat"]:.4f} N</span>
                  <span class="explorer-chip">{place["lon"]:.4f} E</span>
                  <span class="explorer-chip">{place["kind"]}</span>
                </div>
                <div class="explorer-spacer" aria-hidden="true"></div>
                """,
                unsafe_allow_html=True,
            )
            b1, b2 = st.columns(2)
            with b1:
                st.link_button("Open in Google Maps", maps_url, use_container_width=True)
            with b2:
                st.link_button("Open in OpenStreetMap", osm_url, use_container_width=True)

    with right:
        with st.container(border=True):
            st.markdown('<div class="explorer-stage-mark"></div>', unsafe_allow_html=True)
            st.markdown('<div class="explorer-label">INTERACTIVE MAP</div>', unsafe_allow_html=True)

            # OpenStreetMap tiles — free, no API key. CSS filter darkens to match theme.
            import folium
            fmap = folium.Map(
                location=[place["lat"], place["lon"]],
                zoom_start=13 if not place.get("custom") else 14,
                tiles="OpenStreetMap",
                control_scale=True,
                width="100%",
                height=480,
            )
            fmap.get_root().header.add_child(folium.Element("""
<style>
  .leaflet-container { background:#140910 !important; }
  .leaflet-tile-pane { filter:invert(1) hue-rotate(180deg) brightness(.9) contrast(1.05) saturate(.85); }
  .leaflet-control-zoom a {
    background:#1c0c12 !important; color:#E5BC70 !important;
    border-color:rgba(229,188,112,.35) !important;
  }
  .leaflet-control-attribution {
    background:rgba(20,10,16,.85) !important; color:#A58A79 !important;
  }
  .leaflet-control-attribution a { color:#E5BC70 !important; }
</style>
"""))
            for p in KOLKATA_PLACES:
                active = (not place.get("custom")) and p["name"] == selected_name
                folium.CircleMarker(
                    location=[p["lat"], p["lon"]],
                    radius=12 if active else 8,
                    color="#F0CD85" if active else "#C48A39",
                    weight=2,
                    fill=True,
                    fill_color="#D6336C" if active else "#761F35",
                    fill_opacity=0.92 if active else 0.75,
                    tooltip=p["name"],
                    popup=folium.Popup(
                        f"<div style='font-family:Georgia,serif;min-width:180px'>"
                        f"<b style='color:#761F35'>{p['name']}</b><br>"
                        f"<span style='color:#555'>{p['kind']} · {p['area']}</span><br><br>"
                        f"{p['en'][:160]}…"
                        f"</div>",
                        max_width=280,
                    ),
                ).add_to(fmap)

            folium.Marker(
                location=[place["lat"], place["lon"]],
                tooltip=f"Selected · {place['name']}",
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(fmap)

            components.html(fmap._repr_html_(), height=500, scrolling=False)

    st.markdown(
        """
        <div class="explorer-note">
          <b>Map</b> — free OpenStreetMap tiles &amp; Nominatim search (no API key).
          Curated markers stay visible when you search your own place.
          <br><b>Visit mindfully</b> — confirm opening hours and crowd conditions before you go.
          Coordinates are approximate cultural landmarks, not official GIS survey points.
    </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# KOLKATA METRO
# =====================================================

elif page == "Kolkata Metro":
    from modules.metro.metro_ui import render_metro_page

    render_metro_page()


# =====================================================
# ANALYTICS
# =====================================================

elif page == "Analytics":
    import pandas as pd
    import plotly.express as px

    st.markdown('<div class="section-label">READING THE SACRED DATA</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cultural Data Analytics</div>', unsafe_allow_html=True)
    st.write("The living archive of the collection — its shape, weight and composition.")

    if images:

        rows = []
        for p in images:
            size_kb = round(p.stat().st_size/1024,2)
            w,h = None,None
            try:
                w, h = original_image_size(p)
            except Exception:
                pass
            rows.append({
                "Image":p.name,
                "Category":image_category(p.name),
                "Size KB":size_kb,
                "Width":w,"Height":h,
                "Orientation":("Portrait" if h>w else "Square" if h==w else "Landscape") if w else "Unknown"
            })
        df = pd.DataFrame(rows)

        largest = df.loc[df["Size KB"].idxmax()]
        total_mb = df["Size KB"].sum()/1024

        a,b,c,d = st.columns(4)
        metrics = [
            (str(len(df)),"SACRED FRAMES"),
            (str(df["Category"].nunique()),"COLLECTIONS"),
            (f"{total_mb:.1f}","MB OF HERITAGE"),
            (f"{largest['Size KB']/1024:.1f} MB","LARGEST FRAME")
        ]
        for i,(col,(v,l)) in enumerate(zip([a,b,c,d],metrics)):
            with col:
                st.markdown(f"""
                <div class="metric-box" style="animation-delay:{i*0.12}s">
                    <div class="metric-value">{v}</div>
                    <div class="metric-caption">{l}</div>
                </div>
                """,unsafe_allow_html=True)

        PALETTE = ["#E5BC70","#D6336C","#761F35","#F4D7A1","#FF7A3D","#A58A79","#8E5BEF"]

        def theme_fig(fig):
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#B9A7A4",family="Inter"),
                title_font=dict(color="#F8ECDD",family="Cormorant Garamond",size=24),
                legend=dict(font=dict(color="#B9A7A4")),
                margin=dict(t=70,b=30,l=20,r=20)
            )
            return fig

        counts = df["Category"].value_counts().reset_index()
        counts.columns = ["Category","Images"]

        diya_divider()
        st.markdown('<div class="section-label">COMPOSITION</div>',unsafe_allow_html=True)

        with st.expander("📊 Reveal charts — tap to render the visualisations", expanded=False):
            left,right = st.columns(2,gap="large")

            with left:
                fig = px.pie(
                    counts,names="Category",values="Images",hole=0.62,
                    title="Collection by Category",
                    color_discrete_sequence=PALETTE
                )
                fig.update_traces(textfont_color="#F8ECDD",marker=dict(line=dict(color="#0B0608",width=2)))
                st.plotly_chart(theme_fig(fig),use_container_width=True)

            with right:
                orient = df["Orientation"].value_counts().reset_index()
                orient.columns = ["Orientation","Images"]
                fig2 = px.pie(
                    orient,names="Orientation",values="Images",hole=0.62,
                    title="Portrait vs Landscape",
                    color_discrete_sequence=["#D6336C","#E5BC70","#761F35","#A58A79"]
                )
                fig2.update_traces(textfont_color="#F8ECDD",marker=dict(line=dict(color="#0B0608",width=2)))
                st.plotly_chart(theme_fig(fig2),use_container_width=True)

            diya_divider()
            st.markdown('<div class="section-label">WEIGHT OF THE COLLECTION</div>',unsafe_allow_html=True)

            weight = df.groupby("Category",as_index=False)["Size KB"].sum()
            weight["Size MB"] = (weight["Size KB"]/1024).round(2)
            fig3 = px.bar(
                weight,x="Category",y="Size MB",color="Category",
                title="Dataset Weight by Collection",
                color_discrete_sequence=PALETTE
            )
            fig3.update_traces(marker_line_width=0,opacity=.92)
            fig3.update_layout(showlegend=False)
            st.plotly_chart(theme_fig(fig3),use_container_width=True)

        diya_divider()
        st.markdown('<div class="section-label">DIVINE INSIGHTS</div>',unsafe_allow_html=True)

        dominant = counts.iloc[0]
        big = df.loc[df["Size KB"].idxmax()]
        avg_kb = df["Size KB"].mean()

        i1,i2,i3 = st.columns(3)
        insights = [
            (i1,"DOMINANT COLLECTION",dominant["Category"],f"{dominant['Images']} frames lead the archive"),
            (i2,"HEAVIEST FRAME",image_title(Path(big["Image"])),f"{big['Size KB']/1024:.1f} MB of detail"),
            (i3,"AVERAGE WEIGHT",f"{avg_kb/1024:.2f} MB","across the whole collection")
        ]
        for col,label,val,sub in insights:
            with col:
                st.markdown(f"""
                <div class="info-panel" style="text-align:center">
                    <div class="metric-caption" style="text-align:center;margin-bottom:8px">{label}</div>
                    <div style="font-family:'Cormorant Garamond',serif;color:#E5BC70;font-size:24px">{val}</div>
                    <p style="margin:6px 0 0">{sub}</p>
                </div>
                """,unsafe_allow_html=True)

        diya_divider()
        st.markdown('<div class="section-label">DATASET INVENTORY</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title" style="font-size:clamp(28px,3.5vw,40px);margin-bottom:8px">Archive ledger</div>',
            unsafe_allow_html=True,
        )

        inv = df[["Image", "Category", "Width", "Height", "Orientation", "Size KB"]].copy()
        inv = inv.sort_values(["Category", "Image"]).reset_index(drop=True)
        body_rows = []
        for _, row in inv.iterrows():
            w = "—" if pd.isna(row["Width"]) else f'{int(row["Width"])}'
            h = "—" if pd.isna(row["Height"]) else f'{int(row["Height"])}'
            body_rows.append(
                "<tr>"
                f'<td class="inv-name">{html_escape(str(row["Image"]))}</td>'
                f'<td><span class="inv-cat">{html_escape(str(row["Category"]))}</span></td>'
                f'<td class="inv-num">{w}</td>'
                f'<td class="inv-num">{h}</td>'
                f'<td>{html_escape(str(row["Orientation"]))}</td>'
                f'<td class="inv-num">{row["Size KB"]:.2f}</td>'
                "</tr>"
            )
        inventory_html = f"""
<div class="inventory-panel">
  <div class="inventory-scroll">
    <table class="inventory-table">
      <thead>
        <tr>
          <th>Image</th>
          <th>Category</th>
          <th>Width</th>
          <th>Height</th>
          <th>Orientation</th>
          <th>Size KB</th>
        </tr>
      </thead>
      <tbody>
        {''.join(body_rows)}
      </tbody>
    </table>
  </div>
  <div class="inventory-foot">
    <span>{len(inv)} sacred frames in the living archive</span>
    <span>Scroll to explore the full ledger</span>
  </div>
</div>
"""
        st.html(inventory_html)

        try:
            pdf_bytes = build_analytics_pdf(df, counts, weight, total_mb, largest)
        except Exception as e:
            pdf_bytes = None
            st.error(f"Unable to build PDF report: {e}")

        if pdf_bytes:
            with st.container(border=True):
                st.markdown('<div class="inventory-actions-mark"></div>', unsafe_allow_html=True)
        st.download_button(
                    "Download dataset report (PDF)",
                    data=pdf_bytes,
                    file_name="kali_vision_dataset_report.pdf",
                    mime="application/pdf",
        )

    else:
        st.info("Add images to your assets folder to generate analytics.")


# =====================================================
# ABOUT
# =====================================================

elif page == "About":

    st.markdown('<div class="section-label">THE SOUL OF THE PROJECT</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">About KALI VISION AI</div>',unsafe_allow_html=True)

    left,right = st.columns([1.05,0.95],gap="large")

    with left:
        st.markdown("""
        <div class="info-panel" style="animation-delay:.15s">
            <h3 style="color:#E5BC70">The Divine Intelligence of Bengal</h3>
            <p>
            KALI VISION AI is a cultural technology project devoted to Bengal's
            living heritage. On the darkest night of the year, when a million
            diyas answer the Mother, this project asks a modern question —
            can machines learn reverence?
            </p>
            <p>
            Through computer vision, data analytics and curated cultural
            knowledge, it maps the visual and spiritual landscape of Kali Puja:
            the temples, the pandals, the murtis of Kumartuli, the drums and
            the river that carries Her home.
            </p>
        </div>
        """,unsafe_allow_html=True)

        st.markdown("""
        <div class="verse">
            <div class="verse-bn">মা তুমি গো প্রভাতবর, প্রভাতে যার ভবনদ্রমে দুঃখ আঁধারে</div>
            <div class="verse-en">"Mother, you are the dawn's gift — in whose house sorrow dwells in darkness"</div>
            <div class="metric-caption" style="text-align:left;margin-top:8px">SHYAMA SANGEET TRADITION</div>
        </div>
        """,unsafe_allow_html=True)

    with right:
        st.markdown('<div class="hero-frame" style="animation-delay:.25s">',unsafe_allow_html=True)
        about_img = ASSET_DIR / "kali_murti_south_kolkata_01.jpg"
        if not about_img.exists():
            about_img = ASSET_DIR / "maa_kali_hero.webp"
        if not about_img.exists():
            about_img = ASSET_DIR / "maa_kali_hero.png"
        if about_img.exists() and about_img.stat().st_size > 0:
            about_url = web_image(about_img, max_edge=720, quality=56)[0]
            st.markdown(
                f'<img src="{about_url}" alt="Maa Kali" style="width:100%;height:auto;display:block;border-radius:12px;">',
                unsafe_allow_html=True,
            )
        st.markdown('</div>',unsafe_allow_html=True)

    diya_divider()

    st.markdown("""
    <div class="section-label">THE VISION</div>
    <div class="section-title">Preserve · Illuminate · Understand</div>
    """,unsafe_allow_html=True)

    vision = [
        ("01","Preserve","Digitise the visual memory of Kali Puja — pandals, murtis, rituals — before the night fades."),
        ("02","Illuminate","Let light move through the interface like flames through a pandal — culture as experience, not data."),
        ("03","Understand","Teach machines the grammar of devotion: colour, form, symbol, season.")
    ]
    cols = st.columns(3)
    for i,(col,item) in enumerate(zip(cols,vision)):
        with col:
            st.markdown(f"""
            <div class="feature-card" style="animation-delay:{0.15+i*0.12}s">
                <div class="feature-icon">{item[0]}</div>
                <h3>{item[1]}</h3>
                <p>{item[2]}</p>
            </div>
            """,unsafe_allow_html=True)

    diya_divider()

    st.markdown("""
    <div class="section-label">THE TEMPLE'S FRAMEWORK</div>
    <div class="section-title">Technology Stack</div>
    """,unsafe_allow_html=True)

    tech = [
        ("UI","Frontend","Streamlit · bespoke CSS design system"),
        ("PY","Language","Python 3"),
        ("DATA","Data","Pandas · NumPy"),
        ("VIZ","Visualisation","Plotly Express"),
        ("IMG","Imagery","Pillow · sacred gallery archive"),
        ("AI","Intelligence","Curated KB · LLM + RAG (roadmap)")
    ]
    for i in range(0,len(tech),3):
        cols = st.columns(3)
        for j,(col,item) in enumerate(zip(cols,tech[i:i+3])):
            with col:
                st.markdown(f"""
                <div class="feature-card" style="min-height:130px;animation-delay:{(i+j)*0.08}s">
                    <div class="feature-icon">{item[0]}</div>
                    <h3>{item[1]}</h3>
                    <p>{item[2]}</p>
                </div>
                """,unsafe_allow_html=True)

    diya_divider()

    st.markdown("""
    <div class="section-label">THE PATH AHEAD</div>
    <div class="section-title">Journey of the Project</div>
    """,unsafe_allow_html=True)

    m1,m2 = st.columns(2,gap="large")
    with m1:
        st.markdown("""
        <div class="info-panel">
            <h3 style="color:#E5BC70">✦ Now</h3>
            <ul class="road-list">
                <li class="done">Cinematic Kali Puja interface — embers, diyas, alpana</li>
                <li class="done">Sacred gallery — authentic frames of Bengal's Kali Puja</li>
                <li class="done">Devotional audio — Shyama Sangeet site-wide</li>
                <li class="done">Curated knowledge assistant</li>
                <li class="done">Dataset analytics</li>
            </ul>
        </div>
        """,unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="info-panel">
            <h3 style="color:#E5BC70">✦ Next</h3>
            <ul class="road-list">
                <li>Trained murti & pandal classifier (PyTorch)</li>
                <li>Full LLM + RAG conversational assistant</li>
                <li>Interactive map of Kolkata's Kali temples</li>
                <li>Community photo & bhog recipe submissions</li>
                <li>Bengali-first interface mode</li>
            </ul>
        </div>
        """,unsafe_allow_html=True)

    diya_divider()

    st.markdown("""
    <div class="section-label">OFFERINGS & GRATITUDE</div>
    <div class="section-title">Credits</div>
    """,unsafe_allow_html=True)

    st.markdown("""
    <div class="info-panel">
        <p><b style="color:#E5BC70">Photographs</b> — Wikimedia Commons contributors, CC BY / CC BY-SA:
        Kolkata Kali Puja pandals (Behala, College Square, Pramanick Bari),
        Kalighat-style murti replicas, Nimtala Ghat visarjan,
        and Dakshineswar &amp; Kalighat temple photographs.</p>
        <p><b style="color:#E5BC70">Typography</b> — Cormorant Garamond, Cinzel Decorative, Tiro Bangla (Google Fonts)</p>
        <p><b style="color:#E5BC70">Sound</b> — Shyama Sangeet, the devotional song tradition of Bengal</p>
        <p style="margin-top:14px">Made in Bengal, for the Mother. <span class="verse-bn" style="font-size:18px">জয় মা কালী</span></p>
    </div>
    """,unsafe_allow_html=True)


# =====================================================
# FOOTER (hidden on Metro — map is full-bleed; footer caused a black flash)
# =====================================================

if page != "Kolkata Metro":
    st.markdown("""
<div class="footer">
    <div class="footer-diyas"><span>✦</span><span>✦</span><span>✦</span></div>
    ✦ BUILT WITH INTELLIGENCE · INSPIRED BY DIVINITY ✦
    <br><br>
    JAI MAA KALI
    <br><br>
    KALI VISION AI © 2026
</div>
""", unsafe_allow_html=True)
