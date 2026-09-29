import pandas as pd
df = pd.read_csv("data.csv")
print(df.head(10))
print("\n--- Dimensions ---")
print(df.shape)

print("\n--- Types de colonnes ---")
print(df.dtypes)

print("\n--- Valeurs manquantes ---")
print(df.isnull().sum())

print("\n--- Statistiques descriptives ---")
print(df.describe())