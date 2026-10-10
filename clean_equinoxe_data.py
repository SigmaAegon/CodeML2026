#!/usr/bin/env python3
"""
Data Cleaning and Audit Pipeline for Équinoxe Datasets.

Processes:
  1. equinoxe_listings.csv         -> clean_equinoxe_listings.csv
  2. equinoxe_lease_history.csv    -> clean_equinoxe_lease_history.csv
  3. equinoxe_concessions.csv      -> clean_equinoxe_concessions.csv
  4. equinoxe_asking_history.csv   -> clean_equinoxe_asking_history.csv

Outputs:
  - Cleaned CSVs for each source dataset
  - cleaning_audit_report.csv summarizing changes and flags
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

# File mapping configuration
FILE_MAPPING = {
    "listings": {
        "input": "equinoxe_listings.csv",
        "output": "clean_equinoxe_listings.csv"
    },
    "lease_history": {
        "input": "equinoxe_lease_history.csv",
        "output": "clean_equinoxe_lease_history.csv"
    },
    "concessions": {
        "input": "equinoxe_concessions.csv",
        "output": "clean_equinoxe_concessions.csv"
    },
    "asking_history": {
        "input": "equinoxe_asking_history.csv",
        "output": "clean_equinoxe_asking_history.csv"
    }
}

# Explicit identifier columns to read as string (preserve leading zeros)
ID_COLUMNS = [
    "sPropCode", "sUnitCode", "hUnit", "hProp", "sBuilding", 
    "sSite", "hTenant", "hLease", "hConcession", "sCode", "sPostalCode", "sZip"
]

# Explicit date columns
DATE_COLUMNS = [
    "sLeaseFrom", "sLeaseTo", "dtMoveIn", "dtMoveOut", "dtStart", 
    "dtEnd", "dtEffective", "dtFrom", "dtTo", "dtCreated", "dtModified", "dtAvailable"
]

# Numeric columns
NUMERIC_COLUMNS = [
    "sRent", "sRentEffective", "curRent", "dAmount", "dMarketRent", 
    "dRent", "sqft", "dBath", "dBed", "iBeds", "iBaths", "sRenewal"
]


def append_flag(df: pd.DataFrame, mask: pd.Series, reason: str):
    """Appends flag reason to rows matching the mask condition."""
    df.loc[mask, "is_flagged"] = True
    df.loc[mask, "flag_reasons"] = df.loc[mask, "flag_reasons"].apply(
        lambda x: f"{x}; {reason}" if x else reason
    )


def clean_file(key: str, input_path: str, output_path: str) -> dict:
    """Cleans a single CSV file according to data rules and logs audit statistics."""
    if not os.path.exists(input_path):
        print(f"Skipping {input_path}: File not found.")
        return None

    # Force String Dtypes for ID Columns to keep leading zeros
    dtype_map = {col: "string" for col in ID_COLUMNS}
    
    # Read CSV
    df = pd.read_csv(input_path, dtype=dtype_map)
    initial_rows = len(df)

    # 1. Deduplication
    duplicates_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)

    # Initialize Audit Flag Columns
    df["is_flagged"] = False
    df["flag_reasons"] = ""

    # 2. String Cleaning on ID and Categorical Columns
    for col in df.columns:
        if col in ID_COLUMNS or col.startswith(("sProp", "sUnit", "h", "sBuilding", "sState")):
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})

    # 3. Standardize Date Fields
    for col in df.columns:
        if col in DATE_COLUMNS or "date" in col.lower() or col.startswith("dt"):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 4. Standardize Numeric Fields
    for col in df.columns:
        if col in NUMERIC_COLUMNS or "rent" in col.lower() or "amount" in col.lower():
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Data Quality Checks & Flagging (Preserve rows, flag anomalies)
    missing_critical = 0
    invalid_rents = 0
    invalid_dates = 0

    # Critical Identifiers missing
    crit_cols = [c for c in ["sPropCode", "sUnitCode"] if c in df.columns]
    if crit_cols:
        crit_mask = df[crit_cols].isna().any(axis=1)
        append_flag(df, crit_mask, "Missing building or unit identifier")
        missing_critical = int(crit_mask.sum())

    # Zero or Negative Rent Validation
    rent_cols = [c for c in ["sRent", "dAmount", "curRent", "dMarketRent"] if c in df.columns]
    for rcol in rent_cols:
        invalid_rent_mask = df[rcol].notna() & (df[rcol] <= 0)
        append_flag(df, invalid_rent_mask, f"Zero or negative value in {rcol}")
        invalid_rents += int(invalid_rent_mask.sum())

    # Date Sequence Validation
    if "sLeaseFrom" in df.columns and "sLeaseTo" in df.columns:
        invalid_seq = df["sLeaseFrom"].notna() & df["sLeaseTo"].notna() & (df["sLeaseTo"] < df["sLeaseFrom"])
        append_flag(df, invalid_seq, "Invalid lease date sequence (sLeaseTo < sLeaseFrom)")
        invalid_dates += int(invalid_seq.sum())

    if "dtStart" in df.columns and "dtEnd" in df.columns:
        invalid_seq = df["dtStart"].notna() & df["dtEnd"].notna() & (df["dtEnd"] < df["dtStart"])
        append_flag(df, invalid_seq, "Invalid date sequence (dtEnd < dtStart)")
        invalid_dates += int(invalid_seq.sum())

    if "dtFrom" in df.columns and "dtTo" in df.columns:
        invalid_seq = df["dtFrom"].notna() & df["dtTo"].notna() & (df["dtTo"] < df["dtFrom"])
        append_flag(df, invalid_seq, "Invalid date sequence (dtTo < dtFrom)")
        invalid_dates += int(invalid_seq.sum())

    # 6. Save Cleaned Dataset
    df.to_csv(output_path, index=False)

    flagged_count = int(df["is_flagged"].sum())
    final_rows = len(df)

    # Return summary dictionary for audit log
    return {
        "file_name": input_path,
        "output_file": output_path,
        "initial_row_count": initial_rows,
        "final_row_count": final_rows,
        "duplicate_rows_removed": duplicates_count,
        "missing_critical_ids": missing_critical,
        "invalid_rent_values": invalid_rents,
        "invalid_date_sequences": invalid_dates,
        "total_flagged_rows": flagged_count,
    }


def main():
    audit_records = []

    print("Starting Équinoxe Data Cleaning Pipeline...")
    for key, paths in FILE_MAPPING.items():
        metrics = clean_file(key, paths["input"], paths["output"])
        if metrics:
            audit_records.append(metrics)
            print(f"Processed {paths['input']} -> {paths['output']}")

    if audit_records:
        audit_df = pd.DataFrame(audit_records)
        audit_df.to_csv("cleaning_audit_report.csv", index=False)
        print("\nAudit report saved to cleaning_audit_report.csv")
        print("\n--- Audit Summary ---")
        print(audit_df[["file_name", "initial_row_count", "final_row_count", "duplicate_rows_removed", "total_flagged_rows"]].to_string(index=False))


if __name__ == "__main__":
    main()