"""
Step 3 — Data Quality Tests
15 mandatory tests (T01–T15) + 10 good-to-have tests (G01–G10).
"""
from __future__ import annotations

import io
from typing import Callable

import numpy as np
import pandas as pd


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _safe_col(df: pd.DataFrame, col: str) -> pd.Series | None:
    return df[col] if col in df.columns else None


def _pct(n: int, total: int) -> float:
    return round(n / total * 100, 1) if total > 0 else 0.0


# ─── Mandatory tests ──────────────────────────────────────────────────────────

def _t01(df: pd.DataFrame) -> dict:
    col = "user_id"
    if col not in df.columns:
        return {"passed": False, "affected_rows": 0,
                "message": "user_id column not found", "severity": "Critical"}
    n = int(df[col].isnull().sum())
    passed = n == 0
    return {
        "passed": passed,
        "affected_rows": n,
        "message": (
            f"user_id: zero nulls — primary key is clean"
            if passed else
            f"user_id: {n} null values — users have no identity"
        ),
        "severity": "Critical",
    }


def _t02(df: pd.DataFrame) -> dict:
    col = "user_id"
    if col not in df.columns:
        return {"passed": False, "affected_rows": 0,
                "message": "user_id column not found", "severity": "Critical"}
    n = int(df[col].duplicated().sum())
    total = len(df)
    passed = n == 0
    return {
        "passed": passed,
        "affected_rows": n,
        "message": (
            f"user_id: all {total} values unique — one row per user"
            if passed else
            f"user_id: {n} duplicate values — multiple rows for same user"
        ),
        "severity": "Critical",
    }


MANDATORY_COLS_FOR_T03 = [
    "user_id", "completion_rate", "early_drop_rate", "mid_drop_rate",
    "device_type", "is_weekend", "watch_context", "entry_source", "rewatch_flag",
    "skip_intro_rate", "session_duration_min", "num_titles_watched", "time_of_day",
    "buffer_events", "avg_bitrate_mbps", "pause_cluster_pattern", "fav_genre",
    "sports_dependency_score", "binge_index", "avg_watch_gap_days", "plan_type",
    "monthly_price", "is_bundle", "tenure_months", "discount_flag",
    "discount_expectation_flag", "churn_probability", "last_active_days_ago",
    "piracy_exposure_flag", "content_unavailable_flag", "vpn_usage_suspected",
    "piracy_recency_score", "nps_score", "content_satisfaction", "price_perception",
    "city", "isp_partner", "network_type", "event_calendar_flag", "urbanicity",
    "avg_network_jitter", "peak_hour_congestion_flag",
]


def _t03(df: pd.DataFrame) -> dict:
    failures = []
    total = len(df)
    for col in MANDATORY_COLS_FOR_T03:
        if col not in df.columns:
            continue
        n = int(df[col].isnull().sum())
        if col == "piracy_trigger_reason":
            # structural null — allow up to 95%
            if n / total > 0.95:
                failures.append(f"{col}: {n} nulls ({_pct(n, total)}%) exceeds 95% structural threshold")
        elif n > 0:
            failures.append(f"{col}: {n} nulls ({_pct(n, total)}%)")

    passed = len(failures) == 0
    return {
        "passed": passed,
        "affected_rows": len(failures),
        "message": (
            "All mandatory columns: no unexpected nulls"
            if passed else
            "Null issues found — " + "; ".join(failures[:5]) + ("..." if len(failures) > 5 else "")
        ),
        "severity": "Critical",
    }


BINARY_FLAG_COLS = [
    "is_weekend", "is_bundle", "discount_flag", "discount_expectation_flag",
    "content_unavailable_flag", "vpn_usage_suspected", "issue_repeat_flag",
    "event_calendar_flag", "peak_hour_congestion_flag", "hdr_support_flag",
    "rewatch_flag", "casting_usage_flag",
]
VALID_BINARY = {0, 1, True, False, "true", "false", "True", "False", "0", "1",
                0.0, 1.0, "0.0", "1.0"}


