# How Geopolitical Conflict Reshapes Global Energy Trade
## How the Iran conflict reshaped Global Oil Shipping Routes 

## 👥 Team Members

- Ai Nakayama (@ainakayama90) - Reader and Subject Specialist  
- Akyla Imanalieva (@akylaimanalieva) - Trouble shooting and Git specialist. Git arragments. 
- Aston Chia (@AstonChia99) - Data Specialist  
- Ririka Noda (@RirikaNoda) - Reader and Subject Specialist 
- Mami Umeki (@mamiumeki01) - Data Specialist 
- Special thanks to Claude 

# Strait of Hormuz: Assumption Testing Framework

This repository contains the data, modeling, and analytical frameworks used to conduct **Assumption Testing** regarding geopolitical, security, and trade dynamics in the Strait of Hormuz. 

Using Structured Analytic Techniques (SATs), this project identifies, explicitly states, and systematically challenges the core assumptions underlying current policy models and security assessments in this critical maritime chokepoint.


## ❓ Research Question & 🎯 Hypothesis

Topic: How has the US-Iran conflict reshape oil trade routes 

Aim to answer: 
1)        Did tanker traffic through the Strait of Malacca change?
2)        Which chokepoints absorbed rerouted flows?

## 📌 Project Overview
The Strait of Hormuz is one of the world's most strategically important choke points. Policy decisions often rely on deep-seated assumptions regarding state behavior, shipping resilience, and military escalation thresholds. This project subjects those assumptions to empirical and qualitative testing to uncover vulnerabilities, hidden variables, and low-probability, high-impact risks.

## 🛠 Tested Assumptions & Core Scenarios
The framework evaluates several critical hypotheses, including:
* **Assumption 1:** Supply chain elasticity can absorb a temporary closure through alternative routes (e.g., East West Pipeline).
* **Assumption 2:** Escalation dynamics follow predictable, linear deterrence models.
* **Assumption 3:** Non-state actor interventions remain constrained by state sponsor strategic boundaries.

## 📊 Methodology & Repository Structure
This repository contains data pipelines, quantitative models, and econometric analyses used to rigorously test assumptions regarding a potential disruption in the **Strait of Hormuz** and the viability of alternative global crude oil transit routes (e.g., the Malacca Strait, Singapore hubs, and alternative overland pipelines).

## 📊 Repository Structure

Strait-of-Hormuz-Assumption-Testing
├── Data_Loader/              # Data fetching, transformation, and ingestion modules
│   ├── __init__.py
│   ├── libraries.py          # Unified dependencies list
│   ├── dataloader_main.py    # Main orchestration script
│   ├── hormuz_strait_data.py # Hormuz specific data filters
│   ├── dataloader_oil.py     # Global oil trade metrics
│   ├── dataloader_pipeline.py# Overland pipeline data processing (e.g., Yanbu)
│   ├── dataloader_malacca.py # Malacca Strait bypass tracking
│   └── dataloader_singapore.py# Singapore hub metrics
│
├── Data_raw/                 # Raw data outputs, dataframes (.csv, .parquet), and static charts
│   ├── Singapore_TankerArrivalsTotalMonthly.csv
│   ├── clean_volumes.csv
│   ├── crude_oil_expert_quotes.csv
│   ├── crude_oil_export_2026.csv
│   ├── crude_oil_export_voy_intake_index.csv
│   ├── crude_route_comparison.png
│   ├── crude_route_parsed_numbers.csv
│   ├── crude_route_summary_table.csv
│   ├── daily_region_summary.csv
│   ├── daily_vessel_summary.csv
│   ├── malacca_traffic_20260603_112515.parquet
│   ├── malacca_traffic_chart.png
│   ├── oil_prices_20260603_112515.parquet
│   ├── pipelines_20260603_112515.parquet
│   ├── singapore_exports_20260603_112515.parquet
│   ├── singapore_imports_20260603_112515.parquet
│   └── yanbu_volume_candidates.csv
│
├── Visualisation_of_Data/    # Analytical Notebooks and Exploratory Data Analysis (EDA)
│   ├── Cost-Burden_Analysis_(Ai).ipynb
│   ├── Cost-Burden_Analysis2_(Ai & Ririka).ipynb
│   ├── Hormuz_flow_visualization_(Ririka).ipynb
│   ├── Impacts_on_Global_Oil_Trade_(Mami).ipynb
│   ├── Malacca_flow_visualization.py
│   ├── crude_oil_export_analysis (2).ipynb
│   ├── rerouting_additional_cost_and_date_analysis.ipynb
│   ├── tanker_loitering_analysis_(Aston).ipynb
│   ├── yanbu_oil_flow_analysis.ipynb
│   └── test.py
│
├── References/               # Academic literature, policy briefs, and source notes
├── requirements.txt          # Python package environment specifications
└── README.md                 # Project documentation


## 📁 Data Sources

| Source | Description | URL |
|--------|-------------|-----|
| Marine Traffic | Live worldwide marine traffic reporting | (https://www.marinetraffic.org/MALACCA%20STRAIT/ship-traffic-tracker) |
|Port of Singapore Data|Port of Singapore, Tanker Arrival, Total, Monthly up till May 2026|https://data.gov.sg/datasets/d_9adb5ace517591edd9a8c88291ac1f1c/view| 
|Open AIS Data|AISdb|https://github.com/AISViz/AISdb|
| AIS Hub | vessel tracking for selected area |(https://www.aishub.net/api) |
|OECD AIS Report| monthly oil imports and exports of Singapore | (https://oecd-main.shinyapps.io/an-ocean-of-data/) need to select Singapore |
|World Bank | Crude Pricing data | (https://www.fetchseries.com/oil/oil-prices-world-bank-pink-sheets/crude-oil-price-usd-bbl-asia-world-bank-pink-sheets-monthly?utm) |

#### D.1 World Bank  
**Variables:** e.g., NY.GDP.MKTP.CD, SE.PRM.CMPT.ZS

**Granularity:** e.g., Annual data by Country

#### D.2 IMF  
**Variables:** e.g., Consumer Price Index, Interest Rates

**Granularity:** e.g., Quarterly data by Region


#### D.1 AIS vessel tracking data   
**Variables:** e.g., not sure 

**Granularity:** e.g., Daily data of the selected area

#### D.2 Monthly oil exports of Singapore 
**Variables:** e.g., Crude & refined oils

**Granularity:** e.g., Monthly data of Singapore

#### D.3 Monthly oil imports of Singapore 
**Variables:** e.g., Crude & refined oils

**Granularity:** e.g., Monthly data of Singapore

#### D.4 Crude pricing data  Crude oil price (USD/bbl) - Asia
**Variables:** e.g., Asia

**Granularity:** e.g., Manthly data by region


## 📂 Folder Structure

### Folder Structure Notes
- All projects MUST follow this standardized folder structure
- `data/raw/` - **NEVER** edit manually; store original data here
- `data/clean/` - Cleaned datasets ready for analysis
- `data/temp/` - Temporary files (can be deleted)
- `notebooks/` - Jupyter notebooks for analysis
- `src/` - Python code
- `reports/` - Final outputs: plots, summaries, model files
- `docs/` - Project documentation, README, presentations

### Folder Structure Tree



## 📅 Timeline

| Milestone | Deadline | Deliverable |
|-----------|----------|-------------|
| M1        | Date     | Output      |
| M2        | Date     | Output      |
| M3        | Date     | Output      |

## 🤝 Contributions

| Member | Tasks |
|--------|-------|
| Name   | Description of contributions |
| Name   | Description of contributions |

## 🔗 References
- Link to methodology references
