"""
Step 1 — Data Ingestion
Accepts .xlsx or .csv, returns metadata + dataframe.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


def run_step1(file_path: str) -> dict:
    """Load and profile the uploaded dataset.

    Returns a dict with success flag, metadata fields, and the raw DataFrame.
    """
    result: dict = {
        "success": False,
        "error": "",
        "filename": "",
        "file_format": "",
        "file_size_mb": 0.0,
        "total_records": 0,
        "total_columns": 0,
        "column_names": [],
        "dtypes_summary": {},
        "dataframe": None,
    }

    try:
        path = Path(file_path)
        result["filename"] = path.name

        # File size
        try:
            size_bytes = path.stat().st_size
            result["file_size_mb"] = round(size_bytes / (1024 * 1024), 2)
        except Exception:
            result["file_size_mb"] = 0.0

        ext = path.suffix.lower()
        if ext not in (".xlsx", ".xls", ".csv"):
            result["error"] = (
                f"Unsupported file format '{ext}'. Please upload a .xlsx or .csv file."
            )
            return result

        result["file_format"] = ".xlsx" if ext in (".xlsx", ".xls") else ".csv"

        # Load
        df: pd.DataFrame
        if result["file_format"] == ".xlsx":
            try:
                df = pd.read_excel(file_path, sheet_name="Processed Data", engine="openpyxl")
            except Exception:
                # Fall back to first sheet
                try:
                    xl = pd.ExcelFile(file_path, engine="openpyxl")
                    if len(xl.sheet_names) == 0:
                        result["error"] = "Excel file contains no sheets."
                        return result
                    df = xl.parse(xl.sheet_names[0])
                except Exception as e:
                    result["error"] = f"Could not read Excel file: {e}"
                    return result
        else:
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                result["error"] = f"Could not read CSV file: {e}"
                return result

        if df is None or len(df) == 0:
            result["error"] = "File appears to be empty — no rows were loaded."
            return result

        # Profile dtypes
        dtype_counts: dict[str, int] = {}
        for dtype in df.dtypes:
            key = str(dtype)
            dtype_counts[key] = dtype_counts.get(key, 0) + 1

        result["success"] = True
        result["total_records"] = len(df)
        result["total_columns"] = len(df.columns)
        result["column_names"] = list(df.columns)
        result["dtypes_summary"] = dtype_counts
        result["dataframe"] = df

    except Exception as e:
        result["error"] = f"Unexpected error during ingestion: {e}"

    return result