def _t04(df: pd.DataFrame) -> dict:
    failures = []
    for col in BINARY_FLAG_COLS:
        if col not in df.columns:
            continue
        unique_vals = set(df[col].dropna().unique())
        invalid = unique_vals - VALID_BINARY
        if invalid:
            failures.append(f"{col}: {invalid}")
    passed = len(failures) == 0
    return {
        "passed": passed,
        "affected_rows": len(failures),
        "message": (
            "All binary flag columns contain valid values (0/1/True/False)"
            if passed else
            "Invalid binary values — " + "; ".join(failures[:3]) + ("..." if len(failures) > 3 else "")
        ),
        "severity": "Moderate",
    }


PROB_COLS = [
    "completion_rate", "early_drop_rate", "mid_drop_rate", "binge_index",
    "sports_dependency_score", "churn_probability", "piracy_recency_score",
    "skip_intro_rate",
]


def _t05(df: pd.DataFrame) -> dict:
    failures = []
    for col in PROB_COLS:
        if col not in df.columns:
            continue
        try:
            s = pd.to_numeric(df[col], errors="coerce")
            n = int(((s < 0.0) | (s > 1.0)).sum())
            if n > 0:
                failures.append(
                    f"{col}: {n} values outside [0.0, 1.0] — range: {s.min():.4f} to {s.max():.4f}"
                )
        except Exception:
            pass
    passed = len(failures) == 0
    return {
        "passed": passed,
        "affected_rows": len(failures),
        "message": (
            "All probability/rate columns within [0.0, 1.0]"
            if passed else
            "; ".join(failures[:3]) + ("..." if len(failures) > 3 else "")
        ),
        "severity": "Critical",
    }


POSITIVE_COLS = [
    "watch_minutes", "session_duration_min", "num_titles_watched",
    "buffer_events", "avg_bitrate_mbps", "No_of_Pauses", "tenure_months",
    "monthly_price", "avg_watch_gap_days", "last_active_days_ago",
    "avg_network_jitter", "resolution_time_hrs", "csat_score",
]


def _t06(df: pd.DataFrame) -> dict:
    failures = []
    for col in POSITIVE_COLS:
        if col not in df.columns:
            continue
        try:
            s = pd.to_numeric(df[col], errors="coerce")
            n = int((s < 0).sum())
            if n > 0:
                failures.append(f"{col}: {n} negative values (min={s.min():.2f})")
        except Exception:
            pass
    passed = len(failures) == 0
    return {
        "passed": passed,
        "affected_rows": len(failures),
        "message": (
            "No negative values in positive-only columns"
            if passed else
            "; ".join(failures[:3]) + ("..." if len(failures) > 3 else "")
        ),
        "severity": "Moderate",
    }


def _t07(df: pd.DataFrame) -> dict:
    col = "plan_type"
    valid = {"basic", "standard", "premium"}
    if col not in df.columns:
        return {"passed": True, "affected_rows": 0,
                "message": "plan_type not present — skipped", "severity": "Moderate"}
    vals = set(df[col].dropna().str.lower().unique())
    invalid = vals - valid
    passed = len(invalid) == 0
    return {
        "passed": passed,
        "affected_rows": len(invalid),
        "message": (
            "plan_type: valid values only (basic/standard/premium)"
            if passed else
            f"plan_type: invalid values found: {invalid}"
        ),
        "severity": "Moderate",
    }


def _t08(df: pd.DataFrame) -> dict:
    col = "device_type"
    valid = {"mobile", "tablet", "smart_tv", "laptop", "desktop"}
    if col not in df.columns:
        return {"passed": True, "affected_rows": 0,
                "message": "device_type not present — skipped", "severity": "Moderate"}
    vals = set(df[col].dropna().str.lower().unique())
    invalid = vals - valid
    passed = len(invalid) == 0
    return {
        "passed": passed,
        "affected_rows": len(invalid),
        "message": (
            "device_type: valid values only"
            if passed else
            f"device_type: invalid values found: {invalid}"
        ),
        "severity": "Moderate",
    }


