#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                                              __            _
#?            ____ _____  ____ __  __________  / /___ ___  __(_)
#?           / __ `/ __ \/ __ `/ |/_/ ___/ _ \/ / __ `/ / / / /
#?          / /_/ / / / / /_/ />  </ /__/  __/ / /_/ / /_/ / /
#?          \__,_/_/ /_/\__,_/_/|_|\___/\___/_/\__, /\__,_/_/
#?                                            /____/
#?
#? Name:        anaxcelgui.py
#? Purpose:     main window layout. Everything sits in layouts, so the UI scales with any window size and DPI.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     11/11/2025
#? Licence:     Refer to the LICENSE file
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  os

from    PyQt5.QtCore                import  QRect, QSize, Qt, pyqtSignal
from    PyQt5.QtGui                 import  QFont, QFontMetrics, QIcon, QKeySequence, QPainter, QPalette, QPixmap
from    PyQt5.QtWidgets             import  (QAbstractItemView, QAction, QApplication, QButtonGroup, QCheckBox, QComboBox,
                                             QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListWidget, QProgressBar,
                                             QPushButton, QSizePolicy, QStackedWidget, QStyle, QStyledItemDelegate,
                                             QStyleOptionViewItem, QTableView, QVBoxLayout, QWidget)

from    lib.charts                  import  DonutChart, ParetoChart
from    lib.core                    import  __version__, Utils
#?----------------------------------------------------------------------------------------------------------------------------------------
class FileItemDelegate(QStyledItemDelegate):
    """Two-line item: file name on top, its folder underneath in a muted colour."""

    def sizeHint(self, option, index):
        h                   = option.fontMetrics.height()
        return QSize(100, h * 2 + 18)

    def paint(self, painter, option, index):
        opt                 = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text            = ""
        style               = opt.widget.style() if opt.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)

        rect                = opt.rect.adjusted(12, 7, -12, -7)
        name                = index.data(Qt.DisplayRole) or ""
        folder              = os.path.dirname(index.data(Qt.UserRole) or "")
        painter.save()
        bold                = QFont(opt.font)
        bold.setWeight(QFont.DemiBold)
        fm_bold, fm         = QFontMetrics(bold), QFontMetrics(opt.font)
        top                 = QRect(rect.left(), rect.top(), rect.width(), fm_bold.height())
        bottom              = QRect(rect.left(), top.bottom() + 3, rect.width(), fm.height())
        painter.setFont(bold)
        painter.setPen(opt.palette.color(QPalette.Text))
        painter.drawText(top, Qt.AlignLeft | Qt.AlignVCenter, fm_bold.elidedText(name, Qt.ElideRight, rect.width()))
        painter.setFont(opt.font)
        painter.setPen(opt.palette.color(QPalette.PlaceholderText))
        painter.drawText(bottom, Qt.AlignLeft | Qt.AlignVCenter, fm.elidedText(folder, Qt.ElideMiddle, rect.width()))
        painter.restore()
