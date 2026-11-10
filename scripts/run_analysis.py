"""Reproduce the 2025-26 RESP-NET age-specific hospitalization analysis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
BASE_API = "https://data.cdc.gov/resource/kvib-3txy.csv"
NETWORKS = ["COVID-NET", "FluSurv-NET", "RSV-NET"]
NETWORK_LABELS = {"COVID-NET": "COVID-19", "FluSurv-NET": "Influenza", "RSV-NET": "RSV"}
AGE_ORDER = [
    "0-<1 yr", "1-4 yr", "5-11 yr", "12-17 yr", "18-29 yr", "30-39 yr",
    "40-49 yr", "50-64 yr", "65-74 yr", "75-84 yr", "85+ yr",
]
ADULT_AGE_MIDPOINT = {
    "18-29 yr": 23.5, "30-39 yr": 34.5, "40-49 yr": 44.5,
    "50-64 yr": 57.0, "65-74 yr": 69.5, "75-84 yr": 79.5, "85+ yr": 90.0,
}


def source_url() -> str:
    where = (
        "season='2025-26' AND date_type='Week Ending Date' "
        "AND race='All' AND sex='All' AND state='Overall' "
        "AND data_type='Cumulative Rate' AND estimate_type='Rate per 100,000' "
        "AND rate_type='Observed'"
    )
    request = requests.models.PreparedRequest()
    request.prepare_url(BASE_API, {"$where": where, "$limit": 10000})
    return request.url


def download() -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    destination = RAW / "resp_net_2025_26_cumulative_rates.csv"
    response = requests.get(source_url(), timeout=120)
    response.raise_for_status()
    destination.write_bytes(response.content)
    manifest = {
        "retrieved_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "source": source_url(), "dataset_id": "kvib-3txy",
        "sha256": hashlib.sha256(response.content).hexdigest(), "bytes": len(response.content),
    }
    (RAW / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return destination


def clean(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype="string")
    df = df.loc[
        df["surveillance_network"].isin(NETWORKS + ["Combined"])
        & df["age_category"].isin(AGE_ORDER)
    ].copy()
    df["week_ending"] = pd.to_datetime(df["date"], errors="coerce")
    df["cumulative_rate_per_100k"] = pd.to_numeric(df["estimate"], errors="coerce")
    df["age_category"] = pd.Categorical(df["age_category"], AGE_ORDER, ordered=True)
    return df[["surveillance_network", "week_ending", "age_category", "cumulative_rate_per_100k"]].sort_values(
        ["surveillance_network", "age_category", "week_ending"]
    )


def validate(df: pd.DataFrame) -> dict:
    expected_groups = 4 * len(AGE_ORDER)
    group_counts = df.groupby(["surveillance_network", "age_category"], observed=True)["week_ending"].nunique()
    checks = {
        "rows": int(len(df)), "networks": int(df["surveillance_network"].nunique()),
        "age_groups": int(df["age_category"].nunique()), "network_age_groups": int(len(group_counts)),
        "expected_network_age_groups": expected_groups,
        "minimum_weeks_per_series": int(group_counts.min()), "maximum_weeks_per_series": int(group_counts.max()),
        "duplicate_network_age_weeks": int(df.duplicated(["surveillance_network", "age_category", "week_ending"]).sum()),
        "missing_estimates": int(df["cumulative_rate_per_100k"].isna().sum()),
        "negative_estimates": int((df["cumulative_rate_per_100k"] < 0).sum()),
        "first_week": df["week_ending"].min().date().isoformat(),
        "last_week": df["week_ending"].max().date().isoformat(),
    }
    checks["passed"] = bool(
        checks["networks"] == 4 and checks["age_groups"] == len(AGE_ORDER)
        and checks["network_age_groups"] == expected_groups
        and checks["minimum_weeks_per_series"] == checks["maximum_weeks_per_series"]
        and checks["duplicate_network_age_weeks"] == 0
        and checks["missing_estimates"] == 0 and checks["negative_estimates"] == 0
    )
    if not checks["passed"]:
        raise ValueError(f"QA checks failed: {checks}")
    return checks


def final_age_summary(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    last_date = df["week_ending"].max()
    final = df.loc[df["week_ending"].eq(last_date)].copy()
    components = final.loc[final["surveillance_network"].isin(NETWORKS)].pivot(
        index="age_category", columns="surveillance_network", values="cumulative_rate_per_100k"
    ).reindex(AGE_ORDER)
    components.columns.name = None
    components = components.rename(columns=NETWORK_LABELS)
    components["Calculated combined"] = components[["COVID-19", "Influenza", "RSV"]].sum(axis=1)
    published = final.loc[final["surveillance_network"].eq("Combined")].set_index("age_category")
    components["CDC published combined"] = published["cumulative_rate_per_100k"].reindex(AGE_ORDER).to_numpy()
    components["absolute_crosscheck_difference"] = (
        components["Calculated combined"] - components["CDC published combined"]
    ).abs()
    components["dominant_virus"] = components[["COVID-19", "Influenza", "RSV"]].idxmax(axis=1)
    components["dominant_virus_share_pct"] = (
        components[["COVID-19", "Influenza", "RSV"]].max(axis=1) / components["Calculated combined"] * 100
    )
    for virus in ["COVID-19", "Influenza", "RSV"]:
        name = virus.lower().replace("-", "_") + "_share_pct"
        components[name] = components[virus] / components["Calculated combined"] * 100
    components = components.reset_index().rename(columns={"age_category": "age_group"})
    components["burden_rank"] = components["Calculated combined"].rank(method="min", ascending=False).astype(int)

    adult = components.loc[components["age_group"].isin(ADULT_AGE_MIDPOINT)].copy()
    adult["age_midpoint"] = adult["age_group"].map(ADULT_AGE_MIDPOINT)
    rho, p_value = spearmanr(adult["age_midpoint"], adult["Calculated combined"])
    by_age = components.set_index("age_group")["Calculated combined"]
    metrics = {
        "last_week": last_date.date().isoformat(),
        "max_combined_crosscheck_difference": float(components["absolute_crosscheck_difference"].max()),
        "adult_age_burden_spearman_rho": float(rho),
        "adult_age_burden_spearman_p_value": float(p_value),
        "age_85_plus_vs_18_29_rate_ratio": float(by_age["85+ yr"] / by_age["18-29 yr"]),
        "infant_vs_18_29_rate_ratio": float(by_age["0-<1 yr"] / by_age["18-29 yr"]),
    }
    return components, metrics


def weekly_increment_summary(df: pd.DataFrame) -> pd.DataFrame:
    components = df.loc[df["surveillance_network"].isin(NETWORKS)].copy()
    components["weekly_increment"] = components.groupby(
        ["surveillance_network", "age_category"], observed=True
    )["cumulative_rate_per_100k"].diff()
    first = components.groupby(["surveillance_network", "age_category"], observed=True).cumcount().eq(0)
    components.loc[first, "weekly_increment"] = components.loc[first, "cumulative_rate_per_100k"]
    return components


def make_figures(df: pd.DataFrame, summary: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    colors = {"COVID-19": "#7451A4", "Influenza": "#E69F00", "RSV": "#2A9D8F"}
    plot = summary.set_index("age_group").reindex(AGE_ORDER)

    fig, ax = plt.subplots(figsize=(12, 7))
    left = np.zeros(len(plot))
    for virus in ["COVID-19", "Influenza", "RSV"]:
        values = plot[virus].to_numpy()
        ax.barh(plot.index, values, left=left, color=colors[virus], label=virus)
        left += values
    ax.invert_yaxis()
    ax.set(title="2025–26 cumulative respiratory hospitalization rates by age",
           xlabel="Cumulative hospitalizations per 100,000", ylabel="")
    ax.legend(frameon=False, ncol=3)
    ax.text(0, -0.13, "Source: CDC RESP-NET observed cumulative rates. Components are summed across mutually exclusive viruses.",
            transform=ax.transAxes, fontsize=9, color="#555555")
    fig.tight_layout()
    fig.savefig(FIGURES / "age_burden_components.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    shares = summary.set_index("age_group")[["covid_19_share_pct", "influenza_share_pct", "rsv_share_pct"]].astype(float)
    shares.columns = ["COVID-19", "Influenza", "RSV"]
    shares = shares.reindex(AGE_ORDER)
    fig, ax = plt.subplots(figsize=(8.5, 7.2))
    sns.heatmap(shares, annot=True, fmt=".0f", cmap="Blues", vmin=0, vmax=100,
                cbar_kws={"label": "Share of combined cumulative rate (%)"}, ax=ax)
    ax.set(title="Virus contribution shifts sharply across age groups", xlabel="", ylabel="")
    fig.tight_layout()
    fig.savefig(FIGURES / "virus_share_by_age_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    selected = ["0-<1 yr", "18-29 yr", "65-74 yr", "85+ yr"]
    trajectories = df.loc[df["surveillance_network"].isin(NETWORKS) & df["age_category"].isin(selected)].copy()
    trajectories["virus"] = trajectories["surveillance_network"].map(NETWORK_LABELS)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, age in zip(axes.flat, selected):
        subset = trajectories.loc[trajectories["age_category"].eq(age)]
        for virus in ["COVID-19", "Influenza", "RSV"]:
            series = subset.loc[subset["virus"].eq(virus)]
            ax.plot(series["week_ending"], series["cumulative_rate_per_100k"], label=virus,
                    color=colors[virus], lw=2.2)
        ax.set_title(age, loc="left", weight="bold")
        ax.set_ylabel("Cumulative rate")
    axes[0, 0].legend(frameon=False, ncol=3, fontsize=8)
    fig.suptitle("Cumulative hospitalization trajectories reveal age-specific virus patterns",
                 x=0.06, ha="left", fontsize=16, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "selected_age_trajectories.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig = plt.figure(figsize=(14, 8), facecolor="#F6F8FB")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.18, 1], hspace=0.35, wspace=0.25)
    ax1 = fig.add_subplot(grid[:, 0])
    left = np.zeros(len(plot))
    for virus in ["COVID-19", "Influenza", "RSV"]:
        values = plot[virus].to_numpy()
        ax1.barh(plot.index, values, left=left, color=colors[virus], label=virus)
        left += values
    ax1.invert_yaxis()
    ax1.set_xlabel("Cumulative rate per 100,000")
    ax1.set_title("Age-specific cumulative burden", loc="left", fontsize=14, weight="bold")
    ax1.legend(frameon=False, ncol=3, fontsize=8)
    ax2 = fig.add_subplot(grid[0, 1])
    sns.heatmap(shares, annot=True, fmt=".0f", cmap="Blues", vmin=0, vmax=100, cbar=False, ax=ax2)
    ax2.set_title("Virus share (%)", loc="left", fontsize=14, weight="bold")
    ax2.set_xlabel("")
    ax2.set_ylabel("")
    ax3 = fig.add_subplot(grid[1, 1])
    adult = plot.loc[list(ADULT_AGE_MIDPOINT)]
    ax3.plot(adult.index, adult["Calculated combined"], marker="o", color="#C94C4C", lw=2.5)
    ax3.tick_params(axis="x", rotation=35)
    ax3.set_ylabel("Cumulative rate")
    ax3.set_title("Adult age gradient", loc="left", fontsize=14, weight="bold")
    fig.suptitle("Who carried the greatest respiratory hospitalization burden?",
                 x=0.04, y=0.98, ha="left", fontsize=21, weight="bold", color="#183153")
    fig.text(0.04, 0.925, "CDC RESP-NET 2025–26 | SAS + Python | 3 viruses × 11 mutually exclusive age groups",
             fontsize=11, color="#4B6078")
    fig.text(0.04, 0.018, "Population-based surveillance in selected counties; not a national estimate or causal analysis.",
             fontsize=9, color="#5B6573")
    fig.savefig(FIGURES / "portfolio_preview.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    for directory in [PROCESSED, TABLES, FIGURES]:
        directory.mkdir(parents=True, exist_ok=True)
    analytic = clean(download())
    qa = validate(analytic)
    summary, metrics = final_age_summary(analytic)
    increments = weekly_increment_summary(analytic)
    qa.update(metrics)
    analytic.to_csv(PROCESSED / "resp_net_analytic.csv", index=False, date_format="%Y-%m-%d")
    summary.to_csv(TABLES / "age_burden_summary.csv", index=False)
    increments.to_csv(TABLES / "weekly_rate_increments.csv", index=False, date_format="%Y-%m-%d")
    (ROOT / "outputs" / "qa_report.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    make_figures(analytic, summary)
    print(json.dumps({
        "qa": qa,
        "age_summary": summary[["age_group", "Calculated combined", "dominant_virus", "burden_rank"]].to_dict("records"),
    }, indent=2))


if __name__ == "__main__":
    main()

