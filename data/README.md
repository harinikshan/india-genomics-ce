# Data Directory

This folder stores local datasets used by the analysis pipeline.

The open-source release does not bundle full third-party clinical databases.
Download supported datasets with:

```bash
python scripts/fetch_data.py --source all --accept-licenses
```

Downloaded files are placed under `data/external/` by default.
