#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                                              __
#?            ____ _____  ____ __  __________  / /
#?           / __ `/ __ \/ __ `/ |/_/ ___/ _ \/ /
#?          / /_/ / / / / /_/ />  </ /__/  __/ /
#?          \__,_/_/ /_/\__,_/_/|_|\___/\___/_/
#?
#?
#? Name:        anaxcel.py
#? Purpose:     Anaxcel main window: combine Excel/CSV files and analyse them with Pareto and donut charts.
#?              App: application setup (high DPI, theme, splash screen). Start it with `py main.py`.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     11/11/2025
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  os
import  sys

from    PyQt5.QtCore                import  QSettings, Qt, QTimer
from    PyQt5.QtGui                 import  QFont, QGuiApplication, QIcon, QPixmap
from    PyQt5.QtWidgets             import  QApplication, QFileDialog, QListWidgetItem, QMainWindow, QMessageBox, QSplashScreen

from    lib.anaxcelgui              import  Ui_MainWindow
from    lib.core                    import  FILE_FILTER, __version__, DataFrameModel, Loader, LoadWorker, Pareto, Utils
from    lib.dialogs                 import  AboutDialog
from    lib.theme                   import  Theme
#?----------------------------------------------------------------------------------------------------------------------------------------
COMPACT_SIDEBAR_BELOW       = 900                                                      # window width (logical px) under which the sidebar shows icons only
#?----------------------------------------------------------------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    """The application window: wires the UI built by Ui_MainWindow to loading, analysis and export."""

    def __init__(self):
        super().__init__()
        self.settings       = QSettings("Gueni", "Anaxcel")
        self.ui             = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model          = DataFrameModel(self)
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.ui.tableView.setSortingEnabled(True)

        self._worker        = None
        self._loaded_files  = 0
        self._search_timer  = QTimer(self, singleShot=True, interval=200)
        self._search_timer.timeout.connect(self._apply_search)

        self._connect()
        self._restore_geometry()
        self.set_theme(self.settings.value("theme", "dark"))
        self.go_to(0)
        self._update_state()

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Wiring
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _connect(self):
        ui                  = self.ui
        ui.navGroup.idClicked.connect(self.go_to)
        for i, action in enumerate(ui.pageActions):
            action.triggered.connect(lambda _=False, i=i: self.go_to(i))
            self.addAction(action)

        for trigger in (ui.btnAdd.clicked, ui.actionAddFiles.triggered):
            trigger.connect(self.add_files_dialog)
        for trigger in (ui.btnRemove.clicked, ui.actionRemove.triggered, ui.fileList.deleteRequested):
            trigger.connect(self.remove_selected)
        for trigger in (ui.btnClear.clicked, ui.actionClear.triggered):
            trigger.connect(self.clear_all)
        for trigger in (ui.btnLoad.clicked, ui.actionLoad.triggered):
            trigger.connect(self.load_files)
        for trigger in (ui.btnAnalyse.clicked, ui.actionAnalyse.triggered):
            trigger.connect(self.analyse)
        for trigger in (ui.btnTheme.clicked, ui.actionToggleTheme.triggered):
            trigger.connect(self.toggle_theme)

        ui.actionSelectAll.triggered.connect(ui.fileList.selectAll)
        ui.actionExport.triggered.connect(self.export_data)
        ui.actionExit.triggered.connect(self.close)
        ui.actionAbout.triggered.connect(lambda: AboutDialog(self).exec_())

        ui.fileList.filesDropped.connect(self.add_files)
        ui.fileList.itemSelectionChanged.connect(self._update_state)
        ui.fileList.itemDoubleClicked.connect(lambda item: self.load_files([item]))
        ui.searchEdit.textChanged.connect(lambda _: self._search_timer.start())
        ui.categoryCombo.currentIndexChanged.connect(self._update_state)
        ui.valueCombo.currentIndexChanged.connect(self._update_state)

    def go_to(self, index: int):
        self.ui.stack.setCurrentIndex(index)
        self.ui.navButtons[index].setChecked(True)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Files
    #?------------------------------------------------------------------------------------------------------------------------------------
    def add_files_dialog(self):
        start               = self.settings.value("lastDir", os.path.expanduser("~"))
        paths, _            = QFileDialog.getOpenFileNames(self, "Add spreadsheets", start, FILE_FILTER)
        if paths:
            self.settings.setValue("lastDir", os.path.dirname(paths[0]))
            self.add_files(paths)

    def add_files(self, paths):
        file_list           = self.ui.fileList
        existing            = {file_list.item(i).data(Qt.UserRole) for i in range(file_list.count())}
        added = skipped     = 0
        for path in paths:
            path            = os.path.normpath(path)
            if not os.path.isfile(path) or not Utils.is_supported(path) or path in existing:
                skipped    += 1
                continue
            item            = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            file_list.addItem(item)
            existing.add(path)
            added          += 1
        message             = f"Added {added} file{'s' * (added != 1)}"
        if skipped:
            message        += f" · skipped {skipped} (duplicate or unsupported)"
        self.statusBar().showMessage(message, 5000)
        self.go_to(0)
        self._update_state()

    def remove_selected(self):
        file_list           = self.ui.fileList
        for item in file_list.selectedItems():
            file_list.takeItem(file_list.row(item))
        self._update_state()

    def clear_all(self):
        self.ui.fileList.clear()
        self.model.set_frame(self.model.frame.iloc[0:0, 0:0])
        self._loaded_files  = 0
        for combo in (self.ui.categoryCombo, self.ui.valueCombo):
            combo.clear()
        self.ui.searchEdit.clear()
        self.ui.dataSubtitle.setText("No data loaded yet.")
        self._show_result(None)
        self._update_state()

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Loading
    #?------------------------------------------------------------------------------------------------------------------------------------
    def load_files(self, items=None):
        if self._worker is not None:
            return
        file_list           = self.ui.fileList
        if not items:
            items           = file_list.selectedItems() or [file_list.item(i) for i in range(file_list.count())]
        paths               = [item.data(Qt.UserRole) for item in items]
        if not paths:
            self.statusBar().showMessage("Add some files first.", 4000)
            return

        self._worker        = LoadWorker(paths, self.ui.headerCheck.isChecked(), self)
        self._worker.progress.connect(self.ui.progress.setValue)
        self._worker.loaded.connect(self._on_loaded)
        self._worker.finished.connect(self._worker.deleteLater)
        self._loading_count = len(paths)
        self.ui.progress.setRange(0, len(paths))
        self.ui.progress.setValue(0)
        self.ui.progress.show()
        self.statusBar().showMessage(f"Loading {len(paths)} file{'s' * (len(paths) != 1)}…")
        QApplication.setOverrideCursor(Qt.BusyCursor)
        self._worker.start()
        self._update_state()

    def _on_loaded(self, df, errors):
        QApplication.restoreOverrideCursor()
        self.ui.progress.hide()
        self._worker        = None
        self.statusBar().clearMessage()
        if errors:
            QMessageBox.warning(self, "Some files could not be read",
                                "\n\n".join(errors[:8]) + ("\n\n…" if len(errors) > 8 else ""))
        if df.empty:
            self.statusBar().showMessage("No data found in the selected files.", 5000)
            self._update_state()
            return

        self.ui.searchEdit.blockSignals(True)
        self.ui.searchEdit.clear()
        self.ui.searchEdit.blockSignals(False)
        self.model.set_frame(df)
        self.ui.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.ui.tableView.resizeColumnsToContents()
        self._cap_column_widths()

        columns             = [str(c) for c in df.columns]
        category, value     = Loader.guess_columns(df)
        for combo, current in ((self.ui.categoryCombo, category), (self.ui.valueCombo, value)):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(columns)
            combo.setCurrentText(str(current))
            combo.blockSignals(False)

        self._loaded_files  = self._loading_count - len(errors)
        self._show_result(None)
        self._update_data_subtitle()
        self.go_to(1)
        self._update_state()

    def _cap_column_widths(self):
        table               = self.ui.tableView
        cap                 = max(160, table.viewport().width() // 3)
        for col in range(self.model.columnCount()):
            if table.columnWidth(col) > cap:
                table.setColumnWidth(col, cap)

    def _apply_search(self):
        self.model.set_filter(self.ui.searchEdit.text())
        self._update_data_subtitle()

    def _update_data_subtitle(self):
        total, shown, cols  = len(self.model.frame), self.model.rowCount(), self.model.columnCount()
        rows                = f"{total:,} rows" if shown == total else f"{shown:,} of {total:,} rows"
        files               = self._loaded_files
        self.ui.dataSubtitle.setText(f"{rows} × {cols} columns from {files} file{'s' * (files != 1)}.")

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Analysis
    #?------------------------------------------------------------------------------------------------------------------------------------
    def analyse(self):
        if self.model.frame.empty:
            return
        try:
            result          = Pareto.compute(self.model.frame, self.ui.categoryCombo.currentText(), self.ui.valueCombo.currentText())
        except (KeyError, ValueError) as exc:
            QMessageBox.warning(self, "Cannot analyse", str(exc).strip("'\""))
            return
        self._show_result(result)
        self.go_to(2)

    def _show_result(self, result):
        ui                  = self.ui
        ui.paretoChart.plot(result)
        ui.donutChart.plot(result)
        ui.paretoStack.setCurrentIndex(1 if result else 0)
        ui.donutStack.setCurrentIndex(1 if result else 0)
        if result is None:
            ui.paretoSubtitle.setText(ui.PARETO_SUBTITLE)
            ui.donutSubtitle.setText(ui.DONUT_SUBTITLE)
            return
        n                   = len(result.labels)
        summary             = (f"{result.vital_few} of {n} categor{'ies' if n != 1 else 'y'} make up 80 % "
                               f"of the total {result.value} ({result.total:,.6g}).")
        notes               = []
        if result.skipped_rows:
            notes.append(f"{result.skipped_rows:,} rows skipped (empty or non-numeric)")
        if result.dropped_categories:
            notes.append(f"{result.dropped_categories} categories ≤ 0 left out")
        ui.paretoSubtitle.setText(summary + ("  ·  " + "; ".join(notes) if notes else ""))
        ui.donutSubtitle.setText(f"Share of the total {result.value} per {result.category}. Hover a slice for details.")

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Export
    #?------------------------------------------------------------------------------------------------------------------------------------
    def export_data(self):
        if self.model.frame.empty:
            return
        start               = os.path.join(self.settings.value("lastDir", os.path.expanduser("~")), "combined.xlsx")
        path, chosen        = QFileDialog.getSaveFileName(self, "Export data", start, "Excel workbook (*.xlsx);;CSV file (*.csv)")
        if not path:
            return
        frame               = self.model.visible_frame()
        try:
            if path.lower().endswith(".csv") or (chosen.startswith("CSV") and not path.lower().endswith(".xlsx")):
                path        = path if path.lower().endswith(".csv") else path + ".csv"
                frame.to_csv(path, index=False)
            else:
                path        = path if path.lower().endswith(".xlsx") else path + ".xlsx"
                frame.to_excel(path, index=False)
        except Exception as exc:
            QMessageBox.warning(self, "Export failed", str(exc))
            return
        self.statusBar().showMessage(f"Exported {len(frame):,} rows to {path}", 6000)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? State and theme
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _update_state(self):
        ui                  = self.ui
        count               = ui.fileList.count()
        selected            = len(ui.fileList.selectedItems())
        loading             = self._worker is not None
        has_data            = not self.model.frame.empty
        can_analyse         = has_data and ui.categoryCombo.count() > 0 and not loading

        for widget in (ui.btnRemove, ui.actionRemove):
            widget.setEnabled(selected > 0 and not loading)
        for widget in (ui.btnClear, ui.actionClear):
            widget.setEnabled((count > 0 or has_data) and not loading)
        for widget in (ui.btnLoad, ui.actionLoad):
            widget.setEnabled(count > 0 and not loading)
        for widget in (ui.btnAnalyse, ui.actionAnalyse):
            widget.setEnabled(can_analyse)
        ui.actionSelectAll.setEnabled(count > 0)
        ui.actionExport.setEnabled(has_data)
        ui.searchEdit.setEnabled(has_data)
        ui.btnLoad.setText(f"Load {selected} selected  →" if selected else "Load all  →")
        ui.fileCountLabel.setText(f"{count} file{'s' * (count != 1)}" + (f" · {selected} selected" if selected else ""))
        ui.statusInfo.setText(f"{len(self.model.frame):,} rows loaded" if has_data else "")

    def set_theme(self, name: str):
        palette             = Theme.apply(QApplication.instance(), name)
        self._theme         = palette["name"]
        self.ui.set_theme_label(self._theme == "dark")
        self.ui.paretoChart.set_palette(palette)
        self.ui.donutChart.set_palette(palette)

    def toggle_theme(self):
        self.set_theme("light" if self._theme == "dark" else "dark")

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Window
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _restore_geometry(self):
        screen              = (self.screen() if hasattr(self, "screen") else QGuiApplication.primaryScreen()).availableGeometry()
        min_w, min_h        = min(680, screen.width()), min(460, screen.height())
        self.setMinimumSize(min_w, min_h)
        geometry            = self.settings.value("geometry")
        if geometry is not None and self.restoreGeometry(geometry):
            return
        self.resize(max(min_w, int(screen.width() * 0.8)), max(min_h, int(screen.height() * 0.82)))
        self.move(screen.center() - self.rect().center())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.ui.set_sidebar_compact(self.width() < COMPACT_SIDEBAR_BELOW)

    def closeEvent(self, event):
        if not self.model.frame.empty:
            answer          = QMessageBox.question(self, "Quit Anaxcel", "Close Anaxcel? Loaded data will be discarded.",
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if answer != QMessageBox.Yes:
                event.ignore()
                return
        if self._worker is not None:
            self._worker.wait(5000)
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("theme", self._theme)
        event.accept()
#?----------------------------------------------------------------------------------------------------------------------------------------
class App:
    """Application setup and start-up."""

    @staticmethod
    def _enable_high_dpi():
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        if hasattr(QGuiApplication, "setHighDpiScaleFactorRoundingPolicy"):
            QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        if sys.platform == "win32":                                                    # own taskbar icon instead of python.exe's
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Gueni.Anaxcel")
            except Exception:
                pass

    @staticmethod
    def run():
        """Create the application, show the splash screen, then the main window (files given on the command line are added)."""
        App._enable_high_dpi()
        app                 = QApplication(sys.argv)
        app.setApplicationName("Anaxcel")
        app.setOrganizationName("Gueni")
        app.setApplicationVersion(__version__)
        app.setStyle("Fusion")
        app.setWindowIcon(QIcon(Utils.resource_path("icons", "icon.png")))
        if sys.platform == "win32":
            app.setFont(QFont("Segoe UI", 10))

        splash_pix          = QPixmap(Utils.resource_path("icons", "splash.png"))
        splash              = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        if splash_pix.hasAlphaChannel():
            splash.setMask(splash_pix.mask())
        splash.show()
        app.processEvents()

        window              = MainWindow()
        files               = [arg for arg in sys.argv[1:] if os.path.isfile(arg)]
        if files:
            window.add_files(files)

        def reveal():
            window.show()
            splash.finish(window)

        QTimer.singleShot(700, reveal)
        sys.exit(app.exec_())
#?----------------------------------------------------------------------------------------------------------------------------------------
