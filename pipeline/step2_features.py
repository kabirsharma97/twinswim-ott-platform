"""
Step 2 — Feature Presence Check
Compares uploaded file columns against the TwinSwim feature store.
"""
from __future__ import annotations

import pandas as pd

# ─── Feature store definitions ────────────────────────────────────────────────

MANDATORY_FEATURES: list[str] = [
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

OPTIONAL_FEATURES: list[str] = [
    "content_id", "genre", "watch_minutes", "session_start", "No_of_Pauses",
    "Content_Tags", "Content_Length", "session_id", "volume_change_events",
    "attention_decay_curve", "secondary_device", "smart_tv_brand", "app_version",
    "screen_size_category", "casting_usage_flag", "hdr_support_flag",
    "os_version_major", "payment_failure_count", "piracy_trigger_reason",
    "ticket_id", "issue_type", "resolution_time_hrs", "csat_score", "support_channel",
    "issue_repeat_flag", "post_id", "platform", "sentiment_score", "mentioned_genre",
]

# Category → (mandatory_list, optional_list)
CATEGORIES: list[dict] = [
    {
        "name": "User Identity & Content Interaction",
        "mandatory": ["user_id", "completion_rate", "early_drop_rate", "mid_drop_rate",
                      "device_type", "is_weekend"],
        "optional": ["content_id", "genre", "watch_minutes", "session_start",
                     "No_of_Pauses", "Content_Tags", "Content_Length"],
    },
    {
        "name": "Viewing Context & Discovery",
        "mandatory": ["watch_context", "entry_source", "rewatch_flag", "skip_intro_rate"],
        "optional": [],
    },
    {
        "name": "Session Behaviour Metrics",
        "mandatory": ["session_duration_min", "num_titles_watched", "time_of_day",
                      "buffer_events", "avg_bitrate_mbps", "pause_cluster_pattern"],
        "optional": ["session_id", "volume_change_events", "attention_decay_curve"],
    },
    {
        "name": "Content Affinity & Behavioral Traits",
        "mandatory": ["fav_genre", "sports_dependency_score", "binge_index", "avg_watch_gap_days"],
        "optional": [],
    },
    {
        "name": "Editorial / Device Context",
        "mandatory": [],
        "optional": ["secondary_device", "smart_tv_brand", "app_version",
                     "screen_size_category", "casting_usage_flag", "hdr_support_flag",
                     "os_version_major"],
    },
    {
        "name": "Subscription & Commercial Behaviour",
        "mandatory": ["plan_type", "monthly_price", "is_bundle", "tenure_months",
                      "discount_flag", "discount_expectation_flag"],
        "optional": [],
    },
    {
        "name": "Risk, Churn & Piracy Behaviour",
        "mandatory": ["churn_probability", "last_active_days_ago", "piracy_exposure_flag",
                      "content_unavailable_flag", "vpn_usage_suspected", "piracy_recency_score"],
        "optional": ["payment_failure_count", "piracy_trigger_reason"],
    },
    {
        "name": "Support Interaction & Trust",
        "mandatory": [],
        "optional": ["ticket_id", "issue_type", "resolution_time_hrs", "csat_score",
                     "support_channel", "issue_repeat_flag"],
    },
    {
        "name": "Customer Sentiment & Advocacy",
        "mandatory": ["nps_score", "content_satisfaction", "price_perception"],
        "optional": [],
    },
    {
        "name": "Social Media Signals",
        "mandatory": [],
        "optional": ["post_id", "platform", "sentiment_score", "mentioned_genre"],
    },
    {
        "name": "Network & Geographic Context",
        "mandatory": ["city", "isp_partner", "network_type", "event_calendar_flag",
                      "urbanicity", "avg_network_jitter", "peak_hour_congestion_flag"],
        "optional": [],
    },
]


def run_step2(df: pd.DataFrame) -> dict:
    """Compare uploaded columns against the feature store."""
    cols = set(df.columns.tolist())

    mandatory_present = [f for f in MANDATORY_FEATURES if f in cols]
    mandatory_missing = [f for f in MANDATORY_FEATURES if f not in cols]
    optional_present = [f for f in OPTIONAL_FEATURES if f in cols]
    optional_missing = [f for f in OPTIONAL_FEATURES if f not in cols]

    mandatory_coverage = (
        round(len(mandatory_present) / len(MANDATORY_FEATURES) * 100, 1)
        if MANDATORY_FEATURES else 0.0
    )
    optional_coverage = (
        round(len(optional_present) / len(OPTIONAL_FEATURES) * 100, 1)
        if OPTIONAL_FEATURES else 0.0
    )

    category_results = []
    for cat in CATEGORIES:
        m_present = sum(1 for f in cat["mandatory"] if f in cols)
        o_present = sum(1 for f in cat["optional"] if f in cols)
        m_missing = [f for f in cat["mandatory"] if f not in cols]

        if m_missing:
            status = "fail"
        elif len(cat["optional"]) > 0 and o_present < len(cat["optional"]):
            status = "partial"
        else:
            status = "pass"

        category_results.append({
            "name": cat["name"],
            "mandatory_count": len(cat["mandatory"]),
            "mandatory_present": m_present,
            "optional_count": len(cat["optional"]),
            "optional_present": o_present,
            "status": status,
        })

    return {
        "mandatory_total": len(MANDATORY_FEATURES),
        "mandatory_present": len(mandatory_present),
        "mandatory_missing": mandatory_missing,
        "mandatory_coverage_pct": mandatory_coverage,
        "optional_total": len(OPTIONAL_FEATURES),
        "optional_present": len(optional_present),
        "optional_missing": optional_missing,
        "optional_coverage_pct": optional_coverage,
        "categories": category_results,
        "step2_passed": mandatory_coverage == 100.0,
    }
