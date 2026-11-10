/*
  RESP-NET 2025-26 age-specific respiratory hospitalization burden
  SAS 9.4 / SAS OnDemand compatible validation workflow

  Run instructions:
  1. Run scripts/run_analysis.py or use the included processed CSV.
  2. Upload data/processed/resp_net_analytic.csv to SAS OnDemand.
  3. Change PROJECT_DIR to the folder containing that file.

  This program performs typed import, structural QA, final-week cohort
  construction, virus-specific reshaping, combined-rate validation, burden
  ranking, rate-ratio calculation, and an adult age-gradient Spearman test.
*/

%let PROJECT_DIR=/home/&sysuserid;
%let INPUT=&PROJECT_DIR/resp_net_analytic.csv;
%let OUTDIR=&PROJECT_DIR;

options validvarname=v7 nodate nonumber;

proc import datafile="&INPUT" out=work.resp_raw dbms=csv replace;
    guessingrows=max;
    getnames=yes;
run;

data work.resp;
    set work.resp_raw;
    length week_date 8 age_order 8;
    format week_date yymmdd10.;
    week_date=input(strip(week_ending), yymmdd10.);
    select (strip(age_category));
        when ('0-<1 yr') age_order=1;
        when ('1-4 yr') age_order=2;
        when ('5-11 yr') age_order=3;
        when ('12-17 yr') age_order=4;
        when ('18-29 yr') age_order=5;
        when ('30-39 yr') age_order=6;
        when ('40-49 yr') age_order=7;
        when ('50-64 yr') age_order=8;
        when ('65-74 yr') age_order=9;
        when ('75-84 yr') age_order=10;
        when ('85+ yr') age_order=11;
        otherwise age_order=.;
    end;
run;

/* Structural QA. Expected: 4 networks, 11 ages, 53 weeks, no duplicates. */
proc sql;
    create table work.qa_summary as
    select count(*) as rows,
           count(distinct surveillance_network) as networks,
           count(distinct age_category) as age_groups,
           count(distinct week_date) as weeks,
           sum(missing(cumulative_rate_per_100k)) as missing_estimates,
           sum(cumulative_rate_per_100k < 0) as negative_estimates
    from work.resp;

    create table work.duplicate_check as
    select surveillance_network, age_category, week_date, count(*) as n
    from work.resp
    group by surveillance_network, age_category, week_date
    having calculated n > 1;

    select max(week_date) into :final_week trimmed from work.resp;
quit;

title "SAS structural QA";
proc print data=work.qa_summary noobs; run;
proc print data=work.duplicate_check noobs; run;
title;

data work.final_components work.final_published;
    set work.resp;
    where week_date=&final_week;
    if surveillance_network='Combined' then output work.final_published;
    else output work.final_components;
run;

proc sort data=work.final_components; by age_order age_category; run;
proc transpose data=work.final_components out=work.components_wide(drop=_name_) prefix=rate_;
    by age_order age_category;
    id surveillance_network;
    var cumulative_rate_per_100k;
run;

proc sort data=work.final_published; by age_order age_category; run;

data work.age_summary;
    merge work.components_wide(in=a)
          work.final_published(
              keep=age_order age_category cumulative_rate_per_100k
              rename=(cumulative_rate_per_100k=cdc_published_combined)
          );
    by age_order age_category;
    if a;
    calculated_combined=sum(rate_COVID_NET, rate_FluSurv_NET, rate_RSV_NET);
    absolute_crosscheck_difference=abs(calculated_combined-cdc_published_combined);
    length dominant_virus $10;
    max_component=max(rate_COVID_NET, rate_FluSurv_NET, rate_RSV_NET);
    if max_component=rate_COVID_NET then dominant_virus='COVID-19';
    else if max_component=rate_FluSurv_NET then dominant_virus='Influenza';
    else dominant_virus='RSV';
run;

proc sort data=work.age_summary out=work.age_ranked;
    by descending calculated_combined;
run;

data work.age_ranked;
    set work.age_ranked;
    burden_rank=_n_;
run;

/* Adult age-gradient test using non-overlapping adult age groups. */
data work.adult_gradient;
    set work.age_summary;
    select (strip(age_category));
        when ('18-29 yr') age_midpoint=23.5;
        when ('30-39 yr') age_midpoint=34.5;
        when ('40-49 yr') age_midpoint=44.5;
        when ('50-64 yr') age_midpoint=57;
        when ('65-74 yr') age_midpoint=69.5;
        when ('75-84 yr') age_midpoint=79.5;
        when ('85+ yr') age_midpoint=90;
        otherwise delete;
    end;
run;

ods output SpearmanCorr=work.spearman_output;
proc corr data=work.adult_gradient spearman nosimple;
    var age_midpoint calculated_combined;
run;
ods output close;

/* Pre-specified rate ratios against adults ages 18-29. */
proc sql noprint;
    select calculated_combined into :ref_rate
    from work.age_summary where age_category='18-29 yr';
quit;

data work.rate_ratios;
    set work.age_summary;
    if age_category in ('0-<1 yr', '85+ yr');
    rate_ratio_vs_18_29=calculated_combined/&ref_rate;
run;

proc export data=work.age_ranked
    outfile="&OUTDIR/age_burden_summary_sas.csv"
    dbms=csv replace;
run;

title "RESP-NET cumulative hospitalization burden by age, 2025-26";
proc print data=work.age_ranked noobs;
    var burden_rank age_category calculated_combined dominant_virus
        cdc_published_combined absolute_crosscheck_difference;
run;
title;

