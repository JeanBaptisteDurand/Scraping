#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
eth_price_scraper_full.py
--------------------------

Scrape le prix ETH/USD à la minute depuis 2024-04-04
jusqu'à aujourd'hui, par tranches de 90 jours (limite CoinGecko)

Résultat : eth_price_per_minute.csv
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. Paramètres
start_date = datetime.fromisoformat("2024-04-04T22:49:08.582405")
end_date = datetime.now()
delta = timedelta(days=90)

url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart/range"
vs_currency = "usd"

all_data = []

current_start = start_date
print(f"📅 Récupération du prix ETH/USD de {start_date} à {end_date} par tranches de 90 jours...")

# 2. Boucle sur les plages de 90 jours
while current_start < end_date:
    current_end = min(current_start + delta, end_date)
    from_ts = int(current_start.timestamp())
    to_ts = int(current_end.timestamp())

    print(f"→ De {current_start} à {current_end}...", end=" ", flush=True)
    r = requests.get(url, params={
        "vs_currency": vs_currency,
        "from": from_ts,
        "to": to_ts
    })

    if r.status_code != 200:
        print(f"❌ Erreur HTTP {r.status_code}, abandon.")
        break

    prices = r.json().get("prices", [])
    all_data.extend(prices)
    print(f"{len(prices)} points")

    current_start = current_end
    time.sleep(1.2)  # respect API rate limit

# 3. Création du DataFrame final
df = pd.DataFrame(all_data, columns=["timestamp", "eth_price"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

# 4. Nettoyage : 1 ligne par minute
df = df.set_index("timestamp").resample("1T").mean().reset_index()

# 5. Sauvegarde
df.to_csv("eth_price_per_minute.csv", index=False)
print("✅ Fichier complet sauvegardé : eth_price_per_minute.csv")
