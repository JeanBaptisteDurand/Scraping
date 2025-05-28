#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fusionne et trie (ordre décroissant) les fichiers "tokens_*.csv".

• Concatène tous les tokens_*.csv du dossier courant
• Supprime les doublons sur la colonne 'id'
• Trie par 'id' décroissant (le plus grand en haut)
• Écrit le résultat dans 'tokens_merged.csv'
"""

import glob
import pandas as pd

MERGED_NAME = "tokens_merged.csv"

def main() -> None:
    # 1. Trouver les fichiers
    csv_files = sorted(glob.glob("tokens_*.csv"))
    if not csv_files:
        print("Aucun fichier tokens_*.csv trouvé.")
        return
    print(f"{len(csv_files)} fichiers détectés :", *csv_files, sep="\n   ")

    # 2. Charger et concaténer
    frames = [pd.read_csv(path) for path in csv_files]
    df = pd.concat(frames, ignore_index=True)

    # 3. Supprimer les doublons
    if "id" in df.columns:
        avant = len(df)
        df.drop_duplicates(subset="id", inplace=True)
        print(f"Doublons supprimés : {avant - len(df)}")

    # 4. Tri décroissant sur 'id'
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="ignore")
        df.sort_values("id", ascending=False, inplace=True)  # ← ordre décroissant

    # 5. Sauvegarde
    df.to_csv(MERGED_NAME, index=False, encoding="utf-8")
    print(f"✔ Fusion + tri terminés – {len(df)} lignes écrites dans {MERGED_NAME}")

if __name__ == "__main__":
    main()
