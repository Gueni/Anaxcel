# coding=utf-8
"""Smoke tests: core logic on the sample data, and the main window driven offscreen.

Usage:  py tools/make_sample_data.py && py -m pytest -q
"""
import glob
import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA        = os.path.join(ROOT, "data")
sys.path.insert(0, ROOT)

from lib.core import Loader, Pareto                                                    # noqa: E402

DEFECT_FILES = sorted(glob.glob(os.path.join(DATA, "defects_*")))
pytestmark   = pytest.mark.skipif(not DEFECT_FILES, reason="run tools/make_sample_data.py first")


def test_combine_and_pareto():
    df, errors = Loader.combine_files(DEFECT_FILES)
    assert errors == []
    assert len(df) == 400 + 450 + 500 + 300
    assert list(df.columns) == ["Date", "Line", "Defect", "Count", "Cost (EUR)"]
    category, value = Loader.guess_columns(df)
    assert category == "Line" and value == "Cost (EUR)"
    result = Pareto.compute(df, "Defect", "Count")
    assert result.labels[0] == "Scratch"
    assert abs(result.cumulative[-1] - 100) < 1e-9
    assert 1 <= result.vital_few <= len(result.labels)


def test_no_header_and_large():
    df = Loader.read_table(os.path.join(DATA, "sales_no_header.csv"), header=False)
    assert df.shape == (50, 5) and df.columns[0] == "Column 1"
    big, errors = Loader.combine_files([os.path.join(DATA, "sales_large.csv")])
    assert not errors and len(big) == 200_000
    assert Pareto.compute(big, "Product", "Revenue").labels[0] == "Widget"


def test_bad_file_reported(tmp_path):
    bad = tmp_path / "broken.xlsx"
    bad.write_bytes(b"not a spreadsheet")
    df, errors = Loader.combine_files([str(bad), DEFECT_FILES[0]])
    assert len(errors) == 1 and "broken.xlsx" in errors[0]
    assert len(df) == 400


def test_gui_load_analyse(monkeypatch):
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from lib.anaxcel import MainWindow
    from lib.dialogs import AboutDialog

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.add_files(DEFECT_FILES)
    window.load_files()
    worker = getattr(window, "_worker", None)
    for _ in range(600):                                                               # wait for the loader thread
        app.processEvents()
        if window.model.rowCount() == 1650:
            break
        if worker is not None:
            worker.wait(50)
    assert window.model.rowCount() == 1650
    window.analyse()
    app.processEvents()
    assert window.ui.paretoChart is not None
    AboutDialog(window).close()
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)       # modal prompts crash the offscreen platform
    window.close()
