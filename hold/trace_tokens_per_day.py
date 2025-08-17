#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
trace_tokens_per_day.py
-----------------------

Usage :
    python trace_tokens_per_day.py [mon_fichier.csv]

• Charge le CSV (par défaut : tokens_merged.csv)
• Convertit la colonne createDate en datetime
• Compte le nombre de tokens créés par jour
• Enregistre un CSV avec deux colonnes : timestamp, nb
• Trace une ligne « date » vs « nombre de tokens »
• Enregistre le PNG ET ouvre la fenêtre interactive
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
CSV_PATH     = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tokens_merged.csv")
PNG_OUT      = Path("tokens_per_day_log.png")
CSV_OUT      = Path("tokens_per_day.csv")

def main() -> None:
    if not CSV_PATH.exists():
        print(f"Fichier introuvable : {CSV_PATH}")
        sys.exit(1)

    # 1) lecture
    df = pd.read_csv(CSV_PATH)

    # 2) parse date → datetime ; on ignore les erreurs éventuelles
    df["createDate"] = pd.to_datetime(df["createDate"], errors="coerce")

    # 3) regrouper par jour et compter
    daily_counts = (
        df.set_index("createDate")
          .resample("D")
          .size()
          .rename("nb")
    ).reset_index().rename(columns={"createDate": "timestamp"})

    # 4) export CSV
    daily_counts.to_csv(CSV_OUT, index=False)
    print(f"CSV sauvegardé → {CSV_OUT}")

    # 5) tracé
    plt.figure(figsize=(10, 4))
    plt.plot(daily_counts["timestamp"], daily_counts["nb"], linewidth=1.5)
    plt.title("Nouveaux tokens par jour")
    plt.xlabel("Date")
    plt.ylabel("Nb de tokens créés")
    plt.grid(True)
    plt.tight_layout()
    plt.yscale("log")

    # 6) sauvegarde image
    plt.savefig(PNG_OUT, dpi=150)
    print(f"Graphique enregistré → {PNG_OUT}")

    # 7) affichage
    #plt.show()

if __name__ == "__main__":
    main()
