#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fusionne et trie les fichiers « trades_*.csv ».

• Concatène trades_0000-1000.csv … trades_5000-6000.csv
• Supprime les doublons sur la colonne 'id'
• Trie d'abord par 'tokenID' décroissant
  puis, à l'intérieur de chaque tokenID, par 'timeStamp' décroissant
• Écrit le résultat dans 'trades_merged.csv'
"""

import glob
import pandas as pd

MERGED_NAME = "token_trades_merged.csv"

def main() -> None:
    # 1. Repérer les fichiers (on force l’ordre numérique pour éviter « 5000 » avant « 4000 »)
    csv_files = sorted(
        glob.glob("trades_*-[0-9][0-9][0-9][0-9].csv"),
        key=lambda p: int(p.split("_")[1].split("-")[0])
    )
    if not csv_files:
        print("Aucun fichier trades_*.csv trouvé.")
        return
    print(f"{len(csv_files)} fichiers détectés :", *csv_files, sep="\n   ")

    # 2. Chargement + concaténation
    frames = [pd.read_csv(path) for path in csv_files]
    df = pd.concat(frames, ignore_index=True)

    # 3. Suppression des doublons sur 'id'
    if "id" in df.columns:
        avant = len(df)
        df.drop_duplicates(subset="id", inplace=True)
        print(f"Doublons supprimés : {avant - len(df)}")

    # 4. Préparation des colonnes pour le tri
    if "tokenID" in df.columns:
        df["tokenID"] = pd.to_numeric(df["tokenID"], errors="coerce")

    if "timeStamp" in df.columns:
        # On convertit en datetime pour un tri fiable
        df["timeStamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

    # 5. Tri : tokenID ↓ puis timeStamp ↓
    df.sort_values(
        by=["tokenID", "timeStamp"],
        ascending=[False, False],   # deux tris décroissants
        inplace=True,
        na_position="last"
    )

    # 6. Sauvegarde
    df.to_csv(MERGED_NAME, index=False, encoding="utf-8")
    print(f"✔ Fusion + tri terminés – {len(df)} lignes écrites dans {MERGED_NAME}")

if __name__ == "__main__":
    main()
