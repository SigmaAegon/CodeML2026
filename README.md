# CodeML2026
Analyze Equinoxe rental data using Python to identify rent trends, compare lease renewals and tenant turnovers, incorporate external housing and economic indicators, and develop and backtest a data-driven 2026 rent forecast for properties in Quebec and Ontario.

# Equinoxe Rental Market Analysis & 2026 Rent Forecast

## Overview

This project analyzes historical rental data from the Equinoxe residential property portfolio to understand rent trends, compare lease renewals and tenant turnovers, and develop a data-driven forecast of rent increases for 2026.

The project uses Python, pandas, NumPy, and Matplotlib to clean and explore rental datasets, visualize historical patterns, match leases for the same units over time, and evaluate forecasting methods through backtesting.

The analysis also considers external factors, including inflation, housing market indicators, and provincial rent regulations in Quebec and Ontario.

## Project Objectives

- Clean and validate rental datasets before analysis.
- Understand the composition of the rental portfolio.
- Analyze historical rents and changes in rent over time.
- Compare rent increases for lease renewals and tenant turnovers.
- Match consecutive leases for the same rental unit to reduce composition bias.
- Investigate the role of rental concessions in effective rent.
- Incorporate relevant external economic and housing market data.
- Develop a transparent rent forecast for 2026.
- Backtest forecasting methods using historical data from 2023 to 2025.

## Dataset

The project uses four primary CSV datasets:

| File | Description |
|---|---|
| `equinoxe_listings.csv` | Rental listing and property information |
| `equinoxe_lease_history.csv` | Historical lease records, rents, dates, and renewal information |
| `equinoxe_concessions.csv` | Rental concessions, discounts, and incentives |
| `equinoxe_asking_history.csv` | Historical asking rents and listing information over time |

Cleaned versions of the datasets use the `clean_` prefix.

> **Data note:** The source datasets may contain confidential or proprietary information. Do not publish raw or cleaned rental records to a public repository unless you have permission. Use anonymized or synthetic examples when sharing the project publicly.

>Note that the dataset has been removed because the compagny wanted it removed 

## Tools and Technologies

- **Python** — data processing and analysis
- **Jupyter Notebook** — exploratory analysis and documentation
- **pandas** — data cleaning, manipulation, and aggregation
- **NumPy** — numerical calculations
- **Matplotlib** — data visualization
- **CSV** — data storage and exchange

## Project Workflow

### 1. Data Cleaning and Validation

The cleaning process is designed to:

- Inspect column names and data types.
- Preserve property and unit identifiers as strings.
- Convert relevant date columns to datetime format.
- Convert rent, concession, and other numeric fields to appropriate numeric types.
- Identify missing values and duplicate records.
- Flag invalid or unusual rental amounts for investigation.
- Validate building and unit identifiers before joining datasets.
- Document cleaning decisions and exclusions.

Missing values are evaluated according to the requirements of each analysis rather than automatically deleting every incomplete row.

### 2. Exploratory Data Analysis

Exploratory analysis examines the structure and characteristics of the rental portfolio, including:

- Distribution of rents across properties.
- Asking rents compared with contractual rents.
- Historical rent trends.
- Differences between buildings.
- Changes in the composition of the rental portfolio.
- Missing values, unusual observations, and data quality issues.

Visualizations help identify patterns and potential problems before forecasting.

### 3. Same-Unit Lease Matching

Comparing portfolio-wide average rents can be misleading because the properties, units, or tenants represented in the data may change over time.

To reduce this composition effect, the project matches consecutive lease records for the same rental unit where reliable identifiers and dates are available.

For each matched pair, the analysis examines:

- Previous and subsequent contractual rent.
- Time between lease start dates.
- Annualized rent growth.
- Whether the later lease represents a renewal or a tenant turnover.
- Differences in rent growth across buildings and provinces.

Unit identifiers are checked before matching to reduce incorrect joins and duplicate lease pairs.

### 4. Lease Renewals and Tenant Turnovers

Renewals and turnovers are analyzed separately because they may reflect different rent-setting processes.

- **Renewals:** A subsequent lease associated with a continuing tenancy.
- **Turnovers:** A subsequent lease associated with a new tenancy.

The analysis uses the renewal/turnover status recorded for the later lease in each matched pair.

### 5. Rental Concessions

