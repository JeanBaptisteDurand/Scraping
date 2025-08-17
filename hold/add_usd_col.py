import duckdb

TRADES_CSV = "trades_merged.csv"
ETH_PRICE_CSV = "eth_price_per_minute.csv"

query = f"""
WITH trades AS (
    SELECT *,
           strftime(timeStamp, '%Y-%m-%d %H:%M:00') AS rounded_time
    FROM read_csv_auto(
        '{TRADES_CSV}', 
        header=True, 
        timestampformat='%Y-%m-%d %H:%M:%S.%f',
        sample_size=-1,
        types={{
            'nativeOut': 'VARCHAR',
            'nativeIn': 'VARCHAR',
            'tokenIn': 'VARCHAR',
            'tokenOut': 'VARCHAR',
            'tokenChange': 'DOUBLE',
            'nativeVolume': 'DOUBLE',
            'nativePrice': 'DOUBLE',
            'priceBefore': 'BIGINT',
            'priceAfter': 'BIGINT'
        }}
    )
),
eth_prices AS (
    SELECT *
    FROM read_csv_auto('{ETH_PRICE_CSV}', header=True)
)
SELECT 
    t.*, 
    p.eth_price AS eth_usd_price
FROM trades t
LEFT JOIN eth_prices p
    ON t.rounded_time = CAST(p.timestamp AS VARCHAR)
"""

df = duckdb.query(query).df()
df.to_csv("token_trades_with_eth_price.csv", index=False)
print("✅ token_trades_with_eth_price.csv created with eth_usd_price column")
