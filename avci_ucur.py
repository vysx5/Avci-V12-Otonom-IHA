import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping 

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time, math, threading, tkinter as tk
import os, csv, datetime, winsound

# --- STRATEJİK KONFİGÜRASYON ---
HIZ_MAX = 50       # 180 km/s Agresif Hız
HIZ_YAKLASMA = 15  # Hassas Nokta Yaklaşımı
BAGLANTI_ADRESI = 'tcp:127.0.0.1:5762'
LOG_DOSYASI = "avci_kara_kutu.csv"

class AvciGCS:
    def __init__(self, root):
        self.root = root
        self.root.title("AVCI V12 - STRATEJİK OPERASYON MERKEZİ")
        self.root.geometry("600x600")
        self.root.configure(bg='#020202')
        self.vehicle = None
        self.ucis_verileri = []

        # Arayüz Tasarımı
        tk.Label(root, text=">> AVCI OTONOM SEAD SİSTEMİ <<", fg="#00FF41", bg="#020202", font=("Courier", 18, "bold")).pack(pady=20)
        
        self.frm_data = tk.Frame(root, bg="#0a0a0a", highlightthickness=1, highlightbackground="#00FF41")
        self.frm_data.pack(padx=20, pady=10, fill="both", expand=True)

        self.lbl_durum = tk.Label(self.frm_data, text="SİSTEM: BAĞLANTI BEKLENİYOR", fg="orange", bg="#0a0a0a", font=("Courier", 14, "bold"))
        self.lbl_durum.pack(pady=15)
        
        self.lbl_alt = tk.Label(self.frm_data, text="İRTİFA: --", fg="white", bg="#0a0a0a", font=("Courier", 12))
        self.lbl_alt.pack(pady=2)
        self.lbl_volt = tk.Label(self.frm_data, text="BATARYA: --", fg="yellow", bg="#0a0a0a", font=("Courier", 12))
        self.lbl_volt.pack(pady=2)
        self.lbl_dist = tk.Label(self.frm_data, text="MESAFE: --", fg="white", bg="#0a0a0a", font=("Courier", 12))
        self.lbl_dist.pack(pady=2)
        
        self.lbl_hit = tk.Label(self.frm_data, text="", fg="#00FF41", bg="#0a0a0a", font=("Courier", 18, "bold"))
        self.lbl_hit.pack(pady=25)

    def veri_logla(self):
        if self.vehicle:
            v = self.vehicle
            try:
                data = {
                    "zaman": datetime.datetime.now().strftime("%H:%M:%S"),
                    "irtifa": v.location.global_relative_frame.alt,
                    "hiz": v.groundspeed,
                    "volt": v.battery.voltage if v.battery.voltage else 0,
                    "akim": v.battery.current if v.battery.current else 0,
                    "mode": v.mode.name,
                    "armed": v.armed
                }
                self.ucis_verileri.append(data)

                with open(LOG_DOSYASI, "a", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    writer.writerow(data)
                
                self.lbl_alt.config(text=f"İRTİFA: {data['irtifa']:.2f} m")
                self.lbl_volt.config(text=f"BATARYA: {data['volt']:.1f}V | {data['akim']}A")
                
                # İniş ve Bitiş Kontrolleri
                if data['mode'] == "RTL" and 0.2 < data['irtifa'] < 3.0:
                    self.lbl_durum.config(text="SİSTEM: İNİŞ YAPIYOR", fg="#00FFFF")
                
                if not data['armed'] and len(self.ucis_verileri) > 40:
                    self.lbl_durum.config(text="GÖREV TAMAMLANDI", fg="#00FF41")
                    self.lbl_dist.config(text="MESAFE: 0.0 m")

            except: pass
        self.root.after(500, self.veri_logla)

def rapor_yaz(veriler):
    if not veriler: return
    try:
        bas_v = veriler[0]['volt']
        bit_v = veriler[-1]['volt']
        max_h = max(d['hiz'] for d in veriler)
        
        rapor_metni = (
            f"--- AVCI OPERASYONEL ANALİZ ---\n"
            f"Tarih: {datetime.datetime.now()}\n"
            f"Görev Süresi: {len(veriler)} sn\n"
            f"Maksimum Hız: {max_h:.1f} m/s\n"
            f"Enerji Tüketimi: {bas_v - bit_v:.2f}V\n"
            f"Sonuç: BAŞARILI\n"
        )
        with open("avci_gorev_raporu.txt", "w", encoding="utf-8") as f:
            f.write(rapor_metni)
    except: pass

def operasyon_dongusu(panel):
    try:
        with open(LOG_DOSYASI, "w", newline="") as f:
            f.write("zaman,irtifa,hiz,volt,akim,mode,armed\n")

        panel.vehicle = connect(BAGLANTI_ADRESI, wait_ready=True)
        panel.lbl_durum.config(text="SİSTEM: BAĞLANDI", fg="#00FF41")
        panel.veri_logla()
        
        home = panel.vehicle.location.global_relative_frame 

        while not panel.vehicle.is_armable:
            panel.lbl_durum.config(text="DURUM: GPS FIX BEKLENİYOR", fg="yellow")
            time.sleep(1)

        # KALKIŞ
        panel.lbl_durum.config(text="SİSTEM: KALKIŞ YAPILIYOR", fg="cyan")
        panel.vehicle.mode = VehicleMode("GUIDED")
        panel.vehicle.armed = True
        while not panel.vehicle.armed: time.sleep(1)
        
        panel.vehicle.simple_takeoff(25)
        while panel.vehicle.location.global_relative_frame.alt < 24: time.sleep(1)

        # --- YENİ GÜNCELLEME: Hedefe İlerleme Mesajı ---
        panel.lbl_durum.config(text="SİSTEM: HEDEFE İLERLENİYOR", fg="#00FF41")

        start = panel.vehicle.location.global_relative_frame
        target_lon = start.lon - 0.011 
        offset = 0.0009 
        
        rota = [
            LocationGlobalRelative(start.lat + offset, start.lon - 0.003, 25),
            LocationGlobalRelative(start.lat - offset, start.lon - 0.007, 25),
            LocationGlobalRelative(start.lat, target_lon, 25) 
        ]

        for i, nokta in enumerate(rota):
            panel.vehicle.simple_goto(nokta)
            panel.vehicle.groundspeed = HIZ_MAX
            
            while True:
                curr = panel.vehicle.location.global_relative_frame
                d = math.sqrt((nokta.lat-curr.lat)**2 + (nokta.lon-curr.lon)**2) * 111319
                panel.lbl_dist.config(text=f"HEDEFE: {d:.1f} m")
                
                if d < 50: panel.vehicle.groundspeed = HIZ_YAKLASMA
                if d < 6: break
                time.sleep(0.4)
            
            if i == len(rota) - 1:
                panel.lbl_hit.config(text="[ HEDEF VURULDU ]")
                winsound.Beep(1200, 1000) 
                time.sleep(2)

        # RTL
        panel.lbl_durum.config(text="SİSTEM: EVE DÖNÜLÜYOR", fg="lime")
        panel.vehicle.mode = VehicleMode("RTL")
        panel.vehicle.groundspeed = HIZ_MAX
        
        while panel.vehicle.armed:
            c = panel.vehicle.location.global_relative_frame
            d_home = math.sqrt((home.lat-c.lat)**2 + (home.lon-c.lon)**2) * 111319
            panel.lbl_dist.config(text=f"EVE MESAFE: {d_home:.1f} m")
            time.sleep(1)
        
        rapor_yaz(panel.ucis_verileri)

    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AvciGCS(root)
    t = threading.Thread(target=operasyon_dongusu, args=(app,), daemon=True)
    t.start()
    root.mainloop()