#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper pour l’API Ape.store
• Parcourt les pages jusqu’à ce que "items" soit vide
• Affiche chaque token et ses champs dans le terminal
• Enregistre tous les tokens dans un fichier CSV
• Pause : 1 s entre les pages, 3 s (puis retry) si la requête échoue
• Ajoute des en-têtes HTTP type navigateur (User-Agent, Origin, Referer…) pour éviter le 403
"""

import csv
import time
import requests
from typing import Dict, List

# ──────────────────────────────────────────────
BASE_URL       = "https://ape.store/api/tokens"
CSV_FILE       = "tokens.csv"
PAGE_DELAY_S   = 1   # délai entre deux pages
RETRY_DELAY_S  = 3   # délai avant retry en cas d’erreur réseau / 403
# En-têtes « navigateur » qui débloquent l’API
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Origin":  "https://ape.store",
    "Referer": "https://ape.store/",
}
# ──────────────────────────────────────────────


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
    resp.raise_for_status()                # soulève une exception si HTTP != 200
    return resp.json()


def main() -> None:
    page   = 0
    writer = None                          # sera initialisé à la 1ʳᵉ écriture

    with requests.Session() as session, \
         open(CSV_FILE, "w", newline="", encoding="utf-8") as f:

        while True:
            # ───────── Essai / retry ─────────
            try:
                data = fetch_page(session, page)
            except Exception as exc:
                print(f"[⚠] Problème sur la page {page} : {exc}. "
                      f"Nouvel essai dans {RETRY_DELAY_S}s…")
                time.sleep(RETRY_DELAY_S)
                continue

            items: List[Dict] = data.get("items", [])
            if not items:                  # {"items":[],"pageCount":48000} → fin
                print(f"[✔] Page {page} vide : arrêt du scraping.")
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

                # Affichage complet dans le terminal
                print(f"Token {id_} — {name} ({symbol})")
                for k, v in token.items():
                    print(f"   {k}: {v}")
                print("-" * 50)

                # Sauvegarde CSV
                writer.writerow(token)

            page += 1
            time.sleep(PAGE_DELAY_S)

    print(f"[✓] Scraping terminé. {page} pages parcourues. "
          f"Données sauvegardées dans « {CSV_FILE} ».")


if __name__ == "__main__":
    main()
