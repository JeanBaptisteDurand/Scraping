#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper pour l’API Ape.store
• 5 workers parallèles :
    - W1 : pages   0–1000
    - W2 : pages 1000–2000
    - W3 : pages 2000–3000
    - W4 : pages 3000–4000
    - W5 : pages 4000–5000
  (les pages 1000/2000/3000/4000 sont donc scannées deux fois)
• Même logique interne qu’à l’origine ; seule la parallélisation + les compteurs ont été ajoutées
"""

import csv
import sys
import time
import requests
import concurrent.futures
import threading
from typing import Dict, List, Tuple

# ──────────────────────────────────────────────
BASE_URL       = "https://ape.store/api/tokens"
PAGE_DELAY_S   = 1   # délai entre deux pages
RETRY_DELAY_S  = 3   # délai avant retry en cas d’erreur réseau / 403
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Origin":  "https://ape.store",
    "Referer": "https://ape.store/",
}
# Plages [start, end] inclusives + nom du CSV
JOBS: List[Tuple[int, int, str]] = [
    #(   0, 1000, "tokens_0000-1000.csv"),
    #(1000, 2000, "tokens_1000-2000.csv"),
    #(2000, 3000, "tokens_2000-3000.csv"),
    #(3000, 4000, "tokens_3000-4000.csv"),
    #(4000, 5000, "tokens_4000-5000.csv"),
    (5000, 6000, "tokens_5000-6000.csv"),
]
# Progression partagée entre threads
progress_lock = threading.Lock()
progress_pages_done = [0] * len(JOBS)                # pages déjà traitées
progress_total      = [end - start + 1 for start, end, _ in JOBS]
# ──────────────────────────────────────────────


def display_progress() -> None:
    """Écrit la ligne de progression en effaçant la précédente."""
    line = " | ".join(
        f"Worker{i+1} : {progress_pages_done[i]:4}/{progress_total[i]:4}"
        for i in range(len(JOBS))
    )
    # \r retour au début + \033[K efface jusqu’à la fin de ligne
    sys.stdout.write("\r\033[K" + line)
    sys.stdout.flush()


def fetch_page(session: requests.Session, page: int) -> Dict:
    """Récupère une page et renvoie le JSON sous forme de dict."""
    params = {
        "page":   page,
        "sort":   0,
        "order":  1,
        "filter": 0,
        "search": "",
        "chain":  0,
    }
    resp = session.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def scrape_range(job_id: int, start: int, end: int, csv_path: str) -> None:
    """Worker : pages [start, end] inclusives → csv_path."""
    page   = start
    writer = None

    with requests.Session() as session, \
         open(csv_path, "w", newline="", encoding="utf-8") as f:

        while page <= end:
            # ───────── Essai / retry ─────────
            try:
                data = fetch_page(session, page)
            except Exception as exc:
                with progress_lock:
                    print()
                print(f"\n[⚠ W{job_id}] Problème page {page} : {exc}. "
                      f"Retry dans {RETRY_DELAY_S}s…")
                time.sleep(RETRY_DELAY_S)
                continue

            items: List[Dict] = data.get("items", [])
            if not items:                  # page vide → stop
                break

            # ───────── Initialisation du CSV ─────────
            if writer is None:
                headers = list(items[0].keys())
                writer = csv.DictWriter(
                    f, fieldnames=headers, extrasaction="ignore"
                )
                writer.writeheader()

            # ───────── Parcours des tokens ─────────
            for token in items:
                # Variables individuelles (demandé)
                id_           = token["id"]
                chain         = token["chain"]
                protocol      = token["protocol"]
                creator       = token["creator"]
                create_date   = token["createDate"]
                deploy_date   = token["deployDate"]
                king_date     = token["kingDate"]
                launch_date   = token["launchDate"]
                address       = token["address"]
                name          = token["name"]
                symbol        = token["symbol"]
                description   = token["description"]
                twitter       = token["twitter"]
                telegram      = token["telegram"]
                website       = token["website"]
                logo          = token["logo"]
                is_dead       = token["isDead"]
                price_after   = token["priceAfter"]
                chat_count    = token["chatCount"]
                is_king       = token["isKing"]
                market_cap    = token["marketCap"]
                has_map       = token["hasMap"]
                dex_paid      = token["dexPaid"]
                is_streaming  = token["isStreaming"]
                stream_views  = token["streamViewers"]

                # Affichage détaillé désactivé ; on ne garde que la sauvegarde
                writer.writerow(token)

            # ───────── Mise à jour des compteurs ─────────
            with progress_lock:
                progress_pages_done[job_id - 1] += 1
                display_progress()

            page += 1
            time.sleep(PAGE_DELAY_S)

    # Affichage final propre pour ce worker (avec saut de ligne)
    with progress_lock:
        display_progress()
        print(f"\n[✓ W{job_id}] Terminé. Données dans « {csv_path} ».")


def main() -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(JOBS)) as executor:
        futures = [
            executor.submit(scrape_range, i + 1, start, end, csv_file)
            for i, (start, end, csv_file) in enumerate(JOBS)
        ]
        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
    print("\n[✓] Tous les workers ont terminé.")


if __name__ == "__main__":
    main()
