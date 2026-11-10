# Data dictionary

## Processed analytical file

`data/processed/resp_net_analytic.csv`

| Variable | Type | Description |
|---|---|---|
| `surveillance_network` | text | COVID-NET, FluSurv-NET, RSV-NET, or CDC Combined |
| `week_ending` | date | Week-ending date in ISO format |
| `age_category` | ordered text | One of 11 mutually exclusive age groups |
| `cumulative_rate_per_100k` | numeric | Observed cumulative hospitalization rate per 100,000 |

## Age summary

`outputs/tables/age_burden_summary.csv`

| Variable | Description |
|---|---|
| `age_group` | Mutually exclusive age category |
| `COVID-19` | Final COVID-NET cumulative rate per 100,000 |
| `Influenza` | Final FluSurv-NET cumulative rate per 100,000 |
| `RSV` | Final RSV-NET cumulative rate per 100,000 |
| `Calculated combined` | Sum of three virus-specific cumulative rates |
| `CDC published combined` | CDC's separately published combined cumulative rate |
| `absolute_crosscheck_difference` | Absolute difference between calculated and published combined values |
| `dominant_virus` | Virus with the largest cumulative-rate component |
| `dominant_virus_share_pct` | Largest virus component as a percentage of calculated combined rate |
| `covid_19_share_pct` | COVID-19 share of combined rate |
| `influenza_share_pct` | Influenza share of combined rate |
| `rsv_share_pct` | RSV share of combined rate |
| `burden_rank` | Descending rank of calculated combined cumulative rate |

## QA report

`outputs/qa_report.json` contains cohort dimensions, structural QA results, the combined-rate cross-check, the adult Spearman result, and the two pre-specified age rate ratios.

