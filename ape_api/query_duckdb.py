import duckdb

# change si besoin
CSV_FILE = "trades_merged.csv"

# exécution SQL sur CSV
result = duckdb.query(f"""
    SELECT COUNT(*) AS tx_count
    FROM read_csv_auto('{CSV_FILE}', header=True)
""").df()

print(result)

