# Messe UI – Projektübersicht & Setup


Dieses Projekt ist ein vollständiges 
Steuerungs- und Visualisierungssystem für das **Messe-Spielsystem** mit:

- **1 Zentrale** (Raspberry Pi)
- **4 Satelliten** (Raspberry Pi, benannt `stl1–stl4`)

Es besteht aus:
- einem React/Vite-Frontend für die Bedienoberfläche
- einem FastAPI-Backend für Spielsteuerung, NFC-Auswertung und LED-Ansteuerung
- 2 Shell-Skripten zur Automatisierung
- Raspberry-Pi spezifischen Modulen für NFC-Reader und LED-Control

## Tech-Stack

**Frontend**
- React
- Vite
- JS/ESModules

**Backend**
- Python 3
- FastAPI
- httpx / requests
- gpiozero, RPi.GPIO
- MFRC522 (NFC-Reader via joyit-mfrc522)
- SQLite (über die Python-Standardbibliothek)

**Infrastruktur**
- Raspberry Pi OS
- SSH-basierte Remote-Steuerung
- Shellskripte für Start & Datenbank-Cleanup
---

## Projektstruktur

```
messe-ui/
│
├── backend/
│   ├── dist/                    # Gebaute Frontend-Dateien
│   ├── db.py                    # Datenbank-Skript zur Erstellung und Verbindung
│   ├── db_clean.py              # Datenbank-Bereinigungsskript
│   ├── frontend_test_server.py  # Test-Backend ohne RPi Kommunikation
│   ├── server.py                # FastAPI Backend
│   ├── led_controller.py        # LED-Steuerungsskript
│   ├── nfc_reader.py            # Skript für die Nutzung des NFC-Readers
│   ├── sat_config.txt           # Konfigurationsdatei für Satelliten-RPis
│   ├── satellite.txt            # Backend für Satelliten, wird auf den gelaufen
│   └── requirements.txt         # Python-Abhängigkeiten
│
├── frontend/
│   ├── assets/                  # Logos, Bilder und Sounds
│   ├── sounds/
│   ├── index.html               # HTML-Datei
│   ├── App.jsx                  # Haupt React-datei, die als Container für anderen gilt
│   └── ...                      # Rest des Frontend-codes
│
├── cleanup                      # Shell-Skript, um den Datenbank zu reinigen
├── startup                      # Shell-Skript für das Game-Loop
├── scripts/
│
├── package.json                 # Frontend Abhängigkeiten und Vite Config
├── package-lock.json
├── vite.config.js
│
└── README.md                 # Dieses Dokument
```

---
**Vollständiger Setup-Guide im pdf**