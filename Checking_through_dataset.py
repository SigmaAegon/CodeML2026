
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 160)

listings = pd.read_csv("equinoxe_listings.csv")
leases = pd.read_csv("equinoxe_lease_history.csv")
concessions = pd.read_csv("equinoxe_concessions.csv")
asking = pd.read_csv("equinoxe_asking_history.csv")

tables = {
    "listings": listings,
    "leases": leases,
    "concessions": concessions,
    "asking": asking
}

for name, df in tables.items():
    print(f"\n--- {name} ---")
    print("Shape:", df.shape)
    print("\nData types:")
    print(df.dtypes)
    print("\nMissing values:")
    print(df.isna().sum().sort_values(ascending=False).head(10))
    print("\nFirst 3 rows:")
    print(df.head(3))

# Parse dates in the tables where they belong
for col in ["sLeaseFrom", "sLeaseTo", "sSignDate"]:
    if col in leases.columns:
        leases[col] = pd.to_datetime(leases[col], errors="coerce")

if "sAvailable" in listings.columns:
    listings["sAvailable"] = pd.to_datetime(
        listings["sAvailable"], errors="coerce"
    )

if "sMonth" in asking.columns:
    asking["date"] = pd.to_datetime(
        asking["sMonth"].astype(str) + "-01",
        errors="coerce"
    )

# Derive lease year only after converting the date
if "sLeaseFrom" in leases.columns:
    leases["year"] = leases["sLeaseFrom"].dt.year