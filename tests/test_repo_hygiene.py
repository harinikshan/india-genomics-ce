from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent


def test_no_personal_files_tracked_in_release_tree():
    forbidden = [
        PROJECT / "data" / "Fetus_of_Srishankari_8849728.vcf",
        PROJECT / "data" / "genome_fetus_srishankari.txt",
    ]
    for path in forbidden:
        assert not path.exists(), f"Forbidden file present: {path}"


def test_reports_folder_is_clean():
    reports = PROJECT / "reports"
    generated = list(reports.glob("*.md")) + list(reports.glob("*.json"))
    generated = [p for p in generated if p.name != "README.md"]
    assert not generated, f"Generated report files should not be tracked: {generated}"
