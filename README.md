# Genetic Health CE

Local-first genomic analysis pipeline for VCF and 23andMe-style files.

## Why open source
- Privacy-first local processing.
- Transparent analysis/report pipeline.
- Community-auditable code for safer interpretation tooling.

## Community Edition scope (v1.0.0-oss)
- Local CLI + Flask web app.
- Lifestyle SNP analysis and report generation.
- Optional ClinVar/PharmGKB/CPIC data bootstrap script.
- Tests + CI baseline.

## What is not bundled
- Personal genome files and personal reports.
- Full third-party clinical datasets with restrictive licensing.

See `THIRD_PARTY_DATA.md` for data source policies.

## Quickstart (3 commands)
```bash
pip install -r requirements.txt
python scripts/fetch_data.py --source all --accept-licenses
python app.py
```

Open: `http://localhost:8000`
To share on LAN for a session: `python app.py --share-lan`

## CLI usage
```bash
python scripts/run_full_analysis.py examples/genome_demo.txt --name "Demo Subject"
```

## Repo layout
- `app.py` - local web app
- `scripts/` - pipeline and utilities
- `templates/` - web templates
- `data/` - local datasets (downloaded by user)
- `reports/` - generated output
- `tests/` - lightweight public test suite

## Important disclaimer
This software is for informational and educational use only.
It is **not** a medical diagnosis tool.
Always consult qualified clinicians or genetic counselors for medical decisions.

## Contributing
See `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
