"""
Upload page — drag-and-drop file upload with template downloads.
"""
from __future__ import annotations

import reflex as rx

from ..state import AppState
from ..styles import (
    ACCENT, ACCENT_BG, ACCENT_LIGHT, AMBER, AMBER_BG,
    CARD, GREEN, RED, RED_BG, GRAY, BTN_PRIMARY, BTN_OUTLINE, BTN_GRAY,
)


def _template_buttons() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.hstack(
                rx.text("↓", font_size="16px"),
                rx.text("Feature Store Template", font_size="13px", font_weight="500"),
                spacing="1",
                align="center",
            ),
            on_click=rx.download(url="/assets/feature_store_template.xlsx"),
            background="transparent",
            color=ACCENT,
            border=f"1px solid {ACCENT}",
            border_radius="8px",
            padding="8px 14px",
            cursor="pointer",
            _hover={"background": ACCENT_BG},
        ),
        rx.button(
            rx.hstack(
                rx.text("↓", font_size="16px"),
                rx.text("Data Format Sample", font_size="13px", font_weight="500"),
                spacing="1",
                align="center",
            ),
            on_click=rx.download(url="/assets/feature_store_template.xlsx"),
            background="transparent",
            color=GRAY,
            border="1px solid #374151",
            border_radius="8px",
            padding="8px 14px",
            cursor="pointer",
            _hover={"background": "rgba(107,114,128,0.1)"},
        ),
        spacing="3",
        width="100%",
    )


def _upload_zone() -> rx.Component:
    return rx.upload(
        rx.vstack(
            rx.box(
                rx.text("↑", font_size="32px", color=ACCENT),
                width="60px",
                height="60px",
                background=ACCENT_BG,
                border_radius="50%",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text(
                "Drop your Excel or CSV file here",
                font_size="14px",
                font_weight="500",
                color="var(--color-text-primary, #f1f5f9)",
            ),
            rx.text(
                "Supports .xlsx · .csv · one consolidated user-level file",
                font_size="12px",
                color="var(--color-text-tertiary, #64748b)",
            ),
            rx.box(
                rx.text("Browse files", font_size="13px", font_weight="500", color="white"),
                background=ACCENT,
                border_radius="20px",
                padding="6px 20px",
                cursor="pointer",
                _hover={"background": "#4f46e5"},
            ),
            spacing="3",
            align="center",
            padding="40px 20px",
        ),
        id="upload_zone",
        border=f"2px dashed {ACCENT}",
        border_radius="14px",
        background=ACCENT_BG,
        width="100%",
        _hover={"border_color": ACCENT_LIGHT, "background": "rgba(99,102,241,0.15)"},
        on_drop=AppState.handle_upload(rx.upload_files(upload_id="upload_zone")),
        accept={
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
            "text/csv": [".csv"],
            "application/vnd.ms-excel": [".xls"],
        },
        multiple=False,
    )


def _format_info_card() -> rx.Component:
    rows = [
        ("Data structure", "One row per user — user attributes + pre-derived session aggregates"),
        ("File formats", ".xlsx (with 'Processed Data' sheet) or .csv"),
        ("Mandatory features", "42 required · 29 good-to-have"),
        ("Minimum rows", "500 users minimum for clustering"),
    ]
    return rx.box(
        rx.vstack(
            rx.text("Required format", font_size="13px", font_weight="600",
                    color="var(--color-text-secondary, #94a3b8)", margin_bottom="8px"),
            *[
                rx.hstack(
                    rx.text(label, font_size="12px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)", min_width="160px"),
                    rx.text(value, font_size="12px",
                            color="var(--color-text-primary, #f1f5f9)"),
                    spacing="3",
                    padding_y="6px",
                    border_bottom="1px solid var(--color-border-tertiary, #2d3048)",
                )
                for label, value in rows
            ],
            spacing="0",
        ),
        **CARD,
        width="100%",
    )


def _error_banner() -> rx.Component:
    return rx.cond(
        AppState.s1_error != "",
        rx.box(
            rx.hstack(
                rx.text("⚠", font_size="16px"),
                rx.text(AppState.s1_error, font_size="13px", flex="1"),
                rx.button(
                    "Try again",
                    on_click=AppState.reset_all,
                    background="transparent",
                    color=RED,
                    border=f"1px solid {RED}",
                    border_radius="6px",
                    padding="4px 12px",
                    font_size="12px",
                    cursor="pointer",
                ),
                spacing="3",
                align="center",
            ),
            background=RED_BG,
            border=f"1px solid {RED}",
            border_radius="10px",
            padding="12px 16px",
            width="100%",
        ),
        rx.box(),
    )


def _processing_overlay() -> rx.Component:
    return rx.cond(
        AppState.s1_processing,
        rx.box(
            rx.vstack(
                rx.spinner(size="3", color=ACCENT),
                rx.text("Processing your dataset...", font_size="14px",
                        color="var(--color-text-secondary, #94a3b8)"),
                spacing="3",
                align="center",
            ),
            background="rgba(15,17,23,0.8)",
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="1000",
        ),
        rx.box(),
    )


def upload_page() -> rx.Component:
    return rx.box(
        _processing_overlay(),
        rx.vstack(
            # Header
            rx.vstack(
                rx.text("Upload your dataset", font_size="22px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)"),
                rx.text(
                    "One consolidated user-level file — user attributes and pre-derived session features in a single table.",
                    font_size="14px",
                    color="var(--color-text-secondary, #94a3b8)",
                    text_align="center",
                    max_width="460px",
                ),
                spacing="2",
                align="center",
            ),
            # Template downloads
            _template_buttons(),
            # Upload zone
            _upload_zone(),
            # Format info
            _format_info_card(),
            # Error
            _error_banner(),
            spacing="5",
            max_width="560px",
            width="100%",
            margin="0 auto",
            padding_top="32px",
            align="center",
        ),
        width="100%",
        padding="20px",
    )
