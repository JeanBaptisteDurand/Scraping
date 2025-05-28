#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fusionne tous les fichiers CSV "tokens_*.csv" présents dans le répertoire
courant et écrit un seul fichier "tokens_merged.csv".

• Lit chaque fichier avec pandas
• Concatène verticalement
• Supprime les doublons sur la colonne "id" (gardant la première occurrence)
• Conserve l'ordre original des colonnes
"""

import glob
import os
import pandas as pd

MERGED_NAME = "tokens_merged.csv"

def main() -> None:
    # 1. Trouve tous les fichiers tokens_*.csv (triés par nom)
    csv_files = sorted(glob.glob("tokens_*.csv"))
    if not csv_files:
        print("Aucun fichier tokens_*.csv trouvé dans le dossier courant.")
        return

    print(f"{len(csv_files)} fichier(s) détecté(s) :", *csv_files, sep="\n   ")

    # 2. Charge et concatène
    frames = []
    for path in csv_files:
        print(f"Chargement de {path} …")
        frames.append(pd.read_csv(path))

    df = pd.concat(frames, ignore_index=True)

    # 3. Supprime les doublons (colonne 'id')
    if "id" in df.columns:
        before = len(df)
        df.drop_duplicates(subset="id", inplace=True)
        print(f"Doublons supprimés : {before - len(df)}")

    # 4. Sauvegarde
    df.to_csv(MERGED_NAME, index=False, encoding="utf-8")
    print(f"✔ Fusion terminée → {MERGED_NAME} ({len(df)} lignes)")

if __name__ == "__main__":
    main()
