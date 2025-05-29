#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

BASE_URL = "https://api.binance.com/api/v3/klines"
symbol = "ETHUSDT"
interval = "1m"
limit = 1000

start_time = datetime.fromisoformat("2024-04-04T22:49:08.582405")
end_time = datetime.now()

data = []
current = start_time

print(f"📅 Téléchargement du prix ETH/USDT minute depuis {start_time}...")

while current < end_time:
    start_ts = int(current.timestamp() * 1000)

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
        "startTime": start_ts
    }

    r = requests.get(BASE_URL, params=params)
    if r.status_code != 200:
        print(f"❌ Erreur HTTP {r.status_code} : {r.text}")
        break

    klines = r.json()
    if not klines:
        print("⛔️ Plus de données reçues.")
        break

    for k in klines:
        data.append([datetime.fromtimestamp(k[0]/1000), float(k[4])])  # close price

    current = datetime.fromtimestamp(klines[-1][0] / 1000) + timedelta(minutes=1)
    print(f"✓ {len(data)} lignes jusqu’à {current}")
    time.sleep(0.5)  # rate limit safe

# Export CSV
df = pd.DataFrame(data, columns=["timestamp", "eth_price"])
df.to_csv("eth_price_per_minute.csv", index=False)
print("✅ Fichier final : eth_price_per_minute.csv")
