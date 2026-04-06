"""
Step 3 — Quality Tests page.
"""
from __future__ import annotations

import reflex as rx

from ..state import AppState
from ..styles import (
    ACCENT, ACCENT_BG, CARD, GREEN, GREEN_BG, AMBER, AMBER_BG, RED, RED_BG,
    GRAY, GRAY_BG, ORANGE, ORANGE_BG, METRIC,
)


def _mandatory_test_row(test: dict) -> rx.Component:
    """Render one mandatory test row. All branching done via rx.cond."""
    return rx.box(
        rx.hstack(
            # ID
            rx.text(
                test["id"],
                font_size="11px",
                font_weight="700",
                color=rx.cond(
                    test["passed"],
                    GREEN,
                    rx.cond(test["severity"] == "Critical", RED, ORANGE),
                ),
                min_width="40px",
            ),
            # Name
            rx.text(
                test["name"],
                font_size="12px",
                font_weight="500",
                color="var(--color-text-primary, #f1f5f9)",
                flex="1",
                min_width="160px",
            ),
            # Columns tested
            rx.text(
                test["columns_tested"],
                font_size="11px",
                color="var(--color-text-tertiary, #64748b)",
                flex="1",
                min_width="80px",
            ),
            # Result badge
            rx.cond(
                test["passed"],
                rx.badge("PASS", color_scheme="green", variant="soft",
                         font_size="11px", min_width="50px"),
                rx.cond(
                    test["severity"] == "Critical",
                    rx.badge("FAIL", color_scheme="red", variant="soft",
                             font_size="11px", min_width="50px"),
                    rx.badge("FAIL", color_scheme="orange", variant="soft",
                             font_size="11px", min_width="50px"),
                ),
            ),
            # Rows affected
            rx.text(
                test["affected_rows"],
                font_size="11px",
                color="var(--color-text-tertiary, #64748b)",
                min_width="40px",
                text_align="right",
            ),
            # Message
            rx.text(
                test["message"],
                font_size="11px",
                color="var(--color-text-secondary, #94a3b8)",
                flex="2",
                min_width="180px",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        background=rx.cond(
            test["passed"],
            GREEN_BG,
            rx.cond(test["severity"] == "Critical", RED_BG, ORANGE_BG),
        ),
        border_radius="8px",
        padding="10px 12px",
        margin_bottom="2px",
    )


def _optional_test_card(test: dict) -> rx.Component:
    """Render one good-to-have test card. All branching done via rx.cond."""
    return rx.box(
        rx.hstack(
            rx.text(
                test["id"],
                font_size="11px",
                font_weight="700",
                color=rx.cond(test["has_warning"], AMBER, GREEN),
                min_width="40px",
            ),
            rx.text(
                test["name"],
                font_size="12px",
                font_weight="500",
                color="var(--color-text-primary, #f1f5f9)",
                flex="1",
            ),
            rx.cond(
                test["has_warning"],
                rx.badge("Warning", color_scheme="amber", variant="soft", font_size="11px"),
                rx.badge("No issues", color_scheme="green", variant="soft", font_size="11px"),
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        rx.cond(
            test["has_warning"],
            rx.text(
                test["message"],
                font_size="11px",
                color=AMBER,
                margin_top="4px",
                padding_left="52px",
            ),
            rx.box(),
        ),
        background=rx.cond(test["has_warning"], AMBER_BG, GREEN_BG),
        border_radius="8px",
        padding="10px 12px",
        margin_bottom="2px",
    )


def step3_page() -> rx.Component:
    return rx.vstack(
        # Topbar
        rx.hstack(
            rx.vstack(
                rx.text("Step 3 — Quality Tests", font_size="20px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)"),
                rx.hstack(
                    rx.text("15 mandatory tests ·", font_size="13px",
                            color="var(--color-text-secondary, #94a3b8)"),
                    rx.text(AppState.s3_mandatory_passed, font_size="13px",
                            color=GREEN, font_weight="600"),
                    rx.text("passed ·", font_size="13px",
                            color="var(--color-text-secondary, #94a3b8)"),
                    rx.text(AppState.s3_mandatory_failed, font_size="13px",
                            color=rx.cond(AppState.s3_mandatory_failed > 0, RED, GREEN),
                            font_weight="600"),
                    rx.text("failed", font_size="13px",
                            color="var(--color-text-secondary, #94a3b8)"),
                    spacing="1", align="center",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.hstack(
                rx.cond(
                    AppState.s3_report_ready,
                    rx.button(
                        "Download Quality Report",
                        on_click=AppState.download_quality_report,
                        background="transparent", color=ACCENT,
                        border=f"1px solid {ACCENT}", border_radius="8px",
                        padding="8px 14px", font_size="13px", font_weight="500",
                        cursor="pointer", _hover={"background": ACCENT_BG},
                    ),
                    rx.box(),
                ),
                rx.button(
                    "← Re-upload",
                    on_click=AppState.go_upload,
                    background="transparent", color=GRAY,
                    border="1px solid #374151", border_radius="8px",
                    padding="8px 14px", font_size="13px", font_weight="500",
                    cursor="pointer", _hover={"background": GRAY_BG},
                ),
                spacing="2",
            ),
            width="100%",
            align="center",
            padding_bottom="8px",
        ),

        # Summary banner
        rx.cond(
            AppState.s3_all_mandatory_passed,
            rx.box(
                rx.hstack(
                    rx.text("✓", font_size="20px", color=GREEN),
                    rx.text("All mandatory tests passed — dataset is production-ready",
                            font_size="14px", font_weight="600", color=GREEN),
                    rx.spacer(),
                    rx.button(
                        "Proceed to Clustering →",
                        is_disabled=True,
                        background=GREEN, color="white",
                        border_radius="8px", padding="8px 16px",
                        font_size="13px", font_weight="500",
                        opacity="0.5", cursor="not-allowed",
                        title="Clustering module coming in next release",
                        border="none",
                    ),
                    spacing="3", align="center", width="100%",
                ),
                background=GREEN_BG, border=f"1px solid {GREEN}",
                border_radius="10px", padding="16px", width="100%",
            ),
            rx.box(
                rx.hstack(
                    rx.text("✗", font_size="20px", color=RED),
                    rx.text("Quality tests failed — fix issues and re-upload",
                            font_size="14px", font_weight="600", color=RED),
                    spacing="3", align="center",
                ),
                background=RED_BG, border=f"1px solid {RED}",
                border_radius="10px", padding="16px", width="100%",
            ),
        ),

        # Metric cards
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.text("Mandatory Tests", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.hstack(
                        rx.text(AppState.s3_mandatory_passed, font_size="24px",
                                font_weight="700",
                                color=rx.cond(AppState.s3_all_mandatory_passed, GREEN, RED)),
                        rx.text("/15", font_size="16px", font_weight="400",
                                color=GRAY, align_self="flex-end", padding_bottom="3px"),
                        spacing="0", align="end",
                    ),
                    rx.text("passed", font_size="11px",
                            color="var(--color-text-tertiary, #64748b)"),
                    spacing="1",
                ),
                **METRIC,
                border=rx.cond(AppState.s3_all_mandatory_passed,
                               f"1px solid {GREEN_BG}", f"1px solid {RED_BG}"),
                flex="1", min_width="130px",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Tests Failed", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.text(AppState.s3_mandatory_failed, font_size="24px",
                            font_weight="700",
                            color=rx.cond(AppState.s3_mandatory_failed > 0, RED, GREEN)),
                    rx.text("mandatory", font_size="11px",
                            color="var(--color-text-tertiary, #64748b)"),
                    spacing="1",
                ),
                **METRIC,
                border=rx.cond(AppState.s3_mandatory_failed > 0,
                               f"1px solid {RED_BG}", f"1px solid {GREEN_BG}"),
                flex="1", min_width="130px",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Quality Score", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.text(AppState.quality_score_str, font_size="24px",
                            font_weight="700",
                            color=rx.cond(AppState.s3_all_mandatory_passed, GREEN, AMBER)),
                    rx.box(
                        rx.box(
                            width=AppState.quality_score_str,
                            height="6px",
                            background=rx.cond(AppState.s3_all_mandatory_passed, GREEN, AMBER),
                            border_radius="3px",
                        ),
                        background="var(--color-border-tertiary, #2d3048)",
                        border_radius="3px", width="100%", height="6px",
                    ),
                    spacing="1",
                ),
                **METRIC,
                border=f"1px solid {ACCENT_BG}",
                flex="1", min_width="130px",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Warnings", font_size="11px", font_weight="500",
                            color="var(--color-text-tertiary, #64748b)",
                            text_transform="uppercase", letter_spacing="0.05em"),
                    rx.hstack(
                        rx.text(AppState.s3_optional_warnings, font_size="24px",
                                font_weight="700", color=AMBER),
                        rx.text("/10", font_size="16px", font_weight="400",
                                color=GRAY, align_self="flex-end", padding_bottom="3px"),
                        spacing="0", align="end",
                    ),
                    rx.text("good-to-have", font_size="11px",
                            color="var(--color-text-tertiary, #64748b)"),
                    spacing="1",
                ),
                **METRIC,
                border=f"1px solid {AMBER_BG}",
                flex="1", min_width="130px",
            ),
            spacing="3", width="100%", flex_wrap="wrap",
        ),

        # Mandatory tests table
        rx.box(
            rx.vstack(
                rx.text("Mandatory Tests (T01–T15)", font_size="14px", font_weight="600",
                        color="var(--color-text-primary, #f1f5f9)", margin_bottom="4px"),
                # Table header
                rx.hstack(
                    rx.text("ID", font_size="11px", font_weight="600",
                            color=GRAY, min_width="40px"),
                    rx.text("Test Name", font_size="11px", font_weight="600",
                            color=GRAY, flex="1", min_width="160px"),
                    rx.text("Columns", font_size="11px", font_weight="600",
                            color=GRAY, flex="1", min_width="80px"),
                    rx.text("Result", font_size="11px", font_weight="600",
                            color=GRAY, min_width="50px"),
                    rx.text("Affected", font_size="11px", font_weight="600",
                            color=GRAY, min_width="40px", text_align="right"),
                    rx.text("Message", font_size="11px", font_weight="600",
                            color=GRAY, flex="2", min_width="180px"),
                    spacing="3", width="100%",
                    padding="6px 12px",
                    border_bottom="1px solid var(--color-border-tertiary, #2d3048)",
                ),
                rx.foreach(AppState.s3_mandatory_tests, _mandatory_test_row),
                spacing="0",
            ),
            **CARD,
            width="100%",
        ),

        # Good-to-have tests
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Good-to-Have Checks (G01–G10)",
                            font_size="14px", font_weight="600",
                            color="var(--color-text-primary, #f1f5f9)"),
                    rx.badge("Warnings only — you can still proceed",
                             color_scheme="amber", variant="soft", font_size="11px"),
                    spacing="3", align="center", width="100%",
                ),
                rx.text(
                    "These checks are informational. Warnings are handled automatically during feature selection.",
                    font_size="12px",
                    color="var(--color-text-secondary, #94a3b8)",
                ),
                rx.foreach(AppState.s3_optional_tests, _optional_test_card),
                spacing="3",
            ),
            **CARD,
            width="100%",
        ),

        spacing="4",
        width="100%",
        align="start",
    )
