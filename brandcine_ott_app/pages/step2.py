"""
Step 2 — Feature Presence Check page.
"""
from __future__ import annotations

import reflex as rx

from ..state import AppState
from ..styles import (
    ACCENT, ACCENT_BG, CARD, GREEN, GREEN_BG, AMBER, AMBER_BG, RED, RED_BG,
    GRAY, GRAY_BG, METRIC,
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


def _category_card(cat: dict) -> rx.Component:
    """Render one category status card. Uses rx.cond for all status-based logic."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.cond(
                    cat["status"] == "pass",
                    rx.text("✓", font_size="16px", color=GREEN, font_weight="700"),
                    rx.cond(
                        cat["status"] == "partial",
                        rx.text("!", font_size="16px", color=AMBER, font_weight="700"),
                        rx.text("✗", font_size="16px", color=RED, font_weight="700"),
                    ),
                ),
                rx.text(
                    cat["name"],
                    font_size="12px",
                    font_weight="600",
                    color="var(--color-text-primary, #f1f5f9)",
                ),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.text("M:", font_size="11px",
                        color="var(--color-text-secondary, #94a3b8)"),
                rx.text(cat["mandatory_present"], font_size="11px",
                        color="var(--color-text-secondary, #94a3b8)"),
                rx.text("/", font_size="11px", color=GRAY),
                rx.text(cat["mandatory_count"], font_size="11px",
                        color="var(--color-text-secondary, #94a3b8)"),
                rx.text(" · O:", font_size="11px", color=GRAY),
                rx.text(cat["optional_present"], font_size="11px",
                        color="var(--color-text-secondary, #94a3b8)"),
                rx.text("/", font_size="11px", color=GRAY),
                rx.text(cat["optional_count"], font_size="11px",
                        color="var(--color-text-secondary, #94a3b8)"),
                spacing="1",
                align="center",
            ),
            spacing="2",
        ),
        background=rx.cond(
            cat["status"] == "pass",
            GREEN_BG,
            rx.cond(cat["status"] == "partial", AMBER_BG, RED_BG),
        ),
        border_left=rx.cond(
            cat["status"] == "pass",
            f"3px solid {GREEN}",
            rx.cond(
                cat["status"] == "partial",
                f"3px solid {AMBER}",
                f"3px solid {RED}",
            ),
        ),
        border_radius="8px",
        padding="12px",
        flex="1",
        min_width="200px",
    )


def step2_page() -> rx.Component:
    return rx.vstack(
        # Topbar
        rx.hstack(
            rx.vstack(
                rx.text("Step 2 — Feature Presence Check", font_size="20px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)"),
                rx.cond(
                    AppState.s2_passed,
                    rx.badge("All mandatory features present", color_scheme="green",
                             variant="soft", font_size="12px"),
                    rx.badge("Missing mandatory features — re-upload required",
                             color_scheme="red", variant="soft", font_size="12px"),
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.cond(
                AppState.s2_passed,
                rx.button(
                    "Run Quality Tests →",
                    on_click=AppState.go_step3,
                    background=ACCENT, color="white",
                    border_radius="8px", padding="8px 16px",
                    font_size="13px", font_weight="500",
                    cursor="pointer", border="none",
                    _hover={"background": "#4f46e5"},
                ),
                rx.button(
                    "← Re-upload",
                    on_click=AppState.go_upload,
                    background="transparent", color=RED,
                    border=f"1px solid {RED}", border_radius="8px",
                    padding="8px 16px", font_size="13px", font_weight="500",
                    cursor="pointer", _hover={"background": RED_BG},
                ),
            ),
            width="100%",
            align="center",
            padding_bottom="8px",
        ),

        # Metric cards
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.text("Mandatory Features", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.hstack(
                        rx.text(AppState.s2_mandatory_present, font_size="24px",
                                font_weight="700",
                                color=rx.cond(AppState.s2_passed, GREEN, RED)),
                        rx.text(" / 42", font_size="16px", font_weight="400",
                                color=GRAY, align_self="flex-end", padding_bottom="3px"),
                        spacing="0", align="end",
                    ),
                    spacing="1",
                ),
                **METRIC,
                border=rx.cond(AppState.s2_passed, f"1px solid {GREEN_BG}", f"1px solid {RED_BG}"),
                flex="1", min_width="130px",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Good-to-Have Features", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.hstack(
                        rx.text(AppState.s2_optional_present, font_size="24px",
                                font_weight="700", color=AMBER),
                        rx.text(" / 29", font_size="16px", font_weight="400",
                                color=GRAY, align_self="flex-end", padding_bottom="3px"),
                        spacing="0", align="end",
                    ),
                    spacing="1",
                ),
                **METRIC,
                border=f"1px solid {AMBER_BG}",
                flex="1", min_width="130px",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Mandatory Coverage", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.text(AppState.s2_mandatory_coverage_pct, font_size="24px",
                            font_weight="700",
                            color=rx.cond(AppState.s2_passed, GREEN, RED)),
                    rx.box(
                        rx.box(
                            width=AppState.s2_mandatory_coverage_pct.to_string() + "%",
                            height="6px",
                            background=rx.cond(AppState.s2_passed, GREEN, RED),
                            border_radius="3px",
                        ),
                        background="var(--color-border-tertiary, #2d3048)",
                        border_radius="3px", width="100%", height="6px",
                    ),
                    spacing="1",
                ),
                **METRIC,
                border=rx.cond(AppState.s2_passed, f"1px solid {GREEN_BG}", f"1px solid {RED_BG}"),
                flex="1", min_width="130px",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Total Present", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.text(AppState.total_features_present, font_size="24px",
                            font_weight="700", color=ACCENT),
                    rx.text("of 71 total", font_size="11px",
                            color="var(--color-text-tertiary, #64748b)"),
                    spacing="1",
                ),
                **METRIC,
                border=f"1px solid {ACCENT_BG}",
                flex="1", min_width="130px",
            ),
            spacing="3", width="100%", flex_wrap="wrap",
        ),

        # Category grid — uses rx.foreach with rx.cond inside
        rx.box(
            rx.vstack(
                rx.text("Feature Category Breakdown", font_size="14px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)", margin_bottom="4px"),
                rx.flex(
                    rx.foreach(AppState.s2_categories, _category_card),
                    flex_wrap="wrap",
                    gap="10px",
                    width="100%",
                ),
                spacing="3",
            ),
            **CARD,
            width="100%",
        ),

        # Missing mandatory features
        rx.cond(
            AppState.s2_mandatory_missing.length() > 0,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("✗", font_size="18px", color=RED),
                        rx.text("Missing mandatory features — pipeline cannot proceed",
                                font_size="14px", font_weight="600", color=RED),
                        spacing="2", align="center",
                    ),
                    rx.flex(
                        rx.foreach(
                            AppState.s2_mandatory_missing,
                            lambda item: rx.box(
                                rx.text(item, font_size="11px", font_weight="500", color=RED),
                                background=RED_BG, border=f"1px solid {RED}",
                                border_radius="20px", padding="3px 10px", margin="2px",
                            ),
                        ),
                        flex_wrap="wrap", gap="4px",
                    ),
                    rx.button(
                        "Download template to see required format",
                        on_click=rx.download(url="/assets/feature_store_template.xlsx"),
                        background="transparent", color=RED,
                        border=f"1px solid {RED}", border_radius="8px",
                        padding="6px 14px", font_size="12px",
                        cursor="pointer", _hover={"background": RED_BG},
                    ),
                    spacing="3",
                ),
                background=RED_BG, border=f"1px solid {RED}",
                border_radius="10px", padding="16px", width="100%",
            ),
            rx.box(),
        ),

        # Missing optional features
        rx.cond(
            AppState.s2_optional_missing.length() > 0,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("!", font_size="18px", color=AMBER),
                        rx.text("Missing optional features (good-to-have)",
                                font_size="14px", font_weight="600", color=AMBER),
                        spacing="2", align="center",
                    ),
                    rx.flex(
                        rx.foreach(
                            AppState.s2_optional_missing,
                            lambda item: rx.box(
                                rx.text(item, font_size="11px", font_weight="500", color=AMBER),
                                background=AMBER_BG, border=f"1px solid {AMBER}",
                                border_radius="20px", padding="3px 10px", margin="2px",
                            ),
                        ),
                        flex_wrap="wrap", gap="4px",
                    ),
                    rx.text(
                        "These features improve persona quality but are not required to proceed.",
                        font_size="12px",
                        color="var(--color-text-secondary, #94a3b8)",
                    ),
                    spacing="3",
                ),
                background=AMBER_BG, border=f"1px solid {AMBER}",
                border_radius="10px", padding="16px", width="100%",
            ),
            rx.box(),
        ),

        spacing="4",
        width="100%",
        align="start",
    )
