"""Light and dark themes: colour tokens, the Qt palette and the application stylesheet."""
from string import Template

from PyQt5.QtGui import QColor, QPalette

from lib.core import resource_path

PALETTES = {
    "dark": {
        "bg": "#0f1115", "surface": "#171a21", "surface_alt": "#1f232c", "border": "#2a2f3a",
        "scroll": "#3a4150", "text": "#e6e8ee", "text_muted": "#8b93a7",
        "accent": "#4f8cff", "accent_hover": "#6b9fff", "accent_soft": "#1c2a45", "accent_text": "#ffffff",
        "selection": "#24406e", "chart_secondary": "#ffb547", "chart_muted": "#3a4256",
    },
    "light": {
        "bg": "#f4f6fa", "surface": "#ffffff", "surface_alt": "#eef1f6", "border": "#dde2ea",
        "scroll": "#c3cad6", "text": "#1b1f29", "text_muted": "#6b7385",
        "accent": "#2f6fed", "accent_hover": "#4a82f0", "accent_soft": "#e3ecfd", "accent_text": "#ffffff",
        "selection": "#cfe0ff", "chart_secondary": "#e8890c", "chart_muted": "#c5cddb",
    },
}

SERIES_COLORS = ["#4f8cff", "#ffb547", "#3ccf91", "#ef5b8a", "#9b7bff",
                 "#2ec5d3", "#ff8a4c", "#a3b1c9", "#d4c34a", "#6fcf5b"]


def get_palette(name: str) -> dict:
    p = dict(PALETTES.get(name, PALETTES["dark"]))
    p["name"] = name if name in PALETTES else "dark"
    return p


def _icon(name: str) -> str:
    return resource_path("icons", name).replace("\\", "/")


