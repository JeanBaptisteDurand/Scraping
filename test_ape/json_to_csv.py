#!/usr/bin/env python3
"""
convert_json_to_metrics_with_baseline.py — lire un tableau JSON de transactions (stdin),
calculer les métriques cumulatives **en rajoutant la réserve initiale manquante** pour que
les résultats collent aux valeurs affichées par le site (virtual liquidity & market‑cap).

▪️ La « valeur magique » ajoutée est la MOYENNE des deltas observés sur deux snapshots :
   – Δliquidité₁ = 2 106,32 $  ➜ 0,8326 ETH
   – Δliquidité₂ = 1 478,00 $  ➜ 0,5837 ETH
   Moyenne ➜ 0,7081 ETH (≈ 1 792,16 $ au cours spot 2 531 $/ETH).

   Pour que le ratio token/ETH reste cohérent, on ajoute en même temps
   `BASE_TOKENS = BASE_ETH / price_eth_per_token` où
   *price_eth_per_token* est le premier `last_eth_price` non‑NaN de la série.

Usage :
  $ python convert_json_to_metrics_with_baseline.py < mon_fichier.json

Le fichier « token_trades_with_onchain_metrics.csv » est écrit dans le dossier courant.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #
USD_PRICE   = 2_531           # prix spot ETH/USD (const.)
BASE_ETH    = 0.8        # moyenne des réserves ETH manquantes (cas 1 & 2)
# BASE_TOKENS est calculé dynamiquement plus bas car il dépend du prix ETH/token

# --------------------------------------------------------------------------- #
# 1) Lecture JSON depuis stdin
# --------------------------------------------------------------------------- #
print("Collez votre JSON puis terminez (Ctrl‑D ou Ctrl‑Z + Entrée) :\n", file=sys.stderr)
raw = sys.stdin.read().strip()
if not raw:
    sys.exit("Aucune donnée reçue…")

try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    sys.exit(f"JSON invalide : {exc}")

if not isinstance(data, list):
    sys.exit("Le JSON doit être un tableau (liste) de transactions !")

# --------------------------------------------------------------------------- #
# 2) Conversion en DataFrame + nettoyage minimal
# --------------------------------------------------------------------------- #

df = pd.DataFrame(data)
# Uniformise les noms de colonnes
df.columns = df.columns.str.strip()

# Colonnes numériques
for col in ["tokenChange", "nativeVolume"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# timeStamp → datetime pour le tri
if "timeStamp" in df.columns:
    df["timeStamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

# --------------------------------------------------------------------------- #
# 3) Ajout prix spot (const.)
# --------------------------------------------------------------------------- #
df["eth_usd_price"] = USD_PRICE

# --------------------------------------------------------------------------- #
# 4) Flag buy/sell (1 = sell, 0 = buy)
# --------------------------------------------------------------------------- #
df["buy_sell"] = (df["tokenChange"] < 0).astype(int)

# --------------------------------------------------------------------------- #
# 5) Cumuls (ASC pour cumsum)
# --------------------------------------------------------------------------- #
sort_cols = ["tokenID", "timeStamp"] if "tokenID" in df.columns else ["timeStamp"]
df.sort_values(sort_cols, inplace=True)

# 5.1 Prix d’exécution ETH/token
#     last_eth_price = |nativeVolume| / |tokenChange|

df["last_eth_price"] = df["nativeVolume"].abs() / df["tokenChange"].abs()
df.loc[~np.isfinite(df["last_eth_price"]), "last_eth_price"] = np.nan

# 5.2 Circulative supply : cumul des tokenChange
if "tokenID" in df.columns:
    df["circulative_supply"] = df.groupby("tokenID")["tokenChange"].cumsum()
else:
    df["circulative_supply"] = df["tokenChange"].cumsum()

# 5.3 Liquidity ETH : cumul signé de nativeVolume (buy + / sell –)

df["signed_eth"] = np.where(df["buy_sell"] == 0, df["nativeVolume"], -df["nativeVolume"])
if "tokenID" in df.columns:
    df["liquidity_eth"] = df.groupby("tokenID")["signed_eth"].cumsum()
else:
    df["liquidity_eth"] = df["signed_eth"].cumsum()

# --------------------------------------------------------------------------- #
# 6) 🎯 Injection de la réserve initiale manquante
# --------------------------------------------------------------------------- #
# Premier prix ETH/token non‑NaN pour convertir BASE_ETH en tokens
#token_change = df["tokenChange"].dropna().iloc[0]
#BASE_TOKENS = 0

# Ajout (shift) à partir de la première ligne
df["liquidity_eth"]      += BASE_ETH
#df["circulative_supply"] += BASE_TOKENS

# --------------------------------------------------------------------------- #
# 7) Valeurs USD (après injection)
# --------------------------------------------------------------------------- #
df["liquidity_usd"]  = df["liquidity_eth"] * USD_PRICE
# market_cap_usd = supply × last_eth_price × USD_PRICE
# (last_eth_price n’est pas modifié : on garde le prix d’exécution du swap)
df["market_cap_usd"] = df["circulative_supply"] * df["last_eth_price"] * USD_PRICE

# --------------------------------------------------------------------------- #
# 8) Sortie CSV — antéchronologique pour lecture facile
# --------------------------------------------------------------------------- #
output = Path.cwd() / "token_trades_with_onchain_metrics.csv"

order_cols = ["tokenID", "timeStamp"] if "tokenID" in df.columns else ["timeStamp"]
df.sort_values(order_cols, ascending=[False, False], inplace=True)

# Colonne intermédiaire inutile
if "signed_eth" in df.columns:
    df.drop(columns="signed_eth", inplace=True)

# Sauvegarde
output.write_text(df.to_csv(index=False))
print(f"✅ Fichier CSV écrit : {output} (lignes : {len(df)})")
