#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
trace_transactions_per_day.py
-----------------------------

Usage :
    python trace_transactions_per_day.py [mon_fichier.csv]

• Charge le CSV (par défaut : trades_merged.csv)
• Convertit la colonne timeStamp en datetime
• Compte le nombre de transactions par jour
• Enregistre un CSV : timestamp, nb
• Trace deux courbes :
    - une linéaire
    - une logarithmique
• Enregistre les PNGs et ouvre la fenêtre interactive
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
CSV_PATH       = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("trades_merged.csv")
PNG_OUT_NORMAL = Path("transactions_per_day.png")
PNG_OUT_LOG    = Path("transactions_per_day_log.png")
CSV_OUT        = Path("transactions_per_day.csv")

def main() -> None:
    if not CSV_PATH.exists():
        print(f"Fichier introuvable : {CSV_PATH}")
        sys.exit(1)

    # 1) lecture CSV
    df = pd.read_csv(CSV_PATH)

    # 2) parse timeStamp
    df["timeStamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

    # 3) compte des transactions par jour
    daily_counts = (
        df.set_index("timeStamp")
          .resample("D")
          .size()
          .rename("nb")
    ).reset_index().rename(columns={"timeStamp": "timestamp"})

    # 4) export CSV
    daily_counts.to_csv(CSV_OUT, index=False)
    print(f"CSV sauvegardé → {CSV_OUT}")

    # 5) courbe échelle normale
    plt.figure(figsize=(10, 4))
    plt.plot(daily_counts["timestamp"], daily_counts["nb"], label="Transactions", linewidth=1.5)
    plt.title("Nombre de transactions par jour")
    plt.xlabel("Date")
    plt.ylabel("Nombre de transactions")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(PNG_OUT_NORMAL, dpi=150)
    print(f"Graphique linéaire enregistré → {PNG_OUT_NORMAL}")

    # 6) courbe échelle logarithmique
    plt.figure(figsize=(10, 4))
    plt.plot(daily_counts["timestamp"], daily_counts["nb"], label="Transactions (log)", linewidth=1.5)
    plt.title("Nombre de transactions par jour (échelle logarithmique)")
    plt.xlabel("Date")
    plt.ylabel("Transactions (log)")
    plt.grid(True)
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(PNG_OUT_LOG, dpi=150)
    print(f"Graphique logarithmique enregistré → {PNG_OUT_LOG}")

    # 7) affichage interactif
    #plt.show()

if __name__ == "__main__":
    main()
