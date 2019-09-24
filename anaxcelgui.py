from PyQt5 import QtCore, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class ComboBoxNEW(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBoxNEW, self).showPopup()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(888, 595)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 0, 871, 551))
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setTabsClosable(False)
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.listWidget = QtWidgets.QListWidget(self.tab)
        self.listWidget.setGeometry(QtCore.QRect(50, 50, 531, 411))
        self.listWidget.setObjectName("listWidget")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(20, 30, 591, 451))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setGeometry(QtCore.QRect(630, 30, 161, 441))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.pushButtonbrowse = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButtonbrowse.setGeometry(QtCore.QRect(20, 20, 131, 61))
        self.pushButtonbrowse.setObjectName("pushButtonbrowse")
        self.pushButtonclear = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButtonclear.setGeometry(QtCore.QRect(20, 100, 131, 61))
        self.pushButtonclear.setObjectName("pushButtonclear")
        self.pushButtonselall = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButtonselall.setGeometry(QtCore.QRect(20, 180, 131, 61))
        self.pushButtonselall.setObjectName("pushButtonselall")
        self.pushButtonload = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButtonload.setGeometry(QtCore.QRect(20, 260, 131, 61))
        self.pushButtonload.setObjectName("pushButtonload")
        self.comboBoxfiletype = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBoxfiletype.setGeometry(QtCore.QRect(20, 331, 131, 22))
        self.comboBoxfiletype.setObjectName("comboBoxfiletype")
        self.groupBox_2.raise_()
        self.groupBox.raise_()
        self.listWidget.raise_()
        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tableWidget = QtWidgets.QTableWidget(self.tab_2)
        self.tableWidget.setGeometry(QtCore.QRect(0, 50, 861, 471))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.labelicon = QtWidgets.QLabel(self.tab_2)
        self.labelicon.setGeometry(QtCore.QRect(10, 6, 50, 30))
        self.labelicon.setObjectName("labelicon")

        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(70, 6, 150, 30))
        self.label.setObjectName("label")

        self.labelx = QtWidgets.QLabel(self.tab_2)
        self.labelx.setGeometry(QtCore.QRect(200, 6, 20, 30))
        self.labelx.setObjectName("labelx")

        self.labely = QtWidgets.QLabel(self.tab_2)
        self.labely.setGeometry(QtCore.QRect(350, 6, 20, 30))
        self.labely.setObjectName("labely")

        self.comboBoxabsc = ComboBoxNEW(self.tab_2)
        self.comboBoxabsc.setGeometry(QtCore.QRect(230, 6, 100, 30))
        self.comboBoxabsc.setObjectName("comboBoxabsc")

        self.comboBoxordo = ComboBoxNEW(self.tab_2)
        self.comboBoxordo.setGeometry(QtCore.QRect(370, 6, 100, 30))
        self.comboBoxordo.setObjectName("comboBoxordo")

        self.pushButton_5 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_5.setGeometry(QtCore.QRect(690, 10, 161, 31))
        self.pushButton_5.setObjectName("pushButton_5")
        self.tabWidget.addTab(self.tab_2, "")

        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.tabWidget.addTab(self.tab_6, "")

        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 888, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAdd_File = QtWidgets.QAction(MainWindow)
        self.actionAdd_File.setObjectName("actionAdd_File")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionClear = QtWidgets.QAction(MainWindow)
        self.actionClear.setObjectName("actionClear")
        self.actionSelect_All = QtWidgets.QAction(MainWindow)
        self.actionSelect_All.setObjectName("actionSelect_All")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuFile.addAction(self.actionAdd_File)
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionClear)
        self.menuEdit.addAction(self.actionSelect_All)
        self.menuEdit.addAction(self.actionLoad)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", " Anaxcel "))
        self.pushButtonbrowse.setText(_translate("MainWindow", "..."))
        self.pushButtonclear.setText(_translate("MainWindow", "Clear"))
        self.pushButtonselall.setText(_translate("MainWindow", "Select All"))
        self.pushButtonload.setText(_translate("MainWindow", "Load"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "        Home        "))
        self.label.setText(_translate("MainWindow", "TextLabel"))
        self.labelx.setText(_translate("MainWindow", "X"))
        self.labely.setText(_translate("MainWindow", "Y"))
        self.labelicon.setText(_translate("MainWindow", ""))
        self.pushButton_5.setText(_translate("MainWindow", "Analyse"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "        Data        "))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4),
                                  _translate("MainWindow", "        Donut        "))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6),
                                  _translate("MainWindow", "        Pareto Chart        "))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAdd_File.setText(_translate("MainWindow", "Add File"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionClear.setText(_translate("MainWindow", "Clear"))
        self.actionSelect_All.setText(_translate("MainWindow", "Select All"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
