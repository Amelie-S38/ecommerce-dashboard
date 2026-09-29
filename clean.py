import pandas as pd
import csv
df = pd.read_csv("data.csv")

# Conversion de la colonne InvoiceDate en format date
print("Type avant conversion :", df["InvoiceDate"].dtype)

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

print("Type après conversion :", df["InvoiceDate"].dtype)
print(df["InvoiceDate"].head())

# vérification pas d'inversion silencieuse dans les dates
print("\n--- Vérification de la plage de dates ---")
print("Date min :", df["InvoiceDate"].min())
print("Date max :", df["InvoiceDate"].max())

print("\n--- Nombre de lignes par mois ---")
print(df["InvoiceDate"].dt.month.value_counts().sort_index())

# Création d'une colonne pour les commandes annulées
df["IsCancelled"] = df["Invoice"].str.startswith("C")

print("\n--- Nombre d'annulations ---")
print(df["IsCancelled"].value_counts())

# Vérification que que toutes les lignes "annulée" on bien une quantité négative
annulations = df[df["IsCancelled"] == True]

print("\n--- Quantity sur les lignes annulées ---")
print(annulations["Quantity"].describe())

# A l'inverse, est ce que pour toutes les quantités négative on a une commande annulée ?
quantites_negatives = df[df["Quantity"] < 0]

print("\n--- IsCancelled sur les lignes à quantité négative ---")
print(quantites_negatives["IsCancelled"].value_counts())

# Vérification des 3457 False
print("\n--- Aperçu des Invoice à quantité négative mais non marquées annulées ---")

non_marquees = df[(df["Quantity"] < 0) & (df["IsCancelled"] == False)]

print(non_marquees["Invoice"].head(10))

# on vérifie pour ces lignes la description pour vérifier s'il s'agit d'annulation ou non
print(non_marquees[["Invoice", "Description", "Quantity"]].head(10)) 

# création d'une colonne calculant la somme gagné par ligne
df["LineTotal"] = df["Quantity"] * df["Price"]

# Création d'un DF des ventes
ventes = df[(df["Quantity"] > 0) & (df["Price"] > 0)].copy()

print("\n--- Lignes après filtrage ---")
print("Total lignes brutes :", len(df))
print("Total lignes ventes normales :", len(ventes))
print("\nCA total (ventes normales) :", ventes["LineTotal"].sum())

# vérification des lignes manquantes
print("\n--- Lignes avec Price <= 0 ---")

prix_invalides = df[df["Price"] <= 0]

print("Nombre de lignes :", len(prix_invalides))
print(prix_invalides[["Invoice", "Description", "Quantity", "Price"]].head(10))

# Repérer les codes "non-produits"
print("\n--- Codes produits suspects (sans chiffre) ---")

codes_suspects = ventes[~ventes["StockCode"].str.contains(r"\d", regex=True)]

print(codes_suspects["StockCode"].value_counts()) 

# Création d'une liste des codes à exclure et filtration
codes_a_exclure = ["POST", "DOT", "M", "m", "BANK CHARGES", "ADJUST", "D", "AMAZONFEE", "B", "S"]
ventes = ventes[~ventes["StockCode"].isin(codes_a_exclure)]

print("\n--- Lignes après exclusion des codes non-commerciaux ---")
print("Nombre de lignes :", len(ventes))

# Création des colonnes temporelles
ventes["Year"] = ventes["InvoiceDate"].dt.year
ventes["Quarter"] = ventes["InvoiceDate"].dt.quarter
ventes["Month"] = ventes["InvoiceDate"].dt.month

print("\n--- Aperçu des colonnes temporelles ---")
print(ventes[["InvoiceDate", "Year", "Quarter", "Month"]].head(10))

# Ajout d'une colonne YearMonth 
ventes["YearMonth"] = ventes["InvoiceDate"].dt.to_period("M").astype(str)

print("\n--- Aperçu YearMonth ---")
print(ventes[["InvoiceDate", "YearMonth"]].head(10))
print("\nValeurs uniques de YearMonth :", ventes["YearMonth"].nunique())

# Conversion de la colonne Customer ID en format str
ventes["Customer ID"] = ventes["Customer ID"].astype("Int64").astype(str)

print("\n--- Customer ID après conversion ---")
print(ventes["Customer ID"].head(10))
print(ventes["Customer ID"].dtype)

# vérification valeurs manquantes
print(ventes["Customer ID"].isnull().sum())

# Correction orthographe des colonnes Country et Description
ventes["Country"] = ventes["Country"].str.strip().str.title()
ventes["Description"] = ventes["Description"].str.strip().str.title()

print("\n--- Valeurs uniques de Country ---")
print(sorted(ventes["Country"].unique()))

# Correction des acronymes
ventes["Country"] = ventes["Country"].replace({"Usa": "USA", "Rsa": "RSA"})

print(ventes["Country"].unique())

# Export du fichier ventes en csv
import csv
ventes.to_csv("ventes_clean.csv", index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)

# Création d'une table dim_date
toutes_les_dates = pd.date_range(
    start=ventes["InvoiceDate"].min().normalize(),
    end=ventes["InvoiceDate"].max().normalize(),
    freq="D"
)
dim_date = pd.DataFrame({"Date": toutes_les_dates})

# Application sur les colonnes temporelles
dim_date["Year"] = dim_date["Date"].dt.year
dim_date["Quarter"] = dim_date["Date"].dt.quarter
dim_date["Month"] = dim_date["Date"].dt.month
dim_date["YearMonth"] = dim_date["Date"].dt.to_period("M").astype(str)

print("\n--- Aperçu dim_date ---")
print(dim_date.head())
print(dim_date.tail())
print("Nombre de jours :", len(dim_date))

# Export de la table en csv
dim_date.to_csv("dim_date.csv", index=False, encoding="utf-8-sig")

# Diagnostique problème sur colonne LineTotal sur Power BI
print("\n--- Diagnostic LineTotal ---")
print("Type de la colonne :", ventes["LineTotal"].dtype)

print("Valeurs manquantes :", ventes["LineTotal"].isnull().sum())

conversion_test = pd.to_numeric(ventes["LineTotal"], errors="coerce")
lignes_problematiques = ventes[conversion_test.isnull()]
print("\nNombre de lignes qui ne se convertissent pas en nombre :", len(lignes_problematiques))
print(lignes_problematiques[["Invoice", "Quantity", "Price", "LineTotal"]].head(20))

print("\n--- Descriptions contenant une virgule ---")
descriptions_avec_virgule = ventes[ventes["Description"].str.contains(",", na=False)]
print("Nombre de lignes concernées :", len(descriptions_avec_virgule))
print(descriptions_avec_virgule[["Invoice", "Description"]].head(10))