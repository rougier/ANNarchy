# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ANNarchyEditor.ui'
#
# Created: Mon Jan 27 22:44:07 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ANNarchyEditor(object):
    def setupUi(self, ANNarchyEditor):
        ANNarchyEditor.setObjectName(_fromUtf8("ANNarchyEditor"))
        ANNarchyEditor.resize(1201, 624)
        ANNarchyEditor.setMinimumSize(QtCore.QSize(800, 600))
        self.centralwidget = QtGui.QWidget(ANNarchyEditor)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.splitter_2 = QtGui.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setMinimumSize(QtCore.QSize(0, 0))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.views = QtGui.QTabWidget(self.splitter)
        self.views.setObjectName(_fromUtf8("views"))
        self.objects = QtGui.QWidget()
        self.objects.setObjectName(_fromUtf8("objects"))
        self.views.addTab(self.objects, _fromUtf8(""))
        self.editor = QtGui.QWidget()
        self.editor.setMinimumSize(QtCore.QSize(0, 0))
        self.editor.setWhatsThis(_fromUtf8(""))
        self.editor.setObjectName(_fromUtf8("editor"))
        self.views.addTab(self.editor, _fromUtf8(""))
        self.environment = QtGui.QWidget()
        self.environment.setObjectName(_fromUtf8("environment"))
        self.views.addTab(self.environment, _fromUtf8(""))
        self.params = QtGui.QWidget()
        self.params.setObjectName(_fromUtf8("params"))
        self.views.addTab(self.params, _fromUtf8(""))
        self.visualizer = QtGui.QWidget()
        self.visualizer.setObjectName(_fromUtf8("visualizer"))
        self.views.addTab(self.visualizer, _fromUtf8(""))
        self.complete = QtGui.QWidget()
        self.complete.setObjectName(_fromUtf8("complete"))
        self.views.addTab(self.complete, _fromUtf8(""))
        self.special = QtGui.QStackedWidget(self.splitter)
        self.special.setMaximumSize(QtCore.QSize(16777215, 10))
        self.special.setObjectName(_fromUtf8("special"))
        self.propertiesPage1 = QtGui.QWidget()
        self.propertiesPage1.setObjectName(_fromUtf8("propertiesPage1"))
        self.special.addWidget(self.propertiesPage1)
        self.general = QtGui.QStackedWidget(self.splitter_2)
        self.general.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.general.setObjectName(_fromUtf8("general"))
        self.obj_tab = QtGui.QWidget()
        self.obj_tab.setObjectName(_fromUtf8("obj_tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.obj_tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_9 = QtGui.QLabel(self.obj_tab)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout.addWidget(self.label_9)
        self.neur_general = QtGui.QListView(self.obj_tab)
        self.neur_general.setObjectName(_fromUtf8("neur_general"))
        self.verticalLayout.addWidget(self.neur_general)
        self.label_8 = QtGui.QLabel(self.obj_tab)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout.addWidget(self.label_8)
        self.syn_general = QtGui.QListView(self.obj_tab)
        self.syn_general.setObjectName(_fromUtf8("syn_general"))
        self.verticalLayout.addWidget(self.syn_general)
        self.general.addWidget(self.obj_tab)
        self.net_tab = QtGui.QWidget()
        self.net_tab.setObjectName(_fromUtf8("net_tab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.net_tab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_5 = QtGui.QLabel(self.net_tab)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_4.addWidget(self.label_5)
        self.pop_general = QtGui.QListView(self.net_tab)
        self.pop_general.setObjectName(_fromUtf8("pop_general"))
        self.verticalLayout_4.addWidget(self.pop_general)
        self.label_6 = QtGui.QLabel(self.net_tab)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_4.addWidget(self.label_6)
        self.proj_general = QtGui.QListView(self.net_tab)
        self.proj_general.setObjectName(_fromUtf8("proj_general"))
        self.verticalLayout_4.addWidget(self.proj_general)
        self.general.addWidget(self.net_tab)
        self.env_tab = QtGui.QWidget()
        self.env_tab.setObjectName(_fromUtf8("env_tab"))
        self.general.addWidget(self.env_tab)
        self.par_tab = QtGui.QWidget()
        self.par_tab.setObjectName(_fromUtf8("par_tab"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.par_tab)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_7 = QtGui.QLabel(self.par_tab)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_5.addWidget(self.label_7)
        self.par_general = QtGui.QListView(self.par_tab)
        self.par_general.setObjectName(_fromUtf8("par_general"))
        self.verticalLayout_5.addWidget(self.par_general)
        self.general.addWidget(self.par_tab)
        self.vis_tab = QtGui.QWidget()
        self.vis_tab.setObjectName(_fromUtf8("vis_tab"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.vis_tab)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.groupBox = QtGui.QGroupBox(self.vis_tab)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.grid_x_dim = QtGui.QLineEdit(self.groupBox)
        self.grid_x_dim.setObjectName(_fromUtf8("grid_x_dim"))
        self.horizontalLayout_2.addWidget(self.grid_x_dim)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_3.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.grid_y_dim = QtGui.QLineEdit(self.groupBox)
        self.grid_y_dim.setObjectName(_fromUtf8("grid_y_dim"))
        self.horizontalLayout_3.addWidget(self.grid_y_dim)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.change_grid = QtGui.QPushButton(self.groupBox)
        self.change_grid.setObjectName(_fromUtf8("change_grid"))
        self.verticalLayout_2.addWidget(self.change_grid)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_8.addWidget(self.groupBox)
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_3 = QtGui.QLabel(self.vis_tab)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_4.addWidget(self.label_3)
        self.comboBox = QtGui.QComboBox(self.vis_tab)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.horizontalLayout_4.addWidget(self.comboBox)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        self.stackedWidget = QtGui.QStackedWidget(self.vis_tab)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName(_fromUtf8("page_3"))
        self.stackedWidget.addWidget(self.page_3)
        self.verticalLayout_7.addWidget(self.stackedWidget)
        self.verticalLayout_8.addLayout(self.verticalLayout_7)
        spacerItem3 = QtGui.QSpacerItem(20, 174, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem3)
        self.general.addWidget(self.vis_tab)
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.page)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.compile_3 = QtGui.QPushButton(self.page)
        self.compile_3.setObjectName(_fromUtf8("compile_3"))
        self.verticalLayout_6.addWidget(self.compile_3)
        self.general.addWidget(self.page)
        self.horizontalLayout.addWidget(self.splitter_2)
        ANNarchyEditor.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ANNarchyEditor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1201, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        ANNarchyEditor.setMenuBar(self.menubar)
        self.actionOpen = QtGui.QAction(ANNarchyEditor)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionQuit = QtGui.QAction(ANNarchyEditor)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(ANNarchyEditor)
        self.views.setCurrentIndex(5)
        self.general.setCurrentIndex(5)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL(_fromUtf8("triggered()")), ANNarchyEditor.close)
        QtCore.QObject.connect(self.compile_3, QtCore.SIGNAL(_fromUtf8("pressed()")), ANNarchyEditor.compile)
        QtCore.QMetaObject.connectSlotsByName(ANNarchyEditor)

    def retranslateUi(self, ANNarchyEditor):
        ANNarchyEditor.setWindowTitle(QtGui.QApplication.translate("ANNarchyEditor", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.views.setTabText(self.views.indexOf(self.objects), QtGui.QApplication.translate("ANNarchyEditor", "Neuron / Synapses", None, QtGui.QApplication.UnicodeUTF8))
        self.views.setTabText(self.views.indexOf(self.editor), QtGui.QApplication.translate("ANNarchyEditor", "Network", None, QtGui.QApplication.UnicodeUTF8))
        self.views.setTabText(self.views.indexOf(self.environment), QtGui.QApplication.translate("ANNarchyEditor", "Environment", None, QtGui.QApplication.UnicodeUTF8))
        self.views.setTabText(self.views.indexOf(self.params), QtGui.QApplication.translate("ANNarchyEditor", "Parameter", None, QtGui.QApplication.UnicodeUTF8))
        self.views.setTabText(self.views.indexOf(self.visualizer), QtGui.QApplication.translate("ANNarchyEditor", "Visualizer", None, QtGui.QApplication.UnicodeUTF8))
        self.views.setTabText(self.views.indexOf(self.complete), QtGui.QApplication.translate("ANNarchyEditor", "CompleteScript", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("ANNarchyEditor", "Neurons", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("ANNarchyEditor", "Synapses", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ANNarchyEditor", "Populations", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("ANNarchyEditor", "Projections", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("ANNarchyEditor", "Loaded file(s):", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ANNarchyEditor", "Grid configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ANNarchyEditor", "x size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ANNarchyEditor", "y size", None, QtGui.QApplication.UnicodeUTF8))
        self.change_grid.setText(QtGui.QApplication.translate("ANNarchyEditor", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ANNarchyEditor", "Plot Type", None, QtGui.QApplication.UnicodeUTF8))
        self.compile_3.setText(QtGui.QApplication.translate("ANNarchyEditor", "Compile and Run", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("ANNarchyEditor", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("ANNarchyEditor", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setToolTip(QtGui.QApplication.translate("ANNarchyEditor", "Open a scrip", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setShortcut(QtGui.QApplication.translate("ANNarchyEditor", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("ANNarchyEditor", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setShortcut(QtGui.QApplication.translate("ANNarchyEditor", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))

