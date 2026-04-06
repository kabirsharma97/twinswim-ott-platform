# TwinSwim OTT — Persona Intelligence Platform

A Reflex web application for the TwinSwim OTT data readiness pipeline.
Covers file upload → feature presence check → data quality testing, stopping at the clustering gate.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialise Reflex (first time only)
reflex init

# 4. Start the app
reflex run
```

App opens at: http://localhost:3000

## Test the pipeline (without the UI)

```bash
python pipeline/test_pipeline.py --file path/to/OTT_Processed_Data.xlsx
```

Expected output for the 10,000-row reference dataset:
- Step 1: 10,000 records, 71 columns, .xlsx
- Step 2: 42/42 mandatory features present
- Step 3: All 15 mandatory tests PASS
- Quality report saved to `data/test_quality_report.xlsx`

## Folder structure

```
brandcine_ott_app/
├── rxconfig.py                      # Reflex config (ports, app name)
├── requirements.txt
├── Procfile                         # Production deploy command
├── assets/
│   └── feature_store_template.xlsx  # Auto-generated on first run
├── data/uploads/                    # Temporary upload storage
├── pipeline/
│   ├── step1_ingest.py              # File loading + profiling
│   ├── step2_features.py            # Feature presence check
│   ├── step3_quality.py             # 15 mandatory + 10 optional tests
│   ├── create_template.py           # Feature store template generator
│   └── test_pipeline.py             # CLI test runner
└── brandcine_ott_app/
    ├── brandcine_ott_app.py         # App entry + sidebar + routing
    ├── state.py                     # AppState (Reflex state)
    ├── styles.py                    # Design system constants
    └── pages/
        ├── upload.py                # Upload page
        ├── step1.py                 # Ingestion results
        ├── step2.py                 # Feature presence check
        ├── step3.py                 # Quality tests
        └── ready.py                 # Clustering ready page
```

## Deployment

```bash
reflex run --env prod
```

Or use the Procfile with any PaaS that supports Python (Railway, Render, Fly.io).
