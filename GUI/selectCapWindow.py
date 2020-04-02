# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectCapWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_selectCapWindow(object):
    def setupUi(self, selectCapWindow):
        selectCapWindow.setObjectName("selectCapWindow")
        selectCapWindow.resize(411, 478)
        self.centralwidget = QtWidgets.QWidget(selectCapWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.list_selected = QtWidgets.QListView(self.centralwidget)
        self.list_selected.setGeometry(QtCore.QRect(210, 90, 181, 192))
        self.list_selected.setObjectName("list_selected")
        self.search_button = QtWidgets.QPushButton(self.centralwidget)
        self.search_button.setGeometry(QtCore.QRect(140, 60, 61, 23))
        self.search_button.setObjectName("search_button")
        self.list_available = QtWidgets.QListView(self.centralwidget)
        self.list_available.setGeometry(QtCore.QRect(20, 90, 181, 192))
        self.list_available.setObjectName("list_available")
        self.add_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_button.setGeometry(QtCore.QRect(140, 290, 61, 23))
        self.add_button.setObjectName("add_button")
        self.remove_button = QtWidgets.QPushButton(self.centralwidget)
        self.remove_button.setGeometry(QtCore.QRect(210, 290, 61, 23))
        self.remove_button.setObjectName("remove_button")
        self.search_input = QtWidgets.QLineEdit(self.centralwidget)
        self.search_input.setGeometry(QtCore.QRect(20, 60, 113, 20))
        self.search_input.setObjectName("search_input")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(240, 60, 121, 16))
        self.label.setObjectName("label")
        selectCapWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(selectCapWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 411, 21))
        self.menubar.setObjectName("menubar")
        selectCapWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(selectCapWindow)
        self.statusbar.setObjectName("statusbar")
        selectCapWindow.setStatusBar(self.statusbar)

        self.retranslateUi(selectCapWindow)
        QtCore.QMetaObject.connectSlotsByName(selectCapWindow)

    def retranslateUi(self, selectCapWindow):
        _translate = QtCore.QCoreApplication.translate
        selectCapWindow.setWindowTitle(_translate("selectCapWindow", "MainWindow"))
        self.search_button.setText(_translate("selectCapWindow", "Pesquisar"))
        self.add_button.setText(_translate("selectCapWindow", "Adicionar"))
        self.remove_button.setText(_translate("selectCapWindow", "Remover"))
        self.label.setText(_translate("selectCapWindow", "Capacitores Selecionados"))
