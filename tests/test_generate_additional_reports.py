from pathlib import Path

from scripts.generate_additional_reports import generate_swot_report


def test_swot_report_handles_missing_disease_stats(tmp_path):
    health_results = {
        "findings": [],
        "pharmgkb_findings": [],
        "summary": {"total_snps": 0},
    }

    output_path = generate_swot_report(
        health_results=health_results,
        disease_findings=None,
        disease_stats=None,
        output_dir=str(tmp_path),
        subject_name="Demo Subject",
    )

    assert isinstance(output_path, Path)
    assert output_path.exists()
    assert "SWOT_REPORT_Demo_Subject.md" in str(output_path)
