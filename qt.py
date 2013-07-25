#!/usr/bin/env python -W ignore::DeprecationWarning

import sys
from PySide import QtCore, QtGui, QtOpenGL
import OpenGL

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from mmLib import Constants, FileIO, Viewer, R3DDriver, OpenGLDriver, Structure, TLS
from SPaintWidget import *

from GLPropertyBrowser import *
from sequenceSet import sequenceSet
from barcharWidget import barcharWidget

class GLWidget(QtOpenGL.QGLWidget, Viewer.GLViewer):
    def __init__(self, parent=None):
        
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.opengl_driver = OpenGLDriver.OpenGLDriver()

        Viewer.GLViewer.__init__(self)
        
        self.load_struct()
        self.__key = None
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
                
        self.prop_editor = GLPropertyBrowserDialog(
            glo_root      = self.glstruct.glo_get_root() )
                  
    def load_struct(self, path = None):
        
        path = "./data/scTIM.pdb"
        
        try:
            struct = FileIO.LoadStructure(
                fil              = path,
                library_bonds    = True,
                distance_bonds   = True)
                
        except IOError:
            error("file not found: %s" % (path))
            return None

        struct_desc = {}
        struct_desc["struct"] = struct
        struct_desc["path"] = path
                
        self.glstruct = self.glv_add_struct(struct)
        
        return struct
    
    def showDialog(self):
        return
             
    def initializeGL(self):
        self.glv_init()

    def resizeGL(self, width, height):
        self.glv_resize(width, height)

    def paintGL(self):
        self.glv_render()

    def glv_render(self):
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
        # why need to use updateGL, but glv_render() not works.
        # Answer: update Tells QT to refresh the widget
    def update_select(self, fragment_id_list=[]):
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
        self.resize(800, 600)

        self.centralWidget = QtGui.QWidget(self)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        
        self.glWidgetSC = GLWidget(self.centralWidget)
        #self.glWidgetD = GLWidget(self.centralWidget)
        
        self.glWidgetSC.showDialog()
        
        self.dTIMList = ListWidget(self.centralWidget)
        self.scTIMList = ListWidget(self.centralWidget)
        self.TIMs = MyPaintWidget(self.centralWidget)
        self.barchar = barcharWidget(self.centralWidget)

        self.dTIMLabel = QtGui.QLabel("dTIM")
        self.scTIMlabel = QtGui.QLabel("scTIM")

        self.gridlayout.addWidget(self.glWidgetSC, 0, 0, 2, 1)
        #self.gridlayout.addWidget(self.glWidgetD, 0, 1, 2, 1)

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
        self.initListWidget()
        self.initTIMs()
        self.initMenus()
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

        sortingMenu = menuBar.addMenu("&Sorting")
        action_frequency = sortingMenu.addAction("&Residue frequency")
        action_edit_dist = sortingMenu.addAction("&Edit distance")
        action_weighted_edit_dist = sortingMenu.addAction("&Weighted edit distance")
        action_common_resi_with_scTIM = sortingMenu.addAction("&Common residues with scTIM")
        action_normalized_common_resi_with_scTIM = sortingMenu.addAction("&Common residues with scTIM(Normalized)")
        action_number_common_resi_with_scTIM_without_posi = sortingMenu.addAction("&Common resi. with scTIM without position")
        action_percent_common_resi_with_scTIM_without_posi = sortingMenu.addAction("&Common resi. with scTIM without position%")

        self.connect(action_frequency, QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(0))
        self.connect(action_edit_dist, QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(1))
        self.connect(action_weighted_edit_dist, QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(2))
        self.connect(action_common_resi_with_scTIM , QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(3))
        self.connect(action_normalized_common_resi_with_scTIM , QtCore.SIGNAL("triggered()"),
                     lambda: self.set_sorting(4))
        self.connect(action_number_common_resi_with_scTIM_without_posi, QtCore.SIGNAL("triggered()"),
                     lambda: self.set_sorting(5))
        self.connect(action_percent_common_resi_with_scTIM_without_posi , QtCore.SIGNAL("triggered()"),
                     lambda: self.set_sorting(6))

        coloringMenu = menuBar.addMenu("&Coloring")
        action_basic_coloring = coloringMenu.addAction("&Basic coloring")
        action_frequency_color = coloringMenu.addAction("&Frequency Coloring")

        self.connect(action_basic_coloring, QtCore.SIGNAL("triggered()"), lambda: self.set_coloring(0))
        self.connect(action_frequency_color, QtCore.SIGNAL("triggered()"), lambda: self.set_coloring(1))

        self.setMenuBar(menuBar)

    def set_sorting(self, n):
        if n == 0:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_frag_frequency
            self.current_sortting["name"] = "Residues frequency"
        elif n == 1:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_edit_dist
            self.current_sortting["name"] = "Edit distance"
        elif n == 2:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_weighted_edit_dist
            self.current_sortting["name"] = "Weighted edit distance"
        elif n == 3:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_num_of_common_residues_with_scTIM
            self.current_sortting["name"] = "Common residues with scTIM"
        elif n == 4:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_num_of_common_residues_with_scTIM_norm
            self.current_sortting["name"] = "Common residues with scTIM(Normalized)"
        elif n == 5:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_number_of_common_residues_with_scTIM_without_position
            self.current_sortting["name"] = "Common residues number with scTIM without consider the position"
        elif n == 6:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_percent_of_common_residues_with_scTIM_without_position
            self.current_sortting["name"] = "Common residues percentage with scTIM without consider the position"
        self.current_sortting["func"]()
        self.current_coloring["func"]()
        self.updateStatusBar()
        self.__sequenceSet.updateColor(self.TIMs)


    def set_coloring(self, n):
        if n == 0:
            self.current_coloring["func"] = self.__sequenceSet.basicColor
            self.current_coloring["name"] = "Basic coloring(residues are colored by gray)"
        elif n == 1:
            self.current_coloring["func"] = self.__sequenceSet.frequencyColor
            self.current_coloring["name"] = "Frequency coloring(most frequency residue in same column colored by red)"

        self.current_coloring["func"]()
        self.updateStatusBar()
        self.__sequenceSet.updateColor(self.TIMs)

    def updateStatusBar(self):
        self.statusBar().showMessage("Sorting by %s, Coloring by %s "  % (self.current_sortting["name"], self.current_coloring["name"]))

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
        self.__sequenceSet.loadscTIMFromFile("data/scTIM.fa")
        self.current_sortting={"func":"", "name":"Haven't been sorted"}
        self.current_coloring ={"func":self.__sequenceSet.basicColor, "name":"Basic coloring"}
        self.__sequenceSet.basicColor()                 # could use other coloring method
        self.__sequenceSet.updateColor(self.TIMs)
        self.updateStatusBar()

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
