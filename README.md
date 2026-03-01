# india-genomics-ce

India-first, privacy-first genomics toolkit for local DNA analysis and personalized health insights.

## Screenshots

### Upload Flow
![01-upload](https://github.com/user-attachments/assets/ad468b61-0547-4bf5-af60-96244eb96a69)

### Analysis Progress
![02-analysis-progress](https://github.com/user-attachments/assets/44d2ec4d-aebb-460e-af52-a87c469006b4)

### Report Dashboard
![03-results-dashboard](https://github.com/user-attachments/assets/93f437c0-565c-420c-880a-726750cdbaad)

## Vision
Build a transparent, locally runnable genomics foundation for India-focused preventive care and clinician conversations, while keeping personal DNA data under user control.

## Community Edition scope (`v1.0.0-oss`)
- Local web app (`Flask`) and CLI workflow.
- Input support for 23andMe-style text files and `.vcf` conversion.
- Multi-report generation for lifestyle, pharmacogenomics, and prenatal-oriented insights.
- Optional external dataset bootstrap (`ClinVar`, `PharmGKB`, `CPIC`) with explicit license acceptance.
- Open tests and CI baseline for reproducible trust.

## Why this is different (measurable)
| Metric | This project | Why it matters |
|---|---|---|
| Privacy-by-default runtime | Web server binds to `127.0.0.1` by default (`--share-lan` to expose) | Reduces accidental data exposure on shared networks |
| Input flexibility | 2 input styles: 23andMe-like text + `.vcf` | Easier onboarding for both consumers and clinics |
| Output depth | Up to 7 markdown reports + structured JSON | Supports both simple and detailed review workflows |
| Cleanup behavior | 24-hour cleanup of stale web job folders | Lowers residual sensitive data footprint |
| Public verification baseline | `11` automated tests in OSS repo | Improves trust for contributors and adopters |
| India-oriented report content | Dedicated prenatal report path + India-context guidance | Better local relevance than generic global-only templates |

## How this helps real users
- Converts raw DNA files into readable, structured reports.
- Highlights lifestyle and medication-context genetic signals in one place.
- Gives a practical summary users can carry into doctor consultations.
- Runs locally, so users are not forced to upload genome data to third-party cloud services.

## How this helps doctors and genetic counselors
- Provides a pre-visit structured snapshot across lifestyle, drug-response, and risk categories.
- Surfaces pharmacogenomics notes for medication discussion.
- Adds a dedicated prenatal-oriented report to support reproductive counseling conversations.
- Exports markdown and JSON artifacts for easier documentation and review.

## Quickstart (3 commands)
```bash
python3 -m pip install -r requirements.txt
python3 scripts/fetch_data.py --source all --accept-licenses
python3 app.py
```

Open `http://localhost:8000`

Optional LAN sharing for a session:
```bash
python3 app.py --share-lan
```

## CLI run
```bash
python3 scripts/run_full_analysis.py examples/genome_demo.txt --name "Demo Subject"
```

## Sanity checklist
Run these before release/push:

```bash
pytest -q
python3 scripts/fetch_data.py --source all --dry-run --accept-licenses
python3 scripts/run_full_analysis.py examples/genome_demo.txt --name "Demo Subject"
```

Expected:
- tests pass
- dataset bootstrap prints planned downloads and writes a manifest
- CLI pipeline completes and writes reports to `reports/`

## Generated outputs
Depending on available datasets, generated reports include:
- `EXHAUSTIVE_GENETIC_REPORT.md`
- `ACTIONABLE_HEALTH_PROTOCOL_V3.md`
- `SIMPLE_REPORT_<name>.md`
- `COMPLETE_EASY_REPORT_<name>.md`
- `SWOT_REPORT_<name>.md`
- `PRENATAL_REPORT_<name>.md`
- `EXHAUSTIVE_DISEASE_RISK_REPORT.md` (when ClinVar dataset is available)
- `comprehensive_results.json`

## Data and licensing
- This repo does not bundle restricted third-party clinical datasets.
- Use `scripts/fetch_data.py` after clone to download permitted sources.
- See `THIRD_PARTY_DATA.md` for source terms and usage notes.

## Safety and limitations
- Decision-support only. Not a diagnostic medical device.
- Report interpretations must be validated by qualified clinicians.
- Dataset completeness and quality can affect output quality.
- This version is optimized for local use and transparency, not for automated clinical diagnosis.

## What is intentionally not bundled
- Real personal genomes (`.vcf`, personal genome text files).
- Generated personal reports.
- Private/internal caches and restricted redistribution datasets.

## Repo map
- `app.py`: local web app
- `scripts/`: parsers, analyzers, report generators, bootstrap utilities
- `templates/`: web templates
- `data/`: local data folder (downloaded post-clone)
- `reports/`: generated output folder
- `tests/`: public regression/sanity tests

## Contributing and governance
- Contribution guide: `CONTRIBUTING.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- Security disclosure: `SECURITY.md`
- Privacy policy: `PRIVACY.md`
- Roadmap: `ROADMAP.md`

## License
Apache License 2.0 (`LICENSE`).
