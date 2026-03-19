# 🚀 AVCI V12 - Otonom SEAD Sistemi

Bu proje, düşman hava savunma sistemlerini (SEAD) baskılamak için tasarlanmış, yüksek hızlı ve otonom manevra kabiliyetine sahip bir İHA Yer Kontrol İstasyonu (GCS) ve uçuş yazılımıdır. Python ve DroneKit kullanılarak geliştirilmiştir.

## 🛠️ Teknik Özellikler
- **Agresif Otonom Uçuş:** 50 m/s (180 km/s) operasyon hızı ile hızlı müdahale.
- **Radar Yanıltma (Anti-Radar):** Hedefe yaklaşırken +,- 100 metrelik dinamik zikzak manevraları ile beka kabiliyeti.
- **Akıllı Telemetri:** Tkinter tabanlı arayüz üzerinden anlık irtifa, batarya voltajı, akım ve mesafe takibi.
- **Kara Kutu (Logging):** Tüm uçuş verilerinin saniyelik olarak `avci_kara_kutu.csv` dosyasına kaydedilmesi.
- **Operasyon Analizi:** Görev sonunda otomatik olarak oluşturulan detaylı performans raporu.
- **İşitsel Onay:** Hedef imha edildiğinde (noktaya varıldığında) sistem üzerinden sesli geri bildirim.

## 🚀 Kurulum ve Çalıştırma
1. Gerekli kütüphaneyi kurun:
   ```bash
   pip install dronekit
