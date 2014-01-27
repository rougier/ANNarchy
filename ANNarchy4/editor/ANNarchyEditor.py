import sys
import os

from PyQt4.QtGui import QApplication, QMainWindow, QMessageBox
from PyQt4 import QtCore

# generated by pyuic4
from ui_ANNarchyEditor import Ui_ANNarchyEditor 

# buisness logic
from CodeView import CodeView
from ListView import ListView 
from GLWidget import NetworkGLWidget, VisualizerGLWidget

import ANNarchy4

import code
            
class GeneralWidget(object):
    def __init__(self, widget, main_window):
        
        self._neurons = ListView(widget.neur_general, main_window, "neuron type")
        self._neurons.initialize()
        self._synapses = ListView(widget.syn_general, main_window, "synapse type")
        self._synapses.initialize()

        self._populations = ListView(widget.pop_general, main_window, "population")
        self._populations.initialize()
        self._projections = ListView(widget.proj_general, main_window, "projection")
        self._projections.initialize()
        self._params = ListView(widget.par_general, main_window, "params")
        self._params.initialize()
        
class EditorMainWindow(QMainWindow):
    
    def __init__(self, func, vis):
        super(QMainWindow, self).__init__()
        
        self._ui = Ui_ANNarchyEditor()
        self._ui.setupUi(self)
        
        self._func = func
        self._vis = vis
        
        self._tab_index = 0
        
        self._w = self.width()
        self._h = self.height()
        self.setWindowTitle('ANNarchy4.1 ultimate editor')
        
        #
        # editor instances
        self._obj_editor = CodeView(self._ui.objects, int( self._w * 0.80), int ( self._h * 0.90))
        self._env_editor = CodeView(self._ui.environment, int( self._w * 0.80), int ( self._h * 0.90))
        self._comp_editor = CodeView(self._ui.complete, int( self._w * 0.80), int ( self._h * 0.90))
        
        self._net_editor = NetworkGLWidget(self._ui.editor) 
        self._vis_editor = VisualizerGLWidget(self._ui.visualizer)
        # 
        # stack widget for general properties.
        self._general = GeneralWidget(self._ui, self)
        self._connect_signals()

    def _connect_signals(self):
        #
        # if the user changes the view the corresponding properties will be selected
        self._ui.views.connect(self._ui.views, QtCore.SIGNAL("currentChanged(int)"), self._ui.general, QtCore.SLOT("setCurrentIndex(int)"))
        self._ui.views.connect(self._ui.views, QtCore.SIGNAL("currentChanged(int)"), self._ui.special, QtCore.SLOT("setCurrentIndex(int)"))
        self._ui.views.connect(self._ui.views, QtCore.SIGNAL("currentChanged(int)"), self, QtCore.SLOT("_set_current_tab(int)"))
        
        self._ui.actionOpen.triggered[()].connect(self.load_file)
        self._ui.change_grid.pressed[()].connect(self.change_grid)
        
    def change_grid(self):
        """
        check the edit lines and modify width and height of the visualized grid.
        """
        try:
            x_size = int(self._ui.grid_x_dim.text())
            y_size = int(self._ui.grid_y_dim.text())
        except ValueError:
            x_size = 1
            y_size = 1

        self._vis_editor._update_grid.emit(x_size, y_size)
                
    def resizeEvent(self, *args, **kwargs):
        self._w = self.width()
        self._h = self.height()
        
        self._ui.splitter.setMinimumSize( int (self._w * 0.80), int ( self._h * 0.90) )
        self._ui.splitter.setMaximumSize( int (self._w * 0.80)+1, int ( self._h * 0.90)+1 )

        self._vis_editor.setMinimumSize( int (self._w * 0.80), int ( self._h * 0.90) )
        self._vis_editor.setMaximumSize( int (self._w * 0.80)+1, int ( self._h * 0.90)+1 )
        
        self._net_editor.setMinimumSize( int (self._w * 0.80), int ( self._h * 0.90) ) #TODO:
        self._net_editor.setMaximumSize( int (self._w * 0.80)+1, int ( self._h * 0.90)+1 ) # we need to set min and max, else the GL window does not react
        
        self._comp_editor.setMinimumSize( int (self._w * 0.80), int ( self._h * 0.90) ) #TODO:        
        self._env_editor.setMinimumSize( int (self._w * 0.80), int ( self._h * 0.90) ) #TODO:
        self._obj_editor.setMinimumSize( int (self._w * 0.80), int ( self._h * 0.90) ) #TODO:
                
        return QMainWindow.resizeEvent(self, *args, **kwargs)
    
    def compile(self):

        ANNarchy4.compile()
        
        self._func()
    
    @QtCore.pyqtSlot()
    def load_file(self):
        if self._tab_index == 5:
            self._comp_editor.load_file()
        else:
            QMessageBox.warning(self,"Open file", "Opening a file is only possible in the complete script view.")
            self._ui.views.setCurrentIndex(5)
        
    @QtCore.pyqtSlot(str)
    def _update_editor(self, population):
        print 'update:', population

    @QtCore.pyqtSlot(int)
    def _set_current_tab(self, idx):
        self._tab_index = idx
        
class ANNarchyEditor(object):
    
    def __init__(self, func, vis):
        app = QApplication(sys.argv)
         
        w = EditorMainWindow(func, vis)
        
        w.show()
         
        sys.exit(app.exec_())
        
        