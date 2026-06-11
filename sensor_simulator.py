import math
import random
from datetime import datetime
class SensorSimulator:

    def __init__(self, base_temp: float = 27.5, base_humidity: float = 68.0):
        self._step = 0
        self._base_temp = base_temp
        self._base_humidity = base_humidity


    def _temperature(self) -> float:

        swing = math.sin(self._step * 0.08) * 6.0
        noise = random.gauss(0, 0.4)
        return round(max(15.0, min(50.0, self._base_temp + swing + noise)), 2)

    def _humidity(self) -> float:

        temp_influence = -math.sin(self._step * 0.08) * 14.0
        noise = random.gauss(0, 1.5)
        return round(max(20.0, min(98.0, self._base_humidity + temp_influence + noise)), 2)

    def _motion(self) -> bool:

        simulated_hour = (self._step % 240) / 10.0
        probability = 0.25 if 7.0 <= simulated_hour <= 22.0 else 0.04
        return random.random() < probability

    def _heat_index(self, T: float, RH: float) -> float:

        if T < 26.7 or RH < 40:
            return T

        HI = (
                -8.78469475556
                + 1.61139411 * T
                + 2.33854883889 * RH
                + (-0.14611605) * T * RH
                + (-0.012308094) * T ** 2
                + (-0.016424828) * RH ** 2
                + 0.002211732 * T ** 2 * RH
                + 0.00072546 * T * RH ** 2
                + (-0.000003582) * T ** 2 * RH ** 2
        )
        return round(HI, 2)

    def _comfort_level(self, T: float, RH: float) -> str:
        if 20.0 <= T <= 26.0 and 40.0 <= RH <= 60.0:
            return "COMFORTABLE"
        if T > 37.0 or (T > 32.0 and RH > 75.0):
            return "OPPRESSIVE"
        if T > 32.0 or RH > 80.0:
            return "UNCOMFORTABLE"
        if T < 18.0:
            return "COOL"
        return "MODERATE"


    def read(self) -> dict:

        T   = self._temperature()
        RH  = self._humidity()
        mot = self._motion()
        HI  = self._heat_index(T, RH)

        self._step += 1

        return {
            "timestamp":       datetime.now().isoformat(),
            "temperature_c":   T,
            "humidity_pct":    RH,
            "motion_detected": mot,
            "heat_index_c":    HI,
            "comfort_level":   self._comfort_level(T, RH),
            "step":            self._step,
        }
