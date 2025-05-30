import pandas as pd

# Chargement résilient
trades_df = pd.read_csv("token_trades_with_eth_price.csv", low_memory=False)
tokens_df = pd.read_csv("tokens_merged.csv")

# Nettoyage des noms de colonnes
trades_df.columns = trades_df.columns.str.strip()
tokens_df.columns = tokens_df.columns.str.strip()

# Normalisation des adresses
tokens_df["creator"] = tokens_df["creator"].str.lower()
trades_df["to"] = trades_df["to"].str.lower()

# Mapping tokenID → creator
token_creator_map = tokens_df.set_index("id")["creator"].to_dict()

# Ajout de la colonne creator
trades_df["creator"] = trades_df.apply(
    lambda row: 1 if token_creator_map.get(row["tokenID"]) == row["to"] else 0, axis=1
)

# Tri
trades_df = trades_df.sort_values(by=["tokenID", "timeStamp"], ascending=[False, False])

# Sauvegarde
trades_df.to_csv("token_trades_with_creator_flag.csv", index=False)
