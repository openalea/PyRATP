from openalea.ratp import *
from openalea.ratp import grid
from openalea.ratp import pyratp
#from PyQt4 import QtCore, QtGui
from qtpy import QtWidgets, QtGui

from openalea.core.interface import * #IGNORE:W0614,W0401
from openalea.core.observer import lock_notify
from openalea.visualea.node_widget import NodeWidget
import numpy as np


class UI_ratp_Grid(QtGui.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.Layout = QtWidgets.QGridLayout(self)

class ClassUiRATP_Grid(NodeWidget, UI_ratp_Grid):

    def __init__(self, node, parent):
        """
        """

        UI_ratp_Grid.__init__(self, parent)
        NodeWidget.__init__(self, node)
        self.window().setWindowTitle("Grid parameters")
        self.listSpinBox = []
        self.copyVal = None
        self.adjustUI()
        self.input_modified.emit(node)


    def initVal(self):
        self.val.njx = 20
        self.val.njy = 20
        self.val.njz = 20
        self.val.dx = .2
        self.val.dy = .2
        pasdz = .2
        self.val.longitude = 3
        self.val.latitude = 45
        self.val.dz = np.zeros(self.val.njz+1)
        for z in range(self.val.njz):
            self.val.dz[z]= pasdz
        self.val.xorig = 0
        self.val.yorig = 0
        self.val.timezone= 0

        # angle (degree) between axis X+ and North
        self.val.orientation=0

        self.val.idecaly = 0

        # nent: number of vegetation types in the 3D grid
        self.val.nent=1

        self.val.nblosoil =2
        self.val.rs = [0.075 ,0.20]
        grid.initParam(self.val)


    def adjustUI(self):
        listLabel = ['njx','njy','njz','dx','dy','dz','longitude','latitude']
        for i in range(len(listLabel)):


            doubleSpinBox = QtGui.QDoubleSpinBox()
            label = QtGui.QLabel()
            label.setText(listLabel[i])
            self.listSpinBox.append(doubleSpinBox)
            
            doubleSpinBox.editingFinished.connect(self.UpdateVal)

            self.window().Layout.addWidget(label,i,0,)

            self.window().Layout.addWidget(doubleSpinBox,i,1)


        self.checkCentre = QtWidgets.QCheckBox('Centrer la scene')
        self.checkIB = QtWidgets.QCheckBox('Isolated Box')
        self.checkScattering = QtWidgets.QCheckBox('Scattering')
        self.checkCentre.clicked.connect(self.UpdateVal )
        self.checkIB.clicked.connect(self.UpdateVal )
        self.checkScattering.clicked.connect(self.UpdateVal )
        self.window().Layout.addWidget(self.checkIB,i+1,0)
        self.window().Layout.addWidget(self.checkCentre,i+2,0)
        self.window().Layout.addWidget(self.checkScattering,i+3,0)

    def notify(self, sender, event):
        """ Notification sent by node """

        if self.copyVal is not None :
            self.val = self.copyVal
        elif self.node.get_output(0) is None:
            self.val=pyratp.grid3d
            self.initVal()
        else:
            self.val = self.node.get_output(0)


        self.listInput = [self.val.njx,self.val.njy,self.val.njz,self.val.dx,self.val.dy,self.val.dz[0],self.val.longitude,self.val.latitude]

        for n in range(len(self.listInput)):
            self.listSpinBox[n].setValue(self.listInput[n])


    def UpdateVal(self):
        xdeb = self.val.njx * self.val.dx
        ydeb = self.val.njy * self.val.dy

        self.val.njx = self.listSpinBox[0].value()
        self.val.njy = self.listSpinBox[1].value()
        self.val.njz = self.listSpinBox[2].value()
        self.val.dx = self.listSpinBox[3].value()
        self.val.dy = self.listSpinBox[4].value()
        pasdz = self.listSpinBox[5].value()
        self.val.longitude = self.listSpinBox[6].value()
        self.val.latitude = self.listSpinBox[7].value()
        self.val.dz = np.zeros(self.val.njz+1)
        for z in range(self.val.njz):
            self.val.dz[z]= pasdz

        if self.checkCentre.isChecked():
            xfin = self.val.njx * self.val.dx
            yfin = self.val.njy * self.val.dy
            self.val.xorig = (xdeb-xfin)/2
            self.val.yorig = (ydeb-yfin)/2
        grid.initParam(self.val)

##        if self.checkIB.isChecked():
        self.val.int_isolated_box = int(self.checkIB.isChecked())
        self.val.int_scattering = int(self.checkScattering.isChecked())
        self.copyVal = self.val
