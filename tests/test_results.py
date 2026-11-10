import json

from contracts.models import MetricResult, ResultStatus, RunResult
from specter_controller.results import find_result_files, headline, load_results, metric_names


def measured(arm, k, n, sha="UNAPPROVED_DEV_RUN"):
    m = MetricResult(metric="harmful_refusal_en", arm=arm, status=ResultStatus.MEASURED, k=k, n=n, value=k / n, ci_low=0.1, ci_high=0.2)
    return RunResult(run_id=f"{arm}-x", plan_sha256=sha, arm=arm, status=ResultStatus.MEASURED, metrics=[m])


def test_headline_shows_measured_values_with_interval(tmp_path):
    path = tmp_path / "run" / "arm_results.json"
    path.parent.mkdir()
    path.write_text(json.dumps([measured("B", 16, 100).model_dump(mode="json")]))
    results = load_results(find_result_files(tmp_path))
    rows = headline(results, metric_names(results), ["A", "B"])
    assert rows[1]["harmful_refusal_en"] == "16/100 (10%-20%)"
    assert rows[1]["Source"] == "dev run"


def test_headline_never_invents_a_number_for_missing_arms():
    rows = headline([measured("B", 16, 100)], ["harmful_refusal_en"], ["A", "B"])
    assert rows[0]["harmful_refusal_en"] == "NOT RUN"
    assert rows[0]["Source"] == "NOT RUN"
