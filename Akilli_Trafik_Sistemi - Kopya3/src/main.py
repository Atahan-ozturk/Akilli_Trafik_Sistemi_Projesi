import os
import sys
import traci

# SUMO_HOME kontrolü
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Hata: SUMO_HOME ayarlı değil!")

def run_simulation():
    # DOSYA YOLU DÜZELTİLDİ: src içinden simulation klasörüne erişim
    # '../simulation/kavsak.sumocfg' ifadesi bir üst klasöre çıkıp simulation'a girer.
    sumo_cmd = ["sumo-gui", "-c", "../simulation/kavsak.sumocfg", "--start", "--delay", "200"]
    traci.start(sumo_cmd)

    min_yesil_sure = 20  
    son_degisim_adimi = 0
    su_anki_faz = 0 # 0: Kuzey-Güney Yeşil, 2: Doğu-Batı Yeşil

    print("\n--- 4 Yönlü Akıllı Kontrol Sistemi Aktif ---")

    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            sim_zaman = traci.simulation.getTime()
            
            # 4 Yöndeki araç sayılarını oku (Araçlar _1 şeritlerinde)
            k = traci.lane.getLastStepVehicleNumber("kuzey_1")
            g = traci.lane.getLastStepVehicleNumber("guney_1")
            d = traci.lane.getLastStepVehicleNumber("dogu_1")
            b = traci.lane.getLastStepVehicleNumber("bati_1")

            dikey_yogunluk = k + g
            yatay_yogunluk = d + b

            # Akıllı Karar Mekanizması
            if (sim_zaman - son_degisim_adimi) >= min_yesil_sure:
                if dikey_yogunluk > yatay_yogunluk + 2 and su_anki_faz != 0:
                    traci.trafficlight.setPhase("0", 0) # Kuzey-Güney aksını aç
                    su_anki_faz = 0
                    son_degisim_adimi = sim_zaman
                    print(f"Zaman: {sim_zaman} | Dikey Yoğunluk ({dikey_yogunluk}) fazla! K-G açıldı.")
                
                elif yatay_yogunluk > dikey_yogunluk + 2 and su_anki_faz != 2:
                    traci.trafficlight.setPhase("0", 2) # Doğu-Batı aksını aç
                    su_anki_faz = 2
                    son_degisim_adimi = sim_zaman
                    print(f"Zaman: {sim_zaman} | Yatay Yoğunluk ({yatay_yogunluk}) fazla! D-B açıldı.")

    finally:
        traci.close()
        print("Simülasyon başarıyla tamamlandı.")

if __name__ == "__main__":
    run_simulation()