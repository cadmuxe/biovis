#!/usr/bin/env python -W ignore::DeprecationWarning
import sys

from vis import * # includes QT and openGL imports
from GLPropertyBrowser import *
from sequenceSet import sequenceSet

# Class that handles the mouse event filters 
# to link the views
class MouseEventFilter(QtCore.QObject):

    pressed  = QtCore.Signal(QtCore.QEvent)
    moved    = QtCore.Signal(QtCore.QEvent)
    wheeled  = QtCore.Signal(QtCore.QEvent)
    
    def __init__(self):
        super(MouseEventFilter, self).__init__()
        self.press = 0

    def hit(self):
        self.press = 1

    def eventFilter(self, obj, event):
        
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                self.pressed.emit(event)

                if self.press:
                    return 1
                else:
                    self.hit()
        
        elif event.type() == QtCore.QEvent.Wheel:
            self.wheeled.emit(event)
            
        elif event.type() == QtCore.QEvent.MouseMove:
            if self.press:
                self.moved.emit(event)
                return 1
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if self.press:
                self.press = 0
                return 1

        return super(MouseEventFilter,self).eventFilter(obj, event)

class MainWindow(QtGui.QMainWindow):
    
    __key = None
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)#, None, QtCore.Qt.WindowStaysOnTopHint)
            
        self.setWindowTitle("2013 BioVis Contest")
        self.resize(1280, 1024)

        self.centralWidget = QtGui.QWidget(self)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        
        self.glWidgetSC = GLWidget(self.centralWidget)
        self.glWidgetD = GLWidget(self.centralWidget)
                        
        self.dTIMList = ListWidget(self.centralWidget)
        self.scTIMList = ListWidget(self.centralWidget)
        self.TIMs = MyPaintWidget(self.centralWidget)

        self.dTIMLabel = QtGui.QLabel("dTIM")
        self.scTIMlabel = QtGui.QLabel("scTIM")

        self.gridlayout.addWidget(self.glWidgetSC, 0, 0, 2, 1)
        self.gridlayout.addWidget(self.glWidgetD, 0, 1, 2, 1)

        self.gridlayout.addWidget(self.dTIMLabel, 0, 2, 1, 1)
        self.gridlayout.addWidget(self.dTIMList, 1, 2, 1, 1)

        self.gridlayout.addWidget(self.scTIMlabel, 0, 3, 1, 1)
        self.gridlayout.addWidget(self.scTIMList, 1, 3, 1, 1)

        self.gridlayout.addWidget(self.TIMs, 2, 0, 1, 4)
        
        self.gridlayout.setColumnStretch(0,20)
        self.gridlayout.setColumnStretch(1,20)
        self.gridlayout.setColumnStretch(2,1)
        self.gridlayout.setColumnStretch(3,1)

        self.gridlayout.setRowStretch(0,0)
        self.gridlayout.setRowStretch(1,2)
        self.gridlayout.setRowStretch(2,1)

        self.setCentralWidget(self.centralWidget)
        
        # create the mouse event filter
        self.mouseEF = MouseEventFilter()
        
        # link it to each widgets mouse events
        self.mouseEF.pressed.connect(self.pressEvent)
        self.mouseEF.moved.connect(self.moveEvent)
        self.mouseEF.wheeled.connect(self.wheelEvent)
        
        # install the new event filter
        self.glWidgetSC.installEventFilter(self.mouseEF)
        self.glWidgetD.installEventFilter(self.mouseEF)
        
        self.initActions()
        self.initMenus()
        self.initListWidget()
        self.initTIMs()
    
    # mouse actions
    def pressEvent(self, event):
                
        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()
        self.cursor_button = event.button()

    def moveEvent(self, event):

        if self.cursor_button == QtCore.Qt.RightButton or \
                    (self.__key == QtCore.Qt.Key_Shift and self.cursor_button == QtCore.Qt.LeftButton):
            self.glWidgetSC.glv_straif(event.x() - self.cursor_pre_x, self.cursor_pre_y - event.y())
            self.glWidgetD.glv_straif(event.x() - self.cursor_pre_x, self.cursor_pre_y - event.y())
        
        elif self.cursor_button == QtCore.Qt.LeftButton:
            
            self.glWidgetSC.glv_trackball(self.cursor_pre_x, self.cursor_pre_y, event.x(), event.y())
            self.glWidgetSC.glv_trackball(self.cursor_pre_x, self.cursor_pre_y, event.x(), event.y())
        
            self.glWidgetD.glv_trackball(self.cursor_pre_x, self.cursor_pre_y, event.x(), event.y())
            self.glWidgetD.glv_trackball(self.cursor_pre_x, self.cursor_pre_y, event.x(), event.y())
            
        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()
    
    def wheelEvent(self, event):
        self.glWidgetSC.glv_zoom(event.delta())
        self.glWidgetD.glv_zoom(event.delta())
        
    # keyboard actions
        
    def keyPressEvent(self,event):
        self.__key = event.key()
        
    def keyReleaseEvent(self,event):
        self.__key = None
    
    # window actions    
                                  
    def initActions(self):
        self.exitAction = QtGui.QAction('Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), self.close)

    def initListWidget(self):
        # scTIMList
        self.scTIMList.itemSelectionChanged.connect(self.update_scTIM_select)
        self.scTIMList.verticalScrollBar().valueChanged.connect(self.dTIMList.verticalScrollBar().setValue)

        self.dTIMList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.dTIMList.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.dTIMList.verticalScrollBar().valueChanged.connect(self.scTIMList.verticalScrollBar().setValue)

    def update_scTIM_select(self):
        id_list =[]
        for item in self.scTIMList.selectedItems():
            id_list.append(item.get_fragment_id())
        self.glWidgetSC.update_select(id_list)
        for item in self.dTIMList.selectedItems():
            self.dTIMList.setCurrentItem(item, QtGui.QItemSelectionModel.Clear)
        for i in id_list:
            self.dTIMList.setCurrentRow(i-2,QtGui.QItemSelectionModel.Select)

    def initMenus(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.exitAction)

    # Create the lists in the right panel
    def initTIMs(self):
         
        # read dTIM
        f = open("data/dTIM.fa")
        line = f.readline()
        f.close()
        # add each element to a list
        dTIM = [frag for frag in line]

        # read scTIM
        f = open("data/scTIM.fa")
        line = f.readline()
        f.close()
        # add each element to a list
        scTIM =[frag for frag in line]

        # create one list of both TIMs
        frag_id = range(2,300)
        items = zip(frag_id,dTIM,scTIM)
        self.__different_frag_id=set()

        # iterate and find the similarities, then color them accordingly
        for item in items:
            item_d = ListWidgetItem(item[1], self.dTIMList, item[0])
            item_sc = ListWidgetItem(item[2], self.scTIMList, item[0])
            if(item[1] != item[2]):
                self.__different_frag_id.add(item[0])
                item_d.setBackground(QtGui.QBrush(QtGui.QColor(204,204,255)))
                item_sc.setBackground(QtGui.QBrush(QtGui.QColor(204,204,255)))

        # load TIMs, and coloring them and update for darwing
        self.__sequenceSet = sequenceSet("data/cTIM_core_align.fa")
        self.__sequenceSet.frequencyColor()                 # could use other coloring method
        self.__sequenceSet.updateColor(self.TIMs)

    def close(self):
        QtGui.qApp.quit()

app = QtGui.QApplication(sys.argv)

win = MainWindow()

win.show()

sys.exit(app.exec_())