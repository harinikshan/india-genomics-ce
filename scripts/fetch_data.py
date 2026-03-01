#!/usr/bin/env python3
"""
Dataset bootstrap utility for Genetic Health CE.

This script downloads optional external datasets after explicit license acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import textwrap
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = ROOT / "data"

SOURCES = {
    "clinvar": {
        "title": "ClinVar (NCBI)",
        "license_note": (
            "You must comply with NCBI terms for ClinVar data. "
            "This source is not bundled in CE."
        ),
        "files": [
            {
                "url": "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz",
                "dest": "external/clinvar/variant_summary.txt.gz",
                "sha256": None,
            }
        ],
    },
    "pharmgkb": {
        "title": "PharmGKB",
        "license_note": (
            "PharmGKB data usage may include attribution/share-alike/commercial limitations. "
            "Review policy before use."
        ),
        "files": [
            {
                "url": "https://api.pharmgkb.org/v1/download/file/data/clinicalAnnotations.zip",
                "dest": "external/pharmgkb/clinicalAnnotations.zip",
                "sha256": None,
            },
            {
                "url": "https://api.pharmgkb.org/v1/download/file/data/clinicalAnnotationAlleles.zip",
                "dest": "external/pharmgkb/clinicalAnnotationAlleles.zip",
                "sha256": None,
            },
        ],
    },
    "cpic": {
        "title": "CPIC API Exports",
        "license_note": (
            "Use CPIC/API resources according to their published terms and citation policy."
        ),
        "files": [
            {
                "url": "https://api.cpicpgx.org/v1/recommendation",
                "dest": "external/cpic/recommendation.json",
                "sha256": None,
            },
            {
                "url": "https://api.cpicpgx.org/v1/diplotype",
                "dest": "external/cpic/diplotype.json",
                "sha256": None,
            },
            {
                "url": "https://api.cpicpgx.org/v1/sequence_location",
                "dest": "external/cpic/sequence_location.json",
                "sha256": None,
            },
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download optional external datasets")
    parser.add_argument(
        "--source",
        nargs="+",
        default=["all"],
        choices=["all", "clinvar", "pharmgkb", "cpic"],
        help="Data source(s) to download",
    )
    parser.add_argument(
        "--accept-licenses",
        action="store_true",
        help="Accept all source license prompts non-interactively",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without downloading",
    )
    parser.add_argument(
        "--data-dir",
        default=str(DEFAULT_DATA_DIR),
        help="Target data directory (default: ./data)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Download timeout in seconds (default: 120)",
    )
    return parser.parse_args()


def choose_sources(source_args: list[str]) -> list[str]:
    if "all" in source_args:
        return list(SOURCES.keys())
    return source_args


def prompt_acceptance(source_key: str, auto_accept: bool) -> bool:
    source = SOURCES[source_key]
    if auto_accept:
        return True

    message = textwrap.dedent(
        f"""
        Source: {source['title']}
        {source['license_note']}

        Type 'yes' to accept and continue: """
    )
    try:
        response = input(message).strip().lower()
    except EOFError:
        return False
    return response == "yes"


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, destination: Path, timeout: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".part")

    with urllib.request.urlopen(url, timeout=timeout) as response, tmp.open("wb") as out:
        shutil.copyfileobj(response, out)

    tmp.replace(destination)


def run() -> int:
    args = parse_args()
    selected = choose_sources(args.source)
    data_dir = Path(args.data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, dict[str, str]] = {}

    for source_key in selected:
        if not prompt_acceptance(source_key, args.accept_licenses):
            print(f"Skipped {source_key}: license not accepted", file=sys.stderr)
            return 2

        source = SOURCES[source_key]
        print(f"\n== {source['title']} ==")
        summary[source_key] = {}

        for item in source["files"]:
            dest = data_dir / item["dest"]
            print(f"- {item['url']} -> {dest}")

            if args.dry_run:
                summary[source_key][item["dest"]] = "dry-run"
                continue

            try:
                download_file(item["url"], dest, args.timeout)
            except Exception as exc:
                print(f"  download failed: {exc}", file=sys.stderr)
                return 1

            computed = sha256sum(dest)
            expected = item.get("sha256")
            if expected:
                if computed.lower() != expected.lower():
                    print(
                        f"  checksum mismatch for {dest.name}: expected {expected}, got {computed}",
                        file=sys.stderr,
                    )
                    return 1
                status = "ok (checksum verified)"
            else:
                # Store computed checksums for reproducibility if upstream value is unavailable.
                checksum_path = dest.with_suffix(dest.suffix + ".sha256")
                checksum_path.write_text(f"{computed}  {dest.name}\n", encoding="utf-8")
                status = "ok (checksum computed locally)"

            summary[source_key][item["dest"]] = status
            print(f"  {status}")

    manifest_path = data_dir / "external" / "download_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nDone.")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
