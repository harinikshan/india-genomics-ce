# Third-Party Data Policy

This repository does not ship full clinical databases by default.
Use `scripts/fetch_data.py` to download supported external datasets.

## Important
- You must comply with each provider's license and terms.
- This project is software-only and does not convey rights to third-party data.
- Some sources may restrict commercial reuse or require specific attribution.

## Sources

### ClinVar (NCBI)
- URL: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/
- Typical file fetched: `variant_summary.txt.gz`
- License/terms: NCBI terms and data usage policy.

### PharmGKB
- URL: https://www.pharmgkb.org/downloads
- Typical files fetched: clinical annotations exports.
- License/terms: check PharmGKB data usage policy before use.

### CPIC
- URL: https://cpicpgx.org/ and https://api.cpicpgx.org/v1/
- Typical files fetched: recommendation/diplotype JSON exports.
- License/terms: check CPIC/API terms before use.

## Checksums
The fetch script computes SHA-256 for each downloaded file.
If an upstream checksum is available, the script validates it.
