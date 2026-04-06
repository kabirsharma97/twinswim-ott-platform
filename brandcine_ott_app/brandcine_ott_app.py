"""
TwinSwim OTT — Persona Intelligence Platform
Main app entry point with sidebar + page routing.
"""
from __future__ import annotations

import reflex as rx

from .state import AppState
from .styles import (
    ACCENT, ACCENT_BG, ACCENT_LIGHT, GREEN, GREEN_BG, AMBER, AMBER_BG,
    RED, RED_BG, BLUE, GRAY, SIDEBAR_BG,
)
from .pages.upload import upload_page
from .pages.step1 import step1_page
from .pages.step2 import step2_page
from .pages.step3 import step3_page
from .pages.ready import ready_page


# ─── Ensure feature store template exists on startup ─────────────────────────

def _ensure_template() -> None:
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(project_root))
        from pipeline.create_template import ensure_template
        ensure_template()
    except Exception as e:
        print(f"[startup] Template generation skipped: {e}")


_ensure_template()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def _status_dot(color: str, pulsing: bool = False) -> rx.Component:
    dot = rx.box(
        width="8px",
        height="8px",
        background=color,
        border_radius="50%",
        flex_shrink="0",
    )
    return dot


def _nav_item(
    label: str,
    page: str,
    status_color: str,
    is_active: bool,
    on_click,
) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                width="3px",
                height="100%",
                background=rx.cond(is_active, ACCENT, "transparent"),
                border_radius="0 2px 2px 0",
                position="absolute",
                left="0",
                top="0",
            ),
            _status_dot(status_color),
            rx.text(
                label,
                font_size="13px",
                font_weight=rx.cond(is_active, "600", "400"),
                color=rx.cond(is_active, "white", "#94a3b8"),
            ),
            spacing="2",
            align="center",
            padding_left="12px",
        ),
        position="relative",
        background=rx.cond(is_active, ACCENT_BG, "transparent"),
        border_radius="6px",
        padding="9px 8px 9px 0",
        cursor="pointer",
        _hover={"background": "rgba(99,102,241,0.08)"},
        on_click=on_click,
        width="100%",
        overflow="hidden",
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Logo
            rx.hstack(
                rx.box(
                    rx.text("T", font_size="18px", font_weight="800", color="white"),
                    width="36px",
                    height="36px",
                    background=f"linear-gradient(135deg, {ACCENT}, {ACCENT_LIGHT})",
                    border_radius="8px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    flex_shrink="0",
                ),
                rx.vstack(
                    rx.text("TwinSwim OTT", font_size="14px", font_weight="700",
                            color="white", line_height="1"),
                    rx.text("Persona Intelligence", font_size="10px", color="#6b7280",
                            line_height="1"),
                    spacing="0",
                    align="start",
                ),
                spacing="2",
                align="center",
                padding="16px 12px 12px",
            ),

            rx.divider(border_color="#1f2937", margin_y="4px"),

            # Getting Started section
            rx.text("GETTING STARTED", font_size="10px", font_weight="600",
                    color="#4b5563", letter_spacing="0.08em",
                    padding="8px 12px 4px"),

            _nav_item(
                "Upload Dataset",
                "upload",
                rx.cond(AppState.s1_processing, BLUE,
                        rx.cond(AppState.s1_done, GREEN, GRAY)),
                AppState.current_page == "upload",
                AppState.go_upload,
            ),

            rx.divider(border_color="#1f2937", margin_y="4px"),

            # Pipeline section
            rx.text("PIPELINE", font_size="10px", font_weight="600",
                    color="#4b5563", letter_spacing="0.08em",
                    padding="8px 12px 4px"),

            _nav_item(
                "Step 1 — Data Ingestion",
                "step1",
                rx.cond(AppState.s1_done, GREEN, GRAY),
                AppState.current_page == "step1",
                AppState.go_step1,
            ),

            _nav_item(
                "Step 2 — Feature Check",
                "step2",
                rx.cond(
                    AppState.s2_done,
                    rx.cond(AppState.s2_passed, GREEN, RED),
                    GRAY,
                ),
                AppState.current_page == "step2",
                AppState.go_step2,
            ),

            _nav_item(
                "Step 3 — Quality Tests",
                "step3",
                rx.cond(
                    AppState.s3_done,
                    rx.cond(AppState.s3_all_mandatory_passed, GREEN, RED),
                    GRAY,
                ),
                AppState.current_page == "step3",
                AppState.go_step3,
            ),

            rx.cond(
                AppState.s3_all_mandatory_passed,
                _nav_item(
                    "Clustering Ready ✓",
                    "ready",
                    GREEN,
                    AppState.current_page == "ready",
                    AppState.go_ready,
                ),
                rx.box(),
            ),

            rx.spacer(),

            # Footer
            rx.box(
                rx.vstack(
                    rx.text(
                        rx.cond(
                            AppState.s1_done,
                            AppState.s1_filename,
                            "Ready to upload",
                        ),
                        font_size="11px",
                        color="#4b5563",
                        no_of_lines=1,
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    rx.cond(
                        AppState.s1_done,
                        rx.text(
                            AppState.s1_total_records_fmt + " rows",
                            font_size="10px",
                            color="#374151",
                        ),
                        rx.box(),
                    ),
                    spacing="0",
                ),
                border_top="1px solid #1f2937",
                padding="12px",
                width="100%",
            ),

            spacing="0",
            height="100%",
            width="100%",
            align="start",
        ),
        width="220px",
        min_width="220px",
        height="100vh",
        background=SIDEBAR_BG,
        border_right="1px solid #1f2937",
        overflow_y="auto",
        flex_shrink="0",
    )


# ─── Root layout ──────────────────────────────────────────────────────────────

def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.cond(AppState.current_page == "upload", upload_page()),
            rx.cond(AppState.current_page == "step1", step1_page()),
            rx.cond(AppState.current_page == "step2", step2_page()),
            rx.cond(AppState.current_page == "step3", step3_page()),
            rx.cond(AppState.current_page == "ready", ready_page()),
            flex="1",
            overflow_y="auto",
            height="100vh",
            width="100%",
            padding="20px",
        ),
        width="100%",
        height="100vh",
        overflow="hidden",
        background="var(--color-background, #0e1117)",
        spacing="0",
    )


# ─── App definition ───────────────────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="indigo",
    ),
)
app.add_page(index, route="/")
