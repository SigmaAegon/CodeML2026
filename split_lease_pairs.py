#!/usr/bin/env python3
"""
Split matched lease-to-lease rent growth into Québec/Ontario and renewal/turnover CSVs.

Default input: clean_equinoxe_lease_history.csv
Default outputs: four CSVs in the current directory.

Matching uses sPropCode + sUnitCode (not sSite + sUnitCode). Consecutive leases
for a unit are paired chronologically. Only pairs with 0.5–2.5 years between
lease start dates are retained. Growth is annualized from contractual sRent.
The renewal/turnover label comes from sRenewal on the later lease.
"""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np

GROUPS = {
    ("Quebec", "Renewal"): "quebec_renewals.csv",
    ("Quebec", "Turnover"): "quebec_turnovers.csv",
    ("Ontario", "Renewal"): "ontario_renewals.csv",
    ("Ontario", "Turnover"): "ontario_turnovers.csv",
}

def build_pairs(df: pd.DataFrame) -> pd.DataFrame:
    required = ["sPropCode", "sUnitCode", "sState", "sBuilding",
                "sLeaseFrom", "sRent", "sRenewal"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    d = df.copy()
    d["sLeaseFrom"] = pd.to_datetime(d["sLeaseFrom"], errors="coerce")
    d["sRent"] = pd.to_numeric(d["sRent"], errors="coerce")
    d["sRenewal"] = pd.to_numeric(d["sRenewal"], errors="coerce")
    d = d.dropna(subset=["sPropCode", "sUnitCode", "sState", "sLeaseFrom", "sRent"])
    d = d[d["sRent"] > 0].copy()
    d["province"] = d["sState"].astype("string").str.strip().str.casefold().map(
        {"quebec": "Quebec", "québec": "Quebec", "ontario": "Ontario"}
    )
    unknown = sorted(d.loc[d["province"].isna(), "sState"].astype(str).unique())
    if unknown:
        raise ValueError(f"Unrecognized sState values: {unknown}")

    d = d.sort_values(["sPropCode", "sUnitCode", "sLeaseFrom"]).reset_index(drop=True)
    # Shift within the same property/unit to form consecutive lease pairs.
    keys = ["sPropCode", "sUnitCode"]
    grouped = d.groupby(keys, dropna=False, sort=False)
    d["prior_lease_from"] = grouped["sLeaseFrom"].shift(1)
    d["prior_rent"] = grouped["sRent"].shift(1)
    d["prior_lease_to"] = grouped["sLeaseTo"].shift(1) if "sLeaseTo" in d else pd.NaT
    d["prior_renewal"] = grouped["sRenewal"].shift(1)
    d["prior_building"] = grouped["sBuilding"].shift(1)
    d["prior_state"] = grouped["sState"].shift(1)

    d["days_between"] = (d["sLeaseFrom"] - d["prior_lease_from"]).dt.days
    d["years_between"] = d["days_between"] / 365.25
    d = d[d["prior_lease_from"].notna() & d["years_between"].between(0.5, 2.5)].copy()
    d = d[(d["prior_rent"] > 0) & (d["prior_state"] == d["sState"]) &
          (d["prior_building"] == d["sBuilding"])].copy()

    d["growth_pct"] = (
        (d["sRent"] / d["prior_rent"]) ** (365.25 / d["days_between"]) - 1
    ) * 100
    d["year"] = d["sLeaseFrom"].dt.year
    d["lease_type"] = np.where(d["sRenewal"].eq(1), "Renewal", "Turnover")
    d["prior_sRent"] = d["prior_rent"]
    d["current_sRent"] = d["sRent"]
    d["prior_sLeaseFrom"] = d["prior_lease_from"]
    d["current_sLeaseFrom"] = d["sLeaseFrom"]

    cols = [
        "province", "sBuilding", "sPropCode", "sUnitCode", "hUnit",
        "prior_sLeaseFrom", "current_sLeaseFrom", "prior_lease_to",
        "prior_sRent", "current_sRent", "days_between", "years_between",
        "growth_pct", "year", "lease_type", "prior_renewal", "sRenewal",
    ]
    cols = [c for c in cols if c in d.columns]
    result = d[cols].rename(columns={
        "sPropCode": "property_code", "sUnitCode": "unit_code",
        "hUnit": "unit_id", "sBuilding": "building",
        "prior_lease_to": "prior_sLeaseTo",
        "prior_renewal": "prior_sRenewal", "sRenewal": "current_sRenewal",
    })
    return result.sort_values(["province", "building", "unit_code", "current_sLeaseFrom"])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="clean_equinoxe_lease_history.csv",
                        help="Lease history CSV (default: clean file)")
    parser.add_argument("--outdir", default=".", help="Output directory")
    args = parser.parse_args()

    df = pd.read_csv(args.input, dtype={"sPropCode": "string",
                                        "sUnitCode": "string",
                                        "hUnit": "string"})
    pairs = build_pairs(df)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for (province, lease_type), filename in GROUPS.items():
        subset = pairs[(pairs["province"] == province) &
                       (pairs["lease_type"] == lease_type)].copy()
        path = outdir / filename
        subset.to_csv(path, index=False)
        print(f"{path}: {len(subset)} matched pairs")

    print(f"Total retained matched pairs: {len(pairs)}")
    print("Note: These are observed historical pairs, not 2026 forecasts.")

if __name__ == "__main__":
    main()