#?----------------------------------------------------------------------------------------------------------------------------------------
class FileListWidget(QListWidget):
    """List of input files with drag & drop and an empty-state hint."""
    filesDropped            = pyqtSignal(list)
    deleteRequested         = pyqtSignal()

    PLACEHOLDER             = "Drop Excel or CSV files here\nor click “Add files”"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setItemDelegate(FileItemDelegate(self))
        self.setUniformItemSizes(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    dragMoveEvent           = dragEnterEvent

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths           = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            event.acceptProposedAction()
            self.filesDropped.emit(paths)
        else:
            super().dropEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.deleteRequested.emit()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            painter         = QPainter(self.viewport())
            font            = QFont(self.font())
            font.setPointSizeF(font.pointSizeF() * 1.15)
            painter.setFont(font)
            painter.setPen(self.palette().color(QPalette.PlaceholderText))
            painter.drawText(self.viewport().rect(), Qt.AlignCenter, self.PLACEHOLDER)
#?----------------------------------------------------------------------------------------------------------------------------------------
class Widgets:
    """Small factories for the styled widgets used across the pages."""

    @staticmethod
    def button(text, primary=False, tooltip=""):
        button              = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        if primary:
            button.setProperty("primary", True)
        if tooltip:
            button.setToolTip(tooltip)
        return button

    @staticmethod
    def label(text, name=None, wrap=False):
        label               = QLabel(text)
        if name:
            label.setObjectName(name)
        label.setWordWrap(wrap)
        return label

    @staticmethod
    def empty_state(glyph, title, text):
        widget              = QWidget()
        layout              = QVBoxLayout(widget)
        layout.addStretch(1)
        for content, name in ((glyph, "emptyGlyph"), (title, "emptyTitle"), (text, "pageSubtitle")):
            label           = Widgets.label(content, name, wrap=True)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        layout.addStretch(2)
        return widget

    @staticmethod
    def card():
        card                = QFrame()
        card.setObjectName("card")
        return card
#?----------------------------------------------------------------------------------------------------------------------------------------
class Ui_MainWindow:
    """Builds the sidebar, the four pages, the actions, menus and status bar of the main window."""

    NAV                     = [("☰", "Files"), ("▦", "Data"), ("▙", "Pareto"), ("◔", "Donut")]
    PARETO_SUBTITLE         = "Categories sorted by total, with the cumulative share. Hover a bar for details."
    DONUT_SUBTITLE          = "Share of the total per category. Hover a slice for details."

    def setupUi(self, window):
        window.setObjectName("MainWindow")
        window.setWindowTitle("Anaxcel")
        window.setWindowIcon(QIcon(Utils.resource_path("icons", "icon.png")))

        central             = QWidget()
        root                = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())
        self.stack          = QStackedWidget()
        root.addWidget(self.stack, 1)
        for page in (self._build_files_page(), self._build_data_page(),
                     self._build_pareto_page(), self._build_donut_page()):
            self.stack.addWidget(page)
        window.setCentralWidget(central)

        self._build_actions(window)
        self._build_menus(window)
        self._build_statusbar(window)
        self._compact       = None
        self.set_sidebar_compact(False)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Sidebar
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _build_sidebar(self):
        self.sidebar        = QFrame()
        self.sidebar.setObjectName("sidebar")
        layout              = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(10, 18, 10, 14)
        layout.setSpacing(4)

        brand_row           = QHBoxLayout()
        brand_row.setSpacing(10)
        brand_row.setContentsMargins(6, 0, 0, 0)
        self.logo           = QLabel()
        logo                = QPixmap(Utils.resource_path("icons", "icon.png"))
        if not logo.isNull():
            size            = self.sidebar.fontMetrics().height() * 2
            self.logo.setPixmap(logo.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.brand          = Widgets.label("Anaxcel", "brand")
        brand_row.addWidget(self.logo)
        brand_row.addWidget(self.brand, 1)
        layout.addLayout(brand_row)
        layout.addSpacing(22)

        self.navGroup       = QButtonGroup(self.sidebar)
        self.navGroup.setExclusive(True)
        self.navButtons     = []
        for i, (glyph, text) in enumerate(self.NAV):
            button          = QPushButton()
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(f"{text}  (Ctrl+{i + 1})")
            self.navGroup.addButton(button, i)
            self.navButtons.append(button)
            layout.addWidget(button)
        layout.addStretch(1)

        self.btnTheme       = QPushButton()
        self.btnTheme.setObjectName("navButton")
        self.btnTheme.setCursor(Qt.PointingHandCursor)
        self.btnTheme.setToolTip("Toggle light / dark theme  (Ctrl+T)")
        layout.addWidget(self.btnTheme)
        self.versionLabel   = Widgets.label(f"v{__version__}", "version")
        self.versionLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.versionLabel)
        return self.sidebar

    def set_theme_label(self, dark: bool):
        self._theme_text    = ("☀", "Light mode") if dark else ("☾", "Dark mode")
        self._refresh_nav_text()

    def set_sidebar_compact(self, compact: bool):
        if compact == self._compact:
            return
        self._compact       = compact
        fm                  = self.sidebar.fontMetrics()
        self.sidebar.setFixedWidth(fm.height() * 4 if compact else fm.averageCharWidth() * 28)
        self.brand.setVisible(not compact)
        self.versionLabel.setVisible(not compact)
        for button in self.navButtons + [self.btnTheme]:
            button.setProperty("compact", compact)
            button.style().unpolish(button)
            button.style().polish(button)
        self._refresh_nav_text()

    def _refresh_nav_text(self):
        compact             = bool(self._compact)
        for button, (glyph, text) in zip(self.navButtons, self.NAV):
            button.setText(glyph if compact else f"{glyph}    {text}")
        glyph, text         = getattr(self, "_theme_text", ("☀", "Light mode"))
        self.btnTheme.setText(glyph if compact else f"{glyph}    {text}")

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Pages
    #?------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _page(title, subtitle):
        """Empty page with a title / subtitle header. Returns (page, layout, header row, subtitle label)."""
        page                = QWidget()
        page.setObjectName("page")
        layout              = QVBoxLayout(page)
        layout.setContentsMargins(28, 22, 28, 20)
        layout.setSpacing(14)
        header              = QHBoxLayout()
        header.setSpacing(12)
        texts               = QVBoxLayout()
        texts.setSpacing(2)
        texts.addWidget(Widgets.label(title, "pageTitle"))
        sub                 = Widgets.label(subtitle, "pageSubtitle", wrap=True)
        texts.addWidget(sub)
        header.addLayout(texts, 1)
        layout.addLayout(header)
        return page, layout, header, sub

    def _build_files_page(self):
        page, layout, _, _  = self._page("Files", "Add the spreadsheets to combine (.xls, .xlsx, .xlsm, .csv), "
                                                  "then load them. Load uses the selected files, or all of them.")
        row                 = QHBoxLayout()
        row.setSpacing(8)
        self.btnAdd         = Widgets.button("＋  Add files", primary=True, tooltip="Add spreadsheets  (Ctrl+O)")
        self.btnRemove      = Widgets.button("Remove", tooltip="Remove the selected files  (Del)")
        self.btnClear       = Widgets.button("Clear all")
        self.btnLoad        = Widgets.button("Load all  →", primary=True, tooltip="Combine and load  (Ctrl+L)")
        for widget in (self.btnAdd, self.btnRemove, self.btnClear):
            row.addWidget(widget)
        row.addStretch(1)
        row.addWidget(self.btnLoad)
        layout.addLayout(row)

        self.fileList       = FileListWidget()
        layout.addWidget(self.fileList, 1)

        bottom              = QHBoxLayout()
        self.headerCheck    = QCheckBox("First row contains column names")
        self.headerCheck.setChecked(True)
        self.fileCountLabel = Widgets.label("", "muted")
        bottom.addWidget(self.headerCheck)
        bottom.addStretch(1)
        bottom.addWidget(self.fileCountLabel)
        layout.addLayout(bottom)
        return page

    def _build_data_page(self):
        page, layout, header, self.dataSubtitle = self._page("Data", "No data loaded yet.")
        self.searchEdit     = QLineEdit()
        self.searchEdit.setPlaceholderText("Search rows…")
        self.searchEdit.setClearButtonEnabled(True)
        self.searchEdit.setMinimumWidth(140)
        self.searchEdit.setMaximumWidth(320)
        self.searchEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header.addWidget(self.searchEdit, 1, Qt.AlignBottom)

        card                = Widgets.card()
        controls            = QHBoxLayout(card)
        controls.setContentsMargins(14, 10, 10, 10)
        controls.setSpacing(10)
        self.categoryCombo  = QComboBox()
        self.valueCombo     = QComboBox()
        for label, combo in (("Category", self.categoryCombo), ("Value", self.valueCombo)):
            combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            combo.setMinimumContentsLength(6)
            combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            controls.addWidget(Widgets.label(label, "fieldLabel"))
            controls.addWidget(combo, 1)
            controls.addSpacing(6)
        self.btnAnalyse     = Widgets.button("Analyse", primary=True, tooltip="Build the charts  (Ctrl+R)")
        controls.addWidget(self.btnAnalyse)
        layout.addWidget(card)

        self.tableView      = QTableView()
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setShowGrid(False)
        self.tableView.setWordWrap(False)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        h                   = self.tableView.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Interactive)
        h.setStretchLastSection(True)
        h.setResizeContentsPrecision(200)
        h.setHighlightSections(False)
        h.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        v                   = self.tableView.verticalHeader()
        v.setDefaultSectionSize(self.tableView.fontMetrics().height() + 14)
        v.setSectionResizeMode(QHeaderView.Fixed)
        v.setHighlightSections(False)
        layout.addWidget(self.tableView, 1)
        return page

    def _chart_page(self, title, subtitle, chart):
        """Page holding a chart in a card, behind an empty state until there is a result. Returns (page, stack, subtitle)."""
        page, layout, _, sub = self._page(title, subtitle)
        stack               = QStackedWidget()
        stack.addWidget(Widgets.empty_state("▙" if title == "Pareto" else "◔", "No chart yet",
                                            "Load data, choose a category and a value column on the Data page, "
                                            "then click Analyse."))
        card                = Widgets.card()
        card_layout         = QVBoxLayout(card)
        card_layout.setContentsMargins(6, 6, 6, 6)
        card_layout.addWidget(chart)
        stack.addWidget(card)
        layout.addWidget(stack, 1)
        return page, stack, sub

    def _build_pareto_page(self):
        self.paretoChart    = ParetoChart()
        page, self.paretoStack, self.paretoSubtitle = self._chart_page("Pareto", self.PARETO_SUBTITLE, self.paretoChart)
        return page

    def _build_donut_page(self):
        self.donutChart     = DonutChart()
        page, self.donutStack, self.donutSubtitle = self._chart_page("Donut", self.DONUT_SUBTITLE, self.donutChart)
        return page

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Actions, menus and status bar
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _build_actions(self, window):
        def action(text, shortcut=None, tip=""):
            a               = QAction(text, window)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            a.setStatusTip(tip or text)
            return a

        self.actionAddFiles     = action("Add files…",               QKeySequence.Open, "Add spreadsheets to the list")
        self.actionExport       = action("Export data…",             "Ctrl+E",          "Save the visible rows as .xlsx or .csv")
        self.actionExit         = action("Exit",                     "Ctrl+Q")
        self.actionLoad         = action("Load files",               "Ctrl+L",          "Combine and load the selected (or all) files")
        self.actionAnalyse      = action("Analyse",                  "Ctrl+R",          "Build the Pareto and donut charts")
        self.actionSelectAll    = action("Select all files",         "Ctrl+Shift+A")
        self.actionRemove       = action("Remove selected files")
        self.actionClear        = action("Clear all")
        self.actionToggleTheme  = action("Toggle light / dark theme", "Ctrl+T")
        self.actionAbout        = action("About Anaxcel",            "F1")
        self.pageActions        = [action(f"{text}", f"Ctrl+{i + 1}", f"Go to {text}") for i, (_, text) in enumerate(self.NAV)]

    def _build_menus(self, window):
        bar                 = window.menuBar()
        file_menu           = bar.addMenu("&File")
        file_menu.addActions([self.actionAddFiles, self.actionExport])
        file_menu.addSeparator()
        file_menu.addAction(self.actionExit)
        data_menu           = bar.addMenu("&Data")
        data_menu.addActions([self.actionLoad, self.actionAnalyse])
        data_menu.addSeparator()
        data_menu.addActions([self.actionSelectAll, self.actionRemove, self.actionClear])
        view_menu           = bar.addMenu("&View")
        view_menu.addActions(self.pageActions)
        view_menu.addSeparator()
        view_menu.addAction(self.actionToggleTheme)
        help_menu           = bar.addMenu("&Help")
        help_menu.addAction(self.actionAbout)

    def _build_statusbar(self, window):
        self.statusbar      = window.statusBar()
        self.statusbar.setSizeGripEnabled(True)
        self.progress       = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(160)
        self.progress.hide()
        self.statusInfo     = QLabel()
        self.statusbar.addPermanentWidget(self.progress)
        self.statusbar.addPermanentWidget(self.statusInfo)
#?----------------------------------------------------------------------------------------------------------------------------------------
