#!/usr/bin/env python3
# add_onchain_metrics.py
import pandas as pd
import numpy as np

# ------------------------------------------------------------------ #
# Chargement + nettoyage minimal
# ------------------------------------------------------------------ #
df = pd.read_csv("token_trades_with_buy_sell.csv", low_memory=False)
df.columns = df.columns.str.strip()

# ------------------------------------------------------------------ #
# Conversions numériques utiles
# ------------------------------------------------------------------ #
df["tokenChange"]   = pd.to_numeric(df["tokenChange"],   errors="coerce")
df["nativeVolume"]  = pd.to_numeric(df["nativeVolume"],  errors="coerce")
df["eth_usd_price"] = pd.to_numeric(df["eth_usd_price"], errors="coerce")
df["timeStamp"]     = pd.to_datetime(df["timeStamp"],    errors="coerce")

# ------------------------------------------------------------------ #
# Prix ETH par token sur chaque tx
# last_eth_price = |nativeVolume| / |tokenChange|
# ------------------------------------------------------------------ #
df["last_eth_price"] = df["nativeVolume"].abs() / df["tokenChange"].abs()
df.loc[~np.isfinite(df["last_eth_price"]), "last_eth_price"] = np.nan  # gère div/0

# ------------------------------------------------------------------ #
# Cumulatifs PAR TOKEN (du + ancien au + récent)
# ------------------------------------------------------------------ #
df = df.sort_values(["tokenID", "timeStamp"])          # ordre chrono pour cumsum

df["circulative_supply"] = df.groupby("tokenID")["tokenChange"]  .cumsum()
df["liquidity_eth"]      = df.groupby("tokenID")["nativeVolume"].cumsum()

# ------------------------------------------------------------------ #
# Métriques dérivées
# ------------------------------------------------------------------ #
df["liquidity_usd"]  = df["liquidity_eth"]   * df["eth_usd_price"]
df["market_cap_usd"] = df["circulative_supply"] * df["last_eth_price"] * df["eth_usd_price"]

# ------------------------------------------------------------------ #
# Tri final et sauvegarde
# ------------------------------------------------------------------ #
df = df.sort_values(["tokenID", "timeStamp"], ascending=[False, False])
df.to_csv("token_trades_with_onchain_metrics.csv", index=False)
print("✅ token_trades_with_onchain_metrics.csv créé.")
