"""
Depo Radarı - Veri Güncelleme v2

Bu sürüm ayarları depo_radari_ayarlar.txt dosyasından okur.
Ayarları büyütürken dikkatli ol:
- Önce küçük test yap.
- REQUEST_DELAY değerini düşük tutma.
- Çok sık güncelleme çalıştırma.

Kullanım:
1) depo_radari_ayarlar.txt dosyasını kontrol et.
2) DEPO_RADARI_PANEL_V2.bat üzerinden veri güncelle.
"""

"""
Depo Radarı - Veri Güncelleme v1

Güvenli kullanım:
- Siteye aşırı istek atmaz.
- Varsayılan olarak veri çıkan 3 ihale bulana kadar en fazla 20 ihale adayını dener.
- Her veri çıkan ihaleden 5 parti çeker.
- Her istek arasında 3 saniye bekler.
- Aynı ihale_id + parti_no daha önce CSV'de varsa tekrar çekmez.
- Çıktı dosyası: depo_radari_tum_ihaleler_guvenli_v3.csv

Ayarları büyütmek istersen aşağıdaki sabitleri yavaş yavaş artır:
MAX_IHALE_WITH_DATA
MAX_CANDIDATE_IHALE
MAX_ISTIF_PER_IHALE
REQUEST_DELAY
"""

"""
Depo Radarı - Güvenli Çoklu İhale Çekici v3
- v2 ile aynı güvenli sınırlar korunur.
- Dikili Ağaç, İbreli ve Yapraklı ürün/ad türleri de ayrıştırılır.
- Çıktı: depo_radari_tum_ihaleler_guvenli_v3.csv
"""

"""
Depo Radarı - Güvenli Çoklu İhale Çekici v2
- En fazla 20 ihale adayını dener.
- Veri çıkan 3 ihale bulunca durur.
- Her veri çıkan ihaleden 5 parti çeker.
- Her istek arasında 3 saniye bekler.
- Aynı çıktı CSV içinde aynı ihale_id + parti_no varsa tekrar çekmez.
"""

import re
import csv
import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

BASE_URL = "https://esatis.ogm.gov.tr"
LISTE_URL = "https://esatis.ogm.gov.tr/ihaleler"

AYAR_DOSYASI = "depo_radari_ayarlar.txt"

def ayarlari_oku():
    """
    depo_radari_ayarlar.txt dosyasını okur.
    Dosya yoksa güvenli varsayılan ayarlar ile oluşturur.
    """
    varsayilan = {
        "MAX_IHALE_WITH_DATA": "3",
        "MAX_CANDIDATE_IHALE": "20",
        "MAX_ISTIF_PER_IHALE": "5",
        "REQUEST_DELAY": "3.0",
        "OUTPUT_CSV": "depo_radari_tum_ihaleler_guvenli_v3.csv",
    }

    path = AYAR_DOSYASI

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Depo Radarı Ayarları\n")
            f.write("# Çok sık ve yüksek değerlerle çalıştırma.\n")
            f.write("# Güvenli başlangıç değerleri aşağıdadır.\n\n")
            for k, v in varsayilan.items():
                f.write(f"{k}={v}\n")

    ayarlar = varsayilan.copy()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key:
                ayarlar[key] = value

    def to_int_or_none(value):
        if str(value).strip().lower() in ["none", "yok", ""]:
            return None
        return int(value)

    def to_float(value):
        return float(str(value).strip().replace(",", "."))

    return {
        "MAX_IHALE_WITH_DATA": to_int_or_none(ayarlar["MAX_IHALE_WITH_DATA"]),
        "MAX_CANDIDATE_IHALE": to_int_or_none(ayarlar["MAX_CANDIDATE_IHALE"]),
        "MAX_ISTIF_PER_IHALE": to_int_or_none(ayarlar["MAX_ISTIF_PER_IHALE"]),
        "REQUEST_DELAY": to_float(ayarlar["REQUEST_DELAY"]),
        "OUTPUT_CSV": ayarlar["OUTPUT_CSV"],
    }


