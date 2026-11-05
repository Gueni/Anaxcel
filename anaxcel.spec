# -*- mode: python ; coding: utf-8 -*-
# PyInstaller build of Anaxcel (one-folder, windowed).  Run:  .venv\Scripts\pyinstaller anaxcel.spec --noconfirm
import os

ROOT = SPECPATH

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    datas=[(os.path.join(ROOT, "assets", "icons"), os.path.join("assets", "icons"))],
    hiddenimports=["openpyxl", "xlrd", "matplotlib.backends.backend_qt5agg"],
    excludes=["tkinter", "pytest", "IPython", "PyQt5.QtWebEngineWidgets", "PyQt5.QtWebEngineCore",
              "PyQt5.QtQml", "PyQt5.QtQuick", "PyQt5.QtMultimedia", "PyQt5.QtBluetooth", "PyQt5.QtSql"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Anaxcel",
    console=False,
    icon=os.path.join(ROOT, "assets", "icons", "icon_iEd_1.ico"),
    version=os.path.join(ROOT, "installer", "version_info.txt"),
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="Anaxcel", upx=False)
