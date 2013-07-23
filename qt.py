#!/usr/bin/env python -W ignore::DeprecationWarning

import sys
# from PySide import QtCore, QtGui, QtOpenGL

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

import OpenGL

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from mmLib import FileIO, Structure, Viewer, OpenGLDriver
from SPaintWidget import *

from GLPropertyBrowser import *
from sequenceSet import sequenceSet
from barcharWidget import barcharWidget

class GLWidget(QtOpenGL.QGLWidget, Viewer.GLViewer):
    def __init__(self, parent=None):
        
        self.parent = parent
        self.glstruct = None
        
        QtOpenGL.QGLWidget.__init__(self, self.parent)
        self.opengl_driver = OpenGLDriver.OpenGLDriver()
        OpenGL.ERROR_CHECKING = False
                
        self.__key = None
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        Viewer.GLViewer.__init__(self)
        self.load_struct()
                    
    def load_struct(self, path = None):
        
        path = "./data/scTIM.pdb"
        
        try:
            struct = FileIO.LoadStructure(
                fil              = path,
                library_bonds    = True,
                distance_bonds   = True )
        
        except IOError:
            error( "file not found: %s" % (path) )
            return None

        struct_desc = {}
        struct_desc["struct"] = struct
        struct_desc["path"] = path
                
        self.glstruct = self.glv_add_struct(struct)
        
        self.prop_editor = GLPropertyBrowserDialog(
            glo_root      = self.glstruct )
        
        self.prop_editor.show()
        
        return struct
    
    def getStruct(self):
        return self.glstruct
        
    def initializeGL(self):
        #glutInit(sys.argv)
        
        self.glv_init()

    def resizeGL(self, width, height):
        self.glv_resize(width, height)

    def paintGL(self):
            
        self.glv_render()

    def glv_render(self):
           
        # def print_recurse(gl_obj):
        #     
        #     for prop in gl_obj.glo_iter_property_desc():
        #         if prop['name'][0:3] == "cpk":
        #             print prop['name']
        #             print prop.keys()
        #             print " "
        #             print prop.values()
        #             print " "
        #     
        #     for child in gl_obj.glo_iter_children():
        #         print_recurse(child)
        # 
        # if self.glstruct is not None:        
        #     print_recurse(self.glstruct)
                
        self.glv_render_one(self.opengl_driver)
        glFlush()

    def mousePressEvent(self,event):
        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()
        self.cursor_button = event.button()

    def mouseMoveEvent(self,event):
        if self.cursor_button == QtCore.Qt.RightButton or \
                    (self.__key == QtCore.Qt.Key_Shift and self.cursor_button == QtCore.Qt.LeftButton):
            self.glv_straif(event.x() - self.cursor_pre_x, self.cursor_pre_y - event.y())
        elif self.cursor_button == QtCore.Qt.LeftButton:
            self.glv_trackball(self.cursor_pre_x, self.cursor_pre_y, event.x(), event.y())
        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()

    def wheelEvent(self, event):
        self.glv_zoom(event.delta())
    def keyPressEvent(self,event):
        self.__key = event.key()
    def keyReleaseEvent(self,event):
        self.__key = None
    def glv_redraw(self):
        self.updateGL()
        #print "redraw"
        # why need to use updateGL, but glv_render() not works.
        # Answer: update Tells QT to refresh the widget
    def update_select(self, fragment_id_list=[]):
        #print "update_select"
        self.update_fragment_id_list(fragment_id_list)
        self.glv_redraw()

class ListWidget(QtGui.QListWidget):
    def __init__(self,text, parent = None):
        QtGui.QListWidget.__init__(self, parent)
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

class ListWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, text , parent, frag_id=None):
        QtGui.QListWidgetItem.__init__(self, text, parent)
        self.frag_name = text
        self.frag_id = frag_id
        self.__callback = {}
    def get_fragment_id(self):
        return self.frag_id


class MainWindow(QtGui.QMainWindow):

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
        self.barchar = barcharWidget(self.centralWidget)

        self.dTIMLabel = QtGui.QLabel("dTIM")
        self.scTIMlabel = QtGui.QLabel("scTIM")

        self.gridlayout.addWidget(self.glWidgetSC, 0, 0, 2, 1)
        self.gridlayout.addWidget(self.glWidgetD, 0, 1, 2, 1)

        self.gridlayout.addWidget(self.dTIMLabel, 0, 2, 1, 1)
        self.gridlayout.addWidget(self.dTIMList, 1, 2, 1, 1)

        self.gridlayout.addWidget(self.scTIMlabel, 0, 3, 1, 1)
        self.gridlayout.addWidget(self.scTIMList, 1, 3, 1, 1)

        self.gridlayout.addWidget(self.TIMs, 2, 0, 1, 4)
        self.gridlayout.addWidget(self.barchar, 3, 0, 1, 4)

        self.gridlayout.setColumnStretch(0,20)
        self.gridlayout.setColumnStretch(1,20)
        self.gridlayout.setColumnStretch(2,1)
        self.gridlayout.setColumnStretch(3,1)

        self.gridlayout.setRowStretch(0,0)
        self.gridlayout.setRowStretch(1,4)
        self.gridlayout.setRowStretch(2,3)
        self.gridlayout.setRowStretch(3,1)

        self.setCentralWidget(self.centralWidget)

        self.initActions()
        self.initMenus()
        self.initListWidget()
        self.initTIMs()
        self.barchar.update_sequences(0, 9, "ADGDEDSFE",[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] )
        self.TIMs.registerClickCallBack({"name":"barchar","func":self.barchar_update})
                
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

    def barchar_update(self, selection_f, selection_t, seqid, fragid):
        seq = self.__sequenceSet[seqid].seq
        frag_from, frag_to = selection_f, selection_t
        if frag_to > len(seq):
            frag_to = len(seq)
        if frag_from > len(seq):
            frag_from = len(seq)
        frequency = [self.__sequenceSet.frag_frequency[i][seq[i]]/float(len(self.__sequenceSet)) if seq[i] !='-' else 0.0   for i in range(frag_from, frag_to)]
        self.barchar.update_sequences(frag_from, frag_to, seq[frag_from: frag_to],
                                      frequency)

app = QtGui.QApplication(sys.argv)

win = MainWindow()

win.show()

sys.exit(app.exec_())