_QSS = Template(r"""
* { outline: 0; }
QWidget { color: $text; }
QMainWindow, QDialog, QStackedWidget, QWidget#page { background: $bg; }

/* ---------- sidebar ---------- */
QFrame#sidebar { background: $surface; border: none; border-right: 1px solid $border; }
QLabel#brand { font-size: 15pt; font-weight: 700; }
QLabel#version { color: $text_muted; font-size: 8.5pt; }
QPushButton#navButton {
    text-align: left; padding: 9px 14px; border: none; border-radius: 8px;
    background: transparent; color: $text_muted; font-size: 10.5pt;
}
QPushButton#navButton[compact="true"] { text-align: center; padding: 9px 0; font-size: 13pt; }
QPushButton#navButton:hover { background: $surface_alt; color: $text; }
QPushButton#navButton:checked { background: $accent_soft; color: $accent; font-weight: 600; }

/* ---------- headings ---------- */
QLabel#pageTitle { font-size: 19pt; font-weight: 600; }
QLabel#pageSubtitle, QLabel#muted { color: $text_muted; }
QLabel#emptyGlyph { color: $scroll; font-size: 40pt; }
QLabel#emptyTitle { font-size: 13pt; font-weight: 600; }
QLabel#fieldLabel { color: $text_muted; font-weight: 600; }

QFrame#card { background: $surface; border: 1px solid $border; border-radius: 12px; }

/* ---------- buttons ---------- */
QPushButton {
    background: $surface_alt; border: 1px solid $border; border-radius: 8px;
    padding: 7px 16px; min-height: 20px;
}
QPushButton:hover { border-color: $accent; }
QPushButton:pressed { background: $border; }
QPushButton:disabled { color: $text_muted; background: $surface; border-color: $border; }
QPushButton[primary="true"] { background: $accent; color: $accent_text; border: 1px solid $accent; font-weight: 600; }
QPushButton[primary="true"]:hover { background: $accent_hover; border-color: $accent_hover; }
QPushButton[primary="true"]:disabled { background: $accent_soft; border-color: $accent_soft; color: $text_muted; }

/* ---------- inputs ---------- */
QLineEdit, QComboBox {
    background: $surface; border: 1px solid $border; border-radius: 8px;
    padding: 6px 10px; min-height: 20px; selection-background-color: $selection;
}
QLineEdit:focus, QComboBox:focus, QComboBox:on { border-color: $accent; }
QLineEdit:disabled, QComboBox:disabled { color: $text_muted; }
QComboBox::drop-down { border: none; width: 26px; }
QComboBox::down-arrow { image: url($chevron); width: 12px; height: 12px; }
QComboBox QAbstractItemView {
    background: $surface; border: 1px solid $border; padding: 4px;
    selection-background-color: $selection; selection-color: $text;
}
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid $scroll; border-radius: 4px; background: $surface; }
QCheckBox::indicator:hover { border-color: $accent; }
QCheckBox::indicator:checked { background: $accent; border-color: $accent; image: url($check); }

/* ---------- lists & tables ---------- */
QListWidget, QTableView, QTextBrowser {
    background: $surface; border: 1px solid $border; border-radius: 10px;
    alternate-background-color: $surface_alt; gridline-color: $border;
    selection-background-color: $selection; selection-color: $text;
}
QListWidget { padding: 6px; }
QListWidget::item { border-radius: 8px; margin: 2px 0; }
QListWidget::item:hover { background: $surface_alt; }
QListWidget::item:selected { background: $selection; color: $text; }
QTableView::item { border: none; padding: 0 10px; }
QHeaderView { background: $surface_alt; border: none; }
QHeaderView::section {
    background: $surface_alt; color: $text_muted; border: none;
    border-bottom: 1px solid $border; border-right: 1px solid $border;
    padding: 6px 8px; font-weight: 600;
}
QHeaderView::section:hover { color: $text; }
QTableCornerButton::section { background: $surface_alt; border: none; border-bottom: 1px solid $border; }

/* ---------- scrollbars ---------- */
QScrollBar:vertical { background: transparent; width: 12px; margin: 3px; }
QScrollBar:horizontal { background: transparent; height: 12px; margin: 3px; }
QScrollBar::handle { background: $scroll; border-radius: 3px; }
QScrollBar::handle:vertical { min-height: 32px; }
QScrollBar::handle:horizontal { min-width: 32px; }
QScrollBar::handle:hover { background: $text_muted; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }

/* ---------- chrome ---------- */
QMenuBar { background: $surface; border-bottom: 1px solid $border; padding: 2px 6px; }
QMenuBar::item { background: transparent; padding: 5px 10px; border-radius: 6px; }
QMenuBar::item:selected { background: $surface_alt; }
QMenu { background: $surface; border: 1px solid $border; padding: 6px; }
QMenu::item { padding: 6px 28px 6px 12px; border-radius: 6px; }
QMenu::item:selected { background: $selection; color: $text; }
QMenu::item:disabled { color: $text_muted; }
QMenu::separator { height: 1px; background: $border; margin: 5px 8px; }
QStatusBar { background: $surface; color: $text_muted; border-top: 1px solid $border; }
QStatusBar::item { border: none; }
QStatusBar QLabel { color: $text_muted; padding: 0 8px; }
QProgressBar { background: $surface_alt; border: none; border-radius: 3px; max-height: 6px; }
QProgressBar::chunk { background: $accent; border-radius: 3px; }
QToolTip { background: $surface_alt; color: $text; border: 1px solid $border; padding: 6px; }
/* opaque on purpose: matplotlib picks light/dark toolbar icons from this colour */
QToolBar { background: $surface; border: none; spacing: 2px; }
QToolButton { background: transparent; border: none; border-radius: 6px; padding: 4px; }
QToolButton:hover { background: $surface_alt; }
QToolButton:checked { background: $accent_soft; }
QDialogButtonBox QPushButton { min-width: 80px; }
""")


def apply_theme(app, name: str) -> dict:
    """Apply the named theme to the whole application and return its colour tokens."""
    p = get_palette(name)
    c = {k: QColor(v) for k, v in p.items() if isinstance(v, str) and v.startswith("#")}

    pal = QPalette()
    pal.setColor(QPalette.Window, c["bg"])
    pal.setColor(QPalette.WindowText, c["text"])
    pal.setColor(QPalette.Base, c["surface"])
    pal.setColor(QPalette.AlternateBase, c["surface_alt"])
    pal.setColor(QPalette.Text, c["text"])
    pal.setColor(QPalette.Button, c["surface_alt"])
    pal.setColor(QPalette.ButtonText, c["text"])
    pal.setColor(QPalette.Highlight, c["selection"])
    pal.setColor(QPalette.HighlightedText, c["text"])
    pal.setColor(QPalette.ToolTipBase, c["surface_alt"])
    pal.setColor(QPalette.ToolTipText, c["text"])
    pal.setColor(QPalette.PlaceholderText, c["text_muted"])
    pal.setColor(QPalette.Link, c["accent"])
    pal.setColor(QPalette.LinkVisited, c["accent"])
    for role in (QPalette.Text, QPalette.ButtonText, QPalette.WindowText):
        pal.setColor(QPalette.Disabled, role, c["text_muted"])
    app.setPalette(pal)
    app.setStyleSheet(_QSS.substitute(p, chevron=_icon("chevron-down.svg"), check=_icon("check.svg")))
    return p