# Ayar dosyasından oku
_OKUNAN_AYARLAR = ayarlari_oku()
MAX_IHALE_WITH_DATA = _OKUNAN_AYARLAR["MAX_IHALE_WITH_DATA"]
MAX_CANDIDATE_IHALE = _OKUNAN_AYARLAR["MAX_CANDIDATE_IHALE"]
MAX_ISTIF_PER_IHALE = _OKUNAN_AYARLAR["MAX_ISTIF_PER_IHALE"]
REQUEST_DELAY = _OKUNAN_AYARLAR["REQUEST_DELAY"]
OUTPUT_CSV = _OKUNAN_AYARLAR["OUTPUT_CSV"]

LOG_DOSYASI = "depo_radari_log.txt"
OZET_DOSYASI = "depo_radari_ozet.json"


def simdi_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_yaz(mesaj):
    satir = f"[{simdi_str()}] {mesaj}"
    print(satir)
    try:
        with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
            f.write(satir + "\n")
    except Exception:
        pass


def csv_kayit_sayisi(dosya):
    if not os.path.exists(dosya):
        return 0

    try:
        with open(dosya, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return sum(1 for _ in reader)
    except Exception:
        return 0


def ozet_kaydet(ozet):
    try:
        with open(OZET_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(ozet, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Özet kaydedilemedi:", e)


def ozet_oku():
    if not os.path.exists(OZET_DOSYASI):
        return {}

    try:
        with open(OZET_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}



# Güvenli test ayarları

headers = {
    "User-Agent": "Mozilla/5.0 DepoRadariGuvenli/1.0"
}

session = requests.Session()
session.headers.update(headers)


def temizle(text):
    return re.sub(r"\s+", " ", text or "").strip()


def hucre_degeri(cell):
    parcalar = []

    text = temizle(cell.get_text(" ", strip=True))
    if text:
        parcalar.append(text)

    for tag in cell.find_all(["input", "textarea"]):
        value = temizle(tag.get("value", "") or tag.get_text(" ", strip=True))
        if value:
            parcalar.append(value)

    for option in cell.find_all("option"):
        if option.has_attr("selected"):
            value = temizle(option.get_text(" ", strip=True) or option.get("value", ""))
            if value:
                parcalar.append(value)

    for attr, value in cell.attrs.items():
        if attr in ["title", "aria-label", "data-order", "data-search", "data-sort"] or attr.startswith("data-"):
            if isinstance(value, list):
                value = " ".join(value)
            value = temizle(str(value))
            if value:
                parcalar.append(value)

    for tag in cell.find_all(True):
        for attr, value in tag.attrs.items():
            if attr in ["title", "aria-label", "data-order", "data-search", "data-sort"] or attr.startswith("data-"):
                if isinstance(value, list):
                    value = " ".join(value)
                value = temizle(str(value))
                if value:
                    parcalar.append(value)

    sonuc = []
    for p in parcalar:
        if p and p not in sonuc:
            sonuc.append(p)

    return temizle(" ".join(sonuc))


def tablo_satirlari(table):
    satirlar = []

    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue

        values = [hucre_degeri(cell) for cell in cells]

        if any(v != "" for v in values):
            satirlar.append(values)

    return satirlar


def sayfa_oku(url):
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def turk_sayi(value):
    if value is None:
        return None

    s = str(value)
    s = s.replace("TL", "").replace("₺", "")
    s = s.replace("m³", "").replace("m3", "")
    s = s.replace("%", "")
    s = re.sub(r"[^\d,.\-]", "", s)

    if not s:
        return None

    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return None


def yuzde_oran(value):
    sayi = turk_sayi(value)
    if sayi is None:
        return None

    if sayi > 1:
        return sayi / 100

    return sayi


def satiri_dict_yap(headers_row, data_row):
    d = {}

    for i, h in enumerate(headers_row):
        h = temizle(h)
        if not h:
            h = f"kolon_{i + 1}"

        d[h] = data_row[i] if i < len(data_row) else ""

    return d


def ihale_id_bul(url):
    m = re.search(r"/ihaleler/(\d+)/partiler", url)
    return m.group(1) if m else ""


def urun_parcala(urun_adi):
    agac_turleri = [
        "Karaçam", "Sarıçam", "Göknar", "Ladin", "Kayın", "Meşe",
        "Kızılçam", "Sedir", "Kavak", "Kestane", "Gürgen", "Çınar",
        "İbreli", "Yapraklı"
    ]

    urun_turleri = [
        "Maden Direği", "Maden Direk", "Dikili Ağaç", "Tomruk", "Kağıtlık Odun", "Lif Yonga",
        "Sanayi Odunu", "Yakacak Odun", "Tel Direği", "Tel Direk", "Sırık"
    ]

    lower = urun_adi.lower()

    agac_turu = ""
    for agac in agac_turleri:
        if agac.lower() in lower:
            agac_turu = agac
            break

    urun_turu = ""
    for urun in urun_turleri:
        if urun.lower() in lower:
            if urun == "Maden Direk":
                urun_turu = "Maden Direği"
            elif urun == "Tel Direk":
                urun_turu = "Tel Direği"
            else:
                urun_turu = urun
            break

    sinif = ""
    m = re.search(r"(\d+)\s*\.?\s*sn", lower)
    if m:
        sinif = m.group(1) + ". Sınıf"

    kod_text = urun_adi.replace("İ", "I").replace("ı", "i").lower()
    tokens = re.split(r"[\s.]+", kod_text)

    boy_kodu = ""
    if "nb" in tokens:
        boy_kodu = "Normal Boy"
    elif "kb" in tokens:
        boy_kodu = "Kısa Boy"
    elif "ub" in tokens:
        boy_kodu = "Uzun Boy"

    cap_kodu = ""
    if "in" in tokens:
        cap_kodu = "İnce"
    elif "kl" in tokens:
        cap_kodu = "Kalın"

    return {
        "agac_turu": agac_turu,
        "urun_turu": urun_turu,
        "sinif": sinif,
        "boy_kodu": boy_kodu,
        "cap_kodu": cap_kodu
    }


def obm_bolge_bul(obm):
    obm_upper = (obm or "").upper()

    harita = {
        "BURSA": "Marmara",
        "SAKARYA": "Marmara",
        "İSTANBUL": "Marmara",
        "ISTANBUL": "Marmara",
        "BALIKESİR": "Marmara",
        "BALIKESIR": "Marmara",
        "ÇANAKKALE": "Marmara",

        "İZMİR": "Ege",
        "IZMIR": "Ege",
        "MUĞLA": "Ege",
        "MUGLA": "Ege",
        "DENİZLİ": "Ege",
        "DENIZLI": "Ege",
        "KÜTAHYA": "Ege",
        "KUTAHYA": "Ege",
        "AYDIN": "Ege",

        "KASTAMONU": "Karadeniz",
        "BOLU": "Karadeniz",
        "ZONGULDAK": "Karadeniz",
        "AMASYA": "Karadeniz",
        "SAMSUN": "Karadeniz",
        "GİRESUN": "Karadeniz",
        "GIRESUN": "Karadeniz",
        "TRABZON": "Karadeniz",
        "ARTVİN": "Karadeniz",
        "ARTVIN": "Karadeniz",

        "ANTALYA": "Akdeniz",
        "MERSİN": "Akdeniz",
        "MERSIN": "Akdeniz",
        "ADANA": "Akdeniz",
        "KAHRAMANMARAŞ": "Akdeniz",
        "KAHRAMANMARAS": "Akdeniz",
        "ISPARTA": "Akdeniz",

        "ANKARA": "İç Anadolu",
        "KONYA": "İç Anadolu",
        "KAYSERİ": "İç Anadolu",
        "KAYSERI": "İç Anadolu",
        "ESKİŞEHİR": "İç Anadolu",
        "ESKISEHIR": "İç Anadolu",

        "ERZURUM": "Doğu Anadolu",
        "ELAZIĞ": "Doğu Anadolu",
        "ELAZIG": "Doğu Anadolu",
        "MALATYA": "Doğu Anadolu",

        "ŞANLIURFA": "Güneydoğu Anadolu",
        "SANLIURFA": "Güneydoğu Anadolu",
        "DİYARBAKIR": "Güneydoğu Anadolu",
        "DIYARBAKIR": "Güneydoğu Anadolu",
    }

    for anahtar, bolge in harita.items():
        if anahtar in obm_upper:
            return bolge

    return ""


def ihale_listesi_cek():
    html = sayfa_oku(LISTE_URL)
    soup = BeautifulSoup(html, "html.parser")

    ihaleler = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if re.search(r"/ihaleler/\d+/partiler", href):
            link = urljoin(BASE_URL, href)
            ihale_id = ihale_id_bul(link)

            parent = a.find_parent(["tr", "div", "li", "td"])
            baslik = temizle(parent.get_text(" ", strip=True)) if parent else temizle(a.get_text(" ", strip=True))

            if not baslik:
                baslik = temizle(a.get_text(" ", strip=True))

            ihaleler.append({
                "ihale_id": ihale_id,
                "baslik": baslik,
                "partiler_link": link
            })

    unique = {}
    for ihale in ihaleler:
        if ihale["ihale_id"]:
            unique[ihale["ihale_id"]] = ihale

    sonuc = list(unique.values())

    return sonuc


def partiler_bilgi_cek(soup, partiler_url="", liste_baslik=""):
    text = temizle(soup.get_text(" ", strip=True))
    tum_text = temizle((liste_baslik or "") + " " + text)

    bilgi = {
        "ihale_id": ihale_id_bul(partiler_url),
        "ihale_tipi": "",
        "oim": "",
        "obm": "",
        "ihale_no": "",
        "teminat_orani_raw": "",
        "teminat_orani": None
    }

    # Başlıktan yakala:
    # TOSYA OİM (KASTAMONU OBM) 3952 No'lu İhale
    m = re.search(
        r"([A-Za-zÇĞİÖŞÜçğıöşü\s]+?O[İI]M)\s*\(([A-Za-zÇĞİÖŞÜçğıöşü\s]+?OBM)\)\s*(\d+)\s*No",
        tum_text,
        re.IGNORECASE
    )

    if m:
        bilgi["oim"] = temizle(m.group(1)).upper()
        bilgi["obm"] = temizle(m.group(2)).upper()
        bilgi["ihale_no"] = temizle(m.group(3))

    for table in soup.find_all("table"):
        vals = [temizle(x) for x in table.stripped_strings if temizle(x)]
        joined = " ".join(vals).lower()

        if "ihale tipi" in joined and "birim" in joined and "ihale no" in joined:
            if len(vals) >= 6:
                ihale_tipi_aday = vals[3]
                oim_aday = vals[4]
                ihale_no_aday = vals[5]

                if ihale_tipi_aday:
                    bilgi["ihale_tipi"] = ihale_tipi_aday

                if "OİM" in oim_aday.upper() or "OIM" in oim_aday.upper():
                    bilgi["oim"] = oim_aday.upper()

                if ihale_no_aday.isdigit():
                    bilgi["ihale_no"] = ihale_no_aday

        if "teminat oranı" in joined:
            for item in vals:
                if "%" in item:
                    bilgi["teminat_orani_raw"] = item
                    bilgi["teminat_orani"] = yuzde_oran(item)
                    break

    return bilgi


def istif_linkleri_sayfadan_bul(soup, ihale_id):
    linkler = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if re.search(r"/ihaleler/\d+/partiler/\d+/istifler", href):
            full_url = urljoin(BASE_URL, href)

            m = re.search(r"/partiler/(\d+)/istifler", href)
            parti_no = m.group(1) if m else ""

            linkler.append({
                "parti_no": parti_no,
                "link": full_url
            })

    # Link yoksa düz metinden parti numaralarını yakala
    text = temizle(soup.get_text(" ", strip=True))

    for m in re.finditer(r"(\d+)\s+No['’]lu\s+Parti", text, re.IGNORECASE):
        parti_no = m.group(1)

        if ihale_id:
            full_url = f"{BASE_URL}/ihaleler/{ihale_id}/partiler/{parti_no}/istifler"
            linkler.append({
                "parti_no": parti_no,
                "link": full_url
            })

    unique = {}
    for item in linkler:
        if item["parti_no"]:
            unique[item["parti_no"]] = item

    sonuc = list(unique.values())
    sonuc.sort(key=lambda x: int(x["parti_no"]) if str(x["parti_no"]).isdigit() else 0)
    return sonuc


def istif_linklerini_bul(partiler_url, liste_baslik=""):
    html = sayfa_oku(partiler_url)
    soup = BeautifulSoup(html, "html.parser")

    ihale_bilgi = partiler_bilgi_cek(soup, partiler_url, liste_baslik)
    ihale_id = ihale_bilgi.get("ihale_id", "")

    linkler = istif_linkleri_sayfadan_bul(soup, ihale_id)
    return ihale_bilgi, linkler


def para_adaylari_bul(compact):
    if not compact:
        return []

    unit_index = None
    for i, v in enumerate(compact):
        if "m³" in v or "m3" in v.lower():
            unit_index = i
            break

    if unit_index is not None:
        aday_bolum = compact[unit_index + 1:]
    else:
        aday_bolum = compact[2:]

    adaylar = []

    for v in aday_bolum:
        sayi = turk_sayi(v)
        if sayi is not None and sayi > 100:
            adaylar.append(v)

    return adaylar


def istif_detay_cek(ihale_bilgi, parti_no, istif_url):
    html = sayfa_oku(istif_url)
    soup = BeautifulSoup(html, "html.parser")

    parti_bilgi = {
        "parti_no": parti_no,
        "urun_adi": "",
        "katilimci_sayisi": "",
        "parti_durum": ""
    }

    ozet = {
        "boy": "",
        "adet": "",
        "miktar_birim": "",
        "muhammen_bedel": "",
        "teminat_tutari": "",
        "detay_durum": ""
    }

    for table in soup.find_all("table"):
        rows = tablo_satirlari(table)

        if len(rows) < 2:
            continue

        header_text = " ".join(rows[0]).lower()

        if "parti numarası" in header_text and "ürün adı" in header_text:
            d = satiri_dict_yap(rows[0], rows[1])

            parti_bilgi["parti_no"] = d.get("Parti Numarası", parti_no)
            parti_bilgi["urun_adi"] = d.get("Ürün Adı", "")
            parti_bilgi["katilimci_sayisi"] = d.get("Katılımcı Sayısı", "")
            parti_bilgi["parti_durum"] = d.get("Durum", "")

        if "boy" in header_text and "adet" in header_text and "miktar" in header_text and "muh" in header_text:
            headers_row = rows[0]

            for data_row in rows[1:]:
                compact = [temizle(x) for x in data_row if temizle(x)]

                if len(compact) < 4:
                    continue

                d = satiri_dict_yap(headers_row, data_row)

                boy = d.get("Boy", "") or compact[0]
                adet = d.get("Adet", "") or (compact[1] if len(compact) > 1 else "")
                miktar_birim = d.get("Miktar", "")

                if not miktar_birim:
                    for v in compact:
                        if "m³" in v or "m3" in v.lower():
                            miktar_birim = v
                            break

                muhammen = d.get("Muh. Bedel", "") or d.get("Muhammen Bedel", "")
                teminat = d.get("Teminat Tutarı", "")

                para_adaylari = para_adaylari_bul(compact)

                if not turk_sayi(muhammen) and len(para_adaylari) >= 1:
                    muhammen = para_adaylari[0]

                if not turk_sayi(teminat) and len(para_adaylari) >= 2:
                    teminat = para_adaylari[1]

                durum = d.get("Durum", "")
                if not durum:
                    for v in reversed(compact):
                        v_lower = v.lower()
                        if "satıl" in v_lower or "bekliyor" in v_lower or "açık artırma" in v_lower:
                            durum = v
                            break

                if turk_sayi(muhammen):
                    ozet["boy"] = boy
                    ozet["adet"] = adet
                    ozet["miktar_birim"] = miktar_birim
                    ozet["muhammen_bedel"] = muhammen
                    ozet["teminat_tutari"] = teminat
                    ozet["detay_durum"] = durum
                    break

    urun_ek = urun_parcala(parti_bilgi["urun_adi"])

    muhammen_birim_fiyat = turk_sayi(ozet["muhammen_bedel"])
    teminat_tutari = turk_sayi(ozet["teminat_tutari"])
    teminat_orani = ihale_bilgi.get("teminat_orani")

    miktar_m3_hesap = None
    toplam_muhammen_hesap = None

    if (
        muhammen_birim_fiyat
        and teminat_tutari
        and teminat_orani
        and muhammen_birim_fiyat > 0
        and teminat_orani > 0
    ):
        toplam_muhammen_hesap = teminat_tutari / teminat_orani
        miktar_m3_hesap = toplam_muhammen_hesap / muhammen_birim_fiyat

    obm = ihale_bilgi.get("obm", "")
    cografi_bolge = obm_bolge_bul(obm)

    return {
        "ihale_id": ihale_bilgi.get("ihale_id", ""),
        "ihale_no": ihale_bilgi.get("ihale_no", ""),
        "ihale_tipi": ihale_bilgi.get("ihale_tipi", ""),
        "oim": ihale_bilgi.get("oim", ""),
        "obm": obm,
        "cografi_bolge": cografi_bolge,
        "teminat_orani": ihale_bilgi.get("teminat_orani_raw", ""),

        "parti_no": parti_bilgi["parti_no"],
        "urun_adi": parti_bilgi["urun_adi"],
        "urun_turu": urun_ek["urun_turu"],
        "agac_turu": urun_ek["agac_turu"],
        "sinif": urun_ek["sinif"],
        "boy_kodu": urun_ek["boy_kodu"],
        "cap_kodu": urun_ek["cap_kodu"],

        "katilimci_sayisi": parti_bilgi["katilimci_sayisi"],
        "parti_durum": parti_bilgi["parti_durum"],

        "boy": ozet["boy"],
        "adet": ozet["adet"],
        "miktar_birim": ozet["miktar_birim"],
        "miktar_m3_hesap": round(miktar_m3_hesap, 3) if miktar_m3_hesap else "",
        "muhammen_birim_fiyat": muhammen_birim_fiyat if muhammen_birim_fiyat else "",
        "teminat_tutari": teminat_tutari if teminat_tutari else "",
        "toplam_muhammen_hesap": round(toplam_muhammen_hesap, 2) if toplam_muhammen_hesap else "",
        "detay_durum": ozet["detay_durum"],

        "kaynak_link": istif_url
    }


def mevcut_kayit_anahtarlari():
    anahtarlar = set()

    if not os.path.exists(OUTPUT_CSV):
        return anahtarlar

    try:
        with open(OUTPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row.get("ihale_id", ""), row.get("parti_no", ""))
                if key[0] and key[1]:
                    anahtarlar.add(key)
    except Exception:
        return anahtarlar

    return anahtarlar


def csvye_ekle(kayitlar):
    if not kayitlar:
        return

    alanlar = [
        "ihale_id", "ihale_no", "ihale_tipi", "oim", "obm", "cografi_bolge", "teminat_orani",
        "parti_no", "urun_adi", "urun_turu", "agac_turu",
        "sinif", "boy_kodu", "cap_kodu",
        "katilimci_sayisi", "parti_durum",
        "boy", "adet", "miktar_birim", "miktar_m3_hesap",
        "muhammen_birim_fiyat", "teminat_tutari",
        "toplam_muhammen_hesap", "detay_durum",
        "kaynak_link",
        "kayit_tarihi", "guncelleme_id"
    ]

    dosya_var = os.path.exists(OUTPUT_CSV)

    # Eski CSV'lerde yeni kolonlar yoksa dosyayı güvenli şekilde genişlet.
    if dosya_var:
        try:
            with open(OUTPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                mevcut_alanlar = reader.fieldnames or []
                mevcut_satirlar = list(reader)

            tum_alanlar = []
            for alan in alanlar + mevcut_alanlar:
                if alan not in tum_alanlar:
                    tum_alanlar.append(alan)

            # Header farklıysa mevcut dosyayı yeni kolonlarla baştan yaz.
            if mevcut_alanlar != tum_alanlar:
                with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=tum_alanlar, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(mevcut_satirlar)

                alanlar = tum_alanlar
            else:
                alanlar = mevcut_alanlar

        except Exception as e:
            log_yaz(f"CSV kolon genişletme uyarısı: {e}")

    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")

        if not dosya_var:
            writer.writeheader()

        writer.writerows(kayitlar)


def main():
    baslangic = datetime.now()
    guncelleme_id = baslangic.strftime("%Y%m%d_%H%M%S")
    hata_sayisi = 0
    toplam_yeni = 0
    veri_cikan_ihale_sayisi = 0
    denenen_ihale_sayisi = 0
    csv_once = csv_kayit_sayisi(OUTPUT_CSV)

    log_yaz("Depo Radarı veri güncelleme v4 başladı.")
    log_yaz(f"Güncelleme ID: {guncelleme_id}")
    log_yaz(f"Ayarlar: MAX_IHALE_WITH_DATA={MAX_IHALE_WITH_DATA}, MAX_CANDIDATE_IHALE={MAX_CANDIDATE_IHALE}, MAX_ISTIF_PER_IHALE={MAX_ISTIF_PER_IHALE}, REQUEST_DELAY={REQUEST_DELAY}, OUTPUT_CSV={OUTPUT_CSV}")
    log_yaz(f"Mevcut CSV kayıt sayısı: {csv_once}")
    print("=" * 100)

    try:
        ihaleler = ihale_listesi_cek()
    except Exception as e:
        hata_sayisi += 1
        log_yaz(f"İhale listesi okunamadı: {e}")

        ozet = {
            "son_guncelleme": simdi_str(),
            "guncelleme_id": guncelleme_id,
            "durum": "HATA",
            "hata_mesaji": str(e),
            "denenen_ihale": denenen_ihale_sayisi,
            "veri_cikan_ihale": veri_cikan_ihale_sayisi,
            "yeni_kayit": toplam_yeni,
            "csv_once": csv_once,
            "csv_sonra": csv_kayit_sayisi(OUTPUT_CSV),
            "hata_sayisi": hata_sayisi,
            "output_csv": OUTPUT_CSV,
        }
        ozet_kaydet(ozet)
        return

    log_yaz(f"Bulunan ihale linki: {len(ihaleler)}")

    if MAX_CANDIDATE_IHALE is not None:
        ihaleler = ihaleler[:MAX_CANDIDATE_IHALE]

    log_yaz(f"Denecek ihale adayı: {len(ihaleler)}")
    log_yaz(f"Hedef veri çıkan ihale: {MAX_IHALE_WITH_DATA}")
    print("=" * 100)

    mevcutlar = mevcut_kayit_anahtarlari()
    log_yaz(f"CSV içinde daha önce çekilmiş kayıt: {len(mevcutlar)}")
    print("=" * 100)

    for ihale_index, ihale in enumerate(ihaleler, start=1):
        if veri_cikan_ihale_sayisi >= MAX_IHALE_WITH_DATA:
            log_yaz("Hedef veri çıkan ihale sayısına ulaşıldı, durduruldu.")
            break

        denenen_ihale_sayisi += 1

        print(f"\n[{ihale_index}/{len(ihaleler)}] İhale adayı işleniyor")
        print("ID:", ihale["ihale_id"])
        print("Başlık:", ihale["baslik"][:160])
        print("Link:", ihale["partiler_link"])

        try:
            ihale_bilgi, istif_linkleri = istif_linklerini_bul(
                partiler_url=ihale["partiler_link"],
                liste_baslik=ihale["baslik"]
            )
        except Exception as e:
            hata_sayisi += 1
            log_yaz(f"İhale detay linkleri alınamadı. İhale ID={ihale.get('ihale_id')} Hata={e}")
            time.sleep(REQUEST_DELAY)
            continue

        print("  İhale No:", ihale_bilgi.get("ihale_no"))
        print("  OİM:", ihale_bilgi.get("oim"))
        print("  OBM:", ihale_bilgi.get("obm"))
        print("  Bölge:", obm_bolge_bul(ihale_bilgi.get("obm", "")))
        print("  Bulunan parti/istif:", len(istif_linkleri))

        if not istif_linkleri:
            log_yaz(f"Parti linki bulunamadı, geçildi. İhale ID={ihale.get('ihale_id')}")
            time.sleep(REQUEST_DELAY)
            continue

        if MAX_ISTIF_PER_IHALE is not None:
            istif_linkleri = istif_linkleri[:MAX_ISTIF_PER_IHALE]

        print("  Çekilecek parti:", len(istif_linkleri))

        yeni_kayitlar = []

        for parti_index, item in enumerate(istif_linkleri, start=1):
            key = (ihale_bilgi.get("ihale_id", ""), item.get("parti_no", ""))

            if key in mevcutlar:
                print(f"    [{parti_index}/{len(istif_linkleri)}] Parti {item['parti_no']} zaten var, geçildi.")
                continue

            print(f"    [{parti_index}/{len(istif_linkleri)}] Parti çekiliyor:", item["parti_no"])

            try:
                kayit = istif_detay_cek(
                    ihale_bilgi=ihale_bilgi,
                    parti_no=item["parti_no"],
                    istif_url=item["link"]
                )

                kayit["kayit_tarihi"] = simdi_str()
                kayit["guncelleme_id"] = guncelleme_id

                yeni_kayitlar.append(kayit)
                mevcutlar.add(key)

                print("      Ürün:", kayit["urun_adi"])
                print("      Tür:", kayit["agac_turu"], "-", kayit["urun_turu"])
                print("      Miktar:", kayit["miktar_m3_hesap"], "m³")
                print("      Fiyat:", kayit["muhammen_birim_fiyat"], "TL")

            except Exception as e:
                hata_sayisi += 1
                log_yaz(f"Parti çekme hatası. İhale ID={ihale_bilgi.get('ihale_id')} Parti={item.get('parti_no')} Hata={e}")

            time.sleep(REQUEST_DELAY)

        csvye_ekle(yeni_kayitlar)

        toplam_yeni += len(yeni_kayitlar)

        if len(yeni_kayitlar) > 0:
            veri_cikan_ihale_sayisi += 1

        log_yaz(f"İhale tamamlandı. İhale ID={ihale.get('ihale_id')} yeni kayıt={len(yeni_kayitlar)} veri çıkan ihale={veri_cikan_ihale_sayisi}/{MAX_IHALE_WITH_DATA}")
        print("  CSV güncellendi:", OUTPUT_CSV)

        time.sleep(REQUEST_DELAY)

    bitis = datetime.now()
    sure_saniye = round((bitis - baslangic).total_seconds(), 1)
    csv_sonra = csv_kayit_sayisi(OUTPUT_CSV)

    ozet = {
        "son_guncelleme": simdi_str(),
        "guncelleme_id": guncelleme_id,
        "durum": "TAMAMLANDI",
        "denenen_ihale": denenen_ihale_sayisi,
        "veri_cikan_ihale": veri_cikan_ihale_sayisi,
        "yeni_kayit": toplam_yeni,
        "csv_once": csv_once,
        "csv_sonra": csv_sonra,
        "hata_sayisi": hata_sayisi,
        "sure_saniye": sure_saniye,
        "output_csv": OUTPUT_CSV,
        "ayarlar": {
            "MAX_IHALE_WITH_DATA": MAX_IHALE_WITH_DATA,
            "MAX_CANDIDATE_IHALE": MAX_CANDIDATE_IHALE,
            "MAX_ISTIF_PER_IHALE": MAX_ISTIF_PER_IHALE,
            "REQUEST_DELAY": REQUEST_DELAY,
        }
    }

    ozet_kaydet(ozet)

    print("\n" + "=" * 100)
    log_yaz("İşlem tamam.")
    log_yaz(f"Denenen ihale: {denenen_ihale_sayisi}")
    log_yaz(f"Veri çıkan ihale: {veri_cikan_ihale_sayisi}")
    log_yaz(f"Toplam yeni kayıt: {toplam_yeni}")
    log_yaz(f"CSV önce/sonra: {csv_once} -> {csv_sonra}")
    log_yaz(f"Hata sayısı: {hata_sayisi}")
    log_yaz(f"Süre: {sure_saniye} saniye")
    log_yaz(f"Özet dosyası: {OZET_DOSYASI}")
    log_yaz(f"Log dosyası: {LOG_DOSYASI}")


if __name__ == "__main__":
    main()
