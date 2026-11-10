# LinkedIn post draft

**Formula:** F19 — Anecdote-Meets-Evidence Bridge  
**Goal:** Saves and thoughtful comments  
**Suggested window:** Tuesday–Thursday, 7:30–9:00 AM Central  

## Post

53 weeks of respiratory hospitalization data changed the way I looked at “high-risk” age groups.

I started this project expecting one familiar pattern: hospitalization burden increasing with age.

The CDC RESP-NET data confirmed that pattern, but it also showed why a single combined rate can hide the public-health decision.

Adults aged 85 and older had the highest cumulative COVID-19, influenza, and RSV hospitalization rate in 2025–26: 1,339 per 100,000.

Infants younger than 1 year ranked second at 951 per 100,000.

Those two high-burden groups did not have the same virus profile.

RSV accounted for 71% of the infant rate. Influenza was the largest component among adults aged 85 and older and across every age group from 5–11 through 85+.

I built the analysis in Python and a parallel SAS workflow for import, QA, cohort construction, validation, ranking, and statistical analysis. The virus-specific rates reproduced CDC’s published combined series within 1.0 per 100,000 in every age group.

My biggest reminder from this project: surveillance summaries become more useful when we separate who is affected from what is driving the burden.

Which age-by-virus comparison would be most useful for your preparedness or prevention work?

#Epidemiology #HealthcareAnalytics

## First comment

Project repository: https://github.com/gorkira28/resp-net-age-hospitalization-burden

