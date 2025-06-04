
from openalea.ratp import *
from openalea.ratp import grid
from qtpy import QtWidgets, QtGui
#from PyQt4 import QtCore, QtGui
from openalea.core.interface import * #IGNORE:W0614,W0401
from openalea.core.observer import lock_notify
from openalea.visualea.node_widget import NodeWidget
import numpy as np


class UI_ratp_Vege(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.Layout = QtWidgets.QGridLayout(self)

class ClassUiRATP_Vege(NodeWidget, UI_ratp_Vege):

    def __init__(self, node, parent):
        """
        """

        UI_ratp_Vege.__init__(self, parent)
        NodeWidget.__init__(self, node)
        self.window().setWindowTitle("Vegetation parameters")
        self.listSpinBox = []
##        self.val = self.node.get_output(0)
        self.copyVal = None
##        self.initVal()

        self.adjustUI()
        self.notify(node, ('input_modified',))

##    def initVal(self):


    def adjustUI(self):
        listLabel =[]

        for i in range(5):
            doubleSpinBox = QtWidgets.QDoubleSpinBox(self)
            label = QtWidgets.QLabel()
            label.setText('mu '+ str(i+1))
            listLabel.append(label)
            self.listSpinBox.append(doubleSpinBox)
            self.window().Layout.addWidget(label,i,0,)
            self.window().Layout.addWidget(doubleSpinBox,i,1)
            doubleSpinBox.editingFinished.connect(self.UpdateVal)



    def notify(self, sender, event):
        """ Notification sent by node """
        if self.copyVal is not None :
            self.val = self.copyVal
        elif self.node.get_output(0) is None:
            self.val= pyratp.vegetation_types
            self.val.mu = np.zeros(1)
        else:
            self.val = self.node.get_output(0)

        self.listInput = list(self.val.mu)

        for n in range(len(self.listInput)):
            self.listSpinBox[n].setValue(self.listInput[n])


    def UpdateVal(self):

        for a in range(len(self.listInput)):
           self.val.mu[a] = self.listSpinBox[a].value()

##           listLabel[i].setVisible(False)
        self.copyVal = self.val




























