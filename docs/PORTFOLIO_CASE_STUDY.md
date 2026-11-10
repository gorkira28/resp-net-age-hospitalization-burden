# Portfolio case study: Who carried the greatest respiratory hospitalization burden?

## The decision question

Which age groups experienced the greatest cumulative hospitalization burden from COVID-19, influenza, and RSV during the 2025–26 respiratory season, and how did the virus mix change across age?

## What I built

I analyzed 53 weeks of CDC RESP-NET surveillance across 11 mutually exclusive age groups. The workflow uses Python for reproducible acquisition, QA, analysis, and visualization, plus a substantive SAS program that independently rebuilds the final-week cohort, validates combined rates, ranks burden, calculates age-specific rate ratios, and tests the adult age gradient.

## What the data showed

- Adults aged 85+ had the highest combined cumulative rate: 1,339 per 100,000.
- Infants younger than 1 year ranked second at 951 per 100,000.
- RSV represented 71% of the infant rate; influenza was the largest component from ages 5–11 through 85+.
- The 85+ rate was 27.3 times the rate among adults aged 18–29.
- The calculated three-virus totals matched CDC's separately published combined series within 1.0 per 100,000.

## Why it is useful

The project shows why one overall respiratory-season number is not enough. Older-adult burden and infant burden were both high, but the virus composition differed substantially, leading to different prevention and preparedness questions.

## Tools and methods

SAS · Python · pandas · SciPy · Matplotlib · Seaborn · Socrata API · reproducible QA/QC · epidemiologic surveillance

## Interpretation boundary

RESP-NET covers selected counties and is not a national estimate. The results are descriptive, unadjusted, and should not be used as causal evidence or hospital-quality rankings.

