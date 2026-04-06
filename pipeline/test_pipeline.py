#!/usr/bin/env python3
"""
Test pipeline for TwinSwim OTT — runs Step 1, Step 2, Step 3 in sequence.

Usage:
    python pipeline/test_pipeline.py --file path/to/OTT_Processed_Data.xlsx

Expected results for reference dataset (10,000 rows, 71 columns):
    Step 1: 10,000 records, 71 columns, .xlsx
    Step 2: 42/42 mandatory present, all categories green
    Step 3: All 15 mandatory tests PASS, some good-to-have warnings expected
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow running from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run(file_path: str) -> int:
    print("=" * 60)
    print("  TwinSwim OTT — Pipeline Test Runner")
    print("=" * 60)

    # ── Step 1 ────────────────────────────────────────────────────
    print("\n[STEP 1] Data Ingestion")
    print("-" * 40)
    from pipeline.step1_ingest import run_step1
    r1 = run_step1(file_path)
    if not r1["success"]:
        print(f"  ERROR: {r1['error']}")
        return 1

    print(f"  File       : {r1['filename']}")
    print(f"  Format     : {r1['file_format']}")
    print(f"  Size       : {r1['file_size_mb']} MB")
    print(f"  Records    : {r1['total_records']:,}")
    print(f"  Columns    : {r1['total_columns']}")
    print(f"  Dtype mix  : {r1['dtypes_summary']}")
    print("  STATUS     : PASS")

    df = r1["dataframe"]

    # ── Step 2 ────────────────────────────────────────────────────
    print("\n[STEP 2] Feature Presence Check")
    print("-" * 40)
    from pipeline.step2_features import run_step2
    r2 = run_step2(df)

    print(f"  Mandatory  : {r2['mandatory_present']}/{r2['mandatory_total']} present ({r2['mandatory_coverage_pct']}%)")
    print(f"  Optional   : {r2['optional_present']}/{r2['optional_total']} present ({r2['optional_coverage_pct']}%)")

    if r2["mandatory_missing"]:
        print(f"  MISSING MANDATORY: {r2['mandatory_missing']}")

    print("\n  Category breakdown:")
    for cat in r2["categories"]:
        icon = "✓" if cat["status"] == "pass" else ("!" if cat["status"] == "partial" else "✗")
        print(
            f"    [{icon}] {cat['name'][:40]:<40} "
            f"M:{cat['mandatory_present']}/{cat['mandatory_count']}  "
            f"O:{cat['optional_present']}/{cat['optional_count']}"
        )

    step2_status = "PASS" if r2["step2_passed"] else "FAIL"
    print(f"  STATUS     : {step2_status}")

    if not r2["step2_passed"]:
        print("  Pipeline blocked — mandatory features missing.")
        return 1

    # ── Step 3 ────────────────────────────────────────────────────
    print("\n[STEP 3] Quality Tests")
    print("-" * 40)
    from pipeline.step3_quality import run_step3
    r3 = run_step3(df)

    print(f"  Mandatory  : {r3['mandatory_passed']}/15 passed, {r3['mandatory_failed']} failed")
    print(f"  Warnings   : {r3['optional_warnings']}/10 good-to-have warnings")

    print("\n  Mandatory test results:")
    for t in r3["mandatory_tests"]:
        icon = "PASS" if t["passed"] else f"FAIL [{t['severity']}]"
        print(f"    [{icon:16}] {t['id']} — {t['name']}")
        if not t["passed"]:
            print(f"               {t['message']}")

    print("\n  Good-to-have warnings:")
    for t in r3["optional_tests"]:
        icon = "WARN" if t["has_warning"] else "OK  "
        print(f"    [{icon}] {t['id']} — {t['name']}")
        if t["has_warning"]:
            print(f"           {t['message']}")

    # ── Save report ───────────────────────────────────────────────
    report_path = PROJECT_ROOT / "data" / "test_quality_report.xlsx"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        report_bytes = r3["generate_report"]()
        with open(report_path, "wb") as f:
            f.write(report_bytes)
        print(f"\n  Quality report saved → {report_path}")
    except Exception as e:
        print(f"\n  Warning: could not save report: {e}")

    # ── Final result ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    if r3["mandatory_all_passed"]:
        print("  RESULT: ALL MANDATORY TESTS PASSED — Dataset is production-ready")
        print("=" * 60)
        return 0
    else:
        print(f"  RESULT: {r3['mandatory_failed']} MANDATORY TEST(S) FAILED — fix issues and re-upload")
        print("=" * 60)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TwinSwim OTT pipeline test runner"
    )
    parser.add_argument("--file", required=True, help="Path to the dataset file (.xlsx or .csv)")
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    exit_code = run(args.file)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
