import os
import glob
import json
import hashlib
import uuid
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Depo Radarı",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSV_DOSYA = "depo_radari_temiz_v6.csv"
CSV_ONCELIKLI_DOSYALAR = [
    "depo_radari_turkiye_tum_ihaleler.csv",
    "depo_radari_tum_ihaleler_guvenli_v3.csv",
    "depo_radari_tum_ihaleler_guvenli_v2.csv",
    "depo_radari_tum_ihaleler_guvenli.csv",
    "depo_radari_temiz_v6.csv",
    "depo_radari_temiz_v5.csv",
]

OZET_DOSYASI = "depo_radari_ozet.json"
KULLANICI_DOSYASI = "depo_radari_kullanicilar.json"

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .hero {
        border-radius: 20px;
        padding: 22px 26px;
        margin-bottom: 18px;
        background: linear-gradient(135deg, rgba(25, 90, 60, .24), rgba(30, 30, 30, .05));
        border: 1px solid rgba(150,150,150,.25);
    }
    .hero-title {
        font-size: 38px;
        font-weight: 900;
        margin-bottom: 4px;
    }
    .hero-sub {
        font-size: 16px;
        opacity: .80;
        margin-bottom: 0px;
    }
    .small-note {
        font-size: 13px;
        opacity: .72;
        margin-top: 8px;
    }
    .result-card {
        border: 1px solid rgba(150,150,150,.22);
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 14px;
        background: rgba(255,255,255,.035);
    }
    .result-title {
        font-size: 18px;
        font-weight: 850;
        margin-bottom: 8px;
    }
    .badge {
        display: inline-block;
        border: 1px solid rgba(150,150,150,.32);
        border-radius: 999px;
        padding: 4px 9px;
        margin-right: 5px;
        margin-bottom: 8px;
        font-size: 12px;
    }
    .score-badge {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 11px;
        margin-right: 6px;
        margin-bottom: 8px;
        font-size: 12px;
        font-weight: 900;
        background: rgba(46, 204, 113, .16);
        border: 1px solid rgba(46, 204, 113, .50);
    }
    .price {
        font-size: 27px;
        font-weight: 900;
        margin-top: 5px;
        margin-bottom: 6px;
    }
    .mini {
        font-size: 13px;
        opacity: .84;
        line-height: 1.6;
    }
    .warn {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        border: 1px solid rgba(255, 193, 7, .55);
        background: rgba(255, 193, 7, .13);
        font-size: 12px;
        font-weight: 800;
        margin-left: 6px;
    }

    .product-board {
        border: 1px solid rgba(150,150,150,.20);
        border-radius: 16px;
        padding: 12px 14px;
        background: rgba(255,255,255,.032);
        min-height: 132px;
        margin-bottom: 10px;
        border-left-width: 7px;
    }
    .product-board-title {
        font-size: 13px;
        opacity: .82;
        margin-bottom: 6px;
        font-weight: 850;
    }
    .product-board-main {
        font-size: 17px;
        font-weight: 900;
        line-height: 1.25;
    }
    .product-board-sub {
        font-size: 12.5px;
        opacity: .82;
        margin-top: 7px;
        line-height: 1.45;
    }
    .urun-tomruk {
        border-left-color: #f1c40f;
        background: linear-gradient(135deg, rgba(241,196,15,.14), rgba(255,255,255,.025));
    }
    .urun-maden {
        border-left-color: #3498db;
        background: linear-gradient(135deg, rgba(52,152,219,.14), rgba(255,255,255,.025));
    }
    .urun-kagitlik {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, rgba(231,76,60,.14), rgba(255,255,255,.025));
    }
    .urun-sanayi {
        border-left-color: #2ecc71;
        background: linear-gradient(135deg, rgba(46,204,113,.14), rgba(255,255,255,.025));
    }
    .urun-dikili {
        border-left-color: #9b59b6;
        background: linear-gradient(135deg, rgba(155,89,182,.14), rgba(255,255,255,.025));
    }
    .urun-genel {
        border-left-color: #95a5a6;
        background: linear-gradient(135deg, rgba(149,165,166,.14), rgba(255,255,255,.025));
    }
    .compact-note {
        font-size: 13px;
        opacity: .74;
        margin-top: -4px;
        margin-bottom: 10px;
    }
    .price-status {
        display: inline-block;
        border-radius: 999px;
        padding: 4px 9px;
        margin-right: 6px;
        margin-bottom: 8px;
        font-size: 12px;
        font-weight: 850;
        border: 1px solid rgba(150,150,150,.32);
        background: rgba(255,255,255,.04);
    }

    .topbox {
        border: 1px solid rgba(150,150,150,.22);
        border-radius: 16px;
        padding: 13px 14px;
        background: rgba(255,255,255,.035);
        min-height: 126px;
    }
    .topbox-title {
        font-size: 13px;
        opacity: .76;
        margin-bottom: 6px;
    }
    .topbox-main {
        font-size: 19px;
        font-weight: 850;
        line-height: 1.25;
    }
    .topbox-sub {
        font-size: 13px;
        opacity: .78;
        margin-top: 8px;
        line-height: 1.45;
    }



    .watch-card {
        border: 1px solid rgba(150,150,150,.22);
        border-radius: 16px;
        padding: 12px 14px;
        background: rgba(255,255,255,.035);
        margin-bottom: 10px;
    }
    .watch-title {
        font-size: 15px;
        font-weight: 900;
        margin-bottom: 5px;
    }
    .watch-sub {
        font-size: 13px;
        opacity: .82;
        line-height: 1.45;
    }



    .new-record-card {
        border: 1px solid rgba(52, 152, 219, .45);
        border-radius: 16px;
        padding: 13px 15px;
        background: rgba(52, 152, 219, .10);
        margin-bottom: 10px;
    }
    .new-record-title {
        font-size: 16px;
        font-weight: 900;
        margin-bottom: 6px;
    }
    .new-record-sub {
        font-size: 13px;
        opacity: .84;
        line-height: 1.45;
    }

    .alarm-center-card {
        border: 1px solid rgba(46, 204, 113, .45);
        border-radius: 16px;
        padding: 13px 15px;
        background: rgba(46, 204, 113, .10);
        margin-bottom: 10px;
    }
    .alarm-center-title {
        font-size: 16px;
        font-weight: 900;
        margin-bottom: 6px;
    }
    .alarm-center-sub {
        font-size: 13px;
        opacity: .84;
        line-height: 1.45;
    }

    .alarm-on {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 10px;
        margin-top: 8px;
        font-size: 12px;
        font-weight: 900;
        border: 1px solid rgba(46, 204, 113, .65);
        background: rgba(46, 204, 113, .18);
    }
    .alarm-off {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 10px;
        margin-top: 8px;
        font-size: 12px;
        font-weight: 900;
        border: 1px solid rgba(255, 193, 7, .55);
        background: rgba(255, 193, 7, .10);
    }

    .watch-hit {
        display: inline-block;
        border-radius: 999px;
        padding: 4px 9px;
        margin-top: 7px;
        font-size: 12px;
        font-weight: 850;
        border: 1px solid rgba(46, 204, 113, .50);
        background: rgba(46, 204, 113, .13);
    }

    .package-card {
        border: 1px solid rgba(150,150,150,.22);
        border-radius: 16px;
        padding: 13px 15px;
        background: rgba(255,255,255,.035);
        margin-bottom: 12px;
    }
    .package-title {
        font-size: 15px;
        font-weight: 900;
        margin-bottom: 5px;
    }
    .package-sub {
        font-size: 13px;
        opacity: .80;
        line-height: 1.45;
    }
    .locked-card {
        border: 1px dashed rgba(255, 193, 7, .55);
        border-radius: 16px;
        padding: 14px 16px;
        background: rgba(255, 193, 7, .08);
        margin-bottom: 12px;
    }
    .locked-title {
        font-size: 16px;
        font-weight: 900;
        margin-bottom: 5px;
    }
    .locked-sub {
        font-size: 13px;
        opacity: .82;
        line-height: 1.5;
    }

    .updatebox {
        border: 1px solid rgba(150,150,150,.22);
        border-radius: 16px;
        padding: 14px 16px;
        background: rgba(255,255,255,.035);
        margin-bottom: 12px;
    }
    .updatebox-title {
        font-size: 14px;
        opacity: .76;
        margin-bottom: 5px;
    }
    .updatebox-main {
        font-size: 18px;
        font-weight: 850;
    }
    .updatebox-sub {
        font-size: 13px;
        opacity: .78;
        margin-top: 6px;
        line-height: 1.45;
    }


    .main {
        background:
            radial-gradient(circle at top left, rgba(46,204,113,.12), transparent 34%),
            radial-gradient(circle at top right, rgba(52,152,219,.10), transparent 32%);
    }
    .hero {
        position: relative;
        overflow: hidden;
        box-shadow: 0 16px 42px rgba(0,0,0,.18);
    }
    .hero:after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -70px;
        top: -80px;
        background: radial-gradient(circle, rgba(46,204,113,.28), transparent 62%);
        border-radius: 999px;
    }
    .hero-title {
        letter-spacing: -0.8px;
    }
    .section-head {
        border: 1px solid rgba(150,150,150,.20);
        border-radius: 18px;
        padding: 15px 17px;
        margin: 10px 0 14px 0;
        background: linear-gradient(135deg, rgba(255,255,255,.055), rgba(255,255,255,.020));
        box-shadow: 0 10px 25px rgba(0,0,0,.08);
    }
    .section-head-title {
        font-size: 22px;
        font-weight: 950;
        margin-bottom: 4px;
    }
    .section-head-sub {
        font-size: 13px;
        opacity: .78;
        line-height: 1.45;
    }
    .metric-shell {
        border: 1px solid rgba(150,150,150,.20);
        border-radius: 18px;
        padding: 14px 15px;
        background: linear-gradient(135deg, rgba(255,255,255,.050), rgba(255,255,255,.018));
        min-height: 92px;
        margin-bottom: 10px;
    }
    .quick-chip {
        display: inline-block;
        border-radius: 999px;
        padding: 6px 11px;
        margin: 3px 5px 6px 0;
        font-size: 12px;
        font-weight: 850;
        border: 1px solid rgba(150,150,150,.28);
        background: rgba(255,255,255,.045);
    }
    .menu-help {
        border: 1px solid rgba(52, 152, 219, .35);
        border-radius: 14px;
        padding: 10px 12px;
        background: rgba(52, 152, 219, .08);
        font-size: 12.5px;
        line-height: 1.45;
        margin-bottom: 12px;
    }
    div[data-testid="stSidebar"] {
        border-right: 1px solid rgba(150,150,150,.16);
    }
    div[data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }
    div[data-testid="stSidebar"] .stRadio label {
        border: 1px solid rgba(255,255,255,.12);
        background: linear-gradient(135deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
        border-radius: 16px;
        padding: 10px 12px;
        transition: all .18s ease;
        box-shadow: 0 6px 16px rgba(0,0,0,.08);
    }
    div[data-testid="stSidebar"] .stRadio label:hover {
        border-color: rgba(52,152,219,.40);
        transform: translateY(-1px);
    }
    div[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        border-color: rgba(52,152,219,.65);
        background: linear-gradient(135deg, rgba(52,152,219,.18), rgba(46,204,113,.10));
        box-shadow: 0 10px 24px rgba(0,0,0,.14);
    }
    div[data-testid="stSidebar"] .stRadio label p {
        font-weight: 800 !important;
        font-size: 14px !important;
    }
    .menu-title-box {
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 18px;
        padding: 12px 14px;
        background: linear-gradient(135deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
        margin-bottom: 10px;
    }
    .menu-title-box .head {
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 4px;
    }
    .menu-title-box .sub {
        font-size: 12.5px;
        opacity: .78;
        line-height: 1.4;
    }
    .menu-group-note {
        font-size: 12px;
        opacity: .72;
        margin: 6px 2px 10px 2px;
    }
    div[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 16px;
        padding: 0.78rem 0.90rem;
        font-weight: 800;
        justify-content: flex-start;
        text-align: left;
        border: 1px solid rgba(255,255,255,.12);
        background: linear-gradient(135deg, rgba(255,255,255,.06), rgba(255,255,255,.025));
        box-shadow: 0 8px 18px rgba(0,0,0,.08);
        transition: all .18s ease;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(52,152,219,.45);
    }
    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        border-color: rgba(52,152,219,.72);
        background: linear-gradient(135deg, rgba(52,152,219,.24), rgba(46,204,113,.16));
        box-shadow: 0 12px 26px rgba(0,0,0,.14);
    }
    .stButton > button {
        border-radius: 999px;
        font-weight: 850;
    }
    .stDownloadButton > button {
        border-radius: 999px;
        font-weight: 850;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    :root{
        --m-bg:#f4f7fb;
        --m-card:#ffffff;
        --m-line:#d8e2ef;
        --m-text:#0f172a;
        --m-muted:#64748b;
        --m-green:#16a34a;
        --m-blue:#2563eb;
        --m-yellow:#facc15;
        --m-red:#ef4444;
        --m-purple:#7c3aed;
        --m-shadow:0 16px 38px rgba(15,23,42,.08);
    }

    html, body, .stApp{
        background:var(--m-bg) !important;
        color:var(--m-text) !important;
    }

    .block-container{
        max-width:1180px;
        padding-top:1rem !important;
    }

    .hero{
        background:var(--m-card) !important;
        color:var(--m-text) !important;
        border:2px solid var(--m-line) !important;
        border-radius:26px !important;
        box-shadow:var(--m-shadow) !important;
        padding:24px 26px !important;
        margin-bottom:22px !important;
        overflow:hidden;
    }

    .hero:after{display:none !important;}

    .hero-title{
        font-size:44px !important;
        font-weight:950 !important;
        letter-spacing:-1.5px !important;
        color:#111827 !important;
        line-height:1.05 !important;
    }

    .hero-sub{
        color:#4b5563 !important;
        font-weight:750 !important;
        font-size:16px !important;
        margin-top:14px !important;
    }

    .small-note{
        color:#64748b !important;
        font-weight:700 !important;
        font-size:15px !important;
    }

    .mesaha-user-pill{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        border:2px solid #bbf7d0;
        background:#ecfdf5;
        color:#047857;
        border-radius:999px;
        padding:10px 16px;
        font-size:20px;
        font-weight:950;
        float:right;
        margin-top:2px;
    }

    .mesaha-mode-row{
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:14px;
        margin-top:18px;
    }

    .mesaha-mode{
        border:2px solid var(--m-line);
        background:#f8fafc;
        border-radius:28px;
        padding:18px 20px;
        text-align:center;
        font-size:22px;
        font-weight:950;
        color:#111827;
    }

    .mesaha-mode.green{
        background:var(--m-green);
        color:white;
        border-color:var(--m-green);
    }

    .section-head,
    .result-card,
    .product-board,
    .topbox,
    .metric-shell,
    div[data-testid="stExpander"]{
        background:var(--m-card) !important;
        border:2px solid var(--m-line) !important;
        border-radius:24px !important;
        box-shadow:var(--m-shadow) !important;
        color:var(--m-text) !important;
    }

    .section-head{padding:20px 22px !important;}

    .section-head-title{
        font-size:30px !important;
        font-weight:950 !important;
        letter-spacing:-.7px !important;
        color:#111827 !important;
    }

    .section-head-sub{
        color:#64748b !important;
        font-size:15px !important;
        font-weight:700 !important;
    }

    .result-card{
        padding:22px !important;
        margin-bottom:18px !important;
    }

    .result-title{
        font-size:23px !important;
        color:#111827 !important;
        font-weight:950 !important;
    }

    .price{
        font-size:34px !important;
        color:#111827 !important;
        font-weight:950 !important;
    }

    .mini{
        color:#475569 !important;
        font-size:15px !important;
        font-weight:650 !important;
    }

    .badge,
    .score-badge,
    .price-status,
    .warn,
    .quick-chip{
        border-radius:999px !important;
        padding:8px 12px !important;
        font-weight:900 !important;
        border:2px solid var(--m-line) !important;
        background:#f8fafc !important;
        color:#111827 !important;
    }

    .score-badge{
        background:#dcfce7 !important;
        border-color:#86efac !important;
        color:#166534 !important;
    }

    .price-status{
        background:#dbeafe !important;
        border-color:#93c5fd !important;
        color:#1e40af !important;
    }

    .warn{
        background:#fef3c7 !important;
        border-color:#facc15 !important;
        color:#92400e !important;
    }

    div[data-testid="stMetric"]{
        background:var(--m-card) !important;
        border:2px solid var(--m-line) !important;
        border-radius:24px !important;
        box-shadow:var(--m-shadow) !important;
        padding:18px 18px !important;
    }

    div[data-testid="stMetricLabel"] p{
        color:#64748b !important;
        font-weight:900 !important;
        text-transform:uppercase;
        letter-spacing:.04em;
    }

    div[data-testid="stMetricValue"]{
        color:#111827 !important;
        font-size:32px !important;
        font-weight:950 !important;
    }

    div[data-testid="stSidebar"]{
        background:#eef3f9 !important;
        border-right:2px solid var(--m-line) !important;
    }

    div[data-testid="stSidebar"] *{color:#111827 !important;}

    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3{
        color:#111827 !important;
        font-weight:950 !important;
    }

    div[data-testid="stSidebar"] .stButton > button{
        width:100%;
        min-height:54px;
        border-radius:22px !important;
        background:#ffffff !important;
        color:#111827 !important;
        border:2px solid var(--m-line) !important;
        box-shadow:none !important;
        font-size:16px !important;
        font-weight:950 !important;
        justify-content:center !important;
        text-align:center !important;
    }

    div[data-testid="stSidebar"] .stButton > button:hover{
        transform:translateY(-1px);
        border-color:#93c5fd !important;
        background:#f8fafc !important;
    }

    div[data-testid="stSidebar"] .stButton > button[kind="primary"]{
        background:var(--m-blue) !important;
        color:#ffffff !important;
        border-color:var(--m-blue) !important;
        box-shadow:0 12px 24px rgba(37,99,235,.20) !important;
    }

    div[data-testid="stSidebar"] .stSuccess{
        background:#dcfce7 !important;
        border:2px solid #86efac !important;
        border-radius:16px !important;
    }

    div[data-testid="stSidebar"] .stInfo{
        background:#eff6ff !important;
        border:2px solid #bfdbfe !important;
        border-radius:16px !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stTextArea"] textarea{
        background:#ffffff !important;
        color:#111827 !important;
        border:2px solid var(--m-line) !important;
        border-radius:18px !important;
        min-height:52px !important;
        font-weight:800 !important;
        box-shadow:none !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus{
        border-color:var(--m-blue) !important;
        box-shadow:0 0 0 4px rgba(37,99,235,.14) !important;
    }

    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"],
    button[kind="secondary"]{
        border-radius:22px !important;
        font-weight:950 !important;
        border:2px solid var(--m-line) !important;
        min-height:52px !important;
    }

    .stButton > button[kind="primary"],
    button[kind="primary"]{
        background:var(--m-blue) !important;
        color:white !important;
        border-color:var(--m-blue) !important;
    }

    div[data-testid="stTabs"] button{
        border-radius:22px !important;
        border:2px solid var(--m-line) !important;
        background:#ffffff !important;
        color:#111827 !important;
        font-weight:950 !important;
        padding:12px 20px !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"]{
        background:var(--m-blue) !important;
        color:white !important;
        border-color:var(--m-blue) !important;
    }

    .product-board{
        border-width:3px !important;
        border-left-width:10px !important;
    }

    .urun-tomruk{
        background:#fef9c3 !important;
        border-color:#facc15 !important;
        color:#713f12 !important;
    }

    .urun-maden{
        background:#dbeafe !important;
        border-color:#2563eb !important;
        color:#1e3a8a !important;
    }

    .urun-kagitlik{
        background:#fee2e2 !important;
        border-color:#ef4444 !important;
        color:#7f1d1d !important;
    }

    .urun-sanayi{
        background:#dcfce7 !important;
        border-color:#16a34a !important;
        color:#14532d !important;
    }

    .urun-dikili{
        background:#ede9fe !important;
        border-color:#7c3aed !important;
        color:#3b0764 !important;
    }

    .product-board-title,
    .product-board-main,
    .product-board-sub{color:inherit !important;}

    .product-board-title{
        font-size:15px !important;
        font-weight:950 !important;
    }

    .product-board-main{
        font-size:22px !important;
        font-weight:950 !important;
    }

    .product-board-sub{
        font-size:14px !important;
        font-weight:750 !important;
    }

    .topbox{padding:18px !important;}

    .topbox-title{
        color:#64748b !important;
        font-weight:900 !important;
    }

    .topbox-main{
        color:#111827 !important;
        font-size:22px !important;
        font-weight:950 !important;
    }

    .topbox-sub{
        color:#475569 !important;
        font-weight:700 !important;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"]{
        border:2px solid var(--m-line) !important;
        border-radius:24px !important;
        overflow:hidden !important;
        box-shadow:var(--m-shadow) !important;
    }

    .stAlert{
        border-radius:18px !important;
        border-width:2px !important;
    }

    @media (max-width: 800px){
        .hero-title{font-size:34px !important;}
        .mesaha-mode-row{grid-template-columns:1fr;}
        .block-container{padding-left:.75rem !important; padding-right:.75rem !important;}
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero">
        <div class="mesaha-user-pill">Depo • Radarı</div>
        <div class="hero-title">🌲 Depo Radarı</div>
        <p class="hero-sub">Türkiye geneli ihale, parti, fiyat ve fırsat takip ekranı.</p>
        <p class="small-note">Mesaha İO tarzı sade, hızlı ve mobil uyumlu arayüz.</p>
    </div>
    """,
    unsafe_allow_html=True
)

LISANS_DOSYASI = "depo_radari_lisanslar.txt"
TAKIP_DOSYASI = "depo_radari_takip_listesi.json"

def guvenli_dosya_eki(text: str) -> str:
    text = str(text or "").strip()

    if not text:
        text = "varsayilan"

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def takip_kullanici_kodu_al() -> str:
    """
    Public yayında herkesin aynı takip listesini görmemesi için takip listesi
    kullanıcı koduna göre ayrılır.

    V27 düzeltmesi:
    Bu sidebar input sadece ana akışta bir kez çizilir.
    Alt fonksiyonlar tekrar text_input oluşturmaya çalışmaz.
    """
    if "takip_oturum_kodu_v27" not in st.session_state:
        st.session_state["takip_oturum_kodu_v27"] = "misafir-" + str(uuid.uuid4())[:8]

    st.sidebar.markdown("### 📌 Takip")

    kod = st.sidebar.text_input(
        "Takip kodu",
        value=st.session_state.get("takip_kullanici_kodu_v27", ""),
        placeholder="Örn: yakup veya firma kodu",
        help="Aynı takipleri tekrar görmek için aynı kodu gir. Boş kalırsa geçici misafir takip listesi kullanılır.",
        key="takip_kullanici_kodu_v27",
    )

    kod = str(kod or "").strip()

    if not kod:
        kod = st.session_state["takip_oturum_kodu_v27"]
        st.sidebar.caption("Geçici misafir takip listesi aktif.")
    else:
        st.sidebar.caption("Bu koda özel takip listesi aktif.")

    st.session_state["aktif_takip_kodu_v27"] = kod
    st.session_state["aktif_takip_dosyasi_v27"] = f"depo_radari_takip_listesi_{guvenli_dosya_eki(kod)}.json"

    return kod


def takip_dosyasi_yolu() -> str:
    """
    Takip dosya yolunu döndürür.
    Burada sidebar text_input oluşturulmaz; böylece Streamlit duplicate widget hatası oluşmaz.
    """
    dosya = st.session_state.get("aktif_takip_dosyasi_v27")

    if dosya:
        return dosya

    if "takip_oturum_kodu_v27" not in st.session_state:
        st.session_state["takip_oturum_kodu_v27"] = "misafir-" + str(uuid.uuid4())[:8]

    kod = st.session_state.get("aktif_takip_kodu_v27", st.session_state["takip_oturum_kodu_v27"])
    dosya = f"depo_radari_takip_listesi_{guvenli_dosya_eki(kod)}.json"

    st.session_state["aktif_takip_kodu_v27"] = kod
    st.session_state["aktif_takip_dosyasi_v27"] = dosya

    return dosya


TEST_PREMIUM_KODU = "DEPO-PREMIUM-2026"


def lisans_dosyasi_hazirla():
    """
    Test amaçlı lisans dosyası.
    Gerçek yayında bu dosya yerine kullanıcı girişi / sunucu kontrolü bağlanır.
    """
    if not os.path.exists(LISANS_DOSYASI):
        with open(LISANS_DOSYASI, "w", encoding="utf-8") as f:
            f.write("# Depo Radarı lisans kodları\n")
            f.write("# Test premium kodu aşağıdadır.\n")
            f.write("# Gerçek yayında bu kontrol sunucu tarafına taşınacak.\n\n")
            f.write(TEST_PREMIUM_KODU + "\n")


def lisans_kodlari_oku():
    lisans_dosyasi_hazirla()

    kodlar = set()

    try:
        with open(LISANS_DOSYASI, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                kodlar.add(line.upper())
    except Exception:
        pass

    kodlar.add(TEST_PREMIUM_KODU.upper())
    return kodlar


def lisans_kodlarini_oku():
    """
    Yayında lisans kodları GitHub'a yazılmamalı.
    Öncelik sırası:
    1) Streamlit Secrets: PREMIUM_CODES
    2) Ortam değişkeni: PREMIUM_CODES
    3) Yerel geliştirme için depo_radari_lisanslar.txt
    """
    kodlar = set()

    try:
        secret_codes = st.secrets.get("PREMIUM_CODES", "")
        if isinstance(secret_codes, str):
            for kod in secret_codes.replace(",", "\n").splitlines():
                kod = kod.strip()
                if kod and not kod.startswith("#"):
                    kodlar.add(kod)
        elif isinstance(secret_codes, list):
            for kod in secret_codes:
                kod = str(kod).strip()
                if kod:
                    kodlar.add(kod)
    except Exception:
        pass

    try:
        import os
        env_codes = os.environ.get("PREMIUM_CODES", "")
        for kod in env_codes.replace(",", "\n").splitlines():
            kod = kod.strip()
            if kod and not kod.startswith("#"):
                kodlar.add(kod)
    except Exception:
        pass

    # Yerel kullanım için fallback. Public GitHub'da gerçek kod koyma.
    try:
        if os.path.exists(LISANS_DOSYASI):
            with open(LISANS_DOSYASI, "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith("#"):
                        kodlar.add(satir)
    except Exception:
        pass

    return kodlar


OTURUM_GIZLI_ANAHTAR = "depo_radari_oturum_2026"


def sifre_hash_uret(metin: str) -> str:
    return hashlib.sha256(str(metin or "").encode("utf-8")).hexdigest()


def oturum_token_uret(kullanici_adi: str, sifre_hash: str) -> str:
    ham = f"{kullanici_adi}|{sifre_hash}|{OTURUM_GIZLI_ANAHTAR}"
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()


def query_param_getir(anahtar: str, varsayilan: str = "") -> str:
    try:
        deger = st.query_params.get(anahtar, varsayilan)
        if isinstance(deger, list):
            return str(deger[0]) if deger else varsayilan
        return str(deger or varsayilan)
    except Exception:
        return varsayilan


def query_param_ayarla(**kwargs):
    try:
        for key, value in kwargs.items():
            if value is None:
                if key in st.query_params:
                    del st.query_params[key]
            else:
                st.query_params[key] = str(value)
    except Exception:
        pass


def varsayilan_kullanici_dosyasi_olustur():
    """
    İlk kurulumda yönetici kullanıcısını oluşturur.
    Varsayılan: admin / admin123
    """
    if os.path.isfile(KULLANICI_DOSYASI):
        return

    varsayilan = {
        "kullanicilar": [
            {
                "kullanici_adi": "admin",
                "sifre_hash": sifre_hash_uret("admin123"),
                "ad": "Yönetici",
                "rol": "admin",
                "aktif": True,
                "kayit_tarihi": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ]
    }

    try:
        with open(KULLANICI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(varsayilan, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def kullanici_dosyasi_kaydet(veri: dict):
    with open(KULLANICI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def kullanici_verisi_yukle() -> dict:
    varsayilan_kullanici_dosyasi_olustur()

    try:
        with open(KULLANICI_DOSYASI, "r", encoding="utf-8") as f:
            veri = json.load(f)
    except Exception:
        veri = {"kullanicilar": []}

    if "kullanicilar" not in veri or not isinstance(veri["kullanicilar"], list):
        veri["kullanicilar"] = []

    # Eski kullanıcı dosyalarını tamamla.
    degisti = False
    for item in veri["kullanicilar"]:
        if "rol" not in item:
            item["rol"] = "admin" if str(item.get("kullanici_adi", "")).lower() == "admin" else "user"
            degisti = True
        if "aktif" not in item:
            item["aktif"] = True
            degisti = True
        if str(item.get("kullanici_adi", "")).lower() != "admin" and item.get("aktif") is False:
            # Artık yönetici onayı gerekmiyor; eski bekleyenleri de aktif yap.
            item["aktif"] = True
            degisti = True

    if degisti:
        try:
            kullanici_dosyasi_kaydet(veri)
        except Exception:
            pass

    return veri


def kullanicilari_yukle() -> dict:
    veri = kullanici_verisi_yukle()
    sonuc = {}

    for item in veri.get("kullanicilar", []):
        kullanici_adi = str(item.get("kullanici_adi", "") or "").strip()

        if not kullanici_adi:
            continue

        sonuc[kullanici_adi.lower()] = item

    return sonuc


def kullanici_dogrula(kullanici_adi: str, sifre: str):
    kayitlar = kullanicilari_yukle()
    kayit = kayitlar.get(str(kullanici_adi or "").strip().lower())

    if not kayit:
        return None, "Kullanıcı bulunamadı."

    if not bool(kayit.get("aktif", True)):
        return None, "Hesap pasif. Yönetici panelinden aktif yapılması gerekiyor."

    if str(kayit.get("sifre_hash", "")) != sifre_hash_uret(sifre):
        return None, "Şifre yanlış."

    return kayit, ""


def kullanici_kayit_ol(kullanici_adi: str, ad: str, sifre: str, sifre_tekrar: str):
    kullanici_adi = str(kullanici_adi or "").strip()
    ad = str(ad or "").strip()

    if len(kullanici_adi) < 3:
        return False, "Kullanıcı adı en az 3 karakter olmalı."

    if len(sifre) < 6:
        return False, "Şifre en az 6 karakter olmalı."

    if sifre != sifre_tekrar:
        return False, "Şifreler eşleşmiyor."

    veri = kullanici_verisi_yukle()
    mevcutlar = {
        str(item.get("kullanici_adi", "") or "").strip().lower()
        for item in veri.get("kullanicilar", [])
    }

    if kullanici_adi.lower() in mevcutlar:
        return False, "Bu kullanıcı adı zaten var."

    # Artık onay bekletmiyoruz; kullanıcı hemen aktif gelir.
    veri["kullanicilar"].append(
        {
            "kullanici_adi": kullanici_adi,
            "sifre_hash": sifre_hash_uret(sifre),
            "ad": ad or kullanici_adi,
            "rol": "user",
            "aktif": True,
            "kayit_tarihi": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    try:
        kullanici_dosyasi_kaydet(veri)
        return True, "Kayıt tamamlandı. Artık giriş yapabilirsin."
    except Exception as e:
        return False, f"Kayıt kaydedilemedi: {e}"


def oturumu_queryden_yukle():
    """
    Sayfa yenilenince çıkış olmasın diye kullanıcı adı ve token URL parametresinden okunur.
    """
    if st.session_state.get("giris_ok"):
        return

    kullanici_adi = query_param_getir("u")
    token = query_param_getir("oturum")

    if not kullanici_adi or not token:
        return

    kayit = kullanicilari_yukle().get(kullanici_adi.lower())

    if not kayit or not bool(kayit.get("aktif", True)):
        return

    dogru_token = oturum_token_uret(kullanici_adi.lower(), kayit.get("sifre_hash", ""))

    if token == dogru_token:
        st.session_state["giris_ok"] = True
        st.session_state["giris_kullanici"] = str(kayit.get("ad") or kayit.get("kullanici_adi") or kullanici_adi)
        st.session_state["giris_kullanici_adi"] = str(kayit.get("kullanici_adi") or kullanici_adi)
        st.session_state["giris_rol"] = str(kayit.get("rol", "user"))


def giris_zorunlu():
    oturumu_queryden_yukle()

    if st.session_state.get("giris_ok"):
        return

    st.markdown(
        """
        <div class="hero">
            <div class="mesaha-user-pill">Giriş</div>
            <div class="hero-title">🔐 Depo Radarı</div>
            <div class="hero-sub">Kullanıcı adı ve şifre ile giriş yap.</div>
            <p class="small-note">İlk kurulum: <b>admin</b> / <b>admin123</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sol, orta, sag = st.columns([1, 1.25, 1])

    with orta:
        sekme_giris, sekme_kayit = st.tabs(["Giriş yap", "Kayıt ol"])

        with sekme_giris:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            with st.form("giris_formu"):
                kullanici_adi = st.text_input("Kullanıcı adı", key="login_user")
                sifre = st.text_input("Şifre", type="password", key="login_pass")
                beni_hatirla = st.checkbox("Beni hatırla", value=True, key="remember_login")
                giris = st.form_submit_button("Giriş yap", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if giris:
                kayit, mesaj = kullanici_dogrula(kullanici_adi, sifre)

                if kayit:
                    temiz_kullanici = str(kayit.get("kullanici_adi") or kullanici_adi).strip().lower()
                    st.session_state["giris_ok"] = True
                    st.session_state["giris_kullanici"] = str(kayit.get("ad") or kayit.get("kullanici_adi") or kullanici_adi)
                    st.session_state["giris_kullanici_adi"] = temiz_kullanici
                    st.session_state["giris_rol"] = str(kayit.get("rol", "user"))

                    if beni_hatirla:
                        query_param_ayarla(
                            u=temiz_kullanici,
                            oturum=oturum_token_uret(temiz_kullanici, kayit.get("sifre_hash", "")),
                        )

                    st.success("Giriş başarılı. Yönlendiriliyorsun...")
                    st.rerun()
                else:
                    st.error(mesaj or "Kullanıcı adı veya şifre yanlış.")

        with sekme_kayit:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            with st.form("kayit_formu"):
                yeni_ad = st.text_input("Ad / firma adı", key="register_name")
                yeni_kullanici = st.text_input("Kullanıcı adı", key="register_user")
                yeni_sifre = st.text_input("Şifre", type="password", key="register_pass")
                yeni_sifre_tekrar = st.text_input("Şifre tekrar", type="password", key="register_pass2")
                kayit_buton = st.form_submit_button("Kayıt ol", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if kayit_buton:
                ok, mesaj = kullanici_kayit_ol(yeni_kullanici, yeni_ad, yeni_sifre, yeni_sifre_tekrar)
                if ok:
                    st.success(mesaj)
                else:
                    st.error(mesaj)

    st.stop()


def kullanici_oturum_karti():
    ad = st.session_state.get("giris_kullanici", "Kullanıcı")
    rol = st.session_state.get("giris_rol", "user")

    st.sidebar.markdown("### 👤 Oturum")
    st.sidebar.success(f"{ad}")

    if rol == "admin":
        st.sidebar.caption("Yetki: Yönetici")

    if st.sidebar.button("Çıkış yap", key="logout", use_container_width=True):
        for key in ["giris_ok", "giris_kullanici", "giris_kullanici_adi", "giris_rol"]:
            st.session_state.pop(key, None)
        query_param_ayarla(u=None, oturum=None)
        st.rerun()


def kullanicilar_paneli():
    if st.session_state.get("giris_rol") != "admin":
        st.warning("Bu alan sadece yönetici için açık.")
        return

    bolum_basligi("👥 Kullanıcılar", "Kayıt olan kullanıcıları gör, aktif/pasif yap, rol değiştir veya şifre güncelle.")

    veri = kullanici_verisi_yukle()
    kullanicilar = veri.get("kullanicilar", [])

    if not kullanicilar:
        st.info("Kullanıcı bulunamadı.")
        return

    tablo_veri = []
    for item in kullanicilar:
        tablo_veri.append(
            {
                "Kullanıcı adı": item.get("kullanici_adi", ""),
                "Ad": item.get("ad", ""),
                "Rol": item.get("rol", "user"),
                "Aktif": "Evet" if item.get("aktif", False) else "Hayır",
                "Kayıt": item.get("kayit_tarihi", ""),
            }
        )

    st.dataframe(pd.DataFrame(tablo_veri), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Kullanıcı işlemleri")

    for i, item in enumerate(list(kullanicilar)):
        kullanici_adi = str(item.get("kullanici_adi", "") or "")
        rol = str(item.get("rol", "user") or "user")
        aktif = bool(item.get("aktif", False))

        with st.expander(f"{kullanici_adi} — {'Aktif' if aktif else 'Pasif'}", expanded=False):
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                if st.button("Aktif yap", key=f"user_active_{i}"):
                    veri["kullanicilar"][i]["aktif"] = True
                    kullanici_dosyasi_kaydet(veri)
                    st.success("Kullanıcı aktif edildi.")
                    st.rerun()

            with c2:
                if st.button("Pasif yap", key=f"user_passive_{i}"):
                    if kullanici_adi.lower() == "admin":
                        st.warning("Ana yönetici pasifleştirilemez.")
                    else:
                        veri["kullanicilar"][i]["aktif"] = False
                        kullanici_dosyasi_kaydet(veri)
                        st.success("Kullanıcı pasif edildi.")
                        st.rerun()

            with c3:
                yeni_rol = "user" if rol == "admin" else "admin"
                if st.button(f"Rol: {yeni_rol}", key=f"user_role_{i}"):
                    if kullanici_adi.lower() == "admin":
                        st.warning("Ana yönetici rolü değiştirilemez.")
                    else:
                        veri["kullanicilar"][i]["rol"] = yeni_rol
                        kullanici_dosyasi_kaydet(veri)
                        st.success("Rol değiştirildi.")
                        st.rerun()

            with c4:
                if st.button("Sil", key=f"user_delete_{i}"):
                    if kullanici_adi.lower() == "admin":
                        st.warning("Ana yönetici silinemez.")
                    else:
                        veri["kullanicilar"].pop(i)
                        kullanici_dosyasi_kaydet(veri)
                        st.success("Kullanıcı silindi.")
                        st.rerun()

            with st.form(f"sifre_sifirla_form_{i}"):
                yeni_sifre = st.text_input("Yeni şifre", type="password", key=f"reset_pass_{i}")
                kaydet = st.form_submit_button("Şifreyi güncelle")
                if kaydet:
                    if len(yeni_sifre) < 6:
                        st.error("Şifre en az 6 karakter olmalı.")
                    else:
                        veri["kullanicilar"][i]["sifre_hash"] = sifre_hash_uret(yeni_sifre)
                        kullanici_dosyasi_kaydet(veri)
                        st.success("Şifre güncellendi.")
                        st.rerun()

    st.divider()
    st.subheader("Yeni kullanıcı ekle")

    with st.form("admin_user_add"):
        ad = st.text_input("Ad / firma adı")
        kullanici_adi = st.text_input("Kullanıcı adı")
        sifre = st.text_input("Şifre", type="password")
        rol = st.selectbox("Rol", ["user", "admin"])
        aktif = st.checkbox("Aktif", value=True)
        ekle = st.form_submit_button("Kullanıcı ekle", use_container_width=True)

    if ekle:
        ok, mesaj = kullanici_kayit_ol(kullanici_adi, ad, sifre, sifre)
        if ok:
            veri = kullanici_verisi_yukle()
            for item in veri["kullanicilar"]:
                if str(item.get("kullanici_adi", "")).lower() == kullanici_adi.lower():
                    item["rol"] = rol
                    item["aktif"] = aktif
            kullanici_dosyasi_kaydet(veri)
            st.success("Kullanıcı eklendi.")
            st.rerun()
        else:
            st.error(mesaj)


def lisans_kontrolu():
    # V39: premium kilidi açık ama sidebar'da lisans/paket kartı gösterilmez.
    return "Premium"


def premium_aktif(paket):
    return True


def paket_bilgi_goster(paket):
    # V39: paket/premium bilgisi ekranda gösterilmez.
    return


def kilitli_ozellik(baslik, aciklama):
    st.markdown(
        f"""
        <div class="locked-card">
            <div class="locked-title">🔒 {baslik}</div>
            <div class="locked-sub">{aciklama}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def premium_ozellikler_panosu():
    with st.expander("🔒 Premium özellikler", expanded=False):
        kilitli_ozellik(
            "CSV yükleme",
            "Kendi CSV dosyanı yükleyip analiz etme premium lisansa ayrıldı."
        )
        kilitli_ozellik(
            "Analiz görünümü",
            "Grafikler, fiyat dağılımları ve ürün bazlı özetler premium lisansa ayrıldı."
        )
        kilitli_ozellik(
            "Rapor indirme",
            "CSV/Excel raporu indirme premium lisansa ayrıldı."
        )



def takip_listesi_oku():
    dosya = takip_dosyasi_yolu()

    try:
        if os.path.exists(dosya):
            with open(dosya, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    return data
    except Exception:
        pass

    # Eski tek dosyalı sistemden gelen takipleri kaybetmemek için
    # sadece varsayılan/yerel durumda eski dosyadan okumaya çalışır.
    try:
        if os.path.exists(TAKIP_DOSYASI):
            with open(TAKIP_DOSYASI, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    return data
    except Exception:
        pass

    return []


def takip_listesi_yaz(liste):
    dosya = takip_dosyasi_yolu()

    try:
        with open(dosya, "w", encoding="utf-8") as f:
            json.dump(liste, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Takip listesi kaydedilemedi: {e}")


def aktif_filtreleri_al():
    filtreler = {
        "arama": st.session_state.get("arama_v7", ""),
        "bolge": st.session_state.get("bolge_v7", "Tümü"),
        "il": st.session_state.get("il_v34", "Tümü"),
        "obm": st.session_state.get("obm_v7", "Tümü"),
        "oim": st.session_state.get("oim_v7", "Tümü"),
        "urun": st.session_state.get("urun_v7", "Tümü"),
        "agac": st.session_state.get("agac_v7", "Tümü"),
        "sinif": st.session_state.get("sinif_v7", "Tümü"),
        "boy": st.session_state.get("boy_v7", "Tümü"),
        "cap": st.session_state.get("cap_v7", "Tümü"),
    }

    return filtreler


def filtre_ozet_metni(filtreler):
    parcala = []

    etiketler = {
        "arama": "Arama",
        "bolge": "Bölge",
        "il": "İl",
        "obm": "OBM",
        "oim": "OİM",
        "urun": "Ürün",
        "agac": "Ağaç",
        "sinif": "Sınıf",
        "boy": "Boy",
        "cap": "Çap",
    }

    for key, label in etiketler.items():
        val = filtreler.get(key, "")

        if gecerli_metin(val) and val != "Tümü":
            parcala.append(f"{label}: {val}")

    if not parcala:
        return "Genel takip"

    return " | ".join(parcala)


def filtreleri_uygula(df: pd.DataFrame, filtreler: dict) -> pd.DataFrame:
    sonuc = df.copy()

    arama = str(filtreler.get("arama", "")).strip()
    sonuc = genel_arama_uygula(sonuc, arama)

    kolon_haritasi = {
        "bolge": "cografi_bolge",
        "il": "il",
        "obm": "obm",
        "oim": "oim",
        "urun": "urun_turu",
        "agac": "agac_turu",
        "sinif": "sinif",
        "boy": "boy_kodu",
        "cap": "cap_kodu",
    }

    for key, kolon in kolon_haritasi.items():
        val = filtreler.get(key, "Tümü")

        if val != "Tümü" and kolon in sonuc.columns:
            sonuc = sonuc[sonuc[kolon] == val]

    return sonuc


def takip_hedefini_uygula():
    """
    Streamlit'te bir filtre kutusu oluşturulduktan sonra aynı çalıştırmada o kutunun
    session_state değeri değiştirilemez. Bu yüzden takip kartına basınca önce hedef filtre
    saklanır, sayfa yenilenir, filtre kutuları çizilmeden önce burada uygulanır.
    """
    hedef = st.session_state.pop("takip_hedef_filtre_v22", None)

    if not hedef:
        return

    key_map = {
        "arama": "arama_v7",
        "bolge": "bolge_v7",
        "obm": "obm_v7",
        "oim": "oim_v7",
        "urun": "urun_v7",
        "agac": "agac_v7",
        "sinif": "sinif_v7",
        "boy": "boy_v7",
        "cap": "cap_v7",
    }

    for takip_key, widget_key in key_map.items():
        st.session_state[widget_key] = hedef.get(takip_key, "Tümü")

    st.session_state["takip_uygulandi_v22"] = True


def takip_filtrelerine_git(filtreler: dict):
    """
    Kaydedilmiş takip filtresine gitmek için hedef filtreyi saklar ve sayfayı yeniler.
    Asıl uygulama, filtre kutuları çizilmeden önce takip_hedefini_uygula() içinde yapılır.
    """
    st.session_state["takip_hedef_filtre_v22"] = filtreler
    st.rerun()


def takip_sil(index: int):
    liste = takip_listesi_oku()

    if 0 <= index < len(liste):
        liste.pop(index)
        takip_listesi_yaz(liste)
        st.success("Takip silindi.")
        st.rerun()


def alarm_sarti_var(sartlar: dict) -> bool:
    if not sartlar:
        return False

    for key in ["max_fiyat", "min_puan", "min_miktar"]:
        val = sartlar.get(key)

        if val not in [None, "", 0, "0"]:
            try:
                if float(val) > 0:
                    return True
            except Exception:
                pass

    return False


def alarm_sartlari_uygula(df: pd.DataFrame, sartlar: dict) -> pd.DataFrame:
    # Şart girilmediyse alarm üretme.
    # Sadece takip kaydı olsun; alarm merkezi boş kalsın.
    if not alarm_sarti_var(sartlar):
        return df.iloc[0:0].copy()

    sonuc = df.copy()

    max_fiyat = sartlar.get("max_fiyat")
    min_puan = sartlar.get("min_puan")
    min_miktar = sartlar.get("min_miktar")

    if max_fiyat not in [None, "", 0, "0"] and "muhammen_birim_fiyat" in sonuc.columns:
        try:
            sonuc = sonuc[sonuc["muhammen_birim_fiyat"] <= float(max_fiyat)]
        except Exception:
            pass

    if min_puan not in [None, "", 0, "0"] and "firsat_puani" in sonuc.columns:
        try:
            sonuc = sonuc[sonuc["firsat_puani"] >= float(min_puan)]
        except Exception:
            pass

    if min_miktar not in [None, "", 0, "0"] and "miktar_m3_hesap" in sonuc.columns:
        try:
            sonuc = sonuc[sonuc["miktar_m3_hesap"] >= float(min_miktar)]
        except Exception:
            pass

    return sonuc


def alarm_ozet_metni(sartlar: dict) -> str:
    parcala = []

    max_fiyat = sartlar.get("max_fiyat")
    min_puan = sartlar.get("min_puan")
    min_miktar = sartlar.get("min_miktar")

    if max_fiyat not in [None, "", 0, "0"]:
        parcala.append(f"En fazla fiyat: {tl(float(max_fiyat))}")

    if min_puan not in [None, "", 0, "0"]:
        parcala.append(f"Min. fırsat: {int(float(min_puan))}/100")

    if min_miktar not in [None, "", 0, "0"]:
        parcala.append(f"Min. miktar: {m3(float(min_miktar))}")

    if not parcala:
        return "Alarm şartı yok"

    return " | ".join(parcala)



def yeni_kayitlar_panosu(df: pd.DataFrame):
    with st.expander("🆕 Son güncellemede gelen yeni kayıtlar", expanded=False):
        if "guncelleme_id" not in df.columns:
            st.info("Yeni kayıt takibi için veri güncelleme v4 ile CSV oluşturulmalı.")
            st.caption("Eski CSV dosyalarında guncelleme_id kolonu olmadığı için yeni kayıtlar listelenemez.")
            return

        temp = df.copy()
        temp["guncelleme_id"] = temp["guncelleme_id"].apply(lambda x: temiz_metin(x))

        temp = temp[temp["guncelleme_id"].apply(gecerli_metin)]

        if temp.empty:
            st.info("Bu filtrelerde güncelleme ID bilgisi olan yeni kayıt yok.")
            return

        son_id = sorted(temp["guncelleme_id"].unique().tolist())[-1]
        yeni = temp[temp["guncelleme_id"] == son_id].copy()

        if yeni.empty:
            st.info("Son güncellemede gelen kayıt bulunamadı.")
            return

        en_ucuz = yeni["muhammen_birim_fiyat"].min() if "muhammen_birim_fiyat" in yeni.columns else None
        en_puan = yeni["firsat_puani"].max() if "firsat_puani" in yeni.columns else None
        toplam_miktar = yeni["miktar_m3_hesap"].sum() if "miktar_m3_hesap" in yeni.columns else None

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
                <div class="new-record-card">
                    <div class="new-record-title">{len(yeni)} yeni kayıt</div>
                    <div class="new-record-sub">Güncelleme ID: {son_id}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
                <div class="new-record-card">
                    <div class="new-record-title">{tl(en_ucuz)}</div>
                    <div class="new-record-sub">Yeni kayıtlar içinde en ucuz</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                f"""
                <div class="new-record-card">
                    <div class="new-record-title">{sayi(en_puan)}/100</div>
                    <div class="new-record-sub">Yeni kayıtlar içinde en yüksek fırsat</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c4:
            st.markdown(
                f"""
                <div class="new-record-card">
                    <div class="new-record-title">{m3(toplam_miktar)}</div>
                    <div class="new-record-sub">Yeni kayıtlar toplam miktar</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        kolonlar = [
            "kayit_tarihi",
            "guncelleme_id",
            "parti_no",
            "puan_kategorisi",
            "kalite_puani",
            "kalite_ozeti",
            "urun_adi",
            "urun_turu",
            "agac_turu",
            "miktar_m3_hesap",
            "muhammen_birim_fiyat",
            "firsat_puani",
            "fiyat_durumu",
            "il",
            "obm",
            "oim",
            "kaynak_link",
        ]

        kolonlar = [c for c in kolonlar if c in yeni.columns]

        siralama_kolonlari = []
        siralama_yonleri = []

        if "firsat_puani" in yeni.columns:
            siralama_kolonlari.append("firsat_puani")
            siralama_yonleri.append(False)

        if "muhammen_birim_fiyat" in yeni.columns:
            siralama_kolonlari.append("muhammen_birim_fiyat")
            siralama_yonleri.append(True)

        if siralama_kolonlari:
            yeni = yeni.sort_values(siralama_kolonlari, ascending=siralama_yonleri)

        st.dataframe(
            yeni[kolonlar],
            use_container_width=True,
            hide_index=True,
            column_config={
                "kaynak_link": st.column_config.LinkColumn("Kaynakta Aç"),
                "miktar_m3_hesap": st.column_config.NumberColumn("Miktar m³", format="%.3f"),
                "muhammen_birim_fiyat": st.column_config.NumberColumn("Birim Fiyat TL", format="%.0f"),
                "firsat_puani": st.column_config.ProgressColumn("Fırsat Puanı", min_value=0, max_value=100, format="%d"),
            },
        )

def alarm_merkezi_panosu(df: pd.DataFrame):
    liste = takip_listesi_oku()

    if not liste:
        return

    alarm_parcalari = []
    alarm_ozetleri = []

    for i, item in enumerate(liste, start=1):
        ad = item.get("ad", f"Takip {i}")
        filtreler = item.get("filtreler", {})
        sartlar = item.get("sartlar", {})

        if not alarm_sarti_var(sartlar):
            continue

        alt = filtreleri_uygula(df, filtreler)
        alarm_alt = alarm_sartlari_uygula(alt, sartlar)

        if alarm_alt.empty:
            continue

        alarm_alt = alarm_alt.copy()
        alarm_alt.insert(0, "takip_adi", ad)
        alarm_alt.insert(1, "alarm_sarti", alarm_ozet_metni(sartlar))

        alarm_parcalari.append(alarm_alt)

        en_ucuz = tl(alarm_alt["muhammen_birim_fiyat"].min()) if "muhammen_birim_fiyat" in alarm_alt.columns else "-"
        en_puan = sayi(alarm_alt["firsat_puani"].max()) if "firsat_puani" in alarm_alt.columns else "-"

        alarm_ozetleri.append({
            "ad": ad,
            "adet": len(alarm_alt),
            "en_ucuz": en_ucuz,
            "en_puan": en_puan,
            "sart": alarm_ozet_metni(sartlar),
        })

    with st.expander("🚨 Alarm merkezi", expanded=bool(alarm_parcalari)):
        if not alarm_parcalari:
            st.info("Şu anda alarm şartına uyan kayıt yok.")
            st.caption("Takip listesine fiyat, fırsat puanı veya miktar şartı ekleyince burada otomatik görünecek.")
            return

        tum_alarm = pd.concat(alarm_parcalari, ignore_index=True)

        st.success(f"{len(tum_alarm)} alarm eşleşmesi bulundu.")

        kolonlar = st.columns(min(3, len(alarm_ozetleri)))
        if not kolonlar:
            kolonlar = st.columns(1)

        for idx, ozet_item in enumerate(alarm_ozetleri):
            with kolonlar[idx % len(kolonlar)]:
                st.markdown(
                    f"""
                    <div class="alarm-center-card">
                        <div class="alarm-center-title">{ozet_item["ad"]}</div>
                        <div class="alarm-center-sub">
                            {ozet_item["adet"]} uygun kayıt<br>
                            En ucuz: {ozet_item["en_ucuz"]}<br>
                            En yüksek fırsat: {ozet_item["en_puan"]}/100<br>
                            Şart: {ozet_item["sart"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.subheader("Tüm alarm sonuçları")

        siralama_kolonlari = []
        siralama_yonleri = []

        if "firsat_puani" in tum_alarm.columns:
            siralama_kolonlari.append("firsat_puani")
            siralama_yonleri.append(False)

        if "muhammen_birim_fiyat" in tum_alarm.columns:
            siralama_kolonlari.append("muhammen_birim_fiyat")
            siralama_yonleri.append(True)

        if siralama_kolonlari:
            tum_alarm = tum_alarm.sort_values(siralama_kolonlari, ascending=siralama_yonleri)

        kolonlar = [
            "takip_adi",
            "alarm_sarti",
            "parti_no",
            "puan_kategorisi",
            "kalite_puani",
            "kalite_ozeti",
            "urun_adi",
            "urun_turu",
            "agac_turu",
            "miktar_m3_hesap",
            "muhammen_birim_fiyat",
            "firsat_puani",
            "fiyat_durumu",
            "il",
            "obm",
            "oim",
            "kaynak_link",
        ]

        kolonlar = [c for c in kolonlar if c in tum_alarm.columns]

        st.dataframe(
            tum_alarm[kolonlar],
            use_container_width=True,
            hide_index=True,
            column_config={
                "kaynak_link": st.column_config.LinkColumn("Kaynakta Aç"),
                "miktar_m3_hesap": st.column_config.NumberColumn("Miktar m³", format="%.3f"),
                "muhammen_birim_fiyat": st.column_config.NumberColumn("Birim Fiyat TL", format="%.0f"),
                "firsat_puani": st.column_config.ProgressColumn("Fırsat Puanı", min_value=0, max_value=100, format="%d"),
            },
        )

def takip_listesi_panosu(df: pd.DataFrame):
    with st.expander("📌 Takip listesi ve alarm şartları", expanded=False):
        st.caption("Mevcut filtreyi kaydedebilir, alarm şartı ekleyebilir ve aynı takip koduyla kendi listen üzerinden geri dönebilirsin.")

        if st.session_state.get("takip_uygulandi_v22", False):
            st.success("Takip filtresi uygulandı.")
            st.session_state["takip_uygulandi_v22"] = False

        mevcut_filtreler = aktif_filtreleri_al()
        mevcut_ozet = filtre_ozet_metni(mevcut_filtreler)
        aktif_takip_dosyasi = takip_dosyasi_yolu()

        st.info("Takip listesi artık kullanıcı takip koduna göre ayrılır. Aynı listeyi tekrar görmek için sol menüde aynı takip kodunu gir.")

        st.markdown(
            f"""
            <div class="watch-card">
                <div class="watch-title">Mevcut filtre</div>
                <div class="watch-sub">{mevcut_ozet}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        takip_adi = st.text_input("Takip adı", value=mevcut_ozet[:80], key="takip_adi_v18")

        st.caption("Alarm şartları boş kalırsa sadece filtre takibi yapılır.")
        a1, a2, a3 = st.columns(3)

        with a1:
            max_fiyat = st.number_input(
                "Alarm: en fazla fiyat TL/m³",
                min_value=0,
                value=0,
                step=100,
                key="alarm_max_fiyat_v18"
            )

        with a2:
            min_puan = st.number_input(
                "Alarm: minimum fırsat puanı",
                min_value=0,
                max_value=100,
                value=0,
                step=1,
                key="alarm_min_puan_v18"
            )

        with a3:
            min_miktar = st.number_input(
                "Alarm: minimum miktar m³",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key="alarm_min_miktar_v18"
            )

        sartlar = {
            "max_fiyat": max_fiyat,
            "min_puan": min_puan,
            "min_miktar": min_miktar,
        }

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Bu filtreyi takip listesine ekle", key="takip_ekle_v18"):
                liste = takip_listesi_oku()

                yeni = {
                    "ad": takip_adi.strip() or mevcut_ozet,
                    "filtreler": mevcut_filtreler,
                    "sartlar": sartlar,
                }

                liste.append(yeni)
                takip_listesi_yaz(liste)
                st.success("Takip listesine eklendi.")
                st.rerun()

        with c2:
            if st.button("Takip listesini temizle", key="takip_temizle_v18"):
                takip_listesi_yaz([])
                st.success("Takip listesi temizlendi.")
                st.rerun()

        liste = takip_listesi_oku()

        if not liste:
            st.info("Takip listesi boş.")
            return

        st.subheader("Kayıtlı takipler")

        for i, item in enumerate(liste, start=1):
            ad = item.get("ad", f"Takip {i}")
            filtreler = item.get("filtreler", {})
            sartlar = item.get("sartlar", {})
            alt = filtreleri_uygula(df, filtreler)
            alarm_alt = alarm_sartlari_uygula(alt, sartlar)

            if alt.empty:
                hit = "Eşleşen kayıt yok"
                en_ucuz = "-"
                en_puan = "-"
            else:
                hit = f"{len(alt)} kayıt"
                en_ucuz = tl(alt["muhammen_birim_fiyat"].min()) if "muhammen_birim_fiyat" in alt.columns else "-"
                en_puan = sayi(alt["firsat_puani"].max()) if "firsat_puani" in alt.columns else "-"

            if alarm_alt.empty:
                alarm_badge = '<span class="alarm-off">Alarm yok</span>'
                alarm_detay = "Alarm şartına uyan kayıt yok."
            else:
                alarm_badge = f'<span class="alarm-on">Alarm: {len(alarm_alt)} uygun kayıt</span>'
                alarm_en_ucuz = tl(alarm_alt["muhammen_birim_fiyat"].min()) if "muhammen_birim_fiyat" in alarm_alt.columns else "-"
                alarm_en_puan = sayi(alarm_alt["firsat_puani"].max()) if "firsat_puani" in alarm_alt.columns else "-"
                alarm_detay = f"Alarm en ucuz: {alarm_en_ucuz} | Alarm en yüksek fırsat: {alarm_en_puan}/100"

            st.markdown(
                f"""
                <div class="watch-card">
                    <div class="watch-title">{i}. {ad}</div>
                    <div class="watch-sub">
                        {filtre_ozet_metni(filtreler)}<br>
                        Şart: {alarm_ozet_metni(sartlar)}<br>
                        Genel: {hit} | En ucuz: {en_ucuz} | En yüksek fırsat: {en_puan}/100<br>
                        {alarm_detay}
                    </div>
                    {alarm_badge}
                </div>
                """,
                unsafe_allow_html=True,
            )

            b1, b2, b3 = st.columns([1, 1, 1])
            with b1:
                if st.button("Bu takibe git", key=f"takibe_git_v18_{i}"):
                    takip_filtrelerine_git(filtreler)

            with b2:
                if st.button("Alarm sonuçlarını göster", key=f"alarm_goster_v18_{i}"):
                    st.session_state[f"alarm_detay_v18_{i}"] = not st.session_state.get(f"alarm_detay_v18_{i}", False)

            with b3:
                if st.button("Bu takibi sil", key=f"takip_sil_v18_{i}"):
                    takip_sil(i - 1)

            if st.session_state.get(f"alarm_detay_v18_{i}", False):
                if alarm_alt.empty:
                    st.info("Bu alarm şartına uygun kayıt yok.")
                else:
                    gosterilecek = alarm_alt.sort_values(["firsat_puani", "muhammen_birim_fiyat"], ascending=[False, True])
                    kolonlar = [
                        "parti_no",
                        "puan_kategorisi",
                        "urun_adi",
                        "urun_turu",
                        "agac_turu",
                        "miktar_m3_hesap",
                        "muhammen_birim_fiyat",
                        "firsat_puani",
                        "fiyat_durumu",
                        "obm",
                        "oim",
                        "kaynak_link",
                    ]
                    kolonlar = [c for c in kolonlar if c in gosterilecek.columns]
                    st.dataframe(gosterilecek[kolonlar], use_container_width=True, hide_index=True)


def ozet_json_oku():
    if not os.path.exists(OZET_DOSYASI):
        return {}

    try:
        with open(OZET_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guncelleme_ozeti_goster():
    ozet = ozet_json_oku()

    if not ozet:
        st.info("Henüz güncelleme özeti yok. Panelden veri güncelleme çalıştırınca burada özet görünecek.")
        return

    durum = ozet.get("durum", "-")
    son = ozet.get("son_guncelleme", "-")
    yeni = ozet.get("yeni_kayit", 0)
    csv_once = ozet.get("csv_once", 0)
    csv_sonra = ozet.get("csv_sonra", 0)
    denenen = ozet.get("denenen_ihale", 0)
    veri_cikan = ozet.get("veri_cikan_ihale", 0)
    hata = ozet.get("hata_sayisi", 0)
    sure = ozet.get("sure_saniye", 0)
    output = ozet.get("output_csv", "-")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="updatebox">
                <div class="updatebox-title">Son güncelleme</div>
                <div class="updatebox-main">{son}</div>
                <div class="updatebox-sub">Durum: {durum}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="updatebox">
                <div class="updatebox-title">Yeni kayıt</div>
                <div class="updatebox-main">{yeni}</div>
                <div class="updatebox-sub">CSV: {csv_once} → {csv_sonra}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="updatebox">
                <div class="updatebox-title">İhale durumu</div>
                <div class="updatebox-main">{veri_cikan}/{denenen}</div>
                <div class="updatebox-sub">Veri çıkan / denenen ihale</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="updatebox">
                <div class="updatebox-title">Sistem</div>
                <div class="updatebox-main">{hata} hata</div>
                <div class="updatebox-sub">Süre: {sure} sn<br>Çıktı: {output}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )



def en_guncel_csv_bul():
    for dosya in CSV_ONCELIKLI_DOSYALAR:
        if os.path.exists(dosya):
            return dosya

    desenler = [
        "depo_radari_tum_ihaleler*.csv",
        "depo_radari_temiz*.csv",
        "depo_radari*.csv",
    ]

    adaylar = []
    for desen in desenler:
        adaylar.extend(glob.glob(desen))

    adaylar = [a for a in adaylar if os.path.isfile(a)]

    if not adaylar:
        return CSV_DOSYA

    adaylar.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return adaylar[0]


def sunucudaki_csvleri_listele():
    desenler = [
        "depo_radari_turkiye_tum_ihaleler.csv",
        "depo_radari_tum_ihaleler*.csv",
        "depo_radari_temiz*.csv",
        "depo_radari*.csv",
    ]

    dosyalar = []

    for desen in desenler:
        for dosya in glob.glob(desen):
            if os.path.isfile(dosya) and dosya not in dosyalar:
                dosyalar.append(dosya)

    dosyalar.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return dosyalar


def csv_cache_anahtari(path: str):
    try:
        return os.path.getmtime(path), os.path.getsize(path)
    except Exception:
        return 0, 0


@st.cache_data(show_spinner=False)
def csv_oku(path: str, cache_key=None) -> pd.DataFrame:
    # cache_key dosya tarihi/boyutu değişince Streamlit cache'i yenilesin diye var.
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def upload_oku(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file)


def gecerli_metin(value) -> bool:
    if value is None or pd.isna(value):
        return False
    s = str(value).strip()
    if not s:
        return False
    if s.lower() in ["none", "nan", "null", "<na>", "-"]:
        return False
    return True


def temiz_metin(value) -> str:
    return str(value).strip() if gecerli_metin(value) else ""



# V34: CSV'de OBM / bölge boş geldiğinde OİM adından yer bilgisini tamamlamak için kullanılır.
# Bu tablo filtreleme amaçlıdır; kaynakta OBM gelirse kaynak değeri korunur.
OIM_HARITA_JSON_DOSYASI = "depo_radari_oim_konum_haritasi.json"

OIM_KONUM_HARITASI = {
    "AKHİSAR OİM": {"il": "Manisa", "obm": "İZMİR OBM", "bolge": "Ege"},
    "GÖRDES OİM": {"il": "Manisa", "obm": "İZMİR OBM", "bolge": "Ege"},
    "AYDIN OİM": {"il": "Aydın", "obm": "İZMİR OBM", "bolge": "Ege"},
    "ÇAL OİM": {"il": "Denizli", "obm": "DENİZLİ OBM", "bolge": "Ege"},
    "KÖYCEĞİZ OİM": {"il": "Muğla", "obm": "MUĞLA OBM", "bolge": "Ege"},
    "MUĞLA OİM": {"il": "Muğla", "obm": "MUĞLA OBM", "bolge": "Ege"},
    "SEYDİKEMER OİM": {"il": "Muğla", "obm": "MUĞLA OBM", "bolge": "Ege"},
    "YILANLI OİM": {"il": "Muğla", "obm": "MUĞLA OBM", "bolge": "Ege"},
    "TAVŞANLI OİM": {"il": "Kütahya", "obm": "KÜTAHYA OBM", "bolge": "Ege"},
    "SİMAV OİM": {"il": "Kütahya", "obm": "KÜTAHYA OBM", "bolge": "Ege"},

    "AKYAZI OİM": {"il": "Sakarya", "obm": "SAKARYA OBM", "bolge": "Marmara"},
    "HENDEK OİM": {"il": "Sakarya", "obm": "SAKARYA OBM", "bolge": "Marmara"},
    "GÖLCÜK OİM": {"il": "Kocaeli", "obm": "SAKARYA OBM", "bolge": "Marmara"},
    "ANAFARTALAR OİM": {"il": "Çanakkale", "obm": "ÇANAKKALE OBM", "bolge": "Marmara"},
    "AYVACIK OİM": {"il": "Çanakkale", "obm": "ÇANAKKALE OBM", "bolge": "Marmara"},
    "BAYRAMİÇ OİM": {"il": "Çanakkale", "obm": "ÇANAKKALE OBM", "bolge": "Marmara"},
    "KALKIM OİM": {"il": "Çanakkale", "obm": "ÇANAKKALE OBM", "bolge": "Marmara"},
    "KELES OİM": {"il": "Bursa", "obm": "BURSA OBM", "bolge": "Marmara"},
    "BOZÜYÜK OİM": {"il": "Bilecik", "obm": "ESKİŞEHİR OBM", "bolge": "Marmara"},

    "TOSYA OİM": {"il": "Kastamonu", "obm": "KASTAMONU OBM", "bolge": "Karadeniz"},
    "ARAÇ OİM": {"il": "Kastamonu", "obm": "KASTAMONU OBM", "bolge": "Karadeniz"},
    "DEVREKANİ OİM": {"il": "Kastamonu", "obm": "KASTAMONU OBM", "bolge": "Karadeniz"},
    "TAŞKÖPRÜ OİM": {"il": "Kastamonu", "obm": "KASTAMONU OBM", "bolge": "Karadeniz"},
    "SAMATLAR OİM": {"il": "Kastamonu", "obm": "KASTAMONU OBM", "bolge": "Karadeniz"},
    "DİRGİNE OİM": {"il": "Zonguldak", "obm": "ZONGULDAK OBM", "bolge": "Karadeniz"},
    "BOYABAT OİM": {"il": "Sinop", "obm": "KASTAMONU OBM", "bolge": "Karadeniz"},
    "ALAÇAM OİM": {"il": "Samsun", "obm": "SAMSUN OBM", "bolge": "Karadeniz"},
    "KAVAK OİM": {"il": "Samsun", "obm": "SAMSUN OBM", "bolge": "Karadeniz"},
    "ALMUS OİM": {"il": "Tokat", "obm": "AMASYA OBM", "bolge": "Karadeniz"},
    "ERBAA OİM": {"il": "Tokat", "obm": "AMASYA OBM", "bolge": "Karadeniz"},
    "OSMANCIK OİM": {"il": "Çorum", "obm": "AMASYA OBM", "bolge": "Karadeniz"},
    "ARHAVİ OİM": {"il": "Artvin", "obm": "ARTVİN OBM", "bolge": "Karadeniz"},
    "ARTVİN OİM": {"il": "Artvin", "obm": "ARTVİN OBM", "bolge": "Karadeniz"},

    "BEYPAZARI OİM": {"il": "Ankara", "obm": "ANKARA OBM", "bolge": "İç Anadolu"},
    "ÇANKIRI OİM": {"il": "Çankırı", "obm": "ANKARA OBM", "bolge": "İç Anadolu"},
    "BEYŞEHİR OİM": {"il": "Konya", "obm": "KONYA OBM", "bolge": "İç Anadolu"},
    "EREĞLİ OİM": {"il": "Konya", "obm": "KONYA OBM", "bolge": "İç Anadolu"},
    "ERMENEK OİM": {"il": "Karaman", "obm": "KONYA OBM", "bolge": "İç Anadolu"},
    "NİĞDE OİM": {"il": "Niğde", "obm": "KAYSERİ OBM", "bolge": "İç Anadolu"},

    "ELAZIĞ OİM": {"il": "Elazığ", "obm": "ELAZIĞ OBM", "bolge": "Doğu Anadolu"},

    "GAZİANTEP OİM": {"il": "Gaziantep", "obm": "KAHRAMANMARAŞ OBM", "bolge": "Güneydoğu Anadolu"},

    "GÖKSUN OİM": {"il": "Kahramanmaraş", "obm": "KAHRAMANMARAŞ OBM", "bolge": "Akdeniz"},
    "KOZAN OİM": {"il": "Adana", "obm": "ADANA OBM", "bolge": "Akdeniz"},
    "POS OİM": {"il": "Adana", "obm": "ADANA OBM", "bolge": "Akdeniz"},
    "TARSUS OİM": {"il": "Mersin", "obm": "MERSİN OBM", "bolge": "Akdeniz"},
    "ANTAKYA OİM": {"il": "Hatay", "obm": "KAHRAMANMARAŞ OBM", "bolge": "Akdeniz"},
    "DÖRTYOL OİM": {"il": "Hatay", "obm": "KAHRAMANMARAŞ OBM", "bolge": "Akdeniz"},
    "TAŞAĞIL OİM": {"il": "Antalya", "obm": "ANTALYA OBM", "bolge": "Akdeniz"},
    "KAŞ OİM": {"il": "Antalya", "obm": "ANTALYA OBM", "bolge": "Akdeniz"},
    "BUCAK OİM": {"il": "Burdur", "obm": "ISPARTA OBM", "bolge": "Akdeniz"},
    "BURDUR OİM": {"il": "Burdur", "obm": "ISPARTA OBM", "bolge": "Akdeniz"},
    "GÖLHİSAR OİM": {"il": "Burdur", "obm": "ISPARTA OBM", "bolge": "Akdeniz"},
    "ISPARTA OİM": {"il": "Isparta", "obm": "ISPARTA OBM", "bolge": "Akdeniz"},
}



@st.cache_data(show_spinner=False)
def oim_konum_haritasi_oku(cache_key=None):
    """
    Önce resmi OGM tarama scriptinin ürettiği JSON dosyasını okur.
    JSON yoksa app içindeki yedek haritayı kullanır.
    """
    harita = dict(OIM_KONUM_HARITASI)

    if os.path.exists(OIM_HARITA_JSON_DOSYASI):
        try:
            with open(OIM_HARITA_JSON_DOSYASI, "r", encoding="utf-8") as f:
                veri = json.load(f)

            json_harita = veri.get("harita", {})

            for oim, bilgi in json_harita.items():
                key = str(oim or "").strip().upper().replace(" OIM", " OİM")

                if not key:
                    continue

                harita[key] = {
                    "il": bilgi.get("il", "Bilinmeyen"),
                    "obm": bilgi.get("obm", "Bilinmeyen OBM"),
                    "bolge": bilgi.get("bolge", bilgi.get("cografi_bolge", "Bilinmeyen")),
                }

        except Exception:
            pass

    return harita


def oim_harita_cache_key():
    try:
        return os.path.getmtime(OIM_HARITA_JSON_DOSYASI), os.path.getsize(OIM_HARITA_JSON_DOSYASI)
    except Exception:
        return 0, 0

def konum_bilgisi_tamamla(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    harita = oim_konum_haritasi_oku(oim_harita_cache_key())

    if "il" not in df.columns:
        df["il"] = ""

    for kolon in ["il", "obm", "oim", "cografi_bolge"]:
        if kolon not in df.columns:
            df[kolon] = ""

        df[kolon] = df[kolon].fillna("").astype(str).str.strip()

    def bos_mu(v):
        v = str(v or "").strip()
        return v == "" or v.lower() in ["nan", "none", "null", "-"] or "BİLİNMEYEN" in v.upper() or "BILINMEYEN" in v.upper()

    for idx, row in df.iterrows():
        oim = str(row.get("oim", "") or "").strip().upper()
        bilgi = harita.get(oim)

        if not bilgi:
            if bos_mu(row.get("il")):
                df.at[idx, "il"] = "Bilinmeyen"
            if bos_mu(row.get("obm")):
                df.at[idx, "obm"] = "Bilinmeyen OBM"
            if bos_mu(row.get("cografi_bolge")):
                df.at[idx, "cografi_bolge"] = "Bilinmeyen"
            continue

        if bos_mu(row.get("il")):
            df.at[idx, "il"] = bilgi["il"]

        if bos_mu(row.get("obm")):
            df.at[idx, "obm"] = bilgi["obm"]

        if bos_mu(row.get("cografi_bolge")):
            df.at[idx, "cografi_bolge"] = bilgi["bolge"]

    return df

def hazirla(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    sayi_kolonlari = [
        "parti_no",
        "ihale_no",
        "adet",
        "miktar_m3_hesap",
        "muhammen_birim_fiyat",
        "teminat_tutari",
        "toplam_muhammen_hesap",
        "katilimci_sayisi",
    ]

    for kolon in sayi_kolonlari:
        if kolon in df.columns:
            df[kolon] = pd.to_numeric(df[kolon], errors="coerce")

    bos_degerler = {
        "None": "", "none": "", "NONE": "",
        "nan": "", "NaN": "", "NAN": "",
        "<NA>": "", "null": "", "Null": "", "NULL": "",
        "-": ""
    }

    for kolon in df.columns:
        if df[kolon].dtype == "object":
            df[kolon] = df[kolon].fillna("").astype(str).str.strip().replace(bos_degerler)

    metin_kolonlari = [
        "sinif", "boy_kodu", "cap_kodu", "urun_turu", "agac_turu",
        "parti_durum", "detay_durum", "il", "obm", "oim", "cografi_bolge"
    ]

    for kolon in metin_kolonlari:
        if kolon in df.columns:
            df[kolon] = df[kolon].astype(str).str.strip().replace(bos_degerler)

    df = konum_bilgisi_tamamla(df)

    df = puan_kategorisi_olustur(df)
    df = supheli_fiyat_isaretle(df)
    df = firsat_puani_hesapla(df)
    df = fiyat_durumu_hesapla(df)

    return df


def supheli_fiyat_isaretle(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["supheli_fiyat"] = False
    df["supheli_neden"] = ""

    if "muhammen_birim_fiyat" not in df.columns:
        return df

    fiyat = pd.to_numeric(df["muhammen_birim_fiyat"], errors="coerce")

    kosul_dusuk = fiyat.notna() & (fiyat < 1000)
    df.loc[kosul_dusuk, "supheli_fiyat"] = True
    df.loc[kosul_dusuk, "supheli_neden"] = "1000 TL altı"

    grup_kolonlari = [k for k in ["urun_turu", "agac_turu"] if k in df.columns]

    if grup_kolonlari:
        medyan = df.groupby(grup_kolonlari)["muhammen_birim_fiyat"].transform("median")
        kosul = fiyat.notna() & medyan.notna() & (medyan > 0) & (fiyat < medyan * 0.5)
        df.loc[kosul, "supheli_fiyat"] = True
        df.loc[kosul, "supheli_neden"] = "Benzerlerinden çok düşük"

    return df





def kalite_ozeti_olustur(row) -> str:
    parcalar = []

    for kolon, etiket in [
        ("sinif", "Sınıf"),
        ("boy_kodu", "Boy"),
        ("cap_kodu", "Çap"),
    ]:
        val = temiz_metin(row.get(kolon, ""))

        if val:
            parcalar.append(f"{etiket}: {val}")

    return " | ".join(parcalar) if parcalar else "Kalite bilgisi yok"


def puan_kategorisi_olustur(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    ana_kategoriler = []
    detay_kategoriler = []
    kalite_ozetleri = []

    for _, row in df.iterrows():
        agac = temiz_metin(row.get("agac_turu", ""))
        urun = temiz_metin(row.get("urun_turu", ""))
        sinif = temiz_metin(row.get("sinif", ""))
        boy = temiz_metin(row.get("boy_kodu", ""))
        cap = temiz_metin(row.get("cap_kodu", ""))

        ana_parcalar = [x for x in [agac, urun] if x]
        detay_parcalar = [x for x in [agac, urun, sinif, boy, cap] if x]

        ana_kategoriler.append(" ".join(ana_parcalar) if ana_parcalar else "Genel")
        detay_kategoriler.append(" ".join(detay_parcalar) if detay_parcalar else "Genel")
        kalite_ozetleri.append(kalite_ozeti_olustur(row))

    df["ana_puan_kategorisi"] = ana_kategoriler
    df["puan_kategorisi"] = detay_kategoriler
    df["kalite_ozeti"] = kalite_ozetleri

    # Eğer detay kategori tek kayıtsa fiyat kıyasını ana kategoriye düşür.
    # Böylece "Karaçam Tomruk 1. sınıf uzun boy" varsa önce kendi içinde,
    # kendi içinde yeterli kayıt yoksa "Karaçam Tomruk" ana grubunda kıyaslanır.
    detay_adet = df.groupby("puan_kategorisi")["puan_kategorisi"].transform("count")
    df["karsilastirma_kategorisi"] = df["puan_kategorisi"]
    df.loc[detay_adet < 2, "karsilastirma_kategorisi"] = df.loc[detay_adet < 2, "ana_puan_kategorisi"]

    return df


def kalite_puani_hesapla(df: pd.DataFrame) -> pd.Series:
    """
    Kalite puanı fiyatı değil, malın niteliğini destekler.
    1. sınıf / uzun boy gibi mallar biraz pahalı olsa bile tamamen haksız yere düşük puan almasın.
    """
    kalite = pd.Series(0, index=df.index, dtype="float")

    if "sinif" in df.columns:
        sinif = df["sinif"].astype(str).str.lower().str.strip()

        birinci = sinif.str.contains(r"\b1\b|1\.|i\.|ı\.|birinci|1 sınıf|1.sınıf", regex=True, na=False)
        ikinci = sinif.str.contains(r"\b2\b|2\.|ii\.|ikinci|2 sınıf|2.sınıf", regex=True, na=False)
        ucuncu = sinif.str.contains(r"\b3\b|3\.|iii\.|üçüncü|ucuncu|3 sınıf|3.sınıf", regex=True, na=False)

        kalite = kalite.mask(birinci, kalite + 12)
        kalite = kalite.mask(ikinci, kalite + 7)
        kalite = kalite.mask(ucuncu, kalite + 3)

    if "boy_kodu" in df.columns:
        boy = df["boy_kodu"].astype(str).str.lower().str.strip()

        uzun = boy.str.contains("uzun|ub|u/b|u b", regex=True, na=False)
        normal = boy.str.contains("normal|nb|n/b|n b", regex=True, na=False)
        kisa = boy.str.contains("kısa|kisa|kb|k/b|k b", regex=True, na=False)

        kalite = kalite.mask(uzun, kalite + 8)
        kalite = kalite.mask(normal, kalite + 5)
        kalite = kalite.mask(kisa, kalite + 2)

    if "cap_kodu" in df.columns:
        cap = df["cap_kodu"].astype(str).str.lower().str.strip()

        kalin = cap.str.contains("kalın|kalin|kln|büyük|buyuk|geniş|genis", regex=True, na=False)
        orta = cap.str.contains("orta|ort", regex=True, na=False)
        ince = cap.str.contains("ince|inc", regex=True, na=False)

        kalite = kalite.mask(kalin, kalite + 6)
        kalite = kalite.mask(orta, kalite + 4)
        kalite = kalite.mask(ince, kalite + 1)

    return kalite.clip(lower=0, upper=25)


def fiyat_durumu_hesapla(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "muhammen_birim_fiyat" not in df.columns:
        df["fiyat_durumu"] = "Veri Yok"
        return df

    if "karsilastirma_kategorisi" not in df.columns:
        df = puan_kategorisi_olustur(df)

    fiyat = pd.to_numeric(df["muhammen_birim_fiyat"], errors="coerce")
    df["fiyat_durumu"] = "Normal"

    medyan = df.groupby("karsilastirma_kategorisi")["muhammen_birim_fiyat"].transform("median")
    adet = df.groupby("karsilastirma_kategorisi")["muhammen_birim_fiyat"].transform("count")

    # Kıyas artık kaliteyi dikkate alan kategoriyle yapılır:
    # Önce ağaç + ürün + sınıf + boy + çap, veri azsa ağaç + ürün.
    karsilastirilebilir = fiyat.notna() & medyan.notna() & (medyan > 0) & (adet >= 2)

    df.loc[karsilastirilebilir & (fiyat <= medyan * 0.85), "fiyat_durumu"] = "Ucuz"
    df.loc[karsilastirilebilir & (fiyat >= medyan * 1.15), "fiyat_durumu"] = "Pahalı"

    if "supheli_fiyat" in df.columns:
        df.loc[df["supheli_fiyat"] == True, "fiyat_durumu"] = "Şüpheli"

    df.loc[fiyat.isna(), "fiyat_durumu"] = "Veri Yok"

    return df


def firsat_puani_hesapla(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "muhammen_birim_fiyat" not in df.columns:
        df["firsat_puani"] = 0
        df["firsat_seviyesi"] = "Veri Yok"
        df["kalite_puani"] = 0
        return df

    if "karsilastirma_kategorisi" not in df.columns:
        df = puan_kategorisi_olustur(df)

    fiyat = pd.to_numeric(df["muhammen_birim_fiyat"], errors="coerce")
    miktar = pd.to_numeric(df.get("miktar_m3_hesap", pd.Series([None] * len(df))), errors="coerce")

    # KALİTE AĞIRLIKLI PUAN:
    # 1) Fiyat, mümkünse aynı ağaç + ürün + sınıf + boy + çap içinde kıyaslanır.
    # 2) Detay kategori tek kalırsa ağaç + ürün ana grubuna düşer.
    # 3) 1. sınıf / uzun boy / kalın çap gibi kalite bilgileri ayrıca destek puanı alır.
    grup = df.groupby("karsilastirma_kategorisi", dropna=False)

    adet = grup["muhammen_birim_fiyat"].transform("count")
    medyan_fiyat = grup["muhammen_birim_fiyat"].transform("median")
    rank = grup["muhammen_birim_fiyat"].rank(method="min", ascending=True)

    fiyat_puan = pd.Series(35, index=df.index, dtype="float")

    coklu_kategori = adet >= 2
    fiyat_puan = fiyat_puan.mask(
        coklu_kategori,
        20 + ((adet - rank) / (adet - 1)).fillna(0) * 35
    )

    fiyat_puan = fiyat_puan.mask(
        coklu_kategori & fiyat.notna() & medyan_fiyat.notna() & (fiyat <= medyan_fiyat * 0.85),
        fiyat_puan + 8
    )
    fiyat_puan = fiyat_puan.mask(
        coklu_kategori & fiyat.notna() & medyan_fiyat.notna() & (fiyat >= medyan_fiyat * 1.15),
        fiyat_puan - 8
    )

    fiyat_puan = fiyat_puan.clip(lower=8, upper=63)

    kalite_puani = kalite_puani_hesapla(df)
    df["kalite_puani"] = kalite_puani.round(0).astype(int)

    # Miktar puanı da aynı kıyas kategorisi içinde hesaplanır.
    miktar_puan = pd.Series(8, index=df.index, dtype="float")

    if miktar.notna().any() and "miktar_m3_hesap" in df.columns:
        miktar_medyan = grup["miktar_m3_hesap"].transform("median")
        miktar_q75 = grup["miktar_m3_hesap"].transform(lambda x: x.quantile(0.75) if x.notna().any() else None)

        miktar_puan = miktar_puan.mask(miktar.notna() & miktar_medyan.notna() & (miktar >= miktar_medyan), 12)
        miktar_puan = miktar_puan.mask(miktar.notna() & miktar_q75.notna() & (miktar >= miktar_q75), 16)

    durum = df.get("parti_durum", pd.Series([""] * len(df))).astype(str).str.lower()
    durum_puan = pd.Series(4, index=df.index, dtype="float")
    durum_puan = durum_puan.mask(durum.str.contains("bekliyor|açık|satılmayı", case=False, na=False), 8)

    veri_puan = pd.Series(0, index=df.index, dtype="float")
    for kolon in ["kaynak_link", "obm", "oim", "urun_adi", "puan_kategorisi"]:
        if kolon in df.columns:
            veri_puan += df[kolon].apply(lambda x: 1.5 if gecerli_metin(x) else 0)

    ceza = pd.Series(0, index=df.index, dtype="float")
    if "supheli_fiyat" in df.columns:
        ceza = ceza.mask(df["supheli_fiyat"] == True, 25)

    # Kıyas kategorisi tek kayıt kalırsa hâlâ tam emin değiliz; ama kalite varsa puan düşmesin diye ceza az.
    tek_kategori_ceza = pd.Series(0, index=df.index, dtype="float")
    tek_kategori_ceza = tek_kategori_ceza.mask(adet < 2, 5)

    puan = fiyat_puan + kalite_puani + miktar_puan + durum_puan + veri_puan - ceza - tek_kategori_ceza
    puan = puan.clip(lower=0, upper=100).round(0)

    df["firsat_puani"] = puan.astype(int)

    def seviye(p):
        if p >= 80:
            return "Çok İyi"
        if p >= 65:
            return "İyi"
        if p >= 45:
            return "Orta"
        return "Dikkat"

    df["firsat_seviyesi"] = df["firsat_puani"].apply(seviye)
    return df


def secenek(df: pd.DataFrame, kolon: str):
    if kolon not in df.columns:
        return ["Tümü"]
    vals = sorted([str(x).strip() for x in df[kolon].dropna().unique().tolist() if gecerli_metin(x)])
    return ["Tümü"] + vals


def tl(value):
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):,.0f} TL".replace(",", ".")


def m3(value):
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):,.3f} m³".replace(",", "X").replace(".", ",").replace("X", ".")


def sayi(value):
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):,.0f}".replace(",", ".")



def genel_arama_uygula(df: pd.DataFrame, arama: str) -> pd.DataFrame:
    """
    Sidebar arama kutusu artık sadece ürün adında değil;
    parti no, ihale no, ihale id, OİM ve OBM alanlarında da arar.
    """
    q = str(arama or "").strip()

    if not q or df.empty:
        return df

    kolonlar = [
        "urun_adi",
        "parti_no",
        "ihale_no",
        "ihale_id",
        "oim",
        "obm",
        "il",
        "cografi_bolge",
        "agac_turu",
        "urun_turu",
    ]

    mask = pd.Series(False, index=df.index)

    for kolon in kolonlar:
        if kolon in df.columns:
            mask = mask | df[kolon].astype(str).str.contains(q, case=False, na=False)

    # Sayı girildiyse parti no ve ihale no için tam eşleşmeyi ayrıca garantiye al.
    if q.isdigit():
        for kolon in ["parti_no", "ihale_no", "ihale_id"]:
            if kolon in df.columns:
                mask = mask | (df[kolon].astype(str).str.strip() == q)

    return df[mask]

def bolum_basligi(baslik: str, aciklama: str = ""):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-head-title">{baslik}</div>
            <div class="section-head-sub">{aciklama}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sol_menu_oku() -> str:
    secenekler = [
        ("🏠", "Özet"),
        ("🔎", "Sonuçlar"),
        ("⭐", "Fırsat Panosu"),
        ("🆕", "Yeni Kayıtlar"),
    ]

    secenek_degerleri = [f"{ikon} {ad}" for ikon, ad in secenekler]

    if "aktif_sayfa" not in st.session_state:
        st.session_state["aktif_sayfa"] = "🏠 Özet"

    if st.session_state.get("hedef_sayfa") in secenek_degerleri:
        st.session_state["aktif_sayfa"] = st.session_state.get("hedef_sayfa")

    st.sidebar.markdown(
        """
        <div class="side-title-card">
            <div class="side-title">🧭 Menü</div>
            <div class="side-sub">Bölümler bağımsız kartlar halinde çalışır.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for i, (ikon, ad) in enumerate(secenekler):
        secim = f"{ikon} {ad}"
        aktif = st.session_state.get("aktif_sayfa") == secim
        etiket = f"{ikon}  {ad}" if not aktif else f"✅  {ikon}  {ad}"

        if st.sidebar.button(
            etiket,
            key=f"menu_btn_{i}",
            use_container_width=True,
            type="primary" if aktif else "secondary",
        ):
            st.session_state["aktif_sayfa"] = secim
            st.session_state.pop("hedef_sayfa", None)
            st.rerun()

    return st.session_state.get("aktif_sayfa", "🏠 Özet")


def filtrele(df: pd.DataFrame, paket=None) -> pd.DataFrame:
    st.sidebar.header("Filtreler")
    st.sidebar.caption("Önce bölge seçilir. Sonra İl → OBM → OİM seçenekleri sırayla açılır.")

    st.sidebar.success(f"Okunan CSV: {st.session_state.get('okunan_csv', '-')}")

    def secenek_kademeli(temp_df: pd.DataFrame, kolon: str):
        return secenek(temp_df, kolon)

    def uygula_esitlik(temp_df: pd.DataFrame, kolon: str, deger: str):
        if deger != "Tümü" and kolon in temp_df.columns:
            return temp_df[temp_df[kolon] == deger]
        return temp_df

    def key_sifirla(*anahtarlar):
        for anahtar in anahtarlar:
            if st.session_state.get(anahtar) != "Tümü":
                st.session_state[anahtar] = "Tümü"

    arama = st.sidebar.text_input("Genel arama", placeholder="Parti no, ihale no, Karaçam, tomruk...", key="arama_v39")

    filtre_aktif = False
    if str(arama or "").strip():
        filtre_aktif = True

    sonuc = df.copy()
    sonuc = genel_arama_uygula(sonuc, arama)

    bolge = st.sidebar.selectbox(
        "Coğrafi Bölge",
        secenek_kademeli(sonuc, "cografi_bolge"),
        key="bolge_v39"
    )
    sonuc = uygula_esitlik(sonuc, "cografi_bolge", bolge)
    if bolge != "Tümü":
        filtre_aktif = True
    else:
        key_sifirla("il_v39", "obm_v39", "oim_v39", "urun_v39", "agac_v39", "sinif_v39", "boy_v39", "cap_v39")

    il = "Tümü"
    if bolge != "Tümü":
        il = st.sidebar.selectbox(
            "İl",
            secenek_kademeli(sonuc, "il"),
            key="il_v39"
        )
        sonuc = uygula_esitlik(sonuc, "il", il)
        if il != "Tümü":
            filtre_aktif = True
        else:
            key_sifirla("obm_v39", "oim_v39")

    obm = "Tümü"
    if bolge != "Tümü" and il != "Tümü":
        obm = st.sidebar.selectbox(
            "OBM",
            secenek_kademeli(sonuc, "obm"),
            key="obm_v39"
        )
        sonuc = uygula_esitlik(sonuc, "obm", obm)
        if obm != "Tümü":
            filtre_aktif = True
        else:
            key_sifirla("oim_v39")

    oim = "Tümü"
    if bolge != "Tümü" and il != "Tümü" and obm != "Tümü":
        oim = st.sidebar.selectbox(
            "OİM",
            secenek_kademeli(sonuc, "oim"),
            key="oim_v39"
        )
        sonuc = uygula_esitlik(sonuc, "oim", oim)
        if oim != "Tümü":
            filtre_aktif = True

    if bolge == "Tümü":
        st.sidebar.info("Detay filtreleri açmak için önce bölge seç.")
    else:
        urun = st.sidebar.selectbox(
            "Ürün Türü",
            secenek_kademeli(sonuc, "urun_turu"),
            key="urun_v39"
        )
        sonuc = uygula_esitlik(sonuc, "urun_turu", urun)
        if urun != "Tümü":
            filtre_aktif = True

        agac = st.sidebar.selectbox(
            "Ağaç Türü",
            secenek_kademeli(sonuc, "agac_turu"),
            key="agac_v39"
        )
        sonuc = uygula_esitlik(sonuc, "agac_turu", agac)
        if agac != "Tümü":
            filtre_aktif = True

        sinif = st.sidebar.selectbox(
            "Sınıf",
            secenek_kademeli(sonuc, "sinif"),
            key="sinif_v39"
        )
        sonuc = uygula_esitlik(sonuc, "sinif", sinif)
        if sinif != "Tümü":
            filtre_aktif = True

        boy = st.sidebar.selectbox(
            "Boy Kodu",
            secenek_kademeli(sonuc, "boy_kodu"),
            key="boy_v39"
        )
        sonuc = uygula_esitlik(sonuc, "boy_kodu", boy)
        if boy != "Tümü":
            filtre_aktif = True

        cap = st.sidebar.selectbox(
            "Çap Kodu",
            secenek_kademeli(sonuc, "cap_kodu"),
            key="cap_v39"
        )
        sonuc = uygula_esitlik(sonuc, "cap_kodu", cap)
        if cap != "Tümü":
            filtre_aktif = True

    if not sonuc.empty and "muhammen_birim_fiyat" in sonuc.columns and sonuc["muhammen_birim_fiyat"].notna().any():
        min_f = int(sonuc["muhammen_birim_fiyat"].min())
        max_f = int(sonuc["muhammen_birim_fiyat"].max())

        if min_f == max_f:
            st.sidebar.caption(f"Birim fiyat: {tl(min_f)}")
        else:
            fiyat = st.sidebar.slider(
                "Birim fiyat aralığı",
                min_value=min_f,
                max_value=max_f,
                value=(min_f, max_f),
                step=100,
                key="fiyat_v39"
            )
            if fiyat != (min_f, max_f):
                filtre_aktif = True
            sonuc = sonuc[
                (sonuc["muhammen_birim_fiyat"] >= fiyat[0]) &
                (sonuc["muhammen_birim_fiyat"] <= fiyat[1])
            ]

    if not sonuc.empty and "miktar_m3_hesap" in sonuc.columns and sonuc["miktar_m3_hesap"].notna().any():
        min_m = float(round(sonuc["miktar_m3_hesap"].min(), 2))
        max_m = float(round(sonuc["miktar_m3_hesap"].max(), 2))

        if min_m == max_m:
            st.sidebar.caption(f"Miktar: {m3(min_m)}")
        else:
            miktar = st.sidebar.slider(
                "Miktar aralığı m³",
                min_value=min_m,
                max_value=max_m,
                value=(min_m, max_m),
                step=1.0,
                key="miktar_v39"
            )
            if miktar != (min_m, max_m):
                filtre_aktif = True
            sonuc = sonuc[
                (sonuc["miktar_m3_hesap"] >= miktar[0]) &
                (sonuc["miktar_m3_hesap"] <= miktar[1])
            ]

    if not sonuc.empty and "firsat_puani" in sonuc.columns and sonuc["firsat_puani"].notna().any():
        min_puan = int(sonuc["firsat_puani"].min())
        max_puan = int(sonuc["firsat_puani"].max())

        if min_puan == max_puan:
            st.sidebar.caption(f"Fırsat puanı: {min_puan}")
        else:
            puan_araligi = st.sidebar.slider(
                "Fırsat puanı",
                min_value=min_puan,
                max_value=max_puan,
                value=(min_puan, max_puan),
                step=1,
                key="puan_v39"
            )
            if puan_araligi != (min_puan, max_puan):
                filtre_aktif = True
            sonuc = sonuc[
                (sonuc["firsat_puani"] >= puan_araligi[0]) &
                (sonuc["firsat_puani"] <= puan_araligi[1])
            ]

    sadece_supheli = st.sidebar.checkbox("Sadece şüpheli fiyatları göster", key="supheli_v39")
    if sadece_supheli:
        filtre_aktif = True
        sonuc = sonuc[sonuc["supheli_fiyat"] == True]

    siralama = st.sidebar.selectbox(
        "Sıralama",
        [
            "Fırsat puanı yüksek",
            "En ucuz birim fiyat",
            "En pahalı birim fiyat",
            "En yüksek miktar",
            "En düşük miktar",
            "Parti no artan",
        ],
        key="siralama_v39"
    )

    if filtre_aktif:
        st.session_state["hedef_sayfa"] = "🔎 Sonuçlar"

    if sonuc.empty:
        return sonuc

    if siralama == "Fırsat puanı yüksek" and {"firsat_puani", "muhammen_birim_fiyat"}.issubset(sonuc.columns):
        sonuc = sonuc.sort_values(["firsat_puani", "muhammen_birim_fiyat"], ascending=[False, True])
    elif siralama == "En ucuz birim fiyat" and "muhammen_birim_fiyat" in sonuc.columns:
        sonuc = sonuc.sort_values("muhammen_birim_fiyat", ascending=True)
    elif siralama == "En pahalı birim fiyat" and "muhammen_birim_fiyat" in sonuc.columns:
        sonuc = sonuc.sort_values("muhammen_birim_fiyat", ascending=False)
    elif siralama == "En yüksek miktar" and "miktar_m3_hesap" in sonuc.columns:
        sonuc = sonuc.sort_values("miktar_m3_hesap", ascending=False)
    elif siralama == "En düşük miktar" and "miktar_m3_hesap" in sonuc.columns:
        sonuc = sonuc.sort_values("miktar_m3_hesap", ascending=True)
    elif siralama == "Parti no artan" and "parti_no" in sonuc.columns:
        sonuc = sonuc.sort_values("parti_no", ascending=True)

    return sonuc


def firsat_puani_bilgi_kutusu():
    with st.expander("ℹ️ Fırsat puanı nasıl hesaplanır?", expanded=False):
        st.markdown(
            """
            **V21 puan mantığı kalite ağırlıklıdır.**

            Önce ürün şu detaylarla kalite kategorisine ayrılır:

            `Ağaç türü + Ürün türü + Sınıf + Boy kodu + Çap kodu`

            Örnekler:

            - Karaçam Tomruk 1. sınıf uzun boy
            - Kızılçam Tomruk 2. sınıf normal boy
            - Göknar Kağıtlık Odun

            Sistem önce ürünü kendi kalite kategorisi içinde kıyaslar. Eğer o detay kategoride yeterli kayıt yoksa ana kategoriye düşer:

            `Ağaç türü + Ürün türü`

            Ayrıca 1. sınıf, uzun boy ve kalın çap gibi kalite göstergeleri ekstra kalite puanı alır. Böylece iyi mal sadece fiyatı daha pahalı diye haksız yere düşük görünmez.
            """
        )

def ozet(df: pd.DataFrame):
    adet = len(df)
    en_ucuz = df["muhammen_birim_fiyat"].min() if adet else None
    ort = df["muhammen_birim_fiyat"].mean() if adet else None
    toplam_miktar = df["miktar_m3_hesap"].sum() if adet else None
    supheli = int(df["supheli_fiyat"].sum()) if adet else 0
    en_yuksek_puan = df["firsat_puani"].max() if adet and "firsat_puani" in df.columns else None

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Kayıt", sayi(adet))
    c2.metric("En ucuz", tl(en_ucuz))
    c3.metric("Ortalama", tl(ort))
    c4.metric("Toplam miktar", m3(toplam_miktar))
    c5.metric("En yüksek puan", sayi(en_yuksek_puan))
    c6.metric("Şüpheli fiyat", sayi(supheli))


def ozet_kutu(baslik, row):
    if row is None or row.empty:
        st.markdown(
            f"""
            <div class="topbox">
                <div class="topbox-title">{baslik}</div>
                <div class="topbox-main">Veri yok</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="topbox">
            <div class="topbox-title">{baslik}</div>
            <div class="topbox-main">Parti {sayi(row.get("parti_no"))} — {temiz_metin(row.get("urun_adi"))}</div>
            <div class="topbox-sub">
                <b>{tl(row.get("muhammen_birim_fiyat"))} / m³</b><br>
                Miktar: {m3(row.get("miktar_m3_hesap"))}<br>
                Fırsat: {sayi(row.get("firsat_puani"))}/100 — {temiz_metin(row.get("firsat_seviyesi"))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def one_cikanlar(df: pd.DataFrame):
    if df.empty:
        return

    st.subheader("Öne çıkanlar")

    uygun = df.copy()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        row = uygun.sort_values(["firsat_puani", "muhammen_birim_fiyat"], ascending=[False, True]).iloc[0]
        ozet_kutu("En yüksek fırsat puanı", row)

    with c2:
        row = uygun.sort_values("muhammen_birim_fiyat", ascending=True).iloc[0]
        ozet_kutu("En ucuz birim fiyat", row)

    with c3:
        row = uygun.sort_values("miktar_m3_hesap", ascending=False).iloc[0]
        ozet_kutu("En yüksek miktar", row)

    with c4:
        if "Maden Direği" in uygun.get("urun_turu", pd.Series()).values:
            row = uygun[uygun["urun_turu"] == "Maden Direği"].sort_values("muhammen_birim_fiyat", ascending=True).iloc[0]
            ozet_kutu("En ucuz maden direği", row)
        elif "Tomruk" in uygun.get("urun_turu", pd.Series()).values:
            row = uygun[uygun["urun_turu"] == "Tomruk"].sort_values("muhammen_birim_fiyat", ascending=True).iloc[0]
            ozet_kutu("En ucuz tomruk", row)
        else:
            row = uygun.sort_values("muhammen_birim_fiyat", ascending=True).iloc[0]
            ozet_kutu("En ucuz ürün", row)



def urun_eslesir(urun_turu, hedef):
    u = temiz_metin(urun_turu).lower()
    h = hedef.lower()

    if not u:
        return False

    if h == "tomruk":
        return "tomruk" in u
    if h == "maden direği":
        return "maden" in u
    if h == "kağıtlık odun":
        return "kağıt" in u or "kagit" in u
    if h == "sanayi odunu":
        return "sanayi" in u
    if h == "dikili ağaç":
        return "dikili" in u

    return h in u


def urun_pano_kutusu(baslik, alt_df: pd.DataFrame, css_class="urun-genel"):
    if alt_df is None or alt_df.empty:
        st.markdown(
            f"""
            <div class="product-board {css_class}">
                <div class="product-board-title">{baslik}</div>
                <div class="product-board-main">Veri yok</div>
                <div class="product-board-sub">Bu filtrelerde bu ürün türü bulunamadı.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    ucuz = alt_df.sort_values("muhammen_birim_fiyat", ascending=True).iloc[0]
    iyi = alt_df.sort_values(["firsat_puani", "muhammen_birim_fiyat"], ascending=[False, True]).iloc[0]
    ort = alt_df["muhammen_birim_fiyat"].mean()
    toplam_miktar = alt_df["miktar_m3_hesap"].sum() if "miktar_m3_hesap" in alt_df.columns else None

    st.markdown(
        f"""
        <div class="product-board {css_class}">
            <div class="product-board-title">{baslik}</div>
            <div class="product-board-main">Parti {sayi(ucuz.get("parti_no"))} — {tl(ucuz.get("muhammen_birim_fiyat"))} / m³</div>
            <div class="product-board-sub">
                Ürün: {temiz_metin(ucuz.get("urun_adi"))}<br>
                En iyi fırsat: Parti {sayi(iyi.get("parti_no"))} — {sayi(iyi.get("firsat_puani"))}/100<br>
                Ortalama: {tl(ort)} / m³<br>
                Toplam: {m3(toplam_miktar)} | Kayıt: {len(alt_df)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def urun_bazli_firsat_panosu(df: pd.DataFrame):
    if df.empty or "urun_turu" not in df.columns:
        return

    st.markdown('<div class="compact-note">Renkler: Tomruk sarı, Maden direği mavi, Kağıtlık kırmızı, Sanayi yeşil, Dikili mor.</div>', unsafe_allow_html=True)

    urunler = [
        ("Tomruk fırsatları", "tomruk", "urun-tomruk"),
        ("Maden direği fırsatları", "maden direği", "urun-maden"),
        ("Kağıtlık odun fırsatları", "kağıtlık odun", "urun-kagitlik"),
        ("Sanayi odunu fırsatları", "sanayi odunu", "urun-sanayi"),
        ("Dikili ağaç fırsatları", "dikili ağaç", "urun-dikili"),
    ]

    satir1 = st.columns(3)
    satir2 = st.columns(2)

    kolonlar = list(satir1) + list(satir2)

    for kolon, (baslik, hedef, css_class) in zip(kolonlar, urunler):
        alt = df[df["urun_turu"].apply(lambda x: urun_eslesir(x, hedef))]
        with kolon:
            urun_pano_kutusu(baslik, alt, css_class)


def kart(k):
    parti = sayi(k.get("parti_no"))
    urun = temiz_metin(k.get("urun_adi")) or "-"
    fiyat = tl(k.get("muhammen_birim_fiyat"))
    miktar = m3(k.get("miktar_m3_hesap"))
    toplam = tl(k.get("toplam_muhammen_hesap"))
    teminat = tl(k.get("teminat_tutari"))
    il = temiz_metin(k.get("il"))
    obm = temiz_metin(k.get("obm"))
    oim = temiz_metin(k.get("oim"))
    durum = temiz_metin(k.get("parti_durum"))
    link = temiz_metin(k.get("kaynak_link"))
    supheli = bool(k.get("supheli_fiyat", False))
    neden = temiz_metin(k.get("supheli_neden"))
    puan = sayi(k.get("firsat_puani"))
    seviye = temiz_metin(k.get("firsat_seviyesi"))

    tags = []
    tags.append(f'<span class="score-badge">Fırsat {puan}/100 — {seviye}</span>')

    fiyat_durumu = temiz_metin(k.get("fiyat_durumu"))
    if fiyat_durumu:
        tags.append(f'<span class="price-status">Fiyat: {fiyat_durumu}</span>')

    puan_kategorisi = temiz_metin(k.get("puan_kategorisi"))
    if puan_kategorisi:
        tags.append(f'<span class="badge">Kalite kategorisi: {puan_kategorisi}</span>')

    karsilastirma = temiz_metin(k.get("karsilastirma_kategorisi"))
    if karsilastirma and karsilastirma != puan_kategorisi:
        tags.append(f'<span class="badge">Kıyas: {karsilastirma}</span>')

    kalite_puani = k.get("kalite_puani", None)
    if kalite_puani is not None and not pd.isna(kalite_puani):
        tags.append(f'<span class="badge">Kalite puanı: {sayi(kalite_puani)}</span>')

    for alan in ["urun_turu", "agac_turu", "sinif", "boy_kodu", "cap_kodu"]:
        val = k.get(alan, "")
        if gecerli_metin(val):
            tags.append(f'<span class="badge">{str(val).strip()}</span>')

    uyari = f'<span class="warn">⚠️ {neden}</span>' if supheli else ""
    link_html = f'<a href="{link}" target="_blank">Kaynakta Aç</a>' if link else "-"

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-title">Parti {parti} — {urun} {uyari}</div>
            <div>{''.join(tags)}</div>
            <div class="price">{fiyat} / m³</div>
            <div class="mini">
                <b>Miktar:</b> {miktar} &nbsp; | &nbsp;
                <b>Toplam:</b> {toplam} &nbsp; | &nbsp;
                <b>Teminat:</b> {teminat}<br>
                <b>Yer:</b> {il} / {obm} / {oim}<br>
                <b>Durum:</b> {durum}<br>
                {link_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kartlar(df: pd.DataFrame):
    if df.empty:
        st.warning("Bu filtrelere uygun sonuç bulunamadı.")
        return

    toplam = len(df)
    filtre_imza = hashlib.md5(pd.util.hash_pandas_object(df[["ihale_id", "parti_no"]] if {"ihale_id", "parti_no"}.issubset(df.columns) else df.head(1), index=True).values.tobytes()).hexdigest()

    if st.session_state.get("kart_filtre_imza_v31") != filtre_imza:
        st.session_state["kart_filtre_imza_v31"] = filtre_imza
        st.session_state["kart_goster_adet_v31"] = 10

    adet = int(st.session_state.get("kart_goster_adet_v31", 10))
    adet = max(10, min(adet, toplam))

    st.caption(f"{toplam} sonuçtan {adet} tanesi gösteriliyor.")

    for _, row in df.head(adet).iterrows():
        kart(row)

    if adet < toplam:
        c1, c2, c3 = st.columns([1, 1, 2])

        with c1:
            if st.button("➕ 10 kayıt daha yükle", key="daha_fazla_10_v31"):
                st.session_state["kart_goster_adet_v31"] = min(adet + 10, toplam)
                st.rerun()

        with c2:
            if st.button("⬇️ 50 kayıt göster", key="daha_fazla_50_v31"):
                st.session_state["kart_goster_adet_v31"] = min(adet + 50, toplam)
                st.rerun()

        with c3:
            st.caption("Türkiye geneli veri büyük olduğu için kartlar parça parça yüklenir.")
    else:
        st.success("Tüm sonuçlar gösterildi.")


def tablo(df: pd.DataFrame):
    if df.empty:
        st.warning("Bu filtrelere uygun sonuç bulunamadı.")
        return

    kolonlar = [
        "firsat_puani",
        "firsat_seviyesi",
        "fiyat_durumu",
        "kalite_puani",
        "puan_kategorisi",
        "karsilastirma_kategorisi",
        "kalite_ozeti",
        "parti_no",
        "ihale_no",
        "cografi_bolge",
        "il",
        "obm",
        "oim",
        "urun_adi",
        "urun_turu",
        "agac_turu",
        "sinif",
        "boy_kodu",
        "cap_kodu",
        "adet",
        "miktar_m3_hesap",
        "muhammen_birim_fiyat",
        "teminat_tutari",
        "toplam_muhammen_hesap",
        "supheli_fiyat",
        "supheli_neden",
        "kaynak_link",
    ]

    kolonlar = [c for c in kolonlar if c in df.columns]
    gorunen = df[kolonlar].copy()

    metin_kolonlari = [
        "firsat_seviyesi", "fiyat_durumu", "puan_kategorisi", "karsilastirma_kategorisi", "kalite_ozeti", "cografi_bolge", "il", "obm", "oim", "urun_adi", "urun_turu",
        "agac_turu", "sinif", "boy_kodu", "cap_kodu", "supheli_neden"
    ]
    for kolon in metin_kolonlari:
        if kolon in gorunen.columns:
            gorunen[kolon] = gorunen[kolon].apply(lambda x: temiz_metin(x))

    st.dataframe(
        gorunen,
        use_container_width=True,
        hide_index=True,
        column_config={
            "firsat_puani": st.column_config.ProgressColumn("Fırsat Puanı", min_value=0, max_value=100, format="%d"),
            "firsat_seviyesi": "Fırsat Seviyesi",
            "fiyat_durumu": "Fiyat Durumu",
            "kalite_puani": st.column_config.NumberColumn("Kalite Puanı", format="%d"),
            "puan_kategorisi": "Kalite Kategorisi",
            "karsilastirma_kategorisi": "Kıyas Kategorisi",
            "kalite_ozeti": "Kalite Özeti",
            "parti_no": "Parti",
            "ihale_no": "İhale No",
            "cografi_bolge": "Bölge",
            "il": "İl",
            "obm": "OBM",
            "oim": "OİM",
            "urun_adi": "Ürün",
            "urun_turu": "Ürün Türü",
            "agac_turu": "Ağaç Türü",
            "boy_kodu": "Boy",
            "cap_kodu": "Çap",
            "miktar_m3_hesap": st.column_config.NumberColumn("Miktar m³", format="%.3f"),
            "muhammen_birim_fiyat": st.column_config.NumberColumn("Birim Fiyat TL", format="%.0f"),
            "teminat_tutari": st.column_config.NumberColumn("Teminat TL", format="%.0f"),
            "toplam_muhammen_hesap": st.column_config.NumberColumn("Toplam TL", format="%.0f"),
            "supheli_fiyat": "Şüpheli",
            "supheli_neden": "Şüpheli Nedeni",
            "kaynak_link": st.column_config.LinkColumn("Kaynakta Aç"),
        },
    )


def analiz(df: pd.DataFrame):
    if df.empty:
        st.warning("Bu filtrelere uygun sonuç bulunamadı.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Ürün türü")
        st.bar_chart(df["urun_turu"].value_counts())

    with c2:
        st.subheader("Ağaç türü")
        st.bar_chart(df["agac_turu"].value_counts())

    st.subheader("Fırsat puanı dağılımı")
    st.bar_chart(df["firsat_seviyesi"].value_counts())

    if "fiyat_durumu" in df.columns:
        st.subheader("Fiyat durumu dağılımı")
        st.bar_chart(df["fiyat_durumu"].value_counts())

    if "puan_kategorisi" in df.columns:
        st.subheader("Kalite kategorisi dağılımı")
        st.bar_chart(df["puan_kategorisi"].value_counts())

    if "kalite_puani" in df.columns:
        st.subheader("Kalite puanı özeti")
        kalite_ozet = df["kalite_puani"].describe().to_frame("Kalite Puanı")
        st.dataframe(kalite_ozet, use_container_width=True)

    st.subheader("Ortalama fiyat özeti")
    pivot = (
        df.groupby(["agac_turu", "urun_turu"], dropna=False)["muhammen_birim_fiyat"]
        .agg(["count", "min", "mean", "max"])
        .reset_index()
        .rename(
            columns={
                "agac_turu": "Ağaç Türü",
                "urun_turu": "Ürün Türü",
                "count": "Kayıt",
                "min": "En Ucuz",
                "mean": "Ortalama",
                "max": "En Pahalı",
            }
        )
    )
    st.dataframe(pivot, use_container_width=True, hide_index=True)


def alt_csv_yukleme_alani():
    with st.expander("📁 CSV yükleme / veri değiştirme", expanded=False):
        st.caption("CSV yüklemek istersen buradan yükle. Yükleme sonrası sayfa otomatik yenilenir ve yüklenen CSV kullanılır.")
        uploaded = st.file_uploader(
            "Farklı CSV yükle",
            type=["csv"],
            key="alt_csv_yukle_v39"
        )

        if uploaded is not None:
            st.success(f"Yüklenen CSV aktif: {uploaded.name}")

        if uploaded is not None and st.button("Yüklenen CSV'yi bırak, sunucudaki CSV'ye dön", key="csv_reset_v39"):
            st.session_state.pop("alt_csv_yukle_v39", None)
            st.rerun()


paket = lisans_kontrolu()

giris_zorunlu()
kullanici_oturum_karti()
admin_panel_linki_goster()

# Kullanıcı paneli ayrı ekrandır; CSV okumadan açılır.
if query_param_getir("admin") == "1":
    kullanicilar_paneli()
    st.stop()

okunacak_csv = en_guncel_csv_bul()
st.session_state["okunan_csv"] = okunacak_csv

uploaded_csv = st.session_state.get("alt_csv_yukle")

if uploaded_csv is not None:
    df_raw = upload_oku(uploaded_csv)
    st.session_state["okunan_csv"] = f"Yüklenen CSV: {getattr(uploaded_csv, 'name', 'CSV')}"
else:
    df_raw = csv_oku(okunacak_csv, csv_cache_anahtari(okunacak_csv))

if df_raw.empty:
    st.error(
        f"CSV bulunamadı: {okunacak_csv}\n\n"
        "CSV dosyasını bu uygulamayla aynı klasöre koy veya en alttaki CSV yükleme alanından CSV yükle."
    )
    st.stop()

menu_secimi = sol_menu_oku()

df = hazirla(df_raw)
sonuc = filtrele(df, paket)

if st.session_state.get("hedef_sayfa"):
    menu_secimi = st.session_state.get("hedef_sayfa")
    st.session_state["aktif_sayfa"] = menu_secimi
    st.session_state.pop("hedef_sayfa", None)

paket_bilgi_goster(paket)

if menu_secimi == "🏠 Özet":
    bolum_basligi("🏠 Genel Özet", "Filtrelenen kayıtların kısa durumu, son güncelleme bilgisi ve hızlı fırsat kartları.")
    guncelleme_ozeti_goster()
    ozet(sonuc)
    st.markdown(
        """
        <span class="quick-chip">🌲 Tomruk sarı</span>
        <span class="quick-chip">🔵 Maden direği mavi</span>
        <span class="quick-chip">🔴 Kağıtlık kırmızı</span>
        <span class="quick-chip">⚡ Sonuç odaklı hızlı kullanım</span>
        <span class="quick-chip">🔐 Kullanıcı girişi aktif</span>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    one_cikanlar(sonuc)
    st.divider()
    urun_bazli_firsat_panosu(sonuc)

elif menu_secimi == "🔎 Sonuçlar":
    bolum_basligi("🔎 Sonuçlar", "Filtrelenen kayıtları kart, tablo veya analiz olarak incele. Kart görünümünde 10 kayıt daha yükleme vardır.")
    ozet(sonuc)
    st.divider()

    g1, g2 = st.columns([1, 1])
    with g1:
        gorunum = st.radio("Görünüm", ["Kartlar", "Tablo", "Analiz"], horizontal=True, key="gorunum_v31")
    with g2:
        st.write("")

    if gorunum == "Kartlar":
        kartlar(sonuc)
    elif gorunum == "Tablo":
        tablo(sonuc)
    else:
        if premium_aktif(paket):
            analiz(sonuc)
        else:
            kilitli_ozellik(
                "Analiz görünümü",
                "Analiz görünümü aktif."
            )

    st.divider()

    if premium_aktif(paket):
        st.download_button(
            "Filtrelenen sonuçları CSV indir",
            data=sonuc.to_csv(index=False, encoding="utf-8-sig"),
            file_name="depo_radari_filtreli_sonuclar.csv",
            mime="text/csv",
        )
    else:
        kilitli_ozellik(
            "Rapor indirme",
            "Rapor indirme aktif."
        )

elif menu_secimi == "⭐ Fırsat Panosu":
    bolum_basligi("⭐ Fırsat Panosu", "Ürün türlerine göre öne çıkan ucuz ve yüksek puanlı kayıtlar.")
    ozet(sonuc)
    st.divider()
    one_cikanlar(sonuc)
    st.divider()
    urun_bazli_firsat_panosu(sonuc)

elif menu_secimi == "🆕 Yeni Kayıtlar":
    bolum_basligi("🆕 Yeni Kayıtlar", "Son veri güncellemesinde gelen kayıtlar ve onların fırsat özeti.")
    yeni_kayitlar_panosu(sonuc)

# Kullanıcı paneli ayrı ekrandadır.

st.divider()
alt_csv_yukleme_alani()
st.divider()
st.caption("Depo Radarı bağımsız bir analiz prototipidir. Fırsat puanı tahmini karşılaştırma amaçlıdır, kesin alım tavsiyesi değildir.")
