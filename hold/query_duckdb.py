#!/usr/bin/env python3
import duckdb
import sys

# Récupération de l'argument seuil depuis la ligne de commande
if len(sys.argv) < 2:
    print("Usage: python script.py <seuil_liquidity_usd>")
    sys.exit(1)

seuil = float(sys.argv[1])
TRADES_CSV = "token_trades_with_onchain_metrics.csv"

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
)
SELECT
    COUNT(*) AS nb_tokens
FROM (
    SELECT tokenID
    FROM trades
    GROUP BY tokenID
    HAVING MAX(liquidity_usd) > {seuil}
) AS t;
"""

# Exécution et affichage du résultat
result = duckdb.query(query).fetchone()[0]
print(f"✅ Nombre de tokens avec au moins une ligne où liquidity_usd > {seuil}: {result}")
