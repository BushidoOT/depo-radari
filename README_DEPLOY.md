DEPO RADARI V23 / SITE V27

Düzeltme:
- Streamlit Cloud'daki takip kodu hatası düzeltildi.
- Hata sebebi: takip kodu text_input'u aynı sayfa çalışmasında birden fazla kez çiziliyordu.
- V27 ile takip kodu sadece bir kez çizilir.
- Diğer takip/alarm fonksiyonları aynı kodu session_state üzerinden okur.

GitHub deploy:
1) app_v27.py dosyasını indir.
2) Adını app.py yap.
3) GitHub'daki eski app.py ile değiştir.
4) Commit changes.
5) Streamlit otomatik yeniden deploy eder.
