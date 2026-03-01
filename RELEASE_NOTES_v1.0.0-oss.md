# Release Notes: v1.0.0-oss

## Highlights
- First public Community Edition release.
- Local-first web + CLI workflow.
- Added external dataset bootstrap utility (`scripts/fetch_data.py`).
- Removed personal genomic artifacts and generated personal reports.
- Added OSS governance docs, privacy/security policy, and CI tests.

## Breaking/behavior changes
- Full datasets are no longer bundled in-repo.
- Users must fetch external datasets and accept source terms.

## Known limitations
- Third-party data schemas may change upstream.
- Data download endpoints can change without notice.
- Output remains informational and non-diagnostic.
