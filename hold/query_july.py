#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import duckdb
import sys
from datetime import datetime, date, time

# ────────────────────────────────────────────── CLI
if len(sys.argv) < 2:
    print("Usage: python script.py <seuil_liquidity_usd> [chemin_csv]")
    sys.exit(1)

seuil = float(sys.argv[1])
TRADES_CSV = sys.argv[2] if len(sys.argv) > 2 else "token_trades_with_onchain_metrics.csv"

# ────────────────────────────────────────────── Fenêtre temporelle
# Du 2025-07-01 00:00:00 (inclus) à aujourd'hui (ex: 2025-08-17) 23:59:59.999999 (inclus)
START_TS = "2025-07-01 00:00:00"
today = date.today()
END_TS = datetime.combine(today, time.max).strftime("%Y-%m-%d %H:%M:%S.%f")

query = f"""
WITH trades AS (
    SELECT
        CAST(id                  AS BIGINT)            AS id,
        CAST(tokenID             AS BIGINT)            AS tokenID,
        "to"                                          AS to_address,
        CAST(timeStamp           AS TIMESTAMP)         AS timeStamp,
        transactionHash,
        CAST(tokenIn             AS DOUBLE)            AS tokenIn,
        CAST(nativeIn            AS DOUBLE)            AS nativeIn,
        CAST(tokenOut            AS DOUBLE)            AS tokenOut,
        CAST(nativeOut           AS DOUBLE)            AS nativeOut,
        CAST(priceBefore         AS BIGINT)            AS priceBefore,
        CAST(priceAfter          AS BIGINT)            AS priceAfter,
        CAST(tokenChange         AS DOUBLE)            AS tokenChange,
        CAST(nativeVolume        AS DOUBLE)            AS nativeVolume,
        key,
        CAST(nativePrice         AS DOUBLE)            AS nativePrice,
        CAST(bump                AS BOOLEAN)           AS bump,
        tokenAddress,
        strftime(timeStamp, '%Y-%m-%d %H:%M:00')       AS rounded_time,
        CAST(eth_usd_price       AS DOUBLE)            AS eth_usd_price,
        creator,
        CAST(buy_sell            AS SMALLINT)          AS buy_sell,
        CAST(last_eth_price      AS DOUBLE)            AS last_eth_price,
        CAST(circulative_supply  AS DOUBLE)            AS circulative_supply,
        CAST(liquidity_eth       AS DOUBLE)            AS liquidity_eth,
        CAST(liquidity_usd       AS DOUBLE)            AS liquidity_usd,
        CAST(market_cap_usd      AS DOUBLE)            AS market_cap_usd
    FROM read_csv_auto(
        '{TRADES_CSV}',
        header = TRUE,
        timestampformat = '%Y-%m-%d %H:%M:%S.%f',
        sample_size = -1
    )
),
-- Première apparition de chaque token dans TOUT le CSV
first_seen AS (
    SELECT tokenID, MIN(timeStamp) AS first_seen_ts
    FROM trades
    GROUP BY tokenID
),
-- Fenêtre temporelle demandée
period_trades AS (
    SELECT *
    FROM trades
    WHERE timeStamp >= TIMESTAMP '{START_TS}'
      AND timeStamp <= TIMESTAMP '{END_TS}'
),
-- Tokens "créés" dans la période (première apparition ∈ [START, END])
tokens_created_in_period AS (
    SELECT f.tokenID
    FROM first_seen f
    WHERE f.first_seen_ts >= TIMESTAMP '{START_TS}'
      AND f.first_seen_ts <= TIMESTAMP '{END_TS}'
),
-- Tokens (quel que soit leur âge) ayant atteint le seuil de liquidité pendant la période
tokens_reaching_threshold_in_period AS (
    SELECT tokenID
    FROM period_trades
    GROUP BY tokenID
    HAVING MAX(COALESCE(liquidity_usd, 0)) >= {seuil}
),
-- Intersections : tokens créés dans la période ET ayant atteint le seuil dans la période
created_and_reached AS (
    SELECT c.tokenID
    FROM tokens_created_in_period c
    INNER JOIN tokens_reaching_threshold_in_period r
      ON c.tokenID = r.tokenID
)

SELECT
    (SELECT COUNT(*) FROM tokens_created_in_period)                       AS nb_tokens_created,
    (SELECT COUNT(*) FROM tokens_reaching_threshold_in_period)            AS nb_tokens_reached_threshold_any_age,
    (SELECT COUNT(*) FROM created_and_reached)                            AS nb_created_and_reached_threshold;
"""

nb_created, nb_reached_any_age, nb_created_and_reached = duckdb.query(query).fetchone()

print(f"📅 Période: du {START_TS} au {END_TS}")
print(f"✅ Tokens créés dans la période: {nb_created}")
print(f"💧 Tokens (tous âges) ayant atteint une liquidité ≥ {seuil:.2f} USD dans la période: {nb_reached_any_age}")
print(f"🎯 Parmi les tokens créés dans la période, ceux ayant atteint une liquidité ≥ {seuil:.2f} USD: {nb_created_and_reached}")