def _t09(df: pd.DataFrame) -> dict:
    col = "network_type"
    valid = {"4g", "5g", "fiber", "broadband"}
    if col not in df.columns:
        return {"passed": True, "affected_rows": 0,
                "message": "network_type not present — skipped", "severity": "Moderate"}
    vals = set(df[col].dropna().str.lower().unique())
    invalid = vals - valid
    passed = len(invalid) == 0
    return {
        "passed": passed,
        "affected_rows": len(invalid),
        "message": (
            "network_type: valid values only (4G/5G/Fiber/Broadband)"
            if passed else
            f"network_type: invalid values found: {invalid}"
        ),
        "severity": "Moderate",
    }


PLAN_RANGES = {
    "basic": (4.50, 12.00),
    "standard": (9.00, 17.00),
    "premium": (12.00, 22.00),
}


def _t10(df: pd.DataFrame) -> dict:
    if "plan_type" not in df.columns or "monthly_price" not in df.columns:
        return {"passed": True, "affected_rows": 0,
                "message": "plan_type or monthly_price not present — skipped", "severity": "Moderate"}
    try:
        tmp = df[["plan_type", "monthly_price"]].copy()
        tmp["monthly_price"] = pd.to_numeric(tmp["monthly_price"], errors="coerce")
        out_of_range = 0
        for plan, (lo, hi) in PLAN_RANGES.items():
            mask = tmp["plan_type"].str.lower() == plan
            sub = tmp.loc[mask, "monthly_price"]
            out_of_range += int(((sub < lo) | (sub > hi)).sum())
        total = len(df)
        pct = out_of_range / total * 100
        passed = pct <= 1.0
        return {
            "passed": passed,
            "affected_rows": out_of_range,
            "message": (
                "monthly_price within valid range per plan type"
                if passed else
                f"monthly_price: {out_of_range} rows ({pct:.1f}%) outside valid plan ranges"
            ),
            "severity": "Moderate",
        }
    except Exception as e:
        return {"passed": False, "affected_rows": 0,
                "message": f"T10 error: {e}", "severity": "Moderate"}


def _t11(df: pd.DataFrame) -> dict:
    col = "tenure_months"
    if col not in df.columns:
        return {"passed": True, "affected_rows": 0,
                "message": "tenure_months not present — skipped", "severity": "Moderate"}
    try:
        s = pd.to_numeric(df[col], errors="coerce")
        n = int(((s < 1) | (s > 60)).sum())
        passed = n == 0
        return {
            "passed": passed,
            "affected_rows": n,
            "message": (
                "tenure_months: all values within [1, 60]"
                if passed else
                f"tenure_months: {n} values outside [1, 60]"
            ),
            "severity": "Moderate",
        }
    except Exception as e:
        return {"passed": False, "affected_rows": 0,
                "message": f"T11 error: {e}", "severity": "Moderate"}


NUMERIC_TYPE_COLS = [
    "completion_rate", "binge_index", "monthly_price", "churn_probability",
    "avg_watch_gap_days", "early_drop_rate", "mid_drop_rate",
    "sports_dependency_score", "piracy_recency_score", "avg_network_jitter",
    "avg_bitrate_mbps", "nps_score", "content_satisfaction", "price_perception",
    "tenure_months", "last_active_days_ago",
]


def _t12(df: pd.DataFrame) -> dict:
    failures = []
    for col in NUMERIC_TYPE_COLS:
        if col not in df.columns:
            continue
        dtype = str(df[col].dtype)
        if dtype in ("object", "string"):
            failures.append(f"{col}: expected numeric but found {dtype}")
    passed = len(failures) == 0
    return {
        "passed": passed,
        "affected_rows": len(failures),
        "message": (
            "All numeric columns have correct data types"
            if passed else
            "; ".join(failures[:4]) + ("..." if len(failures) > 4 else "")
        ),
        "severity": "Critical",
    }


def _t13(df: pd.DataFrame) -> dict:
    n = int(df.duplicated().sum())
    passed = n == 0
    return {
        "passed": passed,
        "affected_rows": n,
        "message": (
            "No fully duplicate rows found"
            if passed else
            f"{n} fully duplicate rows found — these must be removed"
        ),
        "severity": "Moderate",
    }


CLUSTERING_COLS = [
    "completion_rate", "early_drop_rate", "mid_drop_rate", "binge_index",
    "sports_dependency_score", "churn_probability", "monthly_price",
    "tenure_months", "avg_watch_gap_days", "last_active_days_ago",
    "avg_network_jitter", "avg_bitrate_mbps", "nps_score",
    "content_satisfaction", "price_perception",
]


