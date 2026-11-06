
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import os
import json
import shutil
import ssl
import urllib.error
import urllib.request
from datetime import datetime
from html import escape as html_escape
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageStat
from urllib.parse import quote
import plotly.express as px
import folium
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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

.block-container {
    max-width:1500px;
    padding-top:1.2rem;
    padding-bottom:3rem;
    animation:fadeUp .75s ease both;
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
    grid-template-columns:1.4fr 1fr 1fr 1fr;
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
    opacity:.42;
    filter:sepia(.28) saturate(.8) brightness(.62);
}
.exp-card-bg::after {
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(165deg,rgba(12,6,10,.82) 0%,rgba(18,8,12,.78) 48%,rgba(12,6,10,.9) 100%);
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
    opacity:.48;
    background-position:center 40%;
    filter:sepia(.35) saturate(.85) brightness(.68);
}
.exp-card-01 .exp-card-bg::after {
    background:
        linear-gradient(90deg,rgba(12,6,10,.94) 0%,rgba(12,6,10,.72) 46%,rgba(12,6,10,.28) 100%),
        linear-gradient(180deg,rgba(12,6,10,.2) 0%,rgba(12,6,10,.55) 100%);
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
.exp-card-03 {grid-column:3 / 5;grid-row:1;}
.exp-card-04 {grid-column:2;grid-row:2;}
.exp-card-05 {grid-column:3;grid-row:2;}
.exp-card-06 {grid-column:4;grid-row:2;}
@media (max-width:1100px) {
    .experience-bento {
        grid-template-columns:1.2fr 1fr 1fr;
        grid-template-rows:auto auto auto;
    }
    .exp-card-01 {grid-column:1;grid-row:1 / 3;min-height:280px;}
    .exp-card-02 {grid-column:2;grid-row:1;}
    .exp-card-03 {grid-column:3;grid-row:1;}
    .exp-card-04 {grid-column:2;grid-row:2;}
    .exp-card-05 {grid-column:3;grid-row:2;}
    .exp-card-06 {grid-column:1 / -1;grid-row:3;min-height:120px;}
    .exp-card-06.exp-mini {
        flex-direction:row;
        align-items:center;
        justify-content:space-between;
    }
    .exp-card-06 .exp-mini-body {margin-top:0;flex-direction:row;align-items:center;gap:16px;}
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
    .exp-card-02,.exp-card-03,.exp-card-04,.exp-card-05,.exp-card-06 {
        grid-column:auto;grid-row:auto;
        min-height:150px;
    }
    .exp-card-06.exp-mini {
        flex-direction:column;
        align-items:stretch;
    }
    .exp-card-06 .exp-mini-body {flex-direction:column;align-items:flex-start;}
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
    animation:fadeUp .8s ease both;
}
.gcard img {
    width:100%;
    display:block;
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
    animation:fadeUp .45s ease both;
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
/* Sticky bottom chat bar — transparent dock, input keeps its own surface */
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background:transparent !important;
    background-color:transparent !important;
    border-top:none !important;
    box-shadow:none !important;
    padding-bottom:10px !important;
}
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] [class*="st-emotion-cache"],
[data-testid="stChatInput"] .st-bz,
.st-emotion-cache-1353z0o,
.st-bz {
    background:transparent !important;
    background-color:transparent !important;
}
[data-testid="stChatInput"] {
    border:1px solid rgba(229,188,112,.42) !important;
    border-radius:999px !important;
    box-shadow:none !important;
    max-width:100%;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    color:#F8ECDD !important;
    caret-color:var(--gold);
    background:transparent !important;
    background-color:transparent !important;
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
.stButton>button {
    background:linear-gradient(120deg,#F0CD85,#C48A39);
    color:#180B0C;
    border:none;
    border-radius:30px;
    font-weight:600;
    transition:.3s;
}
.stButton>button:hover {
    background:#FFE0A0;
    color:#180B0C;
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
    z-index:1000;
    width:min(380px,calc(100vw - 36px));
    padding:14px 16px 12px;
    border:1px solid rgba(229,188,112,.38);
    border-radius:16px;
    background:rgba(17,8,14,.97);
    backdrop-filter:blur(12px);
    box-shadow:0 10px 36px rgba(0,0,0,.6),0 0 24px rgba(229,188,112,.12);
    animation:fadeUp .9s .3s ease both;
    font-family:'Inter',sans-serif;
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

/* ---------- HOME / GLOBAL RESPONSIVE ---------- */
div[data-testid="stRadio"] > div {
    flex-wrap:wrap !important;
    gap:6px 4px !important;
}
div[data-testid="stRadio"] label {
    margin-bottom:2px !important;
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
    div[data-testid="stRadio"] label p {font-size:13px !important;}
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

def image_category(filename):
    name = str(filename).lower()
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

def get_image_stats(file):
    with Image.open(file) as img:
        rgb = img.convert("RGB")
        pixels = np.array(rgb.resize((100, 100)))
        stat = ImageStat.Stat(rgb)
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "brightness": round(sum(stat.mean)/3, 2),
            "red": round(stat.mean[0], 2),
            "green": round(stat.mean[1], 2),
            "blue": round(stat.mean[2], 2),
            "aspect_ratio": round(img.width/img.height, 2),
            "pixels": pixels
        }

def build_analytics_pdf(df, counts, weight, total_mb, largest_row):
    """Build a themed PDF dataset report (bytes)."""
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

def sync_static_assets(files, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for p in files:
        d = dest_dir / p.name
        if not d.exists() or d.stat().st_size != p.stat().st_size:
            shutil.copy2(p, d)


# =====================================================
# NAVIGATION
# =====================================================

st.markdown("""
<div class="navbar">
    <div class="brand">✦ KALI VISION AI</div>
    <div class="nav-sub">BENGAL · CULTURE · INTELLIGENCE</div>
</div>
<div class="alpana"></div>
""", unsafe_allow_html=True)

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
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a"}
DEFAULT_MUSIC_VOLUME = 0.05

def get_music_tracks():
    if not MUSIC_DIR.exists():
        return []
    return sorted([
        p for p in MUSIC_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
        and p.stat().st_size > 0
    ])

def pick_shyama_sangeet(tracks):
    for p in tracks:
        n = p.name.lower()
        if "tumi" in n or "giri" in n or "shyama" in n or "sangeet" in n:
            return p
    return tracks[0] if tracks else None

music_tracks = get_music_tracks()
music_track = pick_shyama_sangeet(music_tracks)

if music_track:
    sync_static_assets([music_track], STATIC_MUSIC_DIR)
    music_src = "/app/static/music/" + quote(music_track.name)
    music_title = image_title(music_track)
    vol_pct = int(DEFAULT_MUSIC_VOLUME * 100)
    # Inject into the parent page so controls work and playback
    # survives Streamlit reruns. Autostarts at 1% volume; user can change it.
    components.html(
        f"""
        <script>
        (function () {{
          const doc = window.parent.document;
          const SRC = {music_src!r};
          const TITLE = {music_title!r};
          const DEFAULT_VOL = {vol_pct};

          const PLAYER_VERSION = "v3-no-emoji";
          let player = doc.getElementById("kali-music-player");
          if (player && player.dataset.version !== PLAYER_VERSION) {{
            if (player._kaliBlobUrl) URL.revokeObjectURL(player._kaliBlobUrl);
            player.remove();
            player = null;
          }}
          if (!player) {{
            player = doc.createElement("div");
            player.id = "kali-music-player";
            player.className = "music-player";
            player.dataset.version = PLAYER_VERSION;
            player.innerHTML = `
              <div class="mp-top">
                <span class="mp-diya" id="mp-diya">✦</span>
                <div class="mp-meta">
                  <div class="mp-label">SHYAMA SANGEET</div>
                  <div class="mp-track" id="mp-track"></div>
                </div>
                <span class="mp-status" id="mp-status">Loading</span>
              </div>
              <div class="mp-controls">
                <button type="button" class="mp-btn primary" id="mp-play"
                        aria-label="Play or pause" title="Play / Pause">▶</button>
                <button type="button" class="mp-btn" id="mp-stop"
                        aria-label="Stop" title="Stop">■</button>
                <div class="mp-vol">
                  <span class="mp-vol-icon" id="mp-vol-icon" aria-hidden="true">Vol</span>
                  <input type="range" id="mp-volume" min="0" max="100"
                         aria-label="Volume" title="Volume">
                  <span class="mp-vol-pct" id="mp-vol-pct"></span>
                </div>
              </div>
              <audio id="mp-audio" preload="auto" loop></audio>
            `;
            doc.body.appendChild(player);

            const audio = player.querySelector("#mp-audio");
            const playBtn = player.querySelector("#mp-play");
            const stopBtn = player.querySelector("#mp-stop");
            const statusEl = player.querySelector("#mp-status");
            const diyaEl = player.querySelector("#mp-diya");
            const trackEl = player.querySelector("#mp-track");
            const volInput = player.querySelector("#mp-volume");
            const volPctEl = player.querySelector("#mp-vol-pct");
            const volIcon = player.querySelector("#mp-vol-icon");

            const applyVolume = (pct) => {{
              const v = Math.max(0, Math.min(100, Number(pct))) / 100;
              audio.muted = false;
              audio.volume = v;
              volPctEl.textContent = Math.round(v * 100) + "%";
              volIcon.textContent = v === 0 ? "Mute" : "Vol";
            }};

            const setUi = (state) => {{
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

            const tryAutostart = async () => {{
              if (player._kaliAutostarted || player._kaliUserStopped) return;
              player._kaliAutostarted = true;
              applyVolume(volInput.value || DEFAULT_VOL);
              try {{
                await audio.play();
                setUi("Playing");
                return;
              }} catch (_) {{}}
              // Fallback for strict autoplay policies: start muted, then restore 1%.
              try {{
                audio.muted = true;
                await audio.play();
                audio.muted = false;
                applyVolume(volInput.value || DEFAULT_VOL);
                setUi("Playing");
              }} catch (_) {{
                setUi("Stopped");
                statusEl.textContent = "Tap ▶";
              }}
            }};

            playBtn.addEventListener("click", async () => {{
              try {{
                if (audio.paused) {{
                  player._kaliUserStopped = false;
                  await audio.play();
                  setUi("Playing");
                }} else {{
                  audio.pause();
                  setUi("Paused");
                }}
              }} catch (err) {{
                setUi("Stopped");
                statusEl.textContent = "Blocked";
              }}
            }});

            stopBtn.addEventListener("click", () => {{
              player._kaliUserStopped = true;
              audio.pause();
              audio.currentTime = 0;
              setUi("Stopped");
            }});

            volInput.addEventListener("input", () => applyVolume(volInput.value));
            audio.addEventListener("play", () => setUi("Playing"));
            audio.addEventListener("pause", () => {{
              if (audio.currentTime === 0 || audio.ended) setUi("Stopped");
              else setUi("Paused");
            }});

            volInput.value = String(DEFAULT_VOL);
            applyVolume(DEFAULT_VOL);
            setUi("Loading");
            player._kaliAudio = audio;
            player._kaliTrack = trackEl;
            player._kaliSetUi = setUi;
            player._kaliTryAutostart = tryAutostart;
          }}

          const audio = player._kaliAudio;
          const trackEl = player._kaliTrack;
          trackEl.textContent = TITLE;
          trackEl.title = TITLE;

          // Streamlit serves non-whitelisted static types as text/plain + nosniff,
          // so fetch bytes and attach a proper audio/mpeg blob URL.
          const loadTrack = async () => {{
            if (player._kaliSrc === SRC && audio.src) {{
              if (!player._kaliAutostarted) await player._kaliTryAutostart();
              return;
            }}
            const wasPlaying = !audio.paused && !!audio.src;
            const t = audio.currentTime || 0;
            try {{
              const res = await fetch(SRC);
              if (!res.ok) throw new Error("fetch failed");
              const buf = await res.arrayBuffer();
              if (player._kaliBlobUrl) URL.revokeObjectURL(player._kaliBlobUrl);
              const blobUrl = URL.createObjectURL(new Blob([buf], {{ type: "audio/mpeg" }}));
              player._kaliBlobUrl = blobUrl;
              player._kaliSrc = SRC;
              audio.src = blobUrl;
              audio.load();
              if (wasPlaying) {{
                audio.currentTime = t;
                await audio.play();
              }} else if (!player._kaliAutostarted) {{
                await player._kaliTryAutostart();
              }}
            }} catch (err) {{
              player._kaliSetUi("Stopped");
              const statusEl = player.querySelector("#mp-status");
              if (statusEl) statusEl.textContent = "Unavailable";
            }}
          }};
          loadTrack();
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
else:
    st.caption(
        "Drop a Shyama Sangeet track into assets/music/ "
        "to enable the music player."
    )

pages = [
    "Home", "AI Assistant", "Gallery",
    "Vision Lab", "Kolkata Explorer",
    "Analytics", "About"
]

if "page" not in st.session_state:
    st.session_state.page = "Home"

# Deep-link CTAs from HTML (e.g. Experience "Explore Now")
_nav_q = st.query_params.get("nav")
if _nav_q in pages:
    st.session_state.navigation = _nav_q
    st.query_params.clear()

page = st.radio(
    "Navigation",
    pages,
    horizontal=True,
    label_visibility="collapsed",
    key="navigation"
)

st.divider()

images = get_images()

# =====================================================
# AMBIENT KALI BACKGROUND
# =====================================================

hero_bg = ASSET_DIR / "maa_kali_hero.png"
if not hero_bg.exists():
    hero_bg = ASSET_DIR / "maa_kali_hero.jpg"

if hero_bg.exists() and hero_bg.stat().st_size > 0:
    sync_static_assets([hero_bg], STATIC_IMG_DIR)
    st.markdown(f"""
    <style>
    .stApp {{
        background:
            linear-gradient(165deg,
                rgba(9,4,8,.58) 0%,
                rgba(15,7,12,.74) 42%,
                rgba(9,4,8,.90) 72%,
                rgba(8,5,9,.97) 100%),
            radial-gradient(ellipse at 82% 6%,rgba(118,31,53,.55) 0%,transparent 46%),
            radial-gradient(ellipse at 10% 94%,rgba(214,51,108,.14) 0%,transparent 44%),
            url("/app/static/assets/{quote(hero_bg.name)}") center 12% / cover no-repeat fixed,
            linear-gradient(160deg,#070408 0%,#150810 45%,#1D0A14 78%,#080509);
    }}
    @media (max-width:700px) {{
        .stApp {{
            background:
                linear-gradient(165deg,
                    rgba(9,4,8,.62) 0%,
                    rgba(15,7,12,.78) 42%,
                    rgba(9,4,8,.92) 72%,
                    rgba(8,5,9,.98) 100%),
                radial-gradient(ellipse at 82% 6%,rgba(118,31,53,.5) 0%,transparent 46%),
                radial-gradient(ellipse at 10% 94%,rgba(214,51,108,.12) 0%,transparent 44%),
                url("/app/static/assets/{quote(hero_bg.name)}") center 18% / cover no-repeat scroll,
                linear-gradient(160deg,#070408 0%,#150810 45%,#1D0A14 78%,#080509);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


# =====================================================
# HOME
# =====================================================

if page == "Home":

    metrics = [
        (str(len(images)), "IMAGES"),
        ("07", "MODULES"),
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

    exp_kali = ASSET_DIR / "maa_kali_hero.png"
    card_bgs = {
        "01": ASSET_DIR / "Dakshineswar Temple Aglow by Night.png",
        "02": ASSET_DIR / "eyes-pandal.B-PIDAK9_KeRT9.png",
        "03": ASSET_DIR / "kalighat_temple_kolkata.jpg",
        "04": ASSET_DIR / "kali_puja_pandal_kalighat_replica_behala.jpg",
        "05": ASSET_DIR / "kali_puja_pandal_kolkata_celebration_11.jpg",
        "06": ASSET_DIR / "kali_puja_pandal_pramanick_bari_kolkata.jpg",
    }
    # Fallbacks if a preferred file is missing
    fallbacks = {
        "01": ASSET_DIR / "dakshineswar_temple_real.jpg",
        "02": ASSET_DIR / "kali_murti_south_kolkata_11.jpg",
        "03": ASSET_DIR / "kalighat_temple.jpg",
        "04": ASSET_DIR / "kali_murti_kolkata_17.jpg",
        "05": ASSET_DIR / "kali_puja_pandal_behala_kolkata.jpg",
        "06": ASSET_DIR / "kali_puja_adi_kali_pandal.jpg",
    }
    for key, path in list(card_bgs.items()):
        if not path.exists() or path.stat().st_size == 0:
            card_bgs[key] = fallbacks[key]

    sync_files = [exp_kali] + list(card_bgs.values())
    sync_static_assets(
        [p for p in sync_files if p.exists() and p.stat().st_size > 0],
        STATIC_IMG_DIR,
    )

    def _static_url(path):
        if path.exists() and path.stat().st_size > 0:
            return "/app/static/assets/" + quote(path.name)
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
          <svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"></rect><circle cx="9" cy="11" r="1.6"></circle><path d="m21 16-4.5-4.5L9 19"></path></svg>
        </span>
        <span class="exp-num">02</span>
      </div>
      <div class="exp-mini-body">
        <h4>Vision Intelligence</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Vision+Lab" target="_self">Explore →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-03">
      <div class="exp-card-bg" style="background-image:url('{bg['03']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11z"></path><circle cx="12" cy="10" r="2.4"></circle></svg>
        </span>
        <span class="exp-num">03</span>
      </div>
      <div class="exp-mini-body">
        <h4>Kolkata Explorer</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Kolkata+Explorer" target="_self">Explore →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-04">
      <div class="exp-card-bg" style="background-image:url('{bg['04']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><rect x="4" y="7" width="14" height="12" rx="1.5"></rect><path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h9A1.5 1.5 0 0 1 20 5.5V15"></path><path d="M4 11h14"></path></svg>
        </span>
        <span class="exp-num">04</span>
      </div>
      <div class="exp-mini-body">
        <h4>Divine Gallery</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Gallery" target="_self">Explore →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-05">
      <div class="exp-card-bg" style="background-image:url('{bg['05']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M4 19h16"></path><path d="M7 16V10"></path><path d="M12 16V6"></path><path d="M17 16v-7"></path></svg>
        </span>
        <span class="exp-num">05</span>
      </div>
      <div class="exp-mini-body">
        <h4>Festival Analytics</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=Analytics" target="_self">Explore →</a>
      </div>
    </div>

    <div class="exp-card exp-mini exp-card-06">
      <div class="exp-card-bg" style="background-image:url('{bg['06']}')"></div>
      <div class="exp-mini-top">
        <span class="exp-mini-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 20c0-4 2-6 2-9a2 2 0 1 0-4 0c0 3 2 5 2 9z"></path><path d="M8.5 10c-2-.5-4 1-4 3 2 0 3.5-1 4-3z"></path><path d="M15.5 10c2-.5 4 1 4 3-2 0-3.5-1-4-3z"></path><path d="M9 7c-1-2 0-4 3-4 3 0 4 2 3 4"></path></svg>
        </span>
        <span class="exp-num">06</span>
      </div>
      <div class="exp-mini-body">
        <h4>Cultural Discovery</h4>
        <a class="exp-pill exp-pill-sm" href="?nav=About" target="_self">Explore →</a>
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

    st.write("A curated collection of Kali Puja murtis, pandals and Bengal's sacred heritage — tap any frame to view it in full.")

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
        sync_static_assets(filtered, STATIC_IMG_DIR)
        cards = []
        for i,p in enumerate(filtered):
            src = "/app/static/assets/" + quote(p.name)
            title = image_title(p)
            cat = image_category(p.name)
            try:
                with Image.open(p) as im:
                    meta = f"{im.width} × {im.height} · {round(p.stat().st_size/1024)} KB"
            except Exception:
                meta = f"{round(p.stat().st_size/1024)} KB"
            cards.append(f"""
            <figure class="gcard" style="animation-delay:{min(i*0.05,0.6)}s">
                <a href="{src}" target="_blank" rel="noopener">
                    <img src="{src}" alt="{title}" loading="lazy">
                </a>
                <figcaption class="gcard-overlay">
                    <div class="gcard-name">{title}</div>
                    <div class="gcard-meta"><span class="gcard-cat">{cat.upper()}</span>{meta}</div>
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

    with st.container(border=True):
        st.markdown('<div class="assistant-stage-mark"></div>', unsafe_allow_html=True)
        for m in st.session_state.chat:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    st.html("""
<div class="assistant-footnote">
  <b>Knowledge base</b> — curated Kali Puja lore for Bengal.
  Full LLM + RAG conversational guidance is on the roadmap.
</div>
""")

    # Sticky bottom chat bar — always visible without scrolling
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
        st.rerun()


# =====================================================
# VISION LAB
# =====================================================

elif page == "Vision Lab":

    st.html("""
<div class="vision-header">
  <div class="vision-kicker">READ THE SACRED IMAGE</div>
  <h2 class="vision-title">Vision Intelligence Lab</h2>
  <div class="vision-lede">
    <span class="vision-lede-bar" aria-hidden="true"></span>
    <p>Upload a devotional frame to study its light, colour and proportion — a classical image-processing baseline, not a trained deep-learning classifier.</p>
  </div>
</div>
""")

    with st.container(border=True):
        st.markdown(
            '<div class="vision-upload-mark"></div><div class="vision-label">OFFER AN IMAGE</div>',
            unsafe_allow_html=True,
        )
        upload = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

    if upload:
        try:
            img = Image.open(upload).convert("RGB")
            info = get_image_stats(upload)

            with st.container(border=True):
                st.markdown('<div class="vision-stage-mark"></div>', unsafe_allow_html=True)
                left, right = st.columns([1, 1.05], gap="large")

                with left:
                    st.markdown('<div class="vision-label">SACRED FRAME</div>', unsafe_allow_html=True)
                    st.markdown('<div class="vision-frame">', unsafe_allow_html=True)
                    st.image(img, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with right:
                    st.markdown('<div class="vision-label">IMAGE INTELLIGENCE</div>', unsafe_allow_html=True)
                    st.markdown('<h3 class="vision-report-title">Visual Report</h3>', unsafe_allow_html=True)

                    metrics = [
                        (f"{info['width']}", "WIDTH PX"),
                        (f"{info['height']}", "HEIGHT PX"),
                        (f"{info['brightness']}", "AVG BRIGHTNESS"),
                        (f"{info['aspect_ratio']}", "ASPECT RATIO"),
                    ]
                    m1, m2 = st.columns(2)
                    m3, m4 = st.columns(2)
                    for col, (val, label) in zip([m1, m2, m3, m4], metrics):
                        with col:
                            st.markdown(f"""
                            <div class="metric-box" style="padding:14px 12px;margin-bottom:10px">
                                <div class="metric-value" style="font-size:26px">{val}</div>
                                <div class="metric-caption">{label}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    color_df = pd.DataFrame({
                        "Channel": ["Red", "Green", "Blue"],
                        "Mean intensity": [info["red"], info["green"], info["blue"]],
                    })
                    fig = px.bar(
                        color_df,
                        x="Channel",
                        y="Mean intensity",
                        title="RGB Channel Analysis",
                        color="Channel",
                        color_discrete_map={
                            "Red": "#D6336C",
                            "Green": "#A58A79",
                            "Blue": "#761F35",
                        },
                    )
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#B9A7A4", family="Inter"),
                        title_font=dict(color="#F8ECDD", family="Cormorant Garamond", size=22),
                        showlegend=False,
                        margin=dict(t=56, b=24, l=12, r=12),
                    )
                    fig.update_traces(marker_line_width=0, opacity=0.92)
                    fig.update_xaxes(color="#E8D8C8", gridcolor="rgba(229,188,112,.12)")
                    fig.update_yaxes(color="#E8D8C8", gridcolor="rgba(229,188,112,.12)")
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("""
                    <div class="vision-note">
                      <b>Baseline complete</b> — dimensions, luminance and RGB means extracted with Pillow.
                      A trained murti &amp; pandal classifier remains on the roadmap.
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Unable to process this image: {e}")
    else:
        st.markdown("""
        <div class="vision-empty">
          <h3>Awaiting a sacred frame</h3>
          <p>Offer a JPG, PNG or WebP of a murti, pandal or temple — the lab will read its light and colour signature.</p>
        </div>
        """, unsafe_allow_html=True)


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
# ANALYTICS
# =====================================================

elif page == "Analytics":

    st.markdown('<div class="section-label">READING THE SACRED DATA</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cultural Data Analytics</div>', unsafe_allow_html=True)
    st.write("The living archive of the collection — its shape, weight and composition.")

    if images:

        rows = []
        for p in images:
            size_kb = round(p.stat().st_size/1024,2)
            w,h = None,None
            try:
                with Image.open(p) as im:
                    w,h = im.size
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
            about_img = ASSET_DIR / "maa_kali_hero.png"
        if about_img.exists() and about_img.stat().st_size > 0:
            st.image(str(about_img),use_container_width=True)
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
        ("CV","Vision","Pillow · PyTorch (roadmap)"),
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
                <li class="done">Dataset analytics & Vision Lab</li>
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
# FOOTER
# =====================================================

st.markdown("""
<div class="footer">
    <div class="footer-diyas"><span>✦</span><span>✦</span><span>✦</span></div>
    ✦ BUILT WITH INTELLIGENCE · INSPIRED BY DIVINITY ✦
    <br><br>
    JAI MAA KALI
    <br><br>
    KALI VISION AI © 2026
</div>
""",unsafe_allow_html=True)
