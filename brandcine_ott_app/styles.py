"""
TwinSwim OTT — Design system constants.
"""
from __future__ import annotations

# ─── Colors ───────────────────────────────────────────────────────────────────

SIDEBAR_BG = "#0f1117"
ACCENT = "#6366f1"
ACCENT_HOVER = "#4f46e5"
ACCENT_LIGHT = "#818cf8"
ACCENT_BG = "rgba(99,102,241,0.1)"
GREEN = "#22c55e"
GREEN_BG = "rgba(34,197,94,0.1)"
AMBER = "#f59e0b"
AMBER_BG = "rgba(245,158,11,0.1)"
RED = "#ef4444"
RED_BG = "rgba(239,68,68,0.1)"
BLUE = "#3b82f6"
BLUE_BG = "rgba(59,130,246,0.1)"
GRAY = "#6b7280"
GRAY_BG = "rgba(107,114,128,0.1)"
ORANGE = "#f97316"
ORANGE_BG = "rgba(249,115,22,0.1)"

# ─── Card/container styles ────────────────────────────────────────────────────

CARD: dict = {
    "background": "var(--color-background-primary, #1a1d27)",
    "border": "1px solid var(--color-border-tertiary, #2d3048)",
    "border_radius": "12px",
    "padding": "16px",
}

METRIC: dict = {
    "background": "var(--color-background-secondary, #13151e)",
    "border_radius": "10px",
    "padding": "14px 16px",
}

# ─── Typography helpers ───────────────────────────────────────────────────────

HEADING: dict = {"font_size": "18px", "font_weight": "600", "color": "var(--color-text-primary, #f1f5f9)"}
SUBHEADING: dict = {"font_size": "14px", "font_weight": "500", "color": "var(--color-text-secondary, #94a3b8)"}
LABEL: dict = {"font_size": "12px", "font_weight": "500", "color": "var(--color-text-tertiary, #64748b)"}
BODY: dict = {"font_size": "13px", "color": "var(--color-text-primary, #f1f5f9)"}

# ─── Button styles ────────────────────────────────────────────────────────────

BTN_PRIMARY: dict = {
    "background": ACCENT,
    "color": "white",
    "border_radius": "8px",
    "padding": "8px 16px",
    "font_size": "13px",
    "font_weight": "500",
    "cursor": "pointer",
    "_hover": {"background": ACCENT_HOVER},
    "border": "none",
}

BTN_OUTLINE: dict = {
    "background": "transparent",
    "color": ACCENT,
    "border": f"1px solid {ACCENT}",
    "border_radius": "8px",
    "padding": "8px 16px",
    "font_size": "13px",
    "font_weight": "500",
    "cursor": "pointer",
    "_hover": {"background": ACCENT_BG},
}

BTN_GRAY: dict = {
    "background": "transparent",
    "color": GRAY,
    "border": f"1px solid #374151",
    "border_radius": "8px",
    "padding": "8px 16px",
    "font_size": "13px",
    "font_weight": "500",
    "cursor": "pointer",
    "_hover": {"background": GRAY_BG},
}
