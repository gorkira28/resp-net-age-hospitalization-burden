# SAS validation notes

## Scope

`sas/resp_net_age_burden.sas` provides a complete SAS-compatible replication of the core analytical result. It is designed for SAS OnDemand for Academics or SAS 9.4.

## What the program does

1. Imports the processed CSV with full-row type guessing.
2. Parses ISO dates and assigns an explicit age-order variable.
3. Audits row counts, network counts, age groups, weeks, missing estimates, negative estimates, and duplicates.
4. Selects the final 2025–26 week.
5. Separates CDC's combined series from the three virus components.
6. Transposes the component series from long to wide format.
7. Recalculates combined burden and compares it with CDC's published value.
8. Identifies the dominant virus and ranks age-group burden.
9. Runs a Spearman test across seven non-overlapping adult age groups.
10. Calculates infant and 85+ rate ratios relative to adults aged 18–29.
11. Exports `age_burden_summary_sas.csv`.

## Expected cross-checks

| Check | Expected result |
|---|---|
| Networks | 4 |
| Age groups | 11 |
| Weeks | 53 |
| Duplicate network-age-weeks | 0 |
| Missing estimates | 0 |
| Maximum combined-rate difference | 1.0 per 100,000 |
| Highest-burden group | 85+ years |
| Infant dominant virus | RSV |
| Adult age-burden Spearman ρ | 1.00 |

SAS execution is not available in this workspace, so the code was reviewed for SAS 9.4/OnDemand compatibility and the expected results were independently executed in Python. The README explains the exact upload and run steps.

