# IOT_SMART_HOME

# 🏠 Smart Home IoT

A system for managing and controlling IoT devices (sensors, relays, and actuators) with a graphical user interface (PyQt5), MQTT-based communication, and an SQLite database for storing sensor data.

---

## ✨ Features
- 📡 Communication with sensors and actuators via **MQTT Broker** (HiveMQ / Mosquitto).  
- 🧩 **Simulators** for DHT sensors, relays, and buttons – run without physical hardware.  
- 💾 **SQLite Database** to store sensor readings.  
- 🖥 **Graphical User Interface (GUI)** built with PyQt5 for real-time monitoring and control.  
- 🔄 Control relay switches, toggle sensors on/off, and send custom temperature values.  
- ⚠️ Smart alerts for high/low temperature thresholds.  

---

## 📂 Project Structure

```bash
smart_home_iot/
│
├── database/                 
│   ├── database_manager.py     # Database management functions
│   └── iot_database.db         # Local SQLite database
│
├── simulators/                 # IoT device simulators
│   ├── sensor_dht_emulator.py  # DHT temperature/humidity sensor simulator
│   ├── relay_emulator.py       # Relay switch simulator
│   └── button_emulator.py      # Actuator button simulator
│
├── ui/                         # Graphical User Interface (PyQt5)
│   ├── main_window.py          # Main application window
│   └── ui_helpers.py           # Helper utilities for the GUI
│
├── mqtt/                       
│   └── mqtt_connector.py       # MQTT client and connector
│
├── tests/                      
│   └── test_mqtt.py            # Basic MQTT communication tests
│
├── README.md
└── .gitignore
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+  

### Running the GUI
```bash
python ui/main_window.py
```

### Running Simulators
Each emulator can be run individually, for example:
```bash
python simulators/sensor_dht_emulator.py
python simulators/relay_emulator.py
```

## 🛠 Tech Stack
- **Python 3.10+**  
- **PyQt5** – GUI framework  
- **Paho-MQTT** – MQTT communication  
- **SQLite3** – Local database  