import os
import glob
import json
import hashlib
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


# =========================================================
# DEPO RADARI - TEMIZ, MODERN, STABIL SITE
# =========================================================

st.set_page_config(
    page_title="Depo Radarı",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded",
)


CSV_ONCELIKLI_DOSYALAR = [
    "depo_radari_turkiye_tum_ihaleler.csv",
    "depo_radari_turkiye_tum_ihaleler(1).csv",
    "depo_radari_turkiye_tum_ihaleler_guvenli_v3.csv",
    "depo_radari_tum_ihaleler_guvenli_v3.csv",
    "depo_radari_tum_ihaleler_guvenli_v2.csv",
    "depo_radari_tum_ihaleler_guvenli.csv",
    "depo_radari_temiz_v6.csv",
    "depo_radari_temiz_v5.csv",
]

KULLANICI_DOSYASI = "depo_radari_kullanicilar.json"
OTURUM_GIZLI_ANAHTAR = "depo_radari_2026_guvenli_oturum"

VARSAYILAN_YETKILER = {
    "siteye_giris": True,
    "csv_yukleme": True,
    "analiz": True,
    "rapor_indirme": True,
    "kullanici_yonetimi": False,
}


# =========================================================
# TASARIM
# =========================================================

st.markdown(
    """
    <style>
    :root{
        color-scheme: light !important;
        --bg:#eef1f3;
        --panel:#f8f9f7;
        --card:#ffffff;
        --line:#dfe7e1;
        --text:#132238;
        --muted:#738278;
        --green:#1f8d5d;
        --green-dark:#176948;
        --green-soft:#e8f7ef;
        --red:#dc2626;
        --orange:#d97706;
        --blue:#2563eb;
        --purple:#7048e8;
        --shadow:0 18px 45px rgba(15,23,42,.08);
        --shadow-soft:0 10px 25px rgba(15,23,42,.055);
    }

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main{
        background:
          radial-gradient(circle at 2% 92%, rgba(31,141,93,.18), transparent 20rem),
          radial-gradient(circle at 96% 8%, rgba(126,145,134,.18), transparent 18rem),
          var(--bg) !important;
        color:var(--text) !important;
    }

    header[data-testid="stHeader"]{background:transparent !important;}

    .block-container{
        max-width:1450px;
        padding-top:1.2rem !important;
        padding-bottom:2.8rem !important;
    }

    section[data-testid="stSidebar"]{
        background:rgba(248,249,247,.96) !important;
        border-right:1px solid rgba(210,221,214,.95) !important;
    }

    section[data-testid="stSidebar"] *{color:var(--text) !important;}

    .hero{
        background:rgba(255,255,255,.94);
        border:1px solid rgba(215,224,219,.95);
        border-radius:34px;
        padding:30px 32px;
        box-shadow:var(--shadow);
        margin-bottom:22px;
        position:relative;
        overflow:hidden;
    }

    .hero::before{
        content:"";
        position:absolute;
        top:-70px;
        right:-50px;
        width:240px;
        height:240px;
        border-radius:999px;
        background:radial-gradient(circle, rgba(31,141,93,.16), transparent 68%);
    }

    .hero-head{
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:20px;
        flex-wrap:wrap;
        position:relative;
        z-index:1;
    }

    .hero-title{
        font-size:52px;
        line-height:1.05;
        font-weight:950;
        letter-spacing:-1.3px;
        color:var(--text);
        margin:0 0 10px 0;
    }

    .hero-sub{
        max-width:860px;
        font-size:17px;
        line-height:1.58;
        color:var(--muted);
        font-weight:720;
        margin:0;
    }

    .hero-pill{
        display:inline-flex;
        align-items:center;
        gap:8px;
        border:1.5px solid rgba(31,141,93,.25);
        background:var(--green-soft);
        color:var(--green-dark);
        border-radius:999px;
        padding:12px 18px;
        font-size:16px;
        font-weight:950;
        white-space:nowrap;
    }

    .side-card{
        background:#ffffff;
        border:1px solid rgba(215,224,219,.95);
        border-radius:24px;
        padding:16px 16px;
        margin:10px 0 14px 0;
        box-shadow:var(--shadow-soft);
    }

    .side-card.green{
        background:linear-gradient(180deg, #eff9f2, #e8f6ee);
        border-color:rgba(31,141,93,.25);
    }

    .side-title{
        font-size:19px;
        font-weight:950;
        letter-spacing:-.3px;
        margin-bottom:4px;
        color:var(--text);
    }

    .side-sub{
        color:var(--muted);
        font-size:13px;
        font-weight:750;
        line-height:1.45;
    }

    .section-head{
        background:rgba(255,255,255,.94);
        border:1px solid rgba(215,224,219,.95);
        border-radius:28px;
        padding:22px 24px;
        box-shadow:var(--shadow-soft);
        margin-bottom:18px;
    }

    .section-title{
        font-size:32px;
        font-weight:950;
        letter-spacing:-.7px;
        margin-bottom:6px;
        color:var(--text);
    }

    .section-sub{
        color:var(--muted);
        font-size:15px;
        font-weight:700;
        line-height:1.55;
    }

    div[data-testid="stMetric"],
    .data-card,
    .result-card,
    .user-card,
    .user-table-wrap,
    .help-card,
    .detail-box{
        background:rgba(255,255,255,.94) !important;
        border:1px solid rgba(215,224,219,.95) !important;
        border-radius:24px !important;
        box-shadow:var(--shadow-soft) !important;
    }

    div[data-testid="stMetric"]{padding:10px 8px !important;}
    div[data-testid="stMetric"] *{color:var(--text) !important;}
    div[data-testid="stMetricLabel"] p{color:var(--muted) !important; font-weight:900 !important;}
    div[data-testid="stMetricValue"]{font-weight:950 !important; letter-spacing:-.55px !important;}

    .data-card{
        padding:18px 18px;
        margin-bottom:14px;
    }

    .data-card-title{
        color:var(--muted);
        font-size:13px;
        font-weight:950;
        text-transform:uppercase;
        letter-spacing:.05em;
        margin-bottom:7px;
    }

    .data-card-main{
        color:var(--text);
        font-size:22px;
        font-weight:950;
        line-height:1.25;
    }

    .data-card-sub{
        color:var(--muted);
        font-size:13px;
        font-weight:700;
        line-height:1.45;
        margin-top:7px;
    }

    .result-card{
        padding:20px 20px;
        margin-bottom:16px;
    }

    .result-title{
        font-size:22px;
        font-weight:950;
        color:var(--text);
        margin-bottom:8px;
    }

    .result-price{
        font-size:32px;
        font-weight:950;
        color:var(--text);
        margin:8px 0;
    }

    .result-mini{
        color:var(--muted);
        font-size:14px;
        font-weight:700;
        line-height:1.65;
    }

    .pill{
        display:inline-block;
        border-radius:999px;
        padding:7px 11px;
        background:#f7faf8;
        border:1px solid #dfe7e1;
        color:#32473b;
        font-size:12px;
        font-weight:900;
        margin:0 6px 8px 0;
    }

    .pill.green{background:var(--green-soft); border-color:rgba(31,141,93,.25); color:var(--green-dark);}
    .pill.yellow{background:#fff8e6; border-color:#f5d88f; color:#8a621d;}
    .pill.red{background:#fff0f0; border-color:#f5b4b4; color:#a51c1c;}
    .pill.blue{background:#edf4ff; border-color:#bfd6ff; color:#164a9f;}

    .product-tomruk{border-left:8px solid #d7a600 !important; background:#fff9db !important;}
    .product-maden{border-left:8px solid #276ef1 !important; background:#e9f1ff !important;}
    .product-kagitlik{border-left:8px solid #d92d2d !important; background:#ffecec !important;}
    .product-sanayi{border-left:8px solid #1f8d5d !important; background:#e9f8ef !important;}
    .product-dikili{border-left:8px solid #7048e8 !important; background:#f0ecff !important;}

    .stButton > button,
    .stDownloadButton > button{
        width:100%;
        border-radius:18px !important;
        min-height:52px !important;
        border:1.5px solid rgba(195,205,202,.95) !important;
        background:#ffffff !important;
        color:var(--text) !important;
        font-weight:900 !important;
        font-size:15px !important;
        box-shadow:0 7px 16px rgba(15,23,42,.04) !important;
        transition:all .15s ease !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover{
        transform:translateY(-1px);
        border-color:rgba(31,141,93,.35) !important;
        box-shadow:0 12px 24px rgba(15,23,42,.08) !important;
    }

    .stButton > button[kind="primary"]{
        background:linear-gradient(180deg, #22a267, #1b8d5b) !important;
        border-color:#1b8d5b !important;
        color:#ffffff !important;
        box-shadow:0 12px 26px rgba(31,141,93,.23) !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div{
        background:#ffffff !important;
        border:1.5px solid #d7e0db !important;
        color:var(--text) !important;
        border-radius:16px !important;
        min-height:50px !important;
        font-weight:750 !important;
    }

    [data-testid="stTextInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stFileUploader"] label,
    [data-testid="stCheckbox"] label,
    [data-testid="stSlider"] label,
    [data-testid="stMultiSelect"] label{
        color:#31443b !important;
        font-weight:850 !important;
    }

    [data-testid="stExpander"]{
        background:rgba(255,255,255,.94) !important;
        border:1px solid rgba(215,224,219,.95) !important;
        border-radius:22px !important;
        box-shadow:var(--shadow-soft) !important;
        overflow:hidden !important;
    }

    [data-testid="stExpander"] *{color:var(--text) !important;}

    .user-table-wrap{overflow:auto; margin:14px 0 22px 0;}
    .user-table{width:100%; min-width:920px; border-collapse:collapse;}
    .user-table th{
        background:#f7faf8;
        color:#5e6f65;
        font-size:13px;
        text-align:left;
        padding:14px 12px;
        border-bottom:1px solid #dfe7e1;
        font-weight:950;
        white-space:nowrap;
    }
    .user-table td{
        background:#ffffff;
        color:var(--text);
        padding:14px 12px;
        border-bottom:1px solid #edf2ee;
        font-weight:800;
        white-space:nowrap;
    }

    .user-card{padding:18px 20px; margin:16px 0 10px 0;}
    .user-card-title{font-size:21px; font-weight:950; color:var(--text);}
    .user-card-sub{color:var(--muted); font-size:14px; font-weight:700; margin-top:4px;}

    .user-pill{
        display:inline-block;
        background:var(--green-soft);
        color:var(--green-dark);
        border:1.5px solid rgba(31,141,93,.22);
        border-radius:999px;
        padding:8px 13px;
        font-weight:950;
    }

    .help-card{padding:20px; min-height:150px;}
    .help-card h3{margin:0 0 8px 0; color:var(--text);}
    .help-card p{color:var(--muted); font-weight:700; line-height:1.55;}

    .detail-box{padding:20px; margin-bottom:18px;}
    .detail-row{display:grid; grid-template-columns:170px 1fr; gap:12px; padding:8px 0; border-bottom:1px solid #edf2ee;}
    .detail-row:last-child{border-bottom:none;}
    .detail-key{color:var(--muted); font-weight:900;}
    .detail-val{color:var(--text); font-weight:850;}

    .stTabs [data-baseweb="tab-list"]{gap:12px;}
    .stTabs [data-baseweb="tab"]{
        background:#ffffff;
        border:1.5px solid #d7e0db;
        border-radius:16px;
        color:var(--text);
        font-weight:900;
        box-shadow:var(--shadow-soft);
    }
    .stTabs [aria-selected="true"]{
        background:linear-gradient(180deg, #22a267, #1b8d5b) !important;
        color:#ffffff !important;
        border-color:#1b8d5b !important;
    }

    [data-testid="stAlert"]{
        border-radius:18px !important;
        border:1px solid rgba(215,224,219,.95) !important;
    }

    @media (max-width: 900px){
        .hero-title{font-size:38px;}
        .section-title{font-size:27px;}
        .hero{border-radius:26px; padding:22px 20px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# GENEL YARDIMCI FONKSIYONLAR
# =========================================================

def html_escape(text: str) -> str:
    return (
        str(text if text is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def h(text):
    return html_escape(str(text if text is not None else ""))


def sifre_hash(s: str) -> str:
    return hashlib.sha256(str(s or "").encode("utf-8")).hexdigest()


def token_uret(kullanici_adi: str, sifre_hash_degeri: str) -> str:
    raw = f"{kullanici_adi.lower()}|{sifre_hash_degeri}|{OTURUM_GIZLI_ANAHTAR}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def qp_get(key: str, default: str = "") -> str:
    try:
        val = st.query_params.get(key, default)
        if isinstance(val, list):
            return str(val[0]) if val else default
        return str(val or default)
    except Exception:
        return default


def qp_set(**kwargs):
    try:
        for k, v in kwargs.items():
            if v is None:
                if k in st.query_params:
                    del st.query_params[k]
            else:
                st.query_params[k] = str(v)
    except Exception:
        pass


def fmt_tl(v):
    try:
        if pd.isna(v):
            return "-"
        return f"{float(v):,.0f} TL".replace(",", ".")
    except Exception:
        return "-"


def fmt_m3(v):
    try:
        if pd.isna(v):
            return "-"
        return f"{float(v):,.2f} m³".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "-"


def to_num(s):
    return pd.to_numeric(s, errors="coerce")


# =========================================================
# KULLANICI SISTEMI
# =========================================================

def kullanici_dosyasi_olustur():
    path = Path(KULLANICI_DOSYASI)
    if path.exists():
        return

    data = {
        "kullanicilar": [
            {
                "kullanici_adi": "admin",
                "sifre_hash": sifre_hash("admin123"),
                "ad": "Yönetici",
                "rol": "admin",
                "aktif": True,
                "kayit_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "yetkiler": {
                    "siteye_giris": True,
                    "csv_yukleme": True,
                    "analiz": True,
                    "rapor_indirme": True,
                    "kullanici_yonetimi": True,
                },
            }
        ]
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def kullanici_verisi_yukle() -> dict:
    kullanici_dosyasi_olustur()
    try:
        data = json.loads(Path(KULLANICI_DOSYASI).read_text(encoding="utf-8"))
    except Exception:
        data = {"kullanicilar": []}

    data.setdefault("kullanicilar", [])
    degisti = False

    for u in data["kullanicilar"]:
        u.setdefault("ad", u.get("kullanici_adi", ""))
        u.setdefault("rol", "admin" if str(u.get("kullanici_adi", "")).lower() == "admin" else "user")
        u.setdefault("aktif", True)
        u.setdefault("kayit_tarihi", "")
        if "yetkiler" not in u or not isinstance(u.get("yetkiler"), dict):
            u["yetkiler"] = dict(VARSAYILAN_YETKILER)
            degisti = True
        if str(u.get("rol")) == "admin":
            for k in VARSAYILAN_YETKILER:
                u["yetkiler"][k] = True

    if degisti:
        kullanici_verisi_kaydet(data)

    return data


def kullanici_verisi_kaydet(data: dict):
    Path(KULLANICI_DOSYASI).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def kullanicilar_dict() -> dict:
    data = kullanici_verisi_yukle()
    return {
        str(u.get("kullanici_adi", "")).strip().lower(): u
        for u in data.get("kullanicilar", [])
        if str(u.get("kullanici_adi", "")).strip()
    }


def yetkileri(u: dict) -> dict:
    y = dict(VARSAYILAN_YETKILER)
    if isinstance(u.get("yetkiler"), dict):
        for k in y:
            y[k] = bool(u["yetkiler"].get(k, y[k]))
    if str(u.get("rol", "user")) == "admin":
        for k in y:
            y[k] = True
    return y


def aktif_kullanici() -> dict | None:
    ka = str(st.session_state.get("giris_kullanici_adi", "")).lower()
    if not ka:
        return None
    return kullanicilar_dict().get(ka)


def yetki_var(key: str) -> bool:
    u = aktif_kullanici()
    if not u:
        return False
    return bool(yetkileri(u).get(key, False))


def giris_yap(kullanici_adi: str, sifre: str):
    ka = str(kullanici_adi or "").strip().lower()
    u = kullanicilar_dict().get(ka)
    if not u:
        return False, "Kullanıcı bulunamadı."

    if not bool(u.get("aktif", True)):
        return False, "Bu kullanıcı pasif."

    if u.get("sifre_hash") != sifre_hash(sifre):
        return False, "Şifre yanlış."

    if not yetkileri(u).get("siteye_giris", False):
        return False, "Bu kullanıcının giriş yetkisi kapalı."

    st.session_state["giris_ok"] = True
    st.session_state["giris_kullanici"] = str(u.get("ad") or u.get("kullanici_adi"))
    st.session_state["giris_kullanici_adi"] = ka
    st.session_state["giris_rol"] = str(u.get("rol", "user"))
    return True, ""


def kayit_ol(kullanici_adi: str, ad: str, sifre: str, sifre2: str):
    ka = str(kullanici_adi or "").strip()
    ad = str(ad or "").strip()

    if len(ka) < 3:
        return False, "Kullanıcı adı en az 3 karakter olmalı."
    if len(str(sifre or "")) < 6:
        return False, "Şifre en az 6 karakter olmalı."
    if sifre != sifre2:
        return False, "Şifreler eşleşmiyor."

    data = kullanici_verisi_yukle()
    if ka.lower() in kullanicilar_dict():
        return False, "Bu kullanıcı adı zaten var."

    data["kullanicilar"].append(
        {
            "kullanici_adi": ka,
            "sifre_hash": sifre_hash(sifre),
            "ad": ad or ka,
            "rol": "user",
            "aktif": True,
            "kayit_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "yetkiler": dict(VARSAYILAN_YETKILER),
        }
    )
    kullanici_verisi_kaydet(data)
    return True, "Kayıt tamamlandı. Giriş yapabilirsin."


def oturum_queryden_yukle():
    if st.session_state.get("giris_ok"):
        return

    ka = qp_get("u")
    tok = qp_get("oturum")
    if not ka or not tok:
        return

    u = kullanicilar_dict().get(ka.lower())
    if not u:
        return

    if token_uret(ka.lower(), u.get("sifre_hash", "")) == tok and bool(u.get("aktif", True)):
        st.session_state["giris_ok"] = True
        st.session_state["giris_kullanici"] = str(u.get("ad") or u.get("kullanici_adi"))
        st.session_state["giris_kullanici_adi"] = ka.lower()
        st.session_state["giris_rol"] = str(u.get("rol", "user"))


# =========================================================
# VERI
# =========================================================

def mevcut_csvler():
    found = []
    for f in CSV_ONCELIKLI_DOSYALAR:
        if Path(f).exists():
            found.append(f)
    for f in sorted(glob.glob("*.csv")):
        if f not in found:
            found.append(f)
    return found


def csv_sec():
    files = mevcut_csvler()
    return files[0] if files else ""


@st.cache_data(show_spinner=False)
def csv_oku(path: str, mtime: float):
    if not path or not Path(path).exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        try:
            return pd.read_csv(path, encoding="cp1254")
        except Exception:
            return pd.DataFrame()


def ensure_cols(df: pd.DataFrame):
    cols = [
        "ihale_id", "ihale_no", "ihale_tipi", "oim", "obm", "cografi_bolge", "il",
        "parti_no", "urun_adi", "urun_turu", "agac_turu", "sinif", "boy_kodu",
        "cap_kodu", "parti_durum", "miktar_m3_hesap", "muhammen_birim_fiyat",
        "teminat_tutari", "toplam_muhammen_hesap", "kaynak_link", "kayit_tarihi",
        "guncelleme_id",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def hazirla(df: pd.DataFrame):
    df = df.copy()
    df = ensure_cols(df)

    for c in [
        "miktar_m3_hesap", "muhammen_birim_fiyat", "toplam_muhammen_hesap",
        "teminat_tutari", "parti_no", "ihale_no", "ihale_id",
    ]:
        df[c] = to_num(df[c])

    for c in df.columns:
        if c not in [
            "miktar_m3_hesap", "muhammen_birim_fiyat", "toplam_muhammen_hesap",
            "teminat_tutari", "parti_no", "ihale_no", "ihale_id",
        ]:
            df[c] = df[c].fillna("").astype(str)

    df["puan_kategorisi"] = (
        df["agac_turu"].replace("", "Genel").astype(str).str.strip() + " " +
        df["urun_turu"].replace("", "Ürün").astype(str).str.strip()
    ).str.strip()

    df["firsat_puani"] = 50.0

    for _, idx in df.groupby("puan_kategorisi").groups.items():
        g = df.loc[idx]
        fiyat = g["muhammen_birim_fiyat"]
        miktar = g["miktar_m3_hesap"]

        fiyat_score = pd.Series(50, index=g.index, dtype=float)
        miktar_score = pd.Series(50, index=g.index, dtype=float)

        if fiyat.notna().sum() > 1 and fiyat.max() != fiyat.min():
            fiyat_score = 100 - ((fiyat - fiyat.min()) / (fiyat.max() - fiyat.min()) * 100)

        if miktar.notna().sum() > 1 and miktar.max() != miktar.min():
            miktar_score = ((miktar - miktar.min()) / (miktar.max() - miktar.min()) * 100)

        kalite = pd.Series(50, index=g.index, dtype=float)
        kalite += g["sinif"].str.contains("1", case=False, na=False).astype(int) * 15
        kalite += g["boy_kodu"].str.contains("uzun|orta", case=False, na=False).astype(int) * 8
        kalite += g["cap_kodu"].str.contains("kalın|ince", case=False, na=False).astype(int) * 5

        df.loc[idx, "firsat_puani"] = (
            fiyat_score * 0.55 + miktar_score * 0.25 + kalite.clip(0, 100) * 0.20
        ).round(0)

    df["firsat_puani"] = df["firsat_puani"].fillna(50).clip(0, 100).astype(int)

    return df


# =========================================================
# UI YARDIMCI
# =========================================================

def hero():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-head">
                <div>
                    <div class="hero-title">Depo Radarı</div>
                    <p class="hero-sub">Türkiye geneli ihale, parti, fiyat ve fırsat takibini modern bir panel yapısında gösteren kontrol ekranı.</p>
                </div>
                <div class="hero-pill">● Yeşil Panel</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-title">{h(title)}</div>
            <div class="section-sub">{h(sub)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def login_ekrani():
    hero()
    a, b, c = st.columns([1, 1.2, 1])
    with b:
        g_tab, k_tab = st.tabs(["Giriş yap", "Kayıt ol"])

        with g_tab:
            with st.form("giris_formu"):
                ka = st.text_input("Kullanıcı adı")
                sifre = st.text_input("Şifre", type="password")
                hatirla = st.checkbox("Beni hatırla", value=True)
                ok = st.form_submit_button("Giriş yap", use_container_width=True)

            if ok:
                basarili, mesaj = giris_yap(ka, sifre)
                if basarili:
                    if hatirla:
                        u = kullanicilar_dict()[ka.strip().lower()]
                        qp_set(
                            u=ka.strip().lower(),
                            oturum=token_uret(ka.strip().lower(), u.get("sifre_hash", "")),
                        )
                    st.success("Giriş başarılı.")
                    st.rerun()
                else:
                    st.error(mesaj)

        with k_tab:
            with st.form("kayit_formu"):
                ad = st.text_input("Ad / firma adı")
                yeni_ka = st.text_input("Yeni kullanıcı adı")
                s1 = st.text_input("Şifre", type="password")
                s2 = st.text_input("Şifre tekrar", type="password")
                kayit = st.form_submit_button("Kayıt ol", use_container_width=True)
            if kayit:
                basarili, mesaj = kayit_ol(yeni_ka, ad, s1, s2)
                if basarili:
                    st.success(mesaj)
                else:
                    st.error(mesaj)

    st.stop()


def giris_zorunlu():
    oturum_queryden_yukle()
    if not st.session_state.get("giris_ok"):
        login_ekrani()


def sidebar_oturum():
    st.sidebar.markdown(
        f"""
        <div class="side-card green">
            <div class="side-title">👤 Oturum</div>
            <div class="side-sub">{h(st.session_state.get("giris_kullanici", "Kullanıcı"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("giris_rol") == "admin":
        st.sidebar.caption("Yetki: Yönetici")
        if st.sidebar.button("👥 Kullanıcı panelini aç", key="admin_open"):
            qp_set(admin="1")
            st.rerun()

    if st.sidebar.button("Çıkış yap"):
        for k in ["giris_ok", "giris_kullanici", "giris_kullanici_adi", "giris_rol"]:
            st.session_state.pop(k, None)
        qp_set(u=None, oturum=None, admin=None)
        st.rerun()


def menu():
    opts = [
        ("🏠", "Ana Sayfa"),
        ("🔎", "İhaleler"),
        ("⭐", "Fırsatlar"),
        ("📊", "Analiz"),
        ("🆕", "Yeni Kayıtlar"),
        ("📘", "Kılavuz"),
    ]

    if "sayfa" not in st.session_state:
        st.session_state["sayfa"] = "🏠 Ana Sayfa"

    st.sidebar.markdown(
        """
        <div class="side-card">
            <div class="side-title">🧭 Ana Menü</div>
            <div class="side-sub">Dashboard bölümleri bağımsız kartlar halinde çalışır.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for i, (ico, name) in enumerate(opts):
        val = f"{ico} {name}"
        aktif = st.session_state["sayfa"] == val
        label = f"✅ {ico} {name}" if aktif else f"{ico} {name}"
        if st.sidebar.button(label, key=f"menu_{i}", type="primary" if aktif else "secondary"):
            st.session_state["sayfa"] = val
            st.rerun()

    return st.session_state["sayfa"]


def urun_class(urun):
    u = str(urun or "").lower()
    if "tomruk" in u:
        return "product-tomruk"
    if "maden" in u:
        return "product-maden"
    if "kağıt" in u or "kagit" in u:
        return "product-kagitlik"
    if "sanayi" in u:
        return "product-sanayi"
    if "dikili" in u:
        return "product-dikili"
    return ""


def secenek(df, kolon):
    if kolon not in df.columns:
        return ["Tümü"]
    vals = sorted([
        x for x in df[kolon].dropna().astype(str).str.strip().unique().tolist()
        if x and x.lower() != "nan"
    ])
    return ["Tümü"] + vals


def genel_arama(df, q):
    q = str(q or "").strip()
    if not q:
        return df

    cols = [
        "parti_no", "ihale_no", "ihale_id", "urun_adi", "urun_turu", "agac_turu",
        "oim", "obm", "cografi_bolge", "il", "sinif", "boy_kodu", "cap_kodu",
    ]
    mask = pd.Series(False, index=df.index)
    for c in cols:
        if c in df.columns:
            mask = mask | df[c].astype(str).str.contains(q, case=False, na=False)
    return df[mask]


def filtrele(df):
    st.sidebar.markdown(
        """
        <div class="side-card">
            <div class="side-title">🔎 Filtreler</div>
            <div class="side-sub">Önce bölge seç. Sonra il, OBM ve OİM kademeli açılır.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Filtreleri temizle", key="clear_filters"):
        for k in list(st.session_state.keys()):
            if k.startswith("filtre_"):
                st.session_state.pop(k, None)
        st.rerun()

    q = st.sidebar.text_input("Genel arama", placeholder="Parti no, ihale no, Karaçam, tomruk...", key="filtre_ara")
    sonuc = genel_arama(df, q)

    bolge = st.sidebar.selectbox("Coğrafi Bölge", secenek(sonuc, "cografi_bolge"), key="filtre_bolge")
    if bolge != "Tümü":
        sonuc = sonuc[sonuc["cografi_bolge"] == bolge]

        il = st.sidebar.selectbox("İl", secenek(sonuc, "il"), key="filtre_il")
        if il != "Tümü":
            sonuc = sonuc[sonuc["il"] == il]

            obm = st.sidebar.selectbox("OBM", secenek(sonuc, "obm"), key="filtre_obm")
            if obm != "Tümü":
                sonuc = sonuc[sonuc["obm"] == obm]

                oim = st.sidebar.selectbox("OİM", secenek(sonuc, "oim"), key="filtre_oim")
                if oim != "Tümü":
                    sonuc = sonuc[sonuc["oim"] == oim]
    else:
        st.sidebar.info("Detay filtreleri açmak için önce bölge seç.")

    if bolge != "Tümü":
        urun = st.sidebar.selectbox("Ürün Türü", secenek(sonuc, "urun_turu"), key="filtre_urun")
        if urun != "Tümü":
            sonuc = sonuc[sonuc["urun_turu"] == urun]

        agac = st.sidebar.selectbox("Ağaç Türü", secenek(sonuc, "agac_turu"), key="filtre_agac")
        if agac != "Tümü":
            sonuc = sonuc[sonuc["agac_turu"] == agac]

        sinif = st.sidebar.selectbox("Sınıf", secenek(sonuc, "sinif"), key="filtre_sinif")
        if sinif != "Tümü":
            sonuc = sonuc[sonuc["sinif"] == sinif]

        boy = st.sidebar.selectbox("Boy Kodu", secenek(sonuc, "boy_kodu"), key="filtre_boy")
        if boy != "Tümü":
            sonuc = sonuc[sonuc["boy_kodu"] == boy]

        cap = st.sidebar.selectbox("Çap Kodu", secenek(sonuc, "cap_kodu"), key="filtre_cap")
        if cap != "Tümü":
            sonuc = sonuc[sonuc["cap_kodu"] == cap]

    if not sonuc.empty and sonuc["muhammen_birim_fiyat"].notna().any():
        min_f = int(sonuc["muhammen_birim_fiyat"].min())
        max_f = int(sonuc["muhammen_birim_fiyat"].max())
        if min_f != max_f:
            ar = st.sidebar.slider("Birim fiyat", min_f, max_f, (min_f, max_f), step=100, key="filtre_fiyat")
            sonuc = sonuc[(sonuc["muhammen_birim_fiyat"] >= ar[0]) & (sonuc["muhammen_birim_fiyat"] <= ar[1])]

    min_p, max_p = 0, 100
    puan = st.sidebar.slider("Fırsat puanı", min_p, max_p, (min_p, max_p), step=1, key="filtre_puan")
    sonuc = sonuc[(sonuc["firsat_puani"] >= puan[0]) & (sonuc["firsat_puani"] <= puan[1])]

    sort = st.sidebar.selectbox(
        "Sıralama",
        ["Fırsat puanı yüksek", "En ucuz fiyat", "En yüksek miktar", "Parti no artan"],
        key="filtre_sort",
    )
    if not sonuc.empty:
        if sort == "Fırsat puanı yüksek":
            sonuc = sonuc.sort_values(["firsat_puani", "muhammen_birim_fiyat"], ascending=[False, True])
        elif sort == "En ucuz fiyat":
            sonuc = sonuc.sort_values("muhammen_birim_fiyat", ascending=True)
        elif sort == "En yüksek miktar":
            sonuc = sonuc.sort_values("miktar_m3_hesap", ascending=False)
        elif sort == "Parti no artan":
            sonuc = sonuc.sort_values("parti_no", ascending=True)

    return sonuc


# =========================================================
# SAYFA BILESENLERI
# =========================================================

def ozet_kartlari(df):
    toplam = len(df)
    ihale = df["ihale_no"].dropna().nunique() if "ihale_no" in df else 0
    ort_fiyat = df["muhammen_birim_fiyat"].dropna().mean() if "muhammen_birim_fiyat" in df else 0
    toplam_m3 = df["miktar_m3_hesap"].dropna().sum() if "miktar_m3_hesap" in df else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kayıt", f"{toplam:,}".replace(",", "."))
    c2.metric("İhale", f"{ihale:,}".replace(",", "."))
    c3.metric("Ort. fiyat", fmt_tl(ort_fiyat))
    c4.metric("Toplam miktar", fmt_m3(toplam_m3))


def firsat_panolar(df, limit=9):
    if df.empty:
        st.info("Kayıt yok.")
        return

    cols = st.columns(3)
    i = 0
    for urun, g in df.groupby("urun_turu", dropna=False):
        if str(urun).strip() == "":
            continue
        en = g.sort_values(["firsat_puani", "muhammen_birim_fiyat"], ascending=[False, True]).head(1)
        if en.empty:
            continue
        r = en.iloc[0]
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="data-card {urun_class(urun)}">
                    <div class="data-card-title">{h(urun)}</div>
                    <div class="data-card-main">{h(r.get("agac_turu", ""))} · {fmt_tl(r.get("muhammen_birim_fiyat"))}</div>
                    <div class="data-card-sub">Parti {h(int(r.get("parti_no")) if pd.notna(r.get("parti_no")) else "-")} · Puan {h(r.get("firsat_puani"))} · {h(r.get("oim", ""))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        i += 1
        if i >= limit:
            break


def sonuc_karti(r):
    parti = int(r["parti_no"]) if pd.notna(r.get("parti_no")) else "-"
    ihale = int(r["ihale_no"]) if pd.notna(r.get("ihale_no")) else "-"
    link = str(r.get("kaynak_link", "") or "")

    st.markdown(
        f"""
        <div class="result-card {urun_class(r.get("urun_turu"))}">
            <div class="result-title">Parti {h(parti)} · {h(r.get("urun_adi", ""))}</div>
            <span class="pill green">Puan {h(r.get("firsat_puani", "-"))}</span>
            <span class="pill">{h(r.get("agac_turu", ""))}</span>
            <span class="pill">{h(r.get("urun_turu", ""))}</span>
            <span class="pill">{h(r.get("sinif", ""))}</span>
            <div class="result-price">{fmt_tl(r.get("muhammen_birim_fiyat"))}</div>
            <div class="result-mini">
                İhale: {h(ihale)} · OİM: {h(r.get("oim", ""))} · OBM: {h(r.get("obm", ""))}<br>
                Bölge: {h(r.get("cografi_bolge", ""))} · Miktar: {fmt_m3(r.get("miktar_m3_hesap"))} · Boy: {h(r.get("boy_kodu", ""))} · Çap: {h(r.get("cap_kodu", ""))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if link:
        st.link_button("Kaynak link", link)


def tablo_goster(df):
    show_cols = [
        "ihale_no", "parti_no", "urun_adi", "urun_turu", "agac_turu", "sinif",
        "boy_kodu", "cap_kodu", "oim", "obm", "cografi_bolge",
        "miktar_m3_hesap", "muhammen_birim_fiyat", "firsat_puani", "kaynak_link"
    ]
    show_cols = [c for c in show_cols if c in df.columns]
    st.dataframe(df[show_cols], use_container_width=True, hide_index=True)


def analiz_goster(df):
    if not yetki_var("analiz"):
        st.warning("Bu kullanıcı için analiz yetkisi kapalı.")
        return
    if df.empty:
        st.info("Analiz için kayıt yok.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="data-card"><div class="data-card-title">Ürün türüne göre ortalama fiyat</div></div>', unsafe_allow_html=True)
        st.bar_chart(df.groupby("urun_turu")["muhammen_birim_fiyat"].mean().dropna())
    with c2:
        st.markdown('<div class="data-card"><div class="data-card-title">Bölgeye göre kayıt sayısı</div></div>', unsafe_allow_html=True)
        st.bar_chart(df.groupby("cografi_bolge")["parti_no"].count())

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="data-card"><div class="data-card-title">OİM bazında kayıt sayısı</div></div>', unsafe_allow_html=True)
        st.bar_chart(df.groupby("oim")["parti_no"].count().sort_values(ascending=False).head(12))
    with c4:
        st.markdown('<div class="data-card"><div class="data-card-title">Ağaç türüne göre ortalama puan</div></div>', unsafe_allow_html=True)
        st.bar_chart(df.groupby("agac_turu")["firsat_puani"].mean().dropna())


def detay_paneli(df):
    if df.empty:
        return

    st.subheader("Detaylı kayıt incele")
    options = []
    for idx, r in df.head(300).iterrows():
        parti = int(r["parti_no"]) if pd.notna(r.get("parti_no")) else "-"
        ihale = int(r["ihale_no"]) if pd.notna(r.get("ihale_no")) else "-"
        options.append((idx, f"Parti {parti} · İhale {ihale} · {r.get('urun_adi', '')}"))

    sec = st.selectbox("Detay aç", options, format_func=lambda x: x[1])
    r = df.loc[sec[0]]

    rows = [
        ("İhale No", int(r["ihale_no"]) if pd.notna(r.get("ihale_no")) else "-"),
        ("Parti No", int(r["parti_no"]) if pd.notna(r.get("parti_no")) else "-"),
        ("Ürün", r.get("urun_adi", "")),
        ("Ürün Türü", r.get("urun_turu", "")),
        ("Ağaç Türü", r.get("agac_turu", "")),
        ("Sınıf / Boy / Çap", f"{r.get('sinif', '')} / {r.get('boy_kodu', '')} / {r.get('cap_kodu', '')}"),
        ("OİM / OBM", f"{r.get('oim', '')} / {r.get('obm', '')}"),
        ("Bölge", r.get("cografi_bolge", "")),
        ("Miktar", fmt_m3(r.get("miktar_m3_hesap"))),
        ("Birim Fiyat", fmt_tl(r.get("muhammen_birim_fiyat"))),
        ("Fırsat Puanı", r.get("firsat_puani", "")),
    ]
    html_rows = "".join(
        f'<div class="detail-row"><div class="detail-key">{h(k)}</div><div class="detail-val">{h(v)}</div></div>'
        for k, v in rows
    )
    st.markdown(f'<div class="detail-box">{html_rows}</div>', unsafe_allow_html=True)

    link = str(r.get("kaynak_link", "") or "")
    if link:
        st.link_button("Kaynak link", link)


def csv_yukleme_alani():
    with st.expander("📁 CSV yükleme / veri değiştirme", expanded=False):
        if not yetki_var("csv_yukleme"):
            st.warning("Bu kullanıcı için CSV yükleme yetkisi kapalı.")
            return None
        uploaded = st.file_uploader("Farklı CSV yükle", type=["csv"], key="csv_upload")
        if uploaded is not None:
            st.success(f"Yüklenen CSV aktif: {uploaded.name}")
        return uploaded


# =========================================================
# KULLANICI PANELI
# =========================================================

def kullanici_paneli():
    if st.session_state.get("giris_rol") != "admin":
        st.warning("Bu alan sadece yönetici için açık.")
        return

    section("👥 Kullanıcı Paneli", "Kullanıcı detayları, roller, aktiflik durumu ve yetkiler.")
    if st.button("← Siteye dön"):
        qp_set(admin=None)
        st.rerun()

    data = kullanici_verisi_yukle()
    kullanicilar = data.get("kullanicilar", [])

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam kullanıcı", len(kullanicilar))
    c2.metric("Aktif", sum(1 for u in kullanicilar if u.get("aktif", False)))
    c3.metric("Yönetici", sum(1 for u in kullanicilar if u.get("rol") == "admin"))

    rows = []
    for u in kullanicilar:
        y = yetkileri(u)
        rows.append(
            f"""
            <tr>
                <td>{h(u.get("kullanici_adi"))}</td>
                <td>{h(u.get("ad"))}</td>
                <td>{h(u.get("rol"))}</td>
                <td>{'Evet' if u.get("aktif") else 'Hayır'}</td>
                <td>{'Evet' if y.get("siteye_giris") else 'Hayır'}</td>
                <td>{'Evet' if y.get("csv_yukleme") else 'Hayır'}</td>
                <td>{'Evet' if y.get("analiz") else 'Hayır'}</td>
                <td>{'Evet' if y.get("rapor_indirme") else 'Hayır'}</td>
                <td>{'Evet' if y.get("kullanici_yonetimi") else 'Hayır'}</td>
                <td>{h(u.get("kayit_tarihi"))}</td>
            </tr>
            """
        )

    st.markdown(
        f"""
        <div class="user-table-wrap">
            <table class="user-table">
                <thead>
                    <tr>
                        <th>Kullanıcı adı</th><th>Ad</th><th>Rol</th><th>Aktif</th>
                        <th>Giriş</th><th>CSV</th><th>Analiz</th><th>Rapor</th><th>Yönetim</th><th>Kayıt</th>
                    </tr>
                </thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for i, u in enumerate(list(kullanicilar)):
        y = yetkileri(u)
        ka = str(u.get("kullanici_adi", ""))
        with st.expander(f"{ka} · {u.get('ad', '')} · {u.get('rol', 'user')}", expanded=False):
            st.json({k: v for k, v in u.items() if k != "sifre_hash"})
            a, b, c, d = st.columns(4)
            with a:
                if st.button("Aktif yap", key=f"akt_{i}"):
                    data["kullanicilar"][i]["aktif"] = True
                    kullanici_verisi_kaydet(data)
                    st.rerun()
            with b:
                if st.button("Pasif yap", key=f"pas_{i}"):
                    if ka.lower() != "admin":
                        data["kullanicilar"][i]["aktif"] = False
                        kullanici_verisi_kaydet(data)
                        st.rerun()
            with c:
                yeni_rol = "user" if u.get("rol") == "admin" else "admin"
                if st.button(f"Rol: {yeni_rol}", key=f"rol_{i}"):
                    if ka.lower() != "admin":
                        data["kullanicilar"][i]["rol"] = yeni_rol
                        kullanici_verisi_kaydet(data)
                        st.rerun()
            with d:
                if st.button("Sil", key=f"sil_{i}"):
                    if ka.lower() != "admin":
                        data["kullanicilar"].pop(i)
                        kullanici_verisi_kaydet(data)
                        st.rerun()

            y1, y2, y3 = st.columns(3)
            with y1:
                site = st.checkbox("Siteye giriş", y.get("siteye_giris"), key=f"ysite_{i}")
                csv = st.checkbox("CSV yükleme", y.get("csv_yukleme"), key=f"ycsv_{i}")
            with y2:
                analiz = st.checkbox("Analiz", y.get("analiz"), key=f"yanaliz_{i}")
                rapor = st.checkbox("Rapor indirme", y.get("rapor_indirme"), key=f"yrapor_{i}")
            with y3:
                yonetim = st.checkbox("Kullanıcı yönetimi", y.get("kullanici_yonetimi"), key=f"yyonetim_{i}")

            if st.button("Yetkileri kaydet", key=f"ykaydet_{i}"):
                if ka.lower() == "admin":
                    data["kullanicilar"][i]["yetkiler"] = {k: True for k in VARSAYILAN_YETKILER}
                    data["kullanicilar"][i]["rol"] = "admin"
                    data["kullanicilar"][i]["aktif"] = True
                else:
                    data["kullanicilar"][i]["yetkiler"] = {
                        "siteye_giris": site,
                        "csv_yukleme": csv,
                        "analiz": analiz,
                        "rapor_indirme": rapor,
                        "kullanici_yonetimi": yonetim,
                    }
                kullanici_verisi_kaydet(data)
                st.success("Yetkiler kaydedildi.")
                st.rerun()

            with st.form(f"sifre_form_{i}"):
                yeni = st.text_input("Yeni şifre", type="password")
                kaydet = st.form_submit_button("Şifreyi güncelle")
                if kaydet:
                    if len(yeni) < 6:
                        st.error("Şifre en az 6 karakter olmalı.")
                    else:
                        data["kullanicilar"][i]["sifre_hash"] = sifre_hash(yeni)
                        kullanici_verisi_kaydet(data)
                        st.success("Şifre güncellendi.")
                        st.rerun()

    st.divider()
    st.subheader("Yeni kullanıcı ekle")
    with st.form("admin_add"):
        ad = st.text_input("Ad / firma adı")
        ka = st.text_input("Kullanıcı adı")
        sifre = st.text_input("Şifre", type="password")
        rol = st.selectbox("Rol", ["user", "admin"])
        aktif = st.checkbox("Aktif", value=True)
        ekle = st.form_submit_button("Kullanıcı ekle")
    if ekle:
        ok, msg = kayit_ol(ka, ad, sifre, sifre)
        if ok:
            data = kullanici_verisi_yukle()
            for u in data["kullanicilar"]:
                if u["kullanici_adi"].lower() == ka.lower():
                    u["rol"] = rol
                    u["aktif"] = aktif
                    if rol == "admin":
                        u["yetkiler"] = {k: True for k in VARSAYILAN_YETKILER}
            kullanici_verisi_kaydet(data)
            st.success("Kullanıcı eklendi.")
            st.rerun()
        else:
            st.error(msg)


# =========================================================
# ANA AKIS
# =========================================================

giris_zorunlu()

if qp_get("admin") == "1":
    sidebar_oturum()
    kullanici_paneli()
    st.stop()

sidebar_oturum()
sayfa = menu()

path = csv_sec()
uploaded = st.session_state.get("csv_upload")
if uploaded is not None:
    raw = pd.read_csv(uploaded, encoding="utf-8-sig")
    aktif_csv = getattr(uploaded, "name", "Yüklenen CSV")
else:
    aktif_csv = path
    raw = csv_oku(path, os.path.getmtime(path) if path and Path(path).exists() else 0)

if raw.empty:
    hero()
    st.error("CSV bulunamadı veya okunamadı. GitHub'a CSV yükle ya da alttaki CSV yükleme alanını kullan.")
    csv_yukleme_alani()
    st.stop()

df = hazirla(raw)
sonuc = filtrele(df)

hero()
st.caption(f"Okunan CSV: {aktif_csv}")

if sayfa == "🏠 Ana Sayfa":
    section("Genel Özet", "Öne çıkan metrikler, son güncelleme bilgisi ve fırsat kartları.")
    ozet_kartlari(sonuc)
    st.divider()

    c1, c2 = st.columns([1.15, .85])
    with c1:
        st.subheader("Öne çıkan fırsatlar")
        firsat_panolar(sonuc, limit=6)
    with c2:
        st.subheader("Hızlı detay")
        detay_paneli(sonuc)

elif sayfa == "🔎 İhaleler":
    section("İhaleler", "Filtrelenen kayıtları kart, tablo veya detay görünümünde incele.")
    ozet_kartlari(sonuc)
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Kartlar", "Tablo", "Detay"])
    with tab1:
        if sonuc.empty:
            st.info("Sonuç yok.")
        for _, r in sonuc.head(40).iterrows():
            sonuc_karti(r)
    with tab2:
        tablo_goster(sonuc)
    with tab3:
        detay_paneli(sonuc)

    if yetki_var("rapor_indirme"):
        st.download_button(
            "Filtrelenen sonuçları CSV indir",
            data=sonuc.to_csv(index=False, encoding="utf-8-sig"),
            file_name="depo_radari_filtreli_sonuclar.csv",
            mime="text/csv",
        )
    else:
        st.warning("Bu kullanıcı için rapor indirme yetkisi kapalı.")

elif sayfa == "⭐ Fırsatlar":
    section("Fırsatlar", "Ürün türlerine göre en güçlü kayıtlar ve hızlı fırsat görünümü.")
    ozet_kartlari(sonuc)
    st.divider()
    firsat_panolar(sonuc, limit=12)

elif sayfa == "📊 Analiz":
    section("Analiz", "Ürün, bölge, OİM ve ağaç türlerine göre görsel özet.")
    analiz_goster(sonuc)

elif sayfa == "🆕 Yeni Kayıtlar":
    section("Yeni Kayıtlar", "Son gelen kayıtları ve güncel fırsatları incele.")
    yeni = sonuc.copy()
    if "kayit_tarihi" in yeni.columns:
        yeni = yeni.sort_values("kayit_tarihi", ascending=False)
    for _, r in yeni.head(40).iterrows():
        sonuc_karti(r)

elif sayfa == "📘 Kılavuz":
    section("Kılavuz", "Depo Radarı ekranlarını hızlıca kullanmak için kısa açıklamalar.")
    a, b, c = st.columns(3)
    with a:
        st.markdown(
            """
            <div class="help-card">
                <h3>🔎 Filtreleme</h3>
                <p>Önce bölge seçilir. Sonra il, OBM ve OİM alanları kademeli açılır. Arama kutusuna parti no veya ihale no yazabilirsin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            """
            <div class="help-card">
                <h3>⭐ Fırsat Puanı</h3>
                <p>Puan aynı ürün/ağaç grubu içinde fiyat, miktar ve kalite işaretlerine göre karşılaştırma amaçlı hesaplanır.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            """
            <div class="help-card">
                <h3>👥 Kullanıcılar</h3>
                <p>Admin kullanıcı panelinden giriş, CSV yükleme, analiz ve rapor indirme yetkilerini kullanıcı bazında yönetebilir.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
csv_yukleme_alani()
st.caption("Depo Radarı bağımsız analiz prototipidir. Fırsat puanı karşılaştırma amaçlıdır; kesin alım tavsiyesi değildir.")
