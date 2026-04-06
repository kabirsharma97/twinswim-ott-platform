"""
TwinSwim OTT — Application State
"""
from __future__ import annotations

from pathlib import Path

import reflex as rx


class AppState(rx.State):
    # ── Navigation ────────────────────────────────────────────────
    current_page: str = "upload"

    # ── Step 1 ────────────────────────────────────────────────────
    s1_done: bool = False
    s1_filename: str = ""
    s1_file_format: str = ""
    s1_file_size_mb: float = 0.0
    s1_total_records: int = 0
    s1_total_columns: int = 0
    s1_error: str = ""
    s1_processing: bool = False
    s1_column_names: list[str] = []
    s1_mandatory_cols: list[str] = []
    s1_optional_cols: list[str] = []
    s1_unknown_cols: list[str] = []

    # ── Step 2 ────────────────────────────────────────────────────
    s2_done: bool = False
    s2_mandatory_total: int = 0
    s2_mandatory_present: int = 0
    s2_mandatory_missing: list[str] = []
    s2_mandatory_coverage_pct: float = 0.0
    s2_optional_total: int = 0
    s2_optional_present: int = 0
    s2_optional_missing: list[str] = []
    s2_categories: list[dict] = []
    s2_passed: bool = False

    # ── Step 3 ────────────────────────────────────────────────────
    s3_done: bool = False
    s3_mandatory_tests: list[dict] = []
    s3_optional_tests: list[dict] = []
    s3_mandatory_passed: int = 0
    s3_mandatory_failed: int = 0
    s3_all_mandatory_passed: bool = False
    s3_optional_warnings: int = 0
    s3_report_ready: bool = False

    # ── Internal — store upload path so report download can reload df ──
    _upload_path: str = ""

    def _reload_df(self):
        """Reload dataframe from the saved upload path."""
        if not self._upload_path:
            return None
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from pipeline.step1_ingest import run_step1
            r = run_step1(self._upload_path)
            return r["dataframe"] if r["success"] else None
        except Exception:
            return None

    # ── Computed vars ─────────────────────────────────────────────

    @rx.var
    def quality_score_pct(self) -> int:
        if self.s3_done:
            return int(self.s3_mandatory_passed / 15 * 100)
        return 0

    @rx.var
    def total_features_present(self) -> int:
        return self.s2_mandatory_present + self.s2_optional_present

    @rx.var
    def quality_score_str(self) -> str:
        if self.s3_done:
            return f"{int(self.s3_mandatory_passed / 15 * 100)}%"
        return "—"

    @rx.var
    def s1_total_records_fmt(self) -> str:
        """Records count formatted with commas e.g. 10,000 or 1,200,000."""
        return f"{self.s1_total_records:,}"

    # ── Upload handler ─────────────────────────────────────────────

    async def handle_upload(self, files: list[rx.UploadFile]):
        self.s1_processing = True
        self.s1_error = ""
        self.s1_done = False
        self.s2_done = False
        self.s3_done = False
        yield

        for file in files:
            # ── Read and save file ──────────────────────────────────
            try:
                content = await file.read()
            except Exception as e:
                self.s1_error = f"Could not read uploaded file: {e}"
                self.s1_processing = False
                yield
                return

            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            path = str(upload_dir / file.filename)

            try:
                with open(path, "wb") as f:
                    f.write(content)
            except Exception as e:
                self.s1_error = f"Could not save file: {e}"
                self.s1_processing = False
                yield
                return

            self._upload_path = path

            # ── Step 1 ─────────────────────────────────────────────
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
                from pipeline.step1_ingest import run_step1
                r1 = run_step1(path)
            except Exception as e:
                self.s1_error = f"Ingestion error: {e}"
                self.s1_processing = False
                yield
                return

            if not r1["success"]:
                self.s1_error = r1["error"]
                self.s1_processing = False
                yield
                return

            # df lives in local scope — used for all 3 steps without serialisation
            df = r1["dataframe"]

            self.s1_filename = r1["filename"]
            self.s1_file_format = r1["file_format"]
            self.s1_file_size_mb = r1["file_size_mb"]
            self.s1_total_records = r1["total_records"]
            self.s1_total_columns = r1["total_columns"]
            self.s1_column_names = r1["column_names"]

            try:
                from pipeline.step2_features import MANDATORY_FEATURES, OPTIONAL_FEATURES
                mand_set = set(MANDATORY_FEATURES)
                opt_set = set(OPTIONAL_FEATURES)
                cols = r1["column_names"]
                self.s1_mandatory_cols = [c for c in cols if c in mand_set]
                self.s1_optional_cols = [c for c in cols if c in opt_set]
                self.s1_unknown_cols = [c for c in cols if c not in mand_set and c not in opt_set]
            except Exception:
                self.s1_mandatory_cols = []
                self.s1_optional_cols = []
                self.s1_unknown_cols = r1["column_names"]

            self.s1_done = True
            self.s1_processing = False
            self.current_page = "step1"
            yield  # ← user sees Step 1 results

            # ── Step 2 — df still alive in local scope ──────────────
            try:
                from pipeline.step2_features import run_step2
                r2 = run_step2(df)
            except Exception as e:
                self.s1_error = f"Feature check error: {e}"
                yield
                return

            self.s2_mandatory_total = r2["mandatory_total"]
            self.s2_mandatory_present = r2["mandatory_present"]
            self.s2_mandatory_missing = r2["mandatory_missing"]
            self.s2_mandatory_coverage_pct = r2["mandatory_coverage_pct"]
            self.s2_optional_total = r2["optional_total"]
            self.s2_optional_present = r2["optional_present"]
            self.s2_optional_missing = r2["optional_missing"]
            self.s2_categories = [
                {
                    "name": str(c.get("name", "")),
                    "mandatory_count": int(c.get("mandatory_count", 0)),
                    "mandatory_present": int(c.get("mandatory_present", 0)),
                    "optional_count": int(c.get("optional_count", 0)),
                    "optional_present": int(c.get("optional_present", 0)),
                    "status": str(c.get("status", "pass")),
                }
                for c in r2["categories"]
            ]
            self.s2_passed = r2["step2_passed"]
            self.s2_done = True
            yield  # ← user sees Step 2 results

            if not self.s2_passed:
                self.current_page = "step2"
                yield
                return

            # ── Step 3 — df still alive in local scope ──────────────
            try:
                from pipeline.step3_quality import run_step3
                r3 = run_step3(df)
            except Exception as e:
                self.s1_error = f"Quality test error: {e}"
                yield
                return

            def _cols_str(cols) -> str:
                if isinstance(cols, list):
                    s = ", ".join(cols[:3])
                    return s + ("..." if len(cols) > 3 else "")
                return str(cols)

            self.s3_mandatory_tests = [
                {
                    "id": str(t.get("id", "")),
                    "name": str(t.get("name", "")),
                    "columns_tested": _cols_str(t.get("columns_tested", [])),
                    "passed": bool(t.get("passed", True)),
                    "affected_rows": int(t.get("affected_rows", 0)),
                    "message": str(t.get("message", "")),
                    "severity": str(t.get("severity", "Moderate")),
                }
                for t in r3["mandatory_tests"]
            ]
            self.s3_optional_tests = [
                {
                    "id": str(t.get("id", "")),
                    "name": str(t.get("name", "")),
                    "columns_tested": _cols_str(t.get("columns_tested", [])),
                    "has_warning": bool(t.get("has_warning", False)),
                    "message": str(t.get("message", "")),
                }
                for t in r3["optional_tests"]
            ]
            self.s3_mandatory_passed = r3["mandatory_passed"]
            self.s3_mandatory_failed = r3["mandatory_failed"]
            self.s3_all_mandatory_passed = r3["mandatory_all_passed"]
            self.s3_optional_warnings = r3["optional_warnings"]
            self.s3_done = True
            self.s3_report_ready = True

            if self.s3_all_mandatory_passed:
                self.current_page = "ready"
            else:
                self.current_page = "step3"
            yield  # ← user sees Step 3 / Ready

    # ── Navigation ─────────────────────────────────────────────────

    def go_to_page(self, page: str):
        self.current_page = page

    def go_upload(self):
        self.current_page = "upload"

    def go_step1(self):
        self.current_page = "step1"

    def go_step2(self):
        self.current_page = "step2"

    def go_step3(self):
        self.current_page = "step3"

    def go_ready(self):
        self.current_page = "ready"

    def reset_all(self):
        self.s1_done = False
        self.s1_filename = ""
        self.s1_file_format = ""
        self.s1_file_size_mb = 0.0
        self.s1_total_records = 0
        self.s1_total_columns = 0
        self.s1_error = ""
        self.s1_processing = False
        self.s1_column_names = []
        self.s1_mandatory_cols = []
        self.s1_optional_cols = []
        self.s1_unknown_cols = []
        self.s2_done = False
        self.s2_mandatory_total = 0
        self.s2_mandatory_present = 0
        self.s2_mandatory_missing = []
        self.s2_mandatory_coverage_pct = 0.0
        self.s2_optional_total = 0
        self.s2_optional_present = 0
        self.s2_optional_missing = []
        self.s2_categories = []
        self.s2_passed = False
        self.s3_done = False
        self.s3_mandatory_tests = []
        self.s3_optional_tests = []
        self.s3_mandatory_passed = 0
        self.s3_mandatory_failed = 0
        self.s3_all_mandatory_passed = False
        self.s3_optional_warnings = 0
        self.s3_report_ready = False
        self._upload_path = ""
        self.current_page = "upload"

    def download_quality_report(self):
        """Reload df from saved path and generate Excel quality report."""
        try:
            from pipeline.step3_quality import run_step3
            df = self._reload_df()
            if df is None:
                return
            r3 = run_step3(df)
            report_bytes = r3["generate_report"]()
            return rx.download(data=report_bytes, filename="twinswim_quality_report.xlsx")
        except Exception:
            pass