def _t14(df: pd.DataFrame) -> dict:
    failures = []
    for col in CLUSTERING_COLS:
        if col not in df.columns:
            continue
        try:
            s = pd.to_numeric(df[col], errors="coerce")
            n_nan = int(s.isnull().sum())
            n_inf = int(np.isinf(s.replace([np.nan], [0])).sum())
            total_bad = n_nan + n_inf
            if total_bad > 0:
                failures.append(f"{col}: contains {total_bad} NaN/Inf values — K-Means will fail")
        except Exception:
            pass
    passed = len(failures) == 0
    return {
        "passed": passed,
        "affected_rows": len(failures),
        "message": (
            "No NaN or Inf values in clustering features"
            if passed else
            "; ".join(failures[:3]) + ("..." if len(failures) > 3 else "")
        ),
        "severity": "Critical",
    }


def _t15(df: pd.DataFrame) -> dict:
    n = len(df)
    passed = n >= 500
    return {
        "passed": passed,
        "affected_rows": 0 if passed else 500 - n,
        "message": (
            f"{n:,} rows — well above 500 minimum"
            if passed else
            f"Only {n} rows — minimum 500 required for meaningful clustering"
        ),
        "severity": "Critical",
    }


MANDATORY_TESTS_META = [
    ("T01", "Primary Key Null Check", ["user_id"], _t01),
    ("T02", "user_id Uniqueness", ["user_id"], _t02),
    ("T03", "Mandatory Columns Null Check", ["all mandatory cols"], _t03),
    ("T04", "Binary Flag Validity", BINARY_FLAG_COLS, _t04),
    ("T05", "Probability/Rate Range [0–1]", PROB_COLS, _t05),
    ("T06", "No Negative Values", POSITIVE_COLS, _t06),
    ("T07", "plan_type Valid Categories", ["plan_type"], _t07),
    ("T08", "device_type Valid Categories", ["device_type"], _t08),
    ("T09", "network_type Valid Categories", ["network_type"], _t09),
    ("T10", "monthly_price vs Plan Range", ["plan_type", "monthly_price"], _t10),
    ("T11", "tenure_months Range [1–60]", ["tenure_months"], _t11),
    ("T12", "Data Type Correctness", NUMERIC_TYPE_COLS, _t12),
    ("T13", "No Fully Duplicate Rows", ["all columns"], _t13),
    ("T14", "No NaN/Inf in Clustering Features", CLUSTERING_COLS, _t14),
    ("T15", "Minimum Row Count (500)", ["row count"], _t15),
]


# ─── Good-to-have tests ───────────────────────────────────────────────────────

def _g01(df: pd.DataFrame) -> dict:
    checks = [
        ("piracy_trigger_reason", 85.0, 95.0),
        ("payment_failure_count", 60.0, 95.0),
        ("content_satisfaction", 0.0, 80.0),
    ]
    warnings = []
    total = len(df)
    for col, lo, hi in checks:
        if col not in df.columns:
            continue
        null_rate = _pct(int(df[col].isnull().sum()), total)
        if null_rate < lo or null_rate > hi:
            warnings.append(
                f"{col}: null rate {null_rate}% — outside expected range {lo:.0f}%–{hi:.0f}%"
            )
    has_warning = len(warnings) > 0
    return {
        "has_warning": has_warning,
        "message": (
            "Structural null rates within expected bands"
            if not has_warning else
            "; ".join(warnings)
        ),
    }


def _g02(df: pd.DataFrame) -> dict:
    numerics = df.select_dtypes(include=[np.number])
    low_var = []
    for col in numerics.columns:
        try:
            v = float(numerics[col].var())
            if v < 0.01:
                low_var.append(f"{col}: variance={v:.6f}")
        except Exception:
            pass
    has_warning = len(low_var) > 0
    return {
        "has_warning": has_warning,
        "message": (
            "No near-constant features detected"
            if not has_warning else
            f"{len(low_var)} near-constant feature(s) — will be auto-dropped: " + ", ".join(low_var[:5])
        ),
    }


