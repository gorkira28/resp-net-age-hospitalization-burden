import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_qa_report_passes():
    qa = json.loads((ROOT / "outputs" / "qa_report.json").read_text())
    assert qa["passed"] is True
    assert qa["networks"] == 4
    assert qa["age_groups"] == 11
    assert qa["duplicate_network_age_weeks"] == 0
    assert qa["missing_estimates"] == 0
    assert qa["max_combined_crosscheck_difference"] <= 1.0


def test_age_summary_components_and_ranks():
    summary = pd.read_csv(ROOT / "outputs" / "tables" / "age_burden_summary.csv")
    assert len(summary) == 11
    assert summary["age_group"].nunique() == 11
    assert set(summary["burden_rank"]) == set(range(1, 12))
    component_sum = summary[["COVID-19", "Influenza", "RSV"]].sum(axis=1)
    pd.testing.assert_series_equal(
        component_sum.round(8), summary["Calculated combined"].round(8), check_names=False
    )


def test_processed_outputs_and_figures_exist():
    assert (ROOT / "data" / "processed" / "resp_net_analytic.csv").stat().st_size > 50_000
    for name in [
        "age_burden_components.png",
        "virus_share_by_age_heatmap.png",
        "selected_age_trajectories.png",
        "portfolio_preview.png",
    ]:
        assert (ROOT / "outputs" / "figures" / name).stat().st_size > 20_000

