import threading
import time
from flask import Flask, jsonify, render_template

from sensor_simulator import SensorSimulator
from data_logger import DataLogger
from automation_engine import AutomationEngine
from serial_commander import SerialCommander
app       = Flask(__name__)
simulator = SensorSimulator()
logger    = DataLogger()
engine    = AutomationEngine()
commander = SerialCommander(port='COM5')
commander.connect()

_latest_data:   dict = {}
_event_buffer:  list = []


def _background_loop():

    global _latest_data, _event_buffer
    while True:
        data   = simulator.read()
        logger.log(data)
        events = engine.evaluate(data)
        _latest_data = data

        if events:
            for e in events:
                _event_buffer.append({
                    "timestamp": e.timestamp,
                    "rule": e.rule_name,
                    "level": e.level,
                    "action": e.action,
                })

            # Send highest severity command to ESP32
            level_order = ["INFO", "WARNING", "CRITICAL", "EMERGENCY"]
            highest = max(events, key=lambda x: level_order.index(x.level)
            if x.level in level_order else 0)
            commander.send_alert(highest.level)

            # Auto-clear hardware after 5 seconds
            threading.Timer(5.0, commander.clear).start()

            _event_buffer = _event_buffer[-30:]

        time.sleep(2)

_thread = threading.Thread(target=_background_loop, daemon=True)
_thread.start()

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/current")
def api_current():
    return jsonify(_latest_data)


@app.route("/api/history")
def api_history():
    return jsonify(logger.get_recent(50))


@app.route("/api/stats")
def api_stats():
    return jsonify(logger.get_stats(100))


@app.route("/api/events")
def api_events():
    return jsonify(_event_buffer)

@app.route("/api/hardware")
def api_hardware():
    return jsonify({
        "connected": commander.is_connected(),
        "status": "ESP32 Connected" if commander.is_connected() else "Simulation Only"
    })


if __name__ == "__main__":
    print("EnviroSense running → http://localhost:5000")
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=5000)

