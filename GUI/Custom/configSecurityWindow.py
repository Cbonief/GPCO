# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'configSecurityWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets


class Ui_ConfigSecurityWindow(object):
    def setupUi(self, ConfigSecurityWindow):
        ConfigSecurityWindow.setObjectName("ConfigSecurityWindow")
        ConfigSecurityWindow.resize(324, 430)
        self.centralwidget = QtWidgets.QWidget(ConfigSecurityWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_8.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_Vin = QtWidgets.QLabel(self.centralwidget)
        self.label_Vin.setObjectName("label_Vin")
        self.horizontalLayout.addWidget(self.label_Vin)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.input_fvcmax = QtWidgets.QLineEdit(self.centralwidget)
        self.input_fvcmax.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_fvcmax.setObjectName("input_fvcmax")
        self.horizontalLayout.addWidget(self.input_fvcmax)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_Vo = QtWidgets.QLabel(self.centralwidget)
        self.label_Vo.setObjectName("label_Vo")
        self.horizontalLayout_2.addWidget(self.label_Vo)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.input_fvdmax = QtWidgets.QLineEdit(self.centralwidget)
        self.input_fvdmax.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_fvdmax.setObjectName("input_fvdmax")
        self.horizontalLayout_2.addWidget(self.input_fvdmax)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_Vin_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_Vin_2.setObjectName("label_Vin_2")
        self.horizontalLayout_12.addWidget(self.label_Vin_2)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem5)
        self.input_fvsmax = QtWidgets.QLineEdit(self.centralwidget)
        self.input_fvsmax.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_fvsmax.setObjectName("input_fvsmax")
        self.horizontalLayout_12.addWidget(self.input_fvsmax)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_Vo_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_Vo_2.setObjectName("label_Vo_2")
        self.horizontalLayout_3.addWidget(self.label_Vo_2)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.input_ficmax = QtWidgets.QLineEdit(self.centralwidget)
        self.input_ficmax.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_ficmax.setObjectName("input_ficmax")
        self.horizontalLayout_3.addWidget(self.input_ficmax)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_DeltaIin = QtWidgets.QLabel(self.centralwidget)
        self.label_DeltaIin.setObjectName("label_DeltaIin")
        self.horizontalLayout_4.addWidget(self.label_DeltaIin)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.input_fidmax = QtWidgets.QLineEdit(self.centralwidget)
        self.input_fidmax.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_fidmax.setObjectName("input_fidmax")
        self.horizontalLayout_4.addWidget(self.input_fidmax)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_Vin_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_Vin_3.setObjectName("label_Vin_3")
        self.horizontalLayout_13.addWidget(self.label_Vin_3)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem8)
        self.input_ismax = QtWidgets.QLineEdit(self.centralwidget)
        self.input_ismax.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_ismax.setObjectName("input_ismax")
        self.horizontalLayout_13.addWidget(self.input_ismax)
        self.verticalLayout.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_DeltaVo = QtWidgets.QLabel(self.centralwidget)
        self.label_DeltaVo.setObjectName("label_DeltaVo")
        self.horizontalLayout_5.addWidget(self.label_DeltaVo)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem9)
        self.input_futrafo = QtWidgets.QLineEdit(self.centralwidget)
        self.input_futrafo.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_futrafo.setObjectName("input_futrafo")
        self.horizontalLayout_5.addWidget(self.input_futrafo)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_JMax = QtWidgets.QLabel(self.centralwidget)
        self.label_JMax.setObjectName("label_JMax")
        self.horizontalLayout_6.addWidget(self.label_JMax)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem10)
        self.input_fuLi = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_fuLi.sizePolicy().hasHeightForWidth())
        self.input_fuLi.setSizePolicy(sizePolicy)
        self.input_fuLi.setMinimumSize(QtCore.QSize(20, 20))
        self.input_fuLi.setMaximumSize(QtCore.QSize(60, 20))
        self.input_fuLi.setObjectName("input_fuLi")
        self.horizontalLayout_6.addWidget(self.input_fuLi)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_DeltaVo_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_DeltaVo_2.setObjectName("label_DeltaVo_2")
        self.horizontalLayout_7.addWidget(self.label_DeltaVo_2)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem11)
        self.input_fuLk = QtWidgets.QLineEdit(self.centralwidget)
        self.input_fuLk.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_fuLk.setObjectName("input_fuLk")
        self.horizontalLayout_7.addWidget(self.input_fuLk)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_DeltaVo_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_DeltaVo_3.setObjectName("label_DeltaVo_3")
        self.horizontalLayout_10.addWidget(self.label_DeltaVo_3)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem12)
        self.input_Jmax = QtWidgets.QLineEdit(self.centralwidget)
        self.input_Jmax.setMaximumSize(QtCore.QSize(60, 16777215))
        self.input_Jmax.setObjectName("input_Jmax")
        self.horizontalLayout_10.addWidget(self.input_Jmax)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        spacerItem13 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem13)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem14)
        self.save_configurations_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_configurations_button.setObjectName("save_configurations_button")
        self.horizontalLayout_11.addWidget(self.save_configurations_button)
        spacerItem15 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem15)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_9.addLayout(self.verticalLayout)
        ConfigSecurityWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ConfigSecurityWindow)
        self.statusbar.setObjectName("statusbar")
        ConfigSecurityWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ConfigSecurityWindow)
        QtCore.QMetaObject.connectSlotsByName(ConfigSecurityWindow)

    def retranslateUi(self, ConfigSecurityWindow):
        _translate = QtCore.QCoreApplication.translate
        ConfigSecurityWindow.setWindowTitle(_translate("ConfigSecurityWindow", "MainWindow"))
        self.label.setText(_translate("ConfigSecurityWindow",
                                      "<html><head/><body><p><span style=\" font-size:12pt;\">Configurações de Seguraça</span></p></body></html>"))
        self.label_Vin.setText(_translate("ConfigSecurityWindow", "Fator VcMáx"))
        self.label_Vo.setText(_translate("ConfigSecurityWindow", "Fator VdMáx"))
        self.label_Vin_2.setText(_translate("ConfigSecurityWindow", "Fator VcMáx"))
        self.label_Vo_2.setText(_translate("ConfigSecurityWindow", "Fator Icef Máx"))
        self.label_DeltaIin.setText(_translate("ConfigSecurityWindow", "Fator Idef Máx"))
        self.label_Vin_3.setText(_translate("ConfigSecurityWindow", "Fator IsMáx"))
        self.label_DeltaVo.setText(_translate("ConfigSecurityWindow", "Fu transformador"))
        self.label_JMax.setText(_translate("ConfigSecurityWindow", "Fu indutor de entrada"))
        self.label_DeltaVo_2.setText(_translate("ConfigSecurityWindow", "Fu indutor auxiliar"))
        self.label_DeltaVo_3.setText(_translate("ConfigSecurityWindow", "Jmax"))
        self.save_configurations_button.setText(_translate("ConfigSecurityWindow", "Salvar"))