Concessions can make the effective cost of renting different from the contractual rent.

The project examines concession data to help distinguish between contractual rent and effective rent after incentives. Concession records must be matched and aggregated carefully to avoid multiplying lease records or counting the same incentive more than once.

### 6. External Data Analysis

External data may provide context for historical rental trends and the 2026 forecast.

Potential sources include:

- Consumer Price Index (CPI) data.
- Canada Mortgage and Housing Corporation (CMHC) rental market data.
- Quebec's Tribunal administratif du logement (TAL) rent-adjustment information.
- Ontario's annual rent increase guideline.
- Other relevant housing market and economic indicators.

External indicators are used as context rather than assumed to be direct measures of the rent increase for every unit. Quebec and Ontario have different regulatory frameworks, so provincial differences must be considered.

### 7. Forecasting and Backtesting

The forecasting component is intended to estimate rent increases for 2026 using historical rental patterns and relevant external information.

A backtesting procedure evaluates how the forecasting method would have performed in earlier years, using only information that would have been available at the time.

The planned backtesting period is 2023–2025.

Forecast evaluation considers:

- Predicted versus observed rent growth.
- The number of matched lease pairs available each year.
- Differences between renewals and turnovers.
- Differences between buildings and provinces.
- The limitations of historical data and the forecasting assumptions.

The objective is to produce a transparent, interpretable forecast rather than rely on model complexity alone.

## Installation

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd <YOUR-REPOSITORY-NAME>
```

Replace the placeholders with your repository URL and directory name.

### 2. Install Python dependencies

It is recommended to use a virtual environment.

```bash
python -m venv .venv
```

Activate it on Linux:

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install pandas numpy matplotlib jupyter
```

### 3. Launch Jupyter Notebook

```bash
jupyter notebook
```

Open the project notebook and run the cells in order, ensuring that the required datasets are available in the expected directory.

## Repository Structure

The project may be organized as follows:

```text
equinoxe-rent-analysis/
├── data/
│   ├── raw/
│   │   ├── equinoxe_listings.csv
│   │   ├── equinoxe_lease_history.csv
│   │   ├── equinoxe_concessions.csv
│   │   └── equinoxe_asking_history.csv
│   └── cleaned/
│       ├── clean_equinoxe_listings.csv
│       ├── clean_equinoxe_lease_history.csv
│       ├── clean_equinoxe_concessions.csv
│       └── clean_equinoxe_asking_history.csv
├── notebooks/
│   └── Submission.ipynb
├── scripts/
│   └── data_cleaning.py
|   └── ...
├── reports/
├── README.md
├── requirements.txt
└── .gitignore
```
Note: this structure is not the structure in the github, because the company wanted their csv removed.

This is a suggested structure; filenames and folders should be adjusted to match the actual repository.

## Key Considerations and Limitations

- Portfolio-wide rent changes may reflect changes in the units being rented, not only increases for existing units.
- Same-unit comparisons depend on the consistency and reliability of unit identifiers.
- Asking rents, contractual rents, and effective rents measure different things.
- Concessions may affect effective rent and must be handled carefully.
- Historical lease records may not represent all rental activity or vacancies.
- External market indicators may not directly predict individual unit rent increases.
- Quebec and Ontario rent regulations differ and should not be treated as interchangeable.
- Backtesting results depend on data quality, sample sizes, and assumptions.

## Expected Deliverables

The intended project deliverables include:

- Cleaned and validated rental datasets.
- A data-cleaning audit report.
- Exploratory visualizations and descriptive statistics.
- Same-unit lease matching and rent-growth analysis.
- Renewal-versus-turnover comparisons.
- External data analysis.
- A 2026 rent forecast.
- Historical backtesting results.
- A documented and reproducible Jupyter Notebook.

## Future Improvements

- Improve the matching and validation of lease records.
- Incorporate additional reliable housing market indicators.
- Improve the treatment of concessions and effective rent.
- Compare forecasting methods using consistent backtesting procedures.
- Quantify forecast uncertainty.
- Automate data validation and report generation.

## Disclaimer

This project is an analytical exercise intended to study historical rental patterns and develop a transparent forecasting approach. Forecasts are estimates, not guarantees of future rent changes or legal determinations of permissible rent increases.

All conclusions depend on the quality, coverage, and limitations of the available data.

