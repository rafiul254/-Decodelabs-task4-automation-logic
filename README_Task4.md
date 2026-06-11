<div align="center">

# ⚙️ Task 4 — IoT Automation Logic

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![ESP32](https://img.shields.io/badge/ESP32-Actuator-E7352C?style=flat&logo=espressif&logoColor=white)](https://espressif.com)
[![PlatformIO](https://img.shields.io/badge/PlatformIO-Arduino-F5822A?style=flat&logo=platformio&logoColor=white)](https://platformio.org)
[![PySerial](https://img.shields.io/badge/PySerial-3.5-brightgreen?style=flat)](https://pyserial.readthedocs.io)
[![Internship](https://img.shields.io/badge/Decodelabs-IoT%20Internship-2ea44f?style=flat)](https://www.decodelabs.tech)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

**Decodelabs IoT Internship Program**

> A rule-based IoT automation engine with 6 configurable threshold conditions.  
> When rules fire, the system sends real-time commands via USB Serial to an  
> **ESP32 hardware actuator** — physically triggering LEDs and a buzzer.

</div>

---

## 📌 Goal

> *"Build simple automation rules based on sensor data."*

This project goes beyond basic if-else logic — it implements a full **rule engine** with
per-rule cooldown timers and bridges software automation to physical hardware via Serial.

---

## ✅ Requirements Coverage

| Requirement | Implementation |
|-------------|---------------|
| Define conditions (e.g. temp > limit) | 6 threshold rules in `automation_engine.py` |
| Trigger alerts or actions | Serial commands to ESP32 — LEDs + buzzer fire physically |
| Display automation results | Color-coded event log panel in live dashboard |

---

## 📁 Files

```
task4-automation-logic/
│
├── automation_engine.py    # Rule engine — 6 conditions with cooldown timers
├── serial_commander.py     # Python → ESP32 USB Serial bridge
├── app.py                  # Flask backend — integrates all components
├── sensor_simulator.py     # Sensor data source
├── data_logger.py          # Data logging
│
├── firmware/               # ESP32 Hardware Actuator
│   ├── src/
│   │   └── main.cpp        # Arduino C++ firmware (active buzzer version)
│   └── platformio.ini      # Board config — esp32dev, 9600 baud
│
├── templates/
│   └── dashboard.html      # Live dashboard with automation event log
│
├── assets/
│   ├── dashboard_charts.png
│   └── dashboard_events.png
│
├── requirements.txt
└── README.md
```

---

## ✨ Key Features

| Feature | Detail |
|---------|--------|
| ⚙️ **Rule engine** | 6 configurable threshold rules, each independently evaluated |
| ⏱️ **Cooldown timers** | Each rule has its own cooldown — prevents alert spam |
| 🔌 **ESP32 bridge** | `serial_commander.py` sends single-char commands via USB |
| 💡 **4-level alerts** | INFO → WARNING → CRITICAL → EMERGENCY |
| 🔄 **Graceful fallback** | Runs without ESP32 — simulation mode works automatically |
| 📋 **Event log** | Live color-coded automation log in web dashboard |
| ⚡ **Auto-clear** | Hardware LEDs auto-off after 5 seconds |

---

## 🤖 Automation Rules

| Rule Name | Trigger Condition | Action | Level | Cooldown |
|-----------|------------------|--------|-------|---------|
| `HIGH_TEMP` | Temp > 33°C | Activate cooling fan | ⚠️ WARNING | 30s |
| `CRITICAL_TEMP` | Temp > 38°C | Emergency — all fans + SMS | 🚨 EMERGENCY | 10s |
| `HIGH_HUMIDITY` | Humidity > 80% | Activate dehumidifier | ⚠️ WARNING | 45s |
| `OPPRESSIVE_HEAT_INDEX` | Heat Index > 40°C | Turn ON AC | 🔴 CRITICAL | 20s |
| `MOTION_IN_HOT_ZONE` | Motion + Temp > 32°C | Increase airflow | ℹ️ INFO | 60s |
| `COMFORT_ZONE` | 20–27°C + 40–60% RH | All systems idle | ℹ️ INFO | 120s |

Custom rules can be added via `engine.add_rule()` in `automation_engine.py`.

---

## 🔌 Hardware Setup (ESP32 Actuator)

### Components

| Component | Quantity |
|-----------|---------|
| ESP32 DevKit V1 | 1 |
| Green LED | 1 |
| Yellow LED | 1 |
| Red LED | 1 |
| Active Buzzer | 1 |
| 220Ω Resistor | 3 |

### Wiring

```
ESP32 GPIO25 ──[220Ω]── Green  LED (+) ── GND   → INFO
ESP32 GPIO26 ──[220Ω]── Yellow LED (+) ── GND   → WARNING
ESP32 GPIO27 ──[220Ω]── Red    LED (+) ── GND   → CRITICAL / EMERGENCY
ESP32 GPIO32 ─────────── Active Buzzer (+) ── GND
```

### Alert Behaviour

| Level | LED | Buzzer |
|-------|-----|--------|
| INFO | 🟢 Green ON | 1 beep |
| WARNING | 🟡 Yellow blink ×3 | 2 beeps |
| CRITICAL | 🔴 Red blink ×5 | 3 beeps |
| EMERGENCY | 🔴 Rapid flash | Alarm |
| Clear (5s) | All OFF | Silent |

### Serial Protocol

```
Python sends  →  ESP32 receives  →  Action
    'I'       →       'I'        →  INFO alert
    'W'       →       'W'        →  WARNING alert
    'C'       →       'C'        →  CRITICAL alert
    'E'       →       'E'        →  EMERGENCY alert
    '0'       →       '0'        →  Clear all
```

---

## ⚙️ Installation & Run

**1. Flash ESP32 firmware** *(optional — works without hardware)*
```bash
# Open firmware/ in VSCode with PlatformIO
# Connect ESP32 via USB → click Upload (→)
```

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run full system:**
```bash
python app.py
```

**4. Open dashboard:**
```
http://localhost:5000
```

> If ESP32 is connected, dashboard shows **"⬤ ESP32 Connected"**  
> and physical LEDs + buzzer respond to alerts automatically.  
> Without ESP32, system runs in simulation-only mode.

---

## 🏗️ How It Works

```
Background thread (every 2s)
         ↓
  sensor_simulator reads data
         ↓
  automation_engine evaluates
  all 6 rules → finds triggers
         ↓
       ┌─────────────────┐
       ▼                 ▼
  serial_commander    event_buffer
  sends 'W' / 'C'    updates dashboard
  to ESP32 via USB    event log
       ↓
  ESP32 firmware
  LED blinks + buzzer
  (auto-clear after 5s)
```

---

## 👨‍💻 Author

**Rafi Ul Islam**  
2nd Year — IoT & Robotics Engineering  
University of Frontier Technology, Bangladesh (UFTB) · Student ID: 2301012

[![GitHub](https://img.shields.io/badge/GitHub-rafiul254-181717?style=flat&logo=github)](https://github.com/rafiul254)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/rafiul254)

---

<div align="center">

*Part of the **Decodelabs IoT Internship Program** — Task 4 of 3*

</div>
