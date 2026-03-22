import random
import time

import requests

BASE_URL = "http://127.0.0.1:5000"

lat, lon = 12.9716, 77.5946

print("Starting software IoT simulator for Women Safety Monitoring System...")

while True:
    lat += (random.random() - 0.5) * 0.003
    lon += (random.random() - 0.5) * 0.003

    payload = {"latitude": lat, "longitude": lon, "user_phone": "+918883896269"}
    try:
        res = requests.post(f"{BASE_URL}/update-location", json=payload, timeout=5)
        print("Location update:", res.status_code, res.json())
    except Exception as exc:
        print("Simulator error:", exc)

    if random.random() < 0.15:
        try:
            res = requests.post(f"{BASE_URL}/fall-alert", json=payload, timeout=5)
            print("Fall alert simulation:", res.status_code, res.json())
        except Exception as exc:
            print("Fall alert error:", exc)

    time.sleep(5)
