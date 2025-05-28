#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trades scraper pour l’API Ape.store
==================================

• 6 workers – un par fichier d’input CSV :
      W1 : tokens_0000-1000.csv
      W2 : tokens_1000-2000.csv
      W3 : tokens_2000-3000.csv
      W4 : tokens_3000-4000.csv
      W5 : tokens_4000-5000.csv
      W6 : tokens_5000-6000.csv
• Pour chaque ligne lue, on extrait `address`
  → GET https://ape.store/api/token/8453/<address>/trades
• Toutes les entrées du tableau JSON sont écrites dans
  un CSV dédié au worker : trades_0000-1000.csv, etc.
• Progression en direct : « WorkerX : n / total ».
"""

import csv
import sys
import time
import glob
import requests
import concurrent.futures
import threading
from pathlib import Path
from typing import Dict, List

# ────────────────────────────────────────────── CONFIG
INPUT_FILES = [
    "tokens_0000-1000.csv",
    "tokens_1000-2000.csv",
    "tokens_2000-3000.csv",
    "tokens_3000-4000.csv",
    "tokens_4000-5000.csv",
    "tokens_5000-6000.csv",
]

CHAIN_ID       = 8453
BASE_ENDPOINT  = "https://ape.store/api/token"
RETRY_DELAY_S  = 3
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Origin":  "https://ape.store",
    "Referer": "https://ape.store/",
}
# ────────────────────────────────────────────── PROGRESSION
progress_lock = threading.Lock()
progress_done   : List[int] = []
progress_total  : List[int] = []

def display_progress() -> None:
    line = " | ".join(
        f"Worker{i+1} : {progress_done[i]:4}/{progress_total[i]:4}"
        for i in range(len(progress_total))
    )
    sys.stdout.write("\r\033[K" + line)
    sys.stdout.flush()

# ────────────────────────────────────────────── NETWORK
def fetch_trades(session: requests.Session, address: str) -> List[Dict]:
    """GET /token/<chain>/<address>/trades ; retry illimité."""
    url = f"{BASE_ENDPOINT}/{CHAIN_ID}/{address}/trades"
    while True:
        try:
            r = session.get(url, timeout=10, headers=HEADERS)
            r.raise_for_status()
            return r.json() or []
        except Exception as exc:
            with progress_lock:
                sys.stdout.write("\r\033[K")
                sys.stdout.flush()
                print(f"[⚠] {address[:10]}… : {exc} – retry dans {RETRY_DELAY_S}s")
            time.sleep(RETRY_DELAY_S)

# ────────────────────────────────────────────── WORKER
def scrape_file(job_id: int, in_path: Path) -> None:
    out_path = Path(str(in_path).replace("tokens_", "trades_"))
    writer   = None

    with open(in_path, newline="", encoding="utf-8") as f_in, \
         open(out_path, "w", newline="", encoding="utf-8") as f_out, \
         requests.Session() as session:

        reader = csv.DictReader(f_in)
        addresses = [row["address"] for row in reader]
        progress_total[job_id-1] = len(addresses)

        for addr in addresses:
            trades = fetch_trades(session, addr)

            if trades:
                # initialiser writer avec les champs du JSON + l'adresse
                if writer is None:
                    fieldnames = list(trades[0].keys()) + ["tokenAddress"]
                    writer = csv.DictWriter(f_out, fieldnames=fieldnames,
                                            extrasaction="ignore")
                    writer.writeheader()

                for trade in trades:
                    trade["tokenAddress"] = addr
                    writer.writerow(trade)

            # progression
            with progress_lock:
                progress_done[job_id-1] += 1
                display_progress()

    with progress_lock:
        display_progress()
        print(f"\n[✓ W{job_id}] Terminé → {out_path}")

# ────────────────────────────────────────────── MAIN
def main() -> None:
    # filtre les fichiers réellement présents
    present = [Path(p) for p in INPUT_FILES if Path(p).is_file()]
    if not present:
        print("Aucun fichier d’input trouvé.")
        return

    # init compteurs
    progress_done.extend([0] * len(present))
    progress_total.extend([0] * len(present))

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(present)) as ex:
        futures = [
            ex.submit(scrape_file, i+1, path)
            for i, path in enumerate(present)
        ]
        concurrent.futures.wait(futures)

    print("[✓] Tous les workers ont terminé.")

if __name__ == "__main__":
    main()
