# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '2kgui.ui'
#
# Created: Mon Apr 13 12:51:24 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1276, 700)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_4 = QtGui.QSplitter(self.centralwidget)
        self.splitter_4.setOrientation(QtCore.Qt.Vertical)
        self.splitter_4.setObjectName("splitter_4")
        self.splitter_2 = QtGui.QSplitter(self.splitter_4)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.tabWidget = QtGui.QTabWidget(self.splitter_2)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tab.setObjectName("tab")
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.splitter_4, 0, 1, 1, 1)
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setLineWidth(1)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.groupBox_2 = QtGui.QGroupBox(self.splitter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.archiveTabs = QtGui.QTabWidget(self.groupBox_2)
        self.archiveTabs.setMinimumSize(QtCore.QSize(0, 264))
        self.archiveTabs.setTabPosition(QtGui.QTabWidget.North)
        self.archiveTabs.setTabShape(QtGui.QTabWidget.Rounded)
        self.archiveTabs.setObjectName("archiveTabs")
        self.verticalLayout_5.addWidget(self.archiveTabs)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.searchLabel = QtGui.QLabel(self.groupBox_2)
        self.searchLabel.setObjectName("searchLabel")
        self.horizontalLayout.addWidget(self.searchLabel)
        self.searchBar = QtGui.QLineEdit(self.groupBox_2)
        self.searchBar.setObjectName("searchBar")
        self.horizontalLayout.addWidget(self.searchBar)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.groupBox = QtGui.QGroupBox(self.splitter)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.treeView_2 = QtGui.QTreeView(self.groupBox)
        self.treeView_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_2.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
        self.treeView_2.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        self.treeView_2.setUniformRowHeights(True)
        self.treeView_2.setObjectName("treeView_2")
        self.verticalLayout_3.addWidget(self.treeView_2)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1276, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setStatusTip("")
        self.statusBar.setSizeGripEnabled(True)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionPreferences = QtGui.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionApply_Changes = QtGui.QAction(MainWindow)
        self.actionApply_Changes.setObjectName("actionApply_Changes")
        self.actionSave_Comments = QtGui.QAction(MainWindow)
        self.actionSave_Comments.setObjectName("actionSave_Comments")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionApply_Changes)
        self.menuFile.addAction(self.actionExit)
        self.menuOptions.addAction(self.actionPreferences)
        self.menuOptions.addAction(self.actionSave_Comments)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.archiveTabs.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.archiveTabs, self.searchBar)
        MainWindow.setTabOrder(self.searchBar, self.treeView_2)
        MainWindow.setTabOrder(self.treeView_2, self.tabWidget)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate(
            "MainWindow", "NBA 2K16 Explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate(
            "MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate(
            "MainWindow", "2K Archives List", None, QtGui.QApplication.UnicodeUTF8))
        self.searchLabel.setText(QtGui.QApplication.translate(
            "MainWindow", "Search:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate(
            "MainWindow", "Archive Contents", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate(
            "MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOptions.setTitle(QtGui.QApplication.translate(
            "MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate(
            "MainWindow", "Load Archives", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate(
            "MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate(
            "MainWindow", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionApply_Changes.setText(QtGui.QApplication.translate(
            "MainWindow", "Apply Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Comments.setText(QtGui.QApplication.translate(
            "MainWindow", "Save Comments", None, QtGui.QApplication.UnicodeUTF8))