def _g03(df: pd.DataFrame) -> dict:
    numerics = df.select_dtypes(include=[np.number])
    low_cv = []
    for col in numerics.columns:
        try:
            s = numerics[col].dropna()
            mean = float(s.mean())
            std = float(s.std())
            var = float(s.var())
            if mean != 0 and var > 0.01:
                cv = abs(std / mean)
                if cv < 0.05:
                    low_cv.append(f"{col}: CV={cv:.4f}")
        except Exception:
            pass
    has_warning = len(low_cv) > 0
    return {
        "has_warning": has_warning,
        "message": (
            "No near-uniform distributions detected"
            if not has_warning else
            f"{len(low_cv)} near-uniform feature(s): " + ", ".join(low_cv[:5])
        ),
    }


def _g04(df: pd.DataFrame) -> dict:
    numerics = df.select_dtypes(include=[np.number])
    if numerics.shape[1] < 2:
        return {"has_warning": False, "message": "Not enough numeric columns for correlation check"}
    try:
        corr = numerics.corr().abs()
        pairs = []
        cols = corr.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                r = corr.iloc[i, j]
                if r > 0.85:
                    pairs.append(f"({cols[i]}, {cols[j]}): r={r:.2f}")
        has_warning = len(pairs) > 0
        return {
            "has_warning": has_warning,
            "message": (
                "No highly correlated feature pairs (|r|>0.85)"
                if not has_warning else
                f"{len(pairs)} highly correlated pair(s): " + ", ".join(pairs[:5])
            ),
        }
    except Exception as e:
        return {"has_warning": False, "message": f"Correlation check skipped: {e}"}


def _g05(df: pd.DataFrame) -> dict:
    check_cols = ["plan_type", "network_type", "device_type"]
    warnings = []
    for col in check_cols:
        if col not in df.columns:
            continue
        vc = df[col].value_counts()
        for val, cnt in vc.items():
            if cnt < 50:
                warnings.append(f"{col}: category '{val}' has only {cnt} rows")
    has_warning = len(warnings) > 0
    return {
        "has_warning": has_warning,
        "message": (
            "All categorical classes have adequate representation (≥50 rows)"
            if not has_warning else
            "; ".join(warnings[:5])
        ),
    }


OUTLIER_COLS = [
    "session_duration_min", "monthly_price", "avg_watch_gap_days",
    "num_titles_watched", "avg_network_jitter",
]


def _g06(df: pd.DataFrame) -> dict:
    warnings = []
    total = len(df)
    for col in OUTLIER_COLS:
        if col not in df.columns:
            continue
        try:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            mean, std = float(s.mean()), float(s.std())
            if std == 0:
                continue
            n = int(((s < mean - 3 * std) | (s > mean + 3 * std)).sum())
            pct = _pct(n, total)
            if n > 0:
                warnings.append(f"{col}: {n} outliers ({pct}% of rows) beyond ±3σ — may distort centroids")
        except Exception:
            pass
    has_warning = len(warnings) > 0
    return {
        "has_warning": has_warning,
        "message": (
            "No significant outliers detected beyond ±3σ"
            if not has_warning else
            "; ".join(warnings[:4])
        ),
    }


def _g07(df: pd.DataFrame) -> dict:
    if "network_type" not in df.columns or "avg_network_jitter" not in df.columns:
        return {"has_warning": False, "message": "network_type or avg_network_jitter not present — skipped"}
    try:
        tmp = df[["network_type", "avg_network_jitter"]].copy()
        tmp["avg_network_jitter"] = pd.to_numeric(tmp["avg_network_jitter"], errors="coerce")
        fiber_mean = float(
            tmp.loc[tmp["network_type"].str.lower() == "fiber", "avg_network_jitter"].mean()
        )
        has_warning = fiber_mean > 25.0
        return {
            "has_warning": has_warning,
            "message": (
                f"Fiber jitter within normal range (mean={fiber_mean:.1f}ms)"
                if not has_warning else
                f"Fiber users: mean jitter={fiber_mean:.1f}ms — higher than expected (suggests jitter not network-conditioned)"
            ),
        }
    except Exception as e:
        return {"has_warning": False, "message": f"Jitter check skipped: {e}"}


