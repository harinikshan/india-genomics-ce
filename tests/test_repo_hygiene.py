from pathlib import Path
import subprocess


PROJECT = Path(__file__).resolve().parent.parent


def _tracked_files() -> set[str]:
    out = subprocess.check_output(
        ["git", "-C", str(PROJECT), "ls-files"],
        text=True,
    )
    return {line.strip() for line in out.splitlines() if line.strip()}


def test_no_personal_files_tracked_in_release_tree():
    forbidden = {
        "data/Fetus_of_Srishankari_8849728.vcf",
        "data/genome_fetus_srishankari.txt",
    }
    tracked = _tracked_files()
    found = sorted(forbidden.intersection(tracked))
    assert not found, f"Forbidden files must not be tracked: {found}"


def test_reports_folder_tracks_only_public_placeholders():
    tracked = _tracked_files()
    tracked_reports = sorted(
        p
        for p in tracked
        if p.startswith("reports/") and (p.endswith(".md") or p.endswith(".json"))
    )
    allowed = {"reports/README.md"}
    disallowed = [p for p in tracked_reports if p not in allowed]
    assert not disallowed, f"Generated report files must not be tracked: {disallowed}"
