# Depo Radarı Deploy Paketi

Bu klasör yayın/deploy için hazırlanmış sade pakettir.

## Ana dosyalar

- `app.py`  
  Yayına gidecek ana Streamlit site dosyası.

- `requirements.txt`  
  Sunucuda kurulacak Python paketleri.

- `.streamlit/config.toml`  
  Streamlit tema ve çalışma ayarları.

- `depo_radari_tum_ihaleler_guvenli_v3.csv`  
  Sitenin okuyacağı veri dosyası.

- `depo_radari_lisanslar.txt`  
  Test lisans kodları.

- `depo_radari_takip_listesi.json`  
  Takip listesi kayıtları.

- `depo_radari_ozet.json`  
  Son güncelleme özeti.

- `depo_radari_veri_guncelle_v4.py`  
  Veri güncelleme scripti. İlk deploy aşamasında otomatik çalıştırılmaz.

## Yerelde test

Windows'ta:

```bat
yerelde_test_et.bat
```

veya komutla:

```bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Yayın mantığı

İlk aşamada site CSV dosyasını okuyarak çalışır.  
Daha sonra veri güncelleme, kullanıcı girişi, lisans ve takip listesi veritabanına taşınmalıdır.

## Test premium lisans kodu

```text
DEPO-PREMIUM-2026
```
