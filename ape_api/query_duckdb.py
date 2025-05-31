import duckdb

TRADES_CSV = "token_trades_merged.csv"
ETH_PRICE_CSV = "eth_price_per_minute.csv"

query = f"""
WITH trades AS (
    /* ------------------------------------------------------------------
       Définition « propre » de la table CTE `trades`
       ------------------------------------------------------------------ */
    SELECT
        CAST(id                  AS BIGINT)            AS id,
        CAST(tokenID             AS BIGINT)            AS tokenID,
        /* Adresse du receveur : pas de mot-clé réservé ⟶ alias explicite */
        "to"                                          AS to_address,
        /* Horodatage complet → TIMESTAMP natif */
        CAST(timeStamp           AS TIMESTAMP)         AS timeStamp,
        transactionHash,

        /* Montants : on force DOUBLE pour autoriser les calculs décimaux */
        CAST(tokenIn             AS DOUBLE)            AS tokenIn,
        CAST(nativeIn            AS DOUBLE)            AS nativeIn,
        CAST(tokenOut            AS DOUBLE)            AS tokenOut,
        CAST(nativeOut           AS DOUBLE)            AS nativeOut,

        /* Prix avant / après : BIGINT car ce sont des entiers sur la chaîne */
        CAST(priceBefore         AS BIGINT)            AS priceBefore,
        CAST(priceAfter          AS BIGINT)            AS priceAfter,

        CAST(tokenChange         AS DOUBLE)            AS tokenChange,
        CAST(nativeVolume        AS DOUBLE)            AS nativeVolume,
        key,

        CAST(nativePrice         AS DOUBLE)            AS nativePrice,
        CAST(bump                AS BOOLEAN)           AS bump,
        tokenAddress,

        /* Arrondi à la minute près → pratique pour les jointures temporelles */
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
        sample_size = -1          -- lecture complète
    )
    /* ------------------------------------------------------------------ */
)
SELECT *
FROM trades
"""

df = duckdb.query(query).df()
df.to_csv("token_trades_with_eth_price.csv", index=False)
print("✅ token_trades_with_eth_price.csv created with eth_usd_price column")
