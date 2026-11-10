# Data directory

The analysis downloads public aggregate data at runtime. Raw downloads are intentionally not versioned; the compact processed analytical file and derived tables are included for reproducibility and review.

## Source

**CDC RESP-NET Rates and Clinical Data**  
Socrata dataset ID: `kvib-3txy`  
API: <https://data.cdc.gov/resource/kvib-3txy.csv>  
Dataset page: <https://data.cdc.gov/d/kvib-3txy>  
CDC dashboard and interpretation notes: <https://www.cdc.gov/resp-net/dashboard/>

The cohort is restricted to 2025–26 observed cumulative hospitalization rates for the overall RESP-NET surveillance area, all races, all sexes, and 11 mutually exclusive age groups. CDC's separately published `Combined` network rows are retained only as a validation target.

Run `python scripts/run_analysis.py` from the repository root to recreate the raw file and all outputs.