def _g08(df: pd.DataFrame) -> dict:
    col = "binge_index"
    if col not in df.columns:
        return {"has_warning": False, "message": "binge_index not present — skipped"}
    try:
        std = float(pd.to_numeric(df[col], errors="coerce").std())
        has_warning = std < 0.15
        return {
            "has_warning": has_warning,
            "message": (
                f"binge_index: std={std:.3f} — good spread for persona differentiation"
                if not has_warning else
                f"binge_index: std={std:.3f} — low spread may limit persona differentiation"
            ),
        }
    except Exception as e:
        return {"has_warning": False, "message": f"Binge index check skipped: {e}"}


def _g09(df: pd.DataFrame) -> dict:
    col = "avg_watch_gap_days"
    if col not in df.columns:
        return {"has_warning": False, "message": "avg_watch_gap_days not present — skipped"}
    try:
        max_val = float(pd.to_numeric(df[col], errors="coerce").max())
        has_warning = max_val <= 14.0
        return {
            "has_warning": has_warning,
            "message": (
                f"avg_watch_gap_days: max={max_val:.1f} days — good range coverage"
                if not has_warning else
                f"avg_watch_gap_days: max={max_val:.1f} days — compressed range may prevent re-engager/churn separation"
            ),
        }
    except Exception as e:
        return {"has_warning": False, "message": f"Watch gap check skipped: {e}"}


def _g10(df: pd.DataFrame) -> dict:
    needed = ["completion_rate", "early_drop_rate", "mid_drop_rate"]
    if not all(c in df.columns for c in needed):
        return {"has_warning": False, "message": "Rate columns not all present — skipped"}
    try:
        cr = pd.to_numeric(df["completion_rate"], errors="coerce")
        er = pd.to_numeric(df["early_drop_rate"], errors="coerce")
        mr = pd.to_numeric(df["mid_drop_rate"], errors="coerce")
        total_rate = cr + er + mr
        n = int(((total_rate - 1.0).abs() > 0.01).sum())
        has_warning = n > 0
        return {
            "has_warning": has_warning,
            "message": (
                "Rate sum (completion + early_drop + mid_drop) ≈ 1.0 for all rows"
                if not has_warning else
                f"Rate sum: {n} rows where completion+early_drop+mid_drop ≠ 1.0"
            ),
        }
    except Exception as e:
        return {"has_warning": False, "message": f"Rate sum check skipped: {e}"}


OPTIONAL_TESTS_META = [
    ("G01", "Structural Null Rate Check", ["piracy_trigger_reason", "payment_failure_count", "content_satisfaction"], _g01),
    ("G02", "Zero-Variance Feature Detection", ["all numeric cols"], _g02),
    ("G03", "Near-Uniform Distribution (Low CV)", ["all numeric cols"], _g03),
    ("G04", "Highly Correlated Feature Pairs", ["all numeric cols"], _g04),
    ("G05", "Class Balance Check", ["plan_type", "network_type", "device_type"], _g05),
    ("G06", "Outlier Detection (±3σ)", OUTLIER_COLS, _g06),
    ("G07", "Jitter vs Network Type Consistency", ["network_type", "avg_network_jitter"], _g07),
    ("G08", "binge_index Differentiation", ["binge_index"], _g08),
    ("G09", "avg_watch_gap_days Range Adequacy", ["avg_watch_gap_days"], _g09),
    ("G10", "Rate Sum Consistency", ["completion_rate", "early_drop_rate", "mid_drop_rate"], _g10),
]


# ─── Report generator ─────────────────────────────────────────────────────────

