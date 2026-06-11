import csv
import json
from pathlib import Path
from collections import deque


class DataLogger:

    CSV_PATH  = Path("data/sensor_data.csv")
    JSON_PATH = Path("data/sensor_data.json")
    FIELDNAMES = [
        "timestamp", "temperature_c", "humidity_pct",
        "motion_detected", "heat_index_c", "comfort_level", "step",
    ]

    def __init__(self, max_memory: int = 500):
        self._memory: deque = deque(maxlen=max_memory)
        Path("data").mkdir(exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        if not self.CSV_PATH.exists():
            with open(self.CSV_PATH, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=self.FIELDNAMES).writeheader()

    def log(self, record: dict):
        self._memory.append(record)

        with open(self.CSV_PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES, extrasaction="ignore")
            writer.writerow(record)

        snapshot = list(self._memory)[-100:]
        with open(self.JSON_PATH, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)

    def get_recent(self, count: int = 50) -> list:
        return list(self._memory)[-count:]

    def get_stats(self, count: int = 100) -> dict:
        recent = list(self._memory)[-count:]
        if not recent:
            return {}
        temps  = [r["temperature_c"]  for r in recent]
        hums   = [r["humidity_pct"]   for r in recent]
        motion = [r["motion_detected"] for r in recent]
        return {
            "temp_avg":     round(sum(temps) / len(temps), 2),
            "temp_max":     max(temps),
            "temp_min":     min(temps),
            "hum_avg":      round(sum(hums)  / len(hums),  2),
            "motion_count": sum(1 for m in motion if m),
            "sample_count": len(recent),
        }
