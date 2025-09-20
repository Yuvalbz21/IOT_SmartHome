import sys
import json
import paho.mqtt.publish as publish
import sqlite3
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QLabel,
)
import paho.mqtt.client as mqtt
import os

BROKER = "broker.hivemq.com"
PORT = 1883

CONTROL_TOPIC = "smarthome/control/dht"
SENSOR_TOPIC = "smarthome/sensor/dht"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "..", "database", "iot_database.db")


class SmartHomeGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Home Data Viewer")
        self.resize(650, 500)
        self.relay_state = "off"

        main_layout = QVBoxLayout()

        # 🔹 עיצוב אחיד לכל הכפתורים
        button_style = """
            QPushButton {
                background:#2196F3; 
                color:white; 
                font-weight:bold; 
                padding:6px; 
                border-radius:5px;
            }
            QPushButton:hover { background:#1976D2; }
            QPushButton:pressed { background:#1565C0; }
            QPushButton:checked { background:#0D47A1; border:2px inset #08306b; }
        """

        # שורה עליונה: כותרת + כפתור Refresh בצד ימין
        top_bar = QHBoxLayout()
        self.title_label = QLabel("Smart Home Data Viewer")
        self.title_label.setStyleSheet("font-size:16pt; font-weight:bold; color:#333;")
        top_bar.addWidget(self.title_label)

        self.refresh_button = QPushButton("🔄", self)
        self.refresh_button.setFixedWidth(40)
        self.refresh_button.clicked.connect(self.load_data)
        self.refresh_button.setStyleSheet(button_style)
        top_bar.addStretch()
        top_bar.addWidget(self.refresh_button)
        main_layout.addLayout(top_bar)

        # תיבת לוג
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet(
            "background-color:#1e1e1e; color:#e0e0e0; font-family:Consolas; font-size:10pt;"
        )
        main_layout.addWidget(self.text_display)

        # שורה אמצעית: Relay + Sensor
        mid_buttons = QHBoxLayout()

        self.relay_button = QPushButton("Switch Relay", self)
        self.relay_button.setCheckable(True)
        self.relay_button.clicked.connect(self.toggle_relay)
        self.relay_button.setStyleSheet(button_style)
        mid_buttons.addWidget(self.relay_button)

        self.toggle_sensor_button = QPushButton("Sensor ON/OFF", self)
        self.toggle_sensor_button.setCheckable(True)
        self.toggle_sensor_button.clicked.connect(self.toggle_sensor)
        self.toggle_sensor_button.setStyleSheet(button_style)
        mid_buttons.addWidget(self.toggle_sensor_button)

        main_layout.addLayout(mid_buttons)

        # קלט טמפרטורה
        self.temp_input = QLineEdit(self)
        self.temp_input.setPlaceholderText("Set Your Desired Temperature (°C)")
        self.temp_input.setStyleSheet(
            "padding:4px; border:1px solid #ccc; border-radius:3px;"
        )
        main_layout.addWidget(self.temp_input)

        # כפתור לשליחת טמפרטורה
        self.send_temp_button = QPushButton("Send Custom Temperature", self)
        self.send_temp_button.clicked.connect(self.send_custom_temperature)
        self.send_temp_button.setStyleSheet(button_style)
        main_layout.addWidget(self.send_temp_button)

        self.setLayout(main_layout)
        self.sensor_on = True

        # עיצוב כללי
        self.setStyleSheet(
            """
            QWidget { background-color:#f7f7f7; font-family:Arial; font-size:11pt; }
            QLineEdit:focus { border:1px solid #2196F3; }
        """
        )

        self.load_data()

        # MQTT
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_message = self.on_mqtt_message
            self.mqtt_client.connect(BROKER, PORT, 60)
            self.mqtt_client.subscribe("smarthome/relay")
            self.mqtt_client.loop_start()
        except Exception as e:
            self.log(f"⚠️ Could not connect to MQTT broker: {e}")

    # פונקציה מרכזית ללוגים – גם GUI וגם טרמינל
    def log(self, msg: str):
        self.text_display.append(msg)
        print(msg)

    def toggle_sensor(self):
        if self.sensor_on:
            publish.single(CONTROL_TOPIC, "off", hostname=BROKER)
            self.toggle_sensor_button.setText("Sensor OFF")
            self.log("📴 Sensor turned OFF (command sent)")
            self.sensor_on = False
        else:
            publish.single(CONTROL_TOPIC, "on", hostname=BROKER)
            self.toggle_sensor_button.setText("Sensor ON")
            self.log("✅ Sensor turned ON (command sent)")
            self.sensor_on = True

    def toggle_relay(self):
        try:
            client = mqtt.Client()
            client.connect(BROKER, PORT, 60)
            message = json.dumps({"command": "toggle"})
            topic = "smarthome/actuator/button"
            client.publish(topic, message)
            client.disconnect()

            # שינוי מצב מקומי מיידי
            self.relay_state = "on" if self.relay_state == "off" else "off"
            self.log(f"🔄 Relay TOGGLED: {self.relay_state}")

        except Exception as e:
            self.log(f"❌ Error sending MQTT command: {e}")

    def on_mqtt_message(self, client, userdata, msg):
        status = msg.payload.decode()
        self.relay_state = status
        self.log(f"📩 Relay status update from broker: {status}")

    def send_custom_temperature(self):
        temp_value = self.temp_input.text().strip()
        try:
            temp_float = float(temp_value)
            publish.single(CONTROL_TOPIC, f"temp:{temp_float}", hostname=BROKER)
            self.log(f"📤 Sent Custom Temperature: {temp_float}°C")
        except ValueError:
            self.log("❌ Invalid temperature format! Enter a valid number.")

    def load_data(self):
        rows = self.get_latest_data()
        display_text = ""
        for ts, topic, msg in rows:
            entry = f"[{ts}] {topic}: {msg}"
            if msg.startswith("{") and msg.endswith("}"):
                try:
                    data = json.loads(msg)
                    if "temperature" in data:
                        temp = data["temperature"]
                        if temp > 30:
                            entry += f"  ⚠️ WARNING: High Temperature {temp}°C"
                        elif temp < 20:
                            entry += f"  ❄️ ALERT: Low Temperature {temp}°C"
                except Exception as e:
                    entry += f"  Error processing alert: {e}"
            display_text += entry + "\n"
        self.text_display.setText(display_text if display_text else "No data available")

    def get_latest_data(self, limit=20):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, topic, message FROM sensor_data ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            self.log(f"Error retrieving data: {e}")
            return []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartHomeGUI()
    window.show()
    sys.exit(app.exec_())
