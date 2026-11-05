"""Non-visual core of Anaxcel: file loading, Pareto maths and the table model.

Nothing in here builds widgets, so it can be reused or tested without a UI.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QThread, pyqtSignal

__version__ = "2.0.0"

SUPPORTED_EXTENSIONS = (".xls", ".xlsx", ".xlsm", ".csv")
FILE_FILTER = ("Spreadsheets (*.xls *.xlsx *.xlsm *.csv);;"
               "Excel workbooks (*.xls *.xlsx *.xlsm);;"
               "CSV files (*.csv);;"
               "All files (*)")


def resource_path(*parts: str) -> str:
    """Absolute path to a file under assets/, from source (lib/../assets) or a PyInstaller build."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", *parts)


def is_supported(path: str) -> bool:
    return path.lower().endswith(SUPPORTED_EXTENSIONS)


def format_value(value) -> str:
    """Human-friendly text for a single cell (12.0 -> '12', NaN -> '')."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, (bool, np.bool_)):
        return str(bool(value))
    if isinstance(value, (float, np.floating)):
        v = float(value)
        return str(int(v)) if v.is_integer() and abs(v) < 1e15 else f"{v:.10g}"
    if isinstance(value, pd.Timestamp):
        fmt = "%Y-%m-%d" if value == value.normalize() else "%Y-%m-%d %H:%M:%S"
        return value.strftime(fmt)
    return str(value)


# --------------------------------------------------------------------------- loading
def read_table(path: str, header: bool = True) -> pd.DataFrame:
    """Read the first sheet of an Excel file (or a CSV) into a tidy DataFrame."""
    header_row = 0 if header else None
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path, header=header_row, sep=None, engine="python")
    else:
        df = pd.read_excel(path, header=header_row, sheet_name=0)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    if header:
        df.columns = [str(c).strip() for c in df.columns]
    else:
        df.columns = [f"Column {i + 1}" for i in range(df.shape[1])]
    return df


def combine_files(paths, header=True, on_progress=None):
    """Read and stack several files. Returns (DataFrame, [error messages])."""
    frames, errors = [], []
    for i, path in enumerate(paths, 1):
        try:
            frame = read_table(path, header)
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:  # one bad file must not abort the batch
            errors.append(f"{os.path.basename(path)}: {exc}")
        if on_progress:
            on_progress(i, len(paths))
    df = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    return df, errors


def _numeric_ratio(series: pd.Series) -> float:
    sample = series.dropna().head(500)
    if sample.empty:
        return 0.0
    return float(pd.to_numeric(sample, errors="coerce").notna().mean())


def guess_columns(df: pd.DataFrame):
    """Best guess for (category column, value column)."""
    cols = list(df.columns)
    if not cols:
        return None, None
    numeric = [c for c in cols if _numeric_ratio(df[c]) >= 0.8]
    value = numeric[-1] if numeric else cols[-1]
    text = [c for c in cols if c not in numeric]
    category = text[0] if text else next((c for c in cols if c != value), cols[0])
    return category, value


# --------------------------------------------------------------------------- analysis
@dataclass
class ParetoResult:
    category: str
    value: str
    labels: list
    values: np.ndarray
    cumulative: np.ndarray      # cumulative share in percent
    total: float
    vital_few: int              # number of categories needed to reach 80 %
    skipped_rows: int           # rows with a missing category or non-numeric value
    dropped_categories: int     # categories whose total was <= 0


def compute_pareto(df: pd.DataFrame, category: str, value: str, max_bars: int = 25) -> ParetoResult:
    if category not in df.columns or value not in df.columns:
        raise KeyError("Pick a valid category and value column.")
    cats = df[category]
    vals = pd.to_numeric(df[value], errors="coerce")
    mask = cats.notna() & vals.notna()
    skipped = int((~mask).sum())
    if not mask.any():
        raise ValueError(f"Column “{value}” has no numeric values to analyse.")

    data = pd.DataFrame({"cat": cats[mask].map(format_value).str.strip(), "val": vals[mask]})
    grouped = data.groupby("cat", sort=False)["val"].sum().sort_values(ascending=False, kind="stable")
    positive = grouped[grouped > 0]
    dropped = len(grouped) - len(positive)
    if positive.empty:
        raise ValueError(f"Column “{value}” has no positive totals, so a Pareto chart cannot be drawn.")

    if len(positive) > max_bars:
        head = positive.iloc[: max_bars - 1]
        rest = positive.iloc[max_bars - 1:]
        positive = pd.concat([head, pd.Series({f"Other ({len(rest)})": rest.sum()})])

    total = float(positive.sum())
    cumulative = (positive.cumsum() / total * 100).to_numpy()
    vital = min(int((cumulative < 80).sum()) + 1, len(positive))
    return ParetoResult(category, value, [str(i) for i in positive.index], positive.to_numpy(dtype=float),
                        cumulative, total, vital, skipped, dropped)


# --------------------------------------------------------------------------- Qt model
class DataFrameModel(QAbstractTableModel):
    """Read-only, lazily rendered view of a DataFrame with fast sorting and filtering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_frame(pd.DataFrame(), _reset=False)

    def set_frame(self, df: pd.DataFrame, _reset: bool = True):
        if _reset:
            self.beginResetModel()
        self._df = df.reset_index(drop=True)
        self._values = self._df.to_numpy(dtype=object)
        if self._values.ndim != 2:
            self._values = self._values.reshape(len(self._df), -1)
        self._numeric = [pd.api.types.is_numeric_dtype(t) for t in self._df.dtypes]
        self._date_fmt = [self._date_format(self._df.iloc[:, c]) for c in range(self._df.shape[1])]
        self._col_text = None    # lower-cased cell text per column, built on first search
        self._filter = ""
        self._sort = None
        self._rows = np.arange(len(self._df))
        if _reset:
            self.endResetModel()

    @property
    def frame(self) -> pd.DataFrame:
        return self._df

    def visible_frame(self) -> pd.DataFrame:
        return self._df.iloc[self._rows]

    # -- Qt API
    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else self._values.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self._cell_text(self._rows[index.row()], index.column())
        if role == Qt.TextAlignmentRole:
            return self._alignment(index.column())
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole and orientation == Qt.Horizontal and section < len(self._numeric):
            return self._alignment(section)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section]) if section < len(self._df.columns) else None
        return str(self._rows[section] + 1) if section < len(self._rows) else None

    def sort(self, column, order=Qt.AscendingOrder):
        self.beginResetModel()
        self._sort = (column, order) if 0 <= column < self._values.shape[1] else None
        self._apply()
        self.endResetModel()

    def set_filter(self, text: str):
        text = text.strip().lower()
        if text == self._filter:
            return
        self.beginResetModel()
        self._filter = text
        self._apply()
        self.endResetModel()

    # -- internals
    @staticmethod
    def _date_format(series: pd.Series):
        """One date format per column: drop the time part only if every value is at midnight."""
        if pd.api.types.is_datetime64_any_dtype(series):
            values = series.dropna()
            midnight = (values == values.dt.normalize()).all()
        elif series.dtype == object:  # e.g. dates from .xlsx mixed with text dates from .csv
            stamps = [v for v in series.dropna() if isinstance(v, pd.Timestamp)]
            if not stamps:
                return None
            midnight = all(v == v.normalize() for v in stamps)
        else:
            return None
        return "%Y-%m-%d" if midnight else "%Y-%m-%d %H:%M:%S"

    def _cell_text(self, row: int, col: int) -> str:
        value = self._values[row, col]
        fmt = self._date_fmt[col]
        if fmt and isinstance(value, pd.Timestamp):
            return value.strftime(fmt)
        return format_value(value)

    def _alignment(self, col: int) -> int:
        horizontal = Qt.AlignRight if self._numeric[col] else Qt.AlignLeft
        return int(horizontal | Qt.AlignVCenter)

    def _apply(self):
        rows = self._sorted_rows() if self._sort else np.arange(len(self._df))
        if self._filter:
            if self._col_text is None:
                self._col_text = [pd.Series([self._cell_text(r, c) for r in range(len(self._df))],
                                            dtype=object).str.lower()
                                  for c in range(self._df.shape[1])]
            mask = np.zeros(len(self._df), dtype=bool)
            for col in self._col_text:
                mask |= col.str.contains(self._filter, regex=False).to_numpy()
            rows = rows[mask[rows]]
        self._rows = rows

    def _sorted_rows(self):
        column, order = self._sort
        series = self._df.iloc[:, column]
        numeric = pd.to_numeric(series, errors="coerce")
        if self._numeric[column] or numeric.notna().sum() == series.notna().sum():
            key = numeric
        else:
            key = series.map(format_value).str.lower().where(series.notna())
        return key.sort_values(ascending=order == Qt.AscendingOrder,
                               na_position="last", kind="stable").index.to_numpy()


class LoadWorker(QThread):
    """Reads and combines files off the UI thread."""
    progress = pyqtSignal(int, int)
    loaded = pyqtSignal(object, list)

    def __init__(self, paths, header, parent=None):
        super().__init__(parent)
        self._paths = list(paths)
        self._header = header

    def run(self):
        try:
            df, errors = combine_files(self._paths, self._header, self.progress.emit)
        except Exception as exc:
            df, errors = pd.DataFrame(), [str(exc)]
        self.loaded.emit(df, errors)
