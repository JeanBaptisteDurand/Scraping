#!/usr/bin/env python3
# rebuild_cumulatives.py
import pandas as pd
import numpy as np

src  = "token_trades_with_buy_sell.csv"
dest = "token_trades_with_onchain_metrics.csv"

df = pd.read_csv(src, low_memory=False)
df.columns = df.columns.str.strip()

# ------------------------------------------------------------------ #
# Types
# ------------------------------------------------------------------ #
for col in ["tokenChange", "nativeVolume", "eth_usd_price", "buy_sell"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df["timeStamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

# ------------------------------------------------------------------ #
# 1) Chronologie ASCENDANTE pour un cumsum correct
# ------------------------------------------------------------------ #
df = df.sort_values(["tokenID", "timeStamp"])

# ------------------------------------------------------------------ #
# last_eth_price  (|ETH| / |tokens|)
# ------------------------------------------------------------------ #
df["last_eth_price"] = df["nativeVolume"].abs() / df["tokenChange"].abs()
df.loc[~np.isfinite(df["last_eth_price"]), "last_eth_price"] = np.nan

# ------------------------------------------------------------------ #
# Circulative supply  (cumul natif, signe déjà correct dans tokenChange)
# ------------------------------------------------------------------ #
df["circulative_supply"] = df.groupby("tokenID")["tokenChange"].cumsum()

# ------------------------------------------------------------------ #
# Liquidity ETH  (signe dépend de buy/sell)
#   buy  → +nativeVolume
#   sell → -nativeVolume
# ------------------------------------------------------------------ #
df["signed_eth"] = np.where(df["buy_sell"] == 0,
                            df["nativeVolume"],        # buy  → +
                            -df["nativeVolume"])       # sell → −
df["liquidity_eth"] = df.groupby("tokenID")["signed_eth"].cumsum()

# ------------------------------------------------------------------ #
# Valeurs USD
# ------------------------------------------------------------------ #
df["liquidity_usd"]  = df["liquidity_eth"] * df["eth_usd_price"]
df["market_cap_usd"] = (df["circulative_supply"]
                        * df["last_eth_price"]
                        * df["eth_usd_price"])

# ------------------------------------------------------------------ #
# 2) Affichage final : tokenID ↓ puis timeStamp ↓
# ------------------------------------------------------------------ #
df = df.sort_values(["tokenID", "timeStamp"], ascending=[False, False])

# Nettoyage colonne provisoire
df.drop(columns="signed_eth", inplace=True)

df.to_csv(dest, index=False)
print(f"✅ Cumulatifs reconstruits dans '{dest}'")
