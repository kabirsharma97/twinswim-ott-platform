"""
Step 1 — Data Ingestion results page.
"""
from __future__ import annotations

import reflex as rx

from ..state import AppState
from ..styles import (
    ACCENT, ACCENT_BG, CARD, GREEN, GREEN_BG, AMBER, AMBER_BG, RED, RED_BG,
    BLUE, BLUE_BG, GRAY, GRAY_BG, METRIC,
)


def _metric_card(label: str, value, color: str, bg: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(label, font_size="11px", font_weight="500",
                    color="var(--color-text-tertiary, #64748b)", text_transform="uppercase",
                    letter_spacing="0.05em"),
            rx.text(value, font_size="24px", font_weight="700", color=color),
            spacing="1",
        ),
        **METRIC,
        border=f"1px solid {bg}",
        flex="1",
        min_width="130px",
    )


def _pill(col: str, color: str, bg: str, border: str) -> rx.Component:
    return rx.box(
        rx.text(col, font_size="11px", font_weight="500", color=color),
        background=bg,
        border=f"1px solid {border}",
        border_radius="20px",
        padding="3px 10px",
        margin="2px",
        display="inline-block",
    )


def _col_group(title: str, cols_var, color: str, bg: str, border: str) -> rx.Component:
    return rx.cond(
        cols_var.length() > 0,
        rx.vstack(
            rx.text(title, font_size="11px", font_weight="600",
                    color="var(--color-text-tertiary, #64748b)",
                    text_transform="uppercase", letter_spacing="0.05em"),
            rx.flex(
                rx.foreach(
                    cols_var,
                    lambda col: rx.box(
                        rx.text(col, font_size="11px", font_weight="500", color=color),
                        background=bg,
                        border=f"1px solid {border}",
                        border_radius="20px",
                        padding="3px 10px",
                        margin="2px",
                        display="inline-block",
                    ),
                ),
                flex_wrap="wrap",
                gap="4px",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        rx.box(),
    )


def _column_inventory() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("Column Inventory", font_size="14px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)"),
                rx.text(AppState.s1_total_columns,
                        font_size="13px", font_weight="600", color=ACCENT),
                rx.text("columns detected", font_size="12px",
                        color="var(--color-text-tertiary, #64748b)"),
                spacing="2",
                align="center",
            ),
            # Legend
            rx.hstack(
                rx.box(width="10px", height="10px", background=BLUE_BG,
                       border=f"1px solid {BLUE}", border_radius="3px"),
                rx.text("Mandatory", font_size="11px", color=GRAY),
                rx.box(width="10px", height="10px", background=GRAY_BG,
                       border="1px solid #374151", border_radius="3px"),
                rx.text("Optional", font_size="11px", color=GRAY),
                rx.box(width="10px", height="10px", background=AMBER_BG,
                       border=f"1px solid {AMBER}", border_radius="3px"),
                rx.text("Unknown", font_size="11px", color=GRAY),
                spacing="2",
                align="center",
            ),
            _col_group("Mandatory features", AppState.s1_mandatory_cols,
                       BLUE, BLUE_BG, BLUE),
            _col_group("Optional features", AppState.s1_optional_cols,
                       GRAY, GRAY_BG, "#374151"),
            _col_group("Unknown / extra columns", AppState.s1_unknown_cols,
                       AMBER, AMBER_BG, AMBER),
            spacing="4",
        ),
        **CARD,
        width="100%",
    )


def step1_page() -> rx.Component:
    return rx.vstack(
        # Topbar
        rx.hstack(
            rx.vstack(
                rx.text("Step 1 — Data Ingestion", font_size="20px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)"),
                rx.badge("Ingestion Complete", color_scheme="green", variant="soft",
                         font_size="12px"),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.button(
                "Next: Feature Check →",
                on_click=AppState.go_step2,
                background=ACCENT,
                color="white",
                border_radius="8px",
                padding="8px 16px",
                font_size="13px",
                font_weight="500",
                cursor="pointer",
                _hover={"background": "#4f46e5"},
                border="none",
            ),
            width="100%",
            align="center",
            padding_bottom="8px",
        ),

        # Two metric cards only — Records Ingested + Columns Detected
        rx.hstack(
            _metric_card("Records Ingested", AppState.s1_total_records_fmt, GREEN, GREEN_BG),
            _metric_card("Columns Detected", AppState.s1_total_columns, ACCENT, ACCENT_BG),
            spacing="3",
            width="100%",
        ),

        # Column inventory (colour-coded by group)
        _column_inventory(),

        spacing="4",
        width="100%",
        align="start",
    )
