#!/usr/bin/env python3
# add_buy_sell_flag.py
import pandas as pd

# Chargement
df = pd.read_csv("token_trades_with_creator_flag.csv", low_memory=False)

# Nettoyage des noms de colonnes
df.columns = df.columns.str.strip()

# Ajout de buy_sell  (1 si tokenChange < 0, sinon 0)
df["tokenChange"] = pd.to_numeric(df["tokenChange"], errors="coerce")
df["buy_sell"] = (df["tokenChange"] < 0).astype(int)

# Tri : tokenID ↓ puis timeStamp ↓
df = df.sort_values(["tokenID", "timeStamp"], ascending=[False, False])

# Sauvegarde
df.to_csv("token_trades_with_buy_sell.csv", index=False)
print("✅ token_trades_with_buy_sell.csv créé.")