def _generate_report(mandatory_tests: list[dict], optional_tests: list[dict]) -> bytes:
    output = io.BytesIO()
    workbook = None
    try:
        import xlsxwriter  # type: ignore
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        ws = workbook.add_worksheet("Quality Report")

        # Formats
        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#0D1B2A", "font_color": "#FFFFFF",
            "border": 1, "align": "center", "valign": "vcenter",
        })
        pass_fmt = workbook.add_format({"bg_color": "#D1FAE5", "border": 1, "valign": "vcenter"})
        fail_critical_fmt = workbook.add_format({"bg_color": "#FEE2E2", "border": 1, "valign": "vcenter"})
        fail_moderate_fmt = workbook.add_format({"bg_color": "#FED7AA", "border": 1, "valign": "vcenter"})
        warn_fmt = workbook.add_format({"bg_color": "#FEF3C7", "border": 1, "valign": "vcenter"})
        normal_fmt = workbook.add_format({"border": 1, "valign": "vcenter"})

        headers = ["Test ID", "Test Name", "Column(s) Tested", "Result", "Rows Affected", "Issue / Message", "Severity"]
        col_widths = [10, 35, 45, 12, 14, 60, 12]

        for i, (h, w) in enumerate(zip(headers, col_widths)):
            ws.write(0, i, h, header_fmt)
            ws.set_column(i, i, w)

        row = 1
        for t in mandatory_tests:
            if t["passed"]:
                fmt = pass_fmt
                result_str = "PASS"
            elif t["severity"] == "Critical":
                fmt = fail_critical_fmt
                result_str = "FAIL (Critical)"
            else:
                fmt = fail_moderate_fmt
                result_str = "FAIL (Moderate)"
            cols_str = ", ".join(t["columns_tested"]) if isinstance(t["columns_tested"], list) else str(t["columns_tested"])
            ws.write(row, 0, t["id"], fmt)
            ws.write(row, 1, t["name"], fmt)
            ws.write(row, 2, cols_str, fmt)
            ws.write(row, 3, result_str, fmt)
            ws.write(row, 4, t["affected_rows"], fmt)
            ws.write(row, 5, t["message"], fmt)
            ws.write(row, 6, t["severity"], fmt)
            row += 1

        for t in optional_tests:
            fmt = warn_fmt if t["has_warning"] else pass_fmt
            result_str = "WARNING" if t["has_warning"] else "OK"
            cols_str = ", ".join(t["columns_tested"]) if isinstance(t["columns_tested"], list) else str(t["columns_tested"])
            ws.write(row, 0, t["id"], fmt)
            ws.write(row, 1, t["name"], fmt)
            ws.write(row, 2, cols_str, fmt)
            ws.write(row, 3, result_str, fmt)
            ws.write(row, 4, 0, fmt)
            ws.write(row, 5, t["message"], fmt)
            ws.write(row, 6, "Info", fmt)
            row += 1

        ws.freeze_panes(1, 0)
        workbook.close()
    except Exception:
        if workbook:
            try:
                workbook.close()
            except Exception:
                pass
        output = io.BytesIO(b"")

    return output.getvalue()


# ─── Main entry point ─────────────────────────────────────────────────────────

def run_step3(df: pd.DataFrame) -> dict:
    mandatory_results = []
    for tid, name, cols, fn in MANDATORY_TESTS_META:
        try:
            res = fn(df)
        except Exception as e:
            res = {"passed": False, "affected_rows": 0,
                   "message": f"{tid} encountered an error: {e}", "severity": "Critical"}
        mandatory_results.append({
            "id": tid,
            "name": name,
            "columns_tested": cols if isinstance(cols, list) else [cols],
            "passed": res["passed"],
            "affected_rows": res.get("affected_rows", 0),
            "message": res.get("message", ""),
            "severity": res.get("severity", "Moderate"),
        })

    optional_results = []
    for tid, name, cols, fn in OPTIONAL_TESTS_META:
        try:
            res = fn(df)
        except Exception as e:
            res = {"has_warning": False, "message": f"{tid} skipped: {e}"}
        optional_results.append({
            "id": tid,
            "name": name,
            "columns_tested": cols if isinstance(cols, list) else [cols],
            "has_warning": res.get("has_warning", False),
            "message": res.get("message", ""),
        })

    m_passed = sum(1 for t in mandatory_results if t["passed"])
    m_failed = sum(1 for t in mandatory_results if not t["passed"])
    o_warnings = sum(1 for t in optional_results if t["has_warning"])

    def generate_report() -> bytes:
        return _generate_report(mandatory_results, optional_results)

    return {
        "mandatory_tests": mandatory_results,
        "optional_tests": optional_results,
        "mandatory_passed": m_passed,
        "mandatory_failed": m_failed,
        "mandatory_all_passed": m_failed == 0,
        "optional_warnings": o_warnings,
        "generate_report": generate_report,
    }
