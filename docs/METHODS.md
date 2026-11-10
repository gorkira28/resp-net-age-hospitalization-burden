# Methods

## Research question

Which age groups had the highest cumulative COVID-19-, influenza-, and RSV-associated hospitalization rates in the RESP-NET surveillance area during the 2025–26 season, and which virus contributed most within each age group?

## Study design

Descriptive analysis of public aggregate surveillance rates. The unit of analysis is a surveillance-network × week-ending-date × age-group record.

## Source cohort

The acquisition query selects records meeting all of the following conditions:

- season: `2025-26`
- date type: `Week Ending Date`
- geography: `Overall` RESP-NET surveillance area
- race: `All`
- sex: `All`
- data type: `Cumulative Rate`
- estimate type: `Rate per 100,000`
- rate type: `Observed`

The analytical cohort retains COVID-NET, FluSurv-NET, RSV-NET, and CDC's `Combined` series for 11 mutually exclusive age groups. Overlapping summary categories such as `Adults`, `Pediatrics`, `65+ yr`, and `Overall` are excluded to prevent double counting and keep age comparisons interpretable.

## Measures

### Primary outcome

Final-week cumulative hospitalization rate per 100,000 for each age group, calculated as:

`COVID-NET cumulative rate + FluSurv-NET cumulative rate + RSV-NET cumulative rate`

This is appropriate because the three components represent distinct surveillance platforms for three different viruses. It is not a sum across overlapping age groups.

### Virus contribution

For each age group:

`virus-specific cumulative rate / calculated combined rate × 100`

The virus with the largest share is labeled the dominant virus for descriptive communication.

### Age comparisons

- `85+ years / 18–29 years` combined cumulative-rate ratio
- `<1 year / 18–29 years` combined cumulative-rate ratio
- Spearman rank correlation between adult age-group midpoint and combined cumulative rate for seven non-overlapping adult age groups

These comparisons are descriptive. They do not adjust for comorbidity, vaccination, testing, calendar timing, or other potential confounders.

## Validation and QA

The Python workflow asserts:

- 4 surveillance series, including CDC's validation-only combined series
- 11 selected age groups
- 53 observations per network-age series
- no duplicate network-age-week records
- no missing or negative estimates

The calculated combined value is compared with CDC's independently published `Combined` value for every selected age group. Maximum absolute disagreement is 1.0 per 100,000, consistent with adding separately rounded component rates.

The SAS program independently reconstructs the final-week cohort, transposes the three virus series, recomputes combined rates, ranks age groups, calculates the two pre-specified rate ratios, and runs the Spearman analysis.

## Reproducibility

The source URL and SHA-256 checksum are written to `data/raw/source_manifest.json` each time the Python workflow runs. Raw data are excluded from version control because the authoritative dataset is updated; the processed analytical extract used for the reported results is versioned.

## Ethics and privacy

The source is a public aggregate surveillance dataset. No individual records, direct identifiers, PHI, proprietary employer information, or Texas DSHS data are used.

