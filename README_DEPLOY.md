DEPO RADARI V20 / SITE V24

Duzeltme:
- Streamlit Cloud'daki hata duzeltildi.
- Hata sebebi: premium_aktif fonksiyonu paket verisini dict bekliyordu ama V23'te lisans kontrolu string donduruyordu.
- V24 ile premium_aktif hem string hem dict kabul eder.

GitHub deploy:
1) app_v24.py dosyasını indir.
2) Adını app.py yap.
3) GitHub'daki eski app.py ile değiştir.
4) Commit changes.
5) Streamlit otomatik yeniden deploy eder.
