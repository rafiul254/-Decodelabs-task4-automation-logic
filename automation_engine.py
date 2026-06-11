from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, List, Optional


class AlertLevel(Enum):
    INFO      = "INFO"
    WARNING   = "WARNING"
    CRITICAL  = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class Rule:
    name:             str
    condition:        Callable[[dict], bool]
    action:           str
    level:            AlertLevel
    cooldown_seconds: int = 30


@dataclass
class AutomationEvent:
    timestamp:    str
    rule_name:    str
    level:        str
    action:       str
    sensor_snapshot: dict


class AutomationEngine:

    def __init__(self):
        self._rules:        List[Rule]            = []
        self._event_log:    List[AutomationEvent] = []
        self._last_trigger: dict                  = {}
        self._load_default_rules()

    def _load_default_rules(self):

        self.add_rule(Rule(
            name="HIGH_TEMP",
            condition=lambda d: d["temperature_c"] > 33.0,
            action="Activate cooling fan at LOW speed",
            level=AlertLevel.WARNING,
            cooldown_seconds=30,
        ))
        self.add_rule(Rule(
            name="CRITICAL_TEMP",
            condition=lambda d: d["temperature_c"] > 38.0,
            action="EMERGENCY: All fans ON + send SMS alert",
            level=AlertLevel.EMERGENCY,
            cooldown_seconds=10,
        ))
        self.add_rule(Rule(
            name="HIGH_HUMIDITY",
            condition=lambda d: d["humidity_pct"] > 80.0,
            action="Activate dehumidifier + open ventilation",
            level=AlertLevel.WARNING,
            cooldown_seconds=45,
        ))
        self.add_rule(Rule(
            name="OPPRESSIVE_HEAT_INDEX",
            condition=lambda d: d["heat_index_c"] > 40.0,
            action="Turn ON air conditioning — heat index critical",
            level=AlertLevel.CRITICAL,
            cooldown_seconds=20,
        ))
        self.add_rule(Rule(
            name="MOTION_IN_HOT_ZONE",
            condition=lambda d: d["motion_detected"] and d["temperature_c"] > 32.0,
            action="Person detected in hot zone — increase airflow",
            level=AlertLevel.INFO,
            cooldown_seconds=60,
        ))
        self.add_rule(Rule(
            name="COMFORT_ZONE",
            condition=lambda d: (20.0 <= d["temperature_c"] <= 27.0
                                 and 40.0 <= d["humidity_pct"] <= 60.0),
            action="Environment OPTIMAL — all systems idle",
            level=AlertLevel.INFO,
            cooldown_seconds=120,
        ))

    def add_rule(self, rule: Rule):
        self._rules.append(rule)

    def evaluate(self, sensor_data: dict) -> List[AutomationEvent]:

        now = datetime.now()
        triggered = []

        for rule in self._rules:
            try:
                if not rule.condition(sensor_data):
                    continue

                last = self._last_trigger.get(rule.name)
                elapsed = (now - last).total_seconds() if last else float("inf")
                if elapsed < rule.cooldown_seconds:
                    continue

                event = AutomationEvent(
                    timestamp=now.isoformat(),
                    rule_name=rule.name,
                    level=rule.level.value,
                    action=rule.action,
                    sensor_snapshot=sensor_data.copy(),
                )
                triggered.append(event)
                self._event_log.append(event)
                self._last_trigger[rule.name] = now

            except Exception as exc:
                print(f"[AutomationEngine] Rule '{rule.name}' error: {exc}")

        return triggered

    def recent_events(self, count: int = 20) -> List[dict]:
        return [
            {
                "timestamp": e.timestamp,
                "rule":      e.rule_name,
                "level":     e.level,
                "action":    e.action,
            }
            for e in self._event_log[-count:]
        ]
