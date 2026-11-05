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
#? Purpose:     About and License dialogs.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     11/11/2025
#? Licence:     Refer to the LICENSE file
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    PyQt5.QtCore                import  Qt
from    PyQt5.QtGui                 import  QPixmap
from    PyQt5.QtWidgets             import  QDialog, QDialogButtonBox, QLabel, QTextBrowser, QVBoxLayout

from    lib.core                    import  __version__, Utils
#?----------------------------------------------------------------------------------------------------------------------------------------
LICENSE_HTML                = """
<h3>GNU General Public License v2</h3>
<p>This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 2 of the
License, or (at your option) any later version.</p>
<p>This program is distributed in the hope that it will be useful, but <b>WITHOUT ANY WARRANTY</b>;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.</p>
<p>You should have received a copy of the GNU General Public License along with this program.
If not, see <a href="https://www.gnu.org/licenses/">https://www.gnu.org/licenses/</a>.</p>
"""
#?----------------------------------------------------------------------------------------------------------------------------------------
class LicenseDialog(QDialog):
    """GPLv2 notice in a scrollable browser."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("License")
        layout              = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(14)
        text                = QTextBrowser()
        text.setOpenExternalLinks(True)
        text.setHtml(LICENSE_HTML)
        layout.addWidget(text, 1)
        buttons             = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        fm                  = self.fontMetrics()
        self.resize(fm.averageCharWidth() * 72, fm.height() * 22)
#?----------------------------------------------------------------------------------------------------------------------------------------
class AboutDialog(QDialog):
    """Picture, version, credits and a button to the license."""

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
        links               = QLabel('Uses libraries from the <a href="https://www.qt.io/">Qt</a> project under the GPLv2 license.'
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
        license_button      = buttons.addButton("License", QDialogButtonBox.ActionRole)
        license_button.clicked.connect(lambda: LicenseDialog(self).exec_())
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setMinimumWidth(self.fontMetrics().averageCharWidth() * 56)
#?----------------------------------------------------------------------------------------------------------------------------------------
