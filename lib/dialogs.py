#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                 ___       __
#?            ____/ (_)___ _/ /___  ____ ______
#?           / __  / / __ `/ / __ \/ __ `/ ___/
#?          / /_/ / / /_/ / / /_/ / /_/ (__  )
#?          \__,_/_/\__,_/_/\____/\__, /____/
#?                               /____/
#?
#? Name:        dialogs.py
#? Purpose:     About dialog.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     11/11/2025
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    PyQt5.QtCore                import  Qt
from    PyQt5.QtGui                 import  QPixmap
from    PyQt5.QtWidgets             import  QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from    lib.core                    import  __version__, Utils
#?----------------------------------------------------------------------------------------------------------------------------------------
class AboutDialog(QDialog):
    """Picture, version and credits."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("About Anaxcel")
        layout              = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 20)
        layout.setSpacing(8)

        picture             = QLabel(alignment=Qt.AlignCenter)
        pixmap              = QPixmap(Utils.resource_path("icons", "aboutpic.png"))
        if not pixmap.isNull():
            picture.setPixmap(pixmap.scaledToWidth(min(200, pixmap.width()), Qt.SmoothTransformation))
        layout.addWidget(picture)

        title               = QLabel("Anaxcel", objectName="pageTitle", alignment=Qt.AlignCenter)
        version             = QLabel(f"Version {__version__}", objectName="pageSubtitle", alignment=Qt.AlignCenter)
        description         = QLabel("Combine Excel files and explore them with Pareto and donut charts.",
                                     alignment=Qt.AlignCenter, wordWrap=True)
        links               = QLabel('Built with <a href="https://www.qt.io/">Qt</a>.'
                                     '<br>Author: <a href="https://github.com/Gueni/">Mohamed Gueni</a>',
                                     objectName="muted", alignment=Qt.AlignCenter, wordWrap=True)
        links.setTextFormat(Qt.RichText)
        links.setOpenExternalLinks(True)
        for widget in (title, version):
            layout.addWidget(widget)
        layout.addSpacing(8)
        layout.addWidget(description)
        layout.addWidget(links)
        layout.addSpacing(12)

        buttons             = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setMinimumWidth(self.fontMetrics().averageCharWidth() * 56)
#?----------------------------------------------------------------------------------------------------------------------------------------
