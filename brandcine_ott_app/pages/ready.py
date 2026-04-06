"""
Clustering Ready page — shown when all mandatory tests pass.
"""
from __future__ import annotations

import reflex as rx

from ..state import AppState
from ..styles import (
    ACCENT, ACCENT_BG, CARD, GREEN, GREEN_BG, AMBER, AMBER_BG, GRAY, GRAY_BG, METRIC,
)


def _warning_item(test: dict) -> rx.Component:
    """Render one warning item. Uses rx.cond — no Python-level branching on Vars."""
    return rx.cond(
        test["has_warning"],
        rx.hstack(
            rx.text("·", font_size="14px", color=AMBER),
            rx.text(test["message"], font_size="12px",
                    color="var(--color-text-secondary, #94a3b8)"),
            spacing="2",
            align="start",
        ),
        rx.box(),
    )


def ready_page() -> rx.Component:
    return rx.vstack(
        # Hero
        rx.vstack(
            rx.box(
                rx.text("✓", font_size="40px", color=GREEN, font_weight="700"),
                width="80px",
                height="80px",
                background=GREEN_BG,
                border_radius="50%",
                border=f"2px solid {GREEN}",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text("Dataset: Production-Ready", font_size="26px", font_weight="700",
                    color="var(--color-text-primary, #f1f5f9)", text_align="center"),
            rx.text("All 15 mandatory quality checks passed",
                    font_size="14px", color=GREEN, font_weight="500"),
            rx.text(
                "Your dataset is ready for clustering and persona generation.",
                font_size="14px",
                color="var(--color-text-secondary, #94a3b8)",
                text_align="center",
            ),
            spacing="3",
            align="center",
            padding="32px 20px 24px",
        ),

        # Summary cards
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.text("Records Ready", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.text(AppState.s1_total_records_fmt, font_size="26px",
                            font_weight="700", color=GREEN),
                    rx.text("users validated", font_size="12px",
                            color="var(--color-text-secondary, #94a3b8)"),
                    spacing="1", align="center",
                ),
                **METRIC, border=f"1px solid {GREEN_BG}",
                flex="1", min_width="150px", text_align="center",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Features Validated", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.text(AppState.total_features_present, font_size="26px",
                            font_weight="700", color=ACCENT),
                    rx.text("of 71 total", font_size="12px",
                            color="var(--color-text-secondary, #94a3b8)"),
                    spacing="1", align="center",
                ),
                **METRIC, border=f"1px solid {ACCENT_BG}",
                flex="1", min_width="150px", text_align="center",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Quality Score", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.text("100%", font_size="26px", font_weight="700", color=GREEN),
                    rx.text("all mandatory tests passed", font_size="12px",
                            color="var(--color-text-secondary, #94a3b8)"),
                    spacing="1", align="center",
                ),
                **METRIC, border=f"1px solid {GREEN_BG}",
                flex="1", min_width="150px", text_align="center",
            ),
            spacing="3", width="100%", flex_wrap="wrap", justify="center",
        ),

        # Feature readiness summary
        rx.box(
            rx.vstack(
                rx.text("Feature Readiness Summary", font_size="14px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)"),
                rx.hstack(
                    rx.box(width="10px", height="10px",
                           background=GREEN, border_radius="50%"),
                    rx.text(AppState.s2_mandatory_present, font_size="13px",
                            color="var(--color-text-primary, #f1f5f9)"),
                    rx.text("mandatory features", font_size="13px",
                            color="var(--color-text-primary, #f1f5f9)"),
                    rx.badge("✓ All present", color_scheme="green", variant="soft",
                             font_size="11px"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.box(width="10px", height="10px",
                           background=ACCENT, border_radius="50%"),
                    rx.text(AppState.s2_optional_present, font_size="13px",
                            color="var(--color-text-primary, #f1f5f9)"),
                    rx.text("optional features present", font_size="13px",
                            color="var(--color-text-primary, #f1f5f9)"),
                    spacing="2", align="center",
                ),
                rx.cond(
                    AppState.s2_optional_missing.length() > 0,
                    rx.hstack(
                        rx.box(width="10px", height="10px",
                               background=AMBER, border_radius="50%"),
                        rx.text(AppState.s2_optional_missing.length(), font_size="13px",
                                color=AMBER),
                        rx.text("optional features missing", font_size="13px", color=AMBER),
                        rx.badge("Not blocking", color_scheme="amber", variant="soft",
                                 font_size="11px"),
                        spacing="2", align="center",
                    ),
                    rx.box(),
                ),
                spacing="3",
            ),
            **CARD,
            width="100%",
        ),

        # Warning summary
        rx.cond(
            AppState.s3_optional_warnings > 0,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("!", font_size="18px", color=AMBER),
                        rx.text(AppState.s3_optional_warnings, font_size="14px",
                                font_weight="600", color=AMBER),
                        rx.text("good-to-have warnings — not blocking",
                                font_size="14px", font_weight="600", color=AMBER),
                        spacing="2", align="center",
                    ),
                    rx.text(
                        "These will be automatically handled during feature selection and clustering.",
                        font_size="12px",
                        color="var(--color-text-secondary, #94a3b8)",
                    ),
                    rx.vstack(
                        rx.foreach(AppState.s3_optional_tests, _warning_item),
                        spacing="2",
                    ),
                    spacing="3",
                ),
                background=AMBER_BG, border=f"1px solid {AMBER}",
                border_radius="10px", padding="16px", width="100%",
            ),
            rx.box(),
        ),

        # Action buttons
        rx.vstack(
            rx.button(
                "Proceed to Clustering →",
                is_disabled=True,
                background=GREEN, color="white",
                border_radius="10px", padding="14px 32px",
                font_size="15px", font_weight="600",
                opacity="0.45", cursor="not-allowed",
                width="100%", max_width="400px",
                title="Clustering module coming in next release",
                border="none",
            ),
            rx.text(
                "Clustering module coming in next release",
                font_size="12px",
                color="var(--color-text-tertiary, #64748b)",
                text_align="center",
            ),
            rx.button(
                "Start Over",
                on_click=AppState.reset_all,
                background="transparent", color=GRAY,
                border="1px solid #374151", border_radius="10px",
                padding="10px 32px", font_size="14px", font_weight="500",
                cursor="pointer", width="100%", max_width="400px",
                _hover={"background": GRAY_BG},
            ),
            spacing="2", align="center", width="100%",
        ),

        spacing="5",
        width="100%",
        align="center",
        padding_bottom="40px",
    )
