#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
trace_eth_buy_volume_per_day.py
-------------------------------

Usage :
    python trace_eth_buy_volume_per_day.py [mon_fichier.csv]

• Charge le CSV (par défaut : trades_merged.csv)
• Convertit la colonne timeStamp en datetime
• Filtre les achats où nativeIn > 0 (ETH entrant)
• Convertit nativeIn de wei → ETH
• Additionne le volume ETH par jour
• Enregistre un CSV : timestamp, volume_eth
• Trace deux courbes :
    - une linéaire
    - une logarithmique
• Enregistre les PNG (et affiche rien si plt.show() est commenté)
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
CSV_PATH         = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("token_trades_with_onchain_metrics.csv")
PNG_OUT_NORMAL   = Path("eth_buy_volume_per_day.png")
PNG_OUT_LOG      = Path("eth_buy_volume_per_day_log.png")
CSV_OUT          = Path("eth_buy_volume_per_day.csv")

ETH_WEI = 10 ** 18

def main() -> None:
    if not CSV_PATH.exists():
        print(f"Fichier introuvable : {CSV_PATH}")
        sys.exit(1)

    # 1) lecture CSV
    #    (on laisse pandas inférer; on forcera la conversion numérique après)
    df = pd.read_csv(CSV_PATH)

    # 2) parse timeStamp
    if "timeStamp" not in df.columns:
        print("Colonne 'timeStamp' absente du CSV.")
        sys.exit(1)
    df["timeStamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

    # 3) conversion nativeIn en ETH et filtrage achats (nativeIn > 0)
    if "nativeIn" not in df.columns:
        print("Colonne 'nativeIn' absente du CSV.")
        sys.exit(1)

    df["nativeIn"] = pd.to_numeric(df["nativeIn"], errors="coerce")
    df["nativeIn_eth"] = df["nativeIn"] / ETH_WEI

    # Garde uniquement les lignes avec timeStamp valide et un montant ETH entrant
    df_buy = df[(df["timeStamp"].notna()) & (df["nativeIn_eth"] > 0)]

    if df_buy.empty:
        print("Aucun achat détecté (nativeIn > 0).")
        # On sort quand même un CSV vide cohérent
        pd.DataFrame(columns=["timestamp", "volume_eth"]).to_csv(CSV_OUT, index=False)
        sys.exit(0)

    # 4) agrégation par jour (somme des ETH)
    daily_volume = (
        df_buy.set_index("timeStamp")["nativeIn_eth"]
              .resample("D")
              .sum()
              .rename("volume_eth")
              .reset_index()
              .rename(columns={"timeStamp": "timestamp"})
    )

    # 5) export CSV
    daily_volume.to_csv(CSV_OUT, index=False)
    print(f"CSV sauvegardé → {CSV_OUT}")

    # 6) courbe échelle normale
    plt.figure(figsize=(10, 4))
    plt.plot(daily_volume["timestamp"], daily_volume["volume_eth"], label="Volume achats (ETH)", linewidth=1.5)
    plt.title("Volume d’achats en ETH par jour")
    plt.xlabel("Date")
    plt.ylabel("Volume (ETH)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(PNG_OUT_NORMAL, dpi=150)
    print(f"Graphique linéaire enregistré → {PNG_OUT_NORMAL}")

    # 7) courbe échelle logarithmique
    plt.figure(figsize=(10, 4))
    plt.plot(daily_volume["timestamp"], daily_volume["volume_eth"], label="Volume achats (ETH, log)", linewidth=1.5)
    plt.title("Volume d’achats en ETH par jour (échelle logarithmique)")
    plt.xlabel("Date")
    plt.ylabel("Volume (ETH, log)")
    plt.grid(True)
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(PNG_OUT_LOG, dpi=150)
    print(f"Graphique logarithmique enregistré → {PNG_OUT_LOG}")

    # 8) affichage interactif si tu veux
    # plt.show()

if __name__ == "__main__":
    main()
