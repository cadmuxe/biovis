import sys
from PySide import QtCore, QtGui, QtOpenGL
from OpenGL import GLU
from OpenGL.GL import *
from numpy import array
from mmLib import FileIO, Viewer, OpenGLDriver



class GLWidget(QtOpenGL.QGLWidget, Viewer.GLViewer):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.opengl_driver = OpenGLDriver.OpenGLDriver()
        Viewer.GLViewer.__init__(self)
        self.load_struct()
        self.__key = None
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def load_struct(self, path = None):
        path = "data/scTIM.pdb"

        try:
            struct = FileIO.LoadStructure(
                fil = path,
                distance_bonds = True)
        except IOError:
            error("file not found: %s" % (path))
            return None

        struct_desc = {}
        struct_desc["struct"] = struct
        struct_desc["path"] = path

        glstruct = self.glv_add_struct(struct)

        print "iter"
        root = glstruct.glo_iter_children()
        objects = []
        for r in root:
			objects.append(r)
		
        print "color trace"
        print objects[2].glal_calc_color_trace()    
        print objects[3].glal_calc_color_trace()
        
#        iters = objects[2].glal_iter_atoms()
#        for i in iters:
#            print i
		  
        return struct

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


class MyPaintWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setBackgroundRole(QtGui.QPalette.Base)

        # {id:[color], 1:[1,1,1,0,2,2,2]}  color: each number refer to one kind of color
        self.sequences={"len":0, "max_len_freg":0}
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        # whether to redraw the cache
        self.__TIMs_redraw = True
        # mouse on which sequence and fregment
        self.on_sequences_id = None
        self.on_freg_id = None

        self.__callback={} # callback function,  mouse_click, mouse_over

    def color(self, color_id):
        if color_id == 0:
            return QtCore.Qt.gray
        elif color_id == 1:
            return QtCore.Qt.black
        elif color_id == 2:
            return QtCore.Qt.red
        elif color_id == 3:
            return QtCore.Qt.green
        else:
            pass


    def paintEvent(self, event):
        self.paint_freg_heigh = event.rect().height() / self.sequences["len"]
        self.paint_freg_width = event.rect().width() / self.sequences["max_len_freg"]   # assume all the sequences have the same length

        # cache the result
        if self.__TIMs_redraw:
            self.__TIMs_cache = QtGui.QPixmap(event.rect().width(), event.rect().height())
            self.__TIMs_cache.fill(QtCore.Qt.white)
            painter = QtGui.QPainter(self.__TIMs_cache)
            #painter.begin(self.__TIMs_cache)
            painter.setPen(QtCore.Qt.NoPen)
            for x in range(0,self.sequences["len"]):
                for y in range(0, len(self.sequences[x])):
                    painter.setBrush(self.color(self.sequences[x][y]))
                    painter.drawRect(y * self.paint_freg_width, x*self.paint_freg_heigh,
                                     self.paint_freg_width, self.paint_freg_heigh)
            painter.end()
            self.__TIMs_redraw = False

        painter = QtGui.QPainter(self)
        #painter.begin(self)
        painter.drawPixmap(0,0, self.__TIMs_cache)
        if self.on_sequences_id != None:
            painter.setPen(QtCore.Qt.NoPen)
            for y in range(0, len(self.sequences[self.on_sequences_id])):
                painter.setBrush(self.color(self.sequences[self.on_sequences_id][y]))
                painter.drawRect(y * self.paint_freg_width, self.on_sequences_id * self.paint_freg_heigh,
                                 self.paint_freg_width, 10)
            painter.setPen(QtCore.Qt.white)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(0,self.on_sequences_id * self.paint_freg_heigh,self.paint_freg_width*len(self.sequences[self.on_sequences_id]),10)
        painter.end()

    def mouseMoveEvent(self,event):
        x,y = event.x(),event.y()
        self.on_sequences_id = y / self.paint_freg_heigh
        self.on_freg_id = x / self.paint_freg_width
        if self.on_sequences_id >= self.sequences["len"]:
            self.on_sequences_id = self.sequences["len"] - 1
        if self.on_freg_id >= len(self.sequences[self.on_sequences_id]):
            self.on_freg_id = len(self.sequences[self.on_sequences_id]) -1

        print self.on_sequences_id,self.on_freg_id
        self.update()



    def update_color(self,sequence_id, new_color_list):
        self.sequences[sequence_id] = new_color_list
        self.sequences["len"] = len(self.sequences) - 2
        if self.sequences["max_len_freg"] < len(self.sequences[sequence_id]):
            self.sequences["max_len_freg"] = len(self.sequences[sequence_id])
    def update_freg_color(self, sequence_id, freg_id, color):
        if not self.sequences.has_key(sequence_id):
            self.sequences[sequence_id] = []
        try:
            self.sequences[sequence_id][freg_id] = color
        except IndexError:
            self.sequences[sequence_id].append(color)
        self.sequences["len"] = len(self.sequences) - 2
        if self.sequences["max_len_freg"] < len(self.sequences[sequence_id]):
            self.sequences["max_len_freg"] = len(self.sequences[sequence_id])

    def registerClickCallBack(self, d):
        self.__callback[d["name"]] = d["func"]
    def resizeEvent(self, *args, **kwargs):
        self.__TIMs_redraw = True

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
            
        self.setWindowTitle("2013 BioVis Contest")
        self.resize(800, 600)

        self.centralWidget = QtGui.QWidget(self)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)

        #self.glWidget = GLWidget(self.centralWidget)
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

        self.initActions()
        self.initMenus()
        self.initListWidget()
        self.initTIMs()

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
        dTIM =[]
        for c in line:
            dTIM.append(c)
		
		# read scTIM
        f = open("data/scTIM.fa")
        line = f.readline()
       	f.close()
        
        # add each element to a list
        scTIM =[]
        for c in line:
             scTIM.append(c)

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
		
		# read the alignment file
        f = open("data/cTIM_align_small.fa")
        lines = f.readlines()
        f.close()
		
		# determine the orientation and store in a list
        self.TIMs_raw=[]
        for l in lines:
            if l[0] == ">" or l[0] == '\n':
                continue
            self.TIMs_raw.append(l)
        
        # bottom widget
        for seq_id in range(len(self.TIMs_raw)):
            seq=[]
            for c in self.TIMs_raw[seq_id]:
                if c=='-':
                    seq.append(0)
                elif c =='\n':
                    continue
                else:
                    seq.append(1)
            self.TIMs.update_color(seq_id, seq)

    def close(self):
        QtGui.qApp.quit()

app = QtGui.QApplication(sys.argv)

win = MainWindow()

win.show()

sys.exit(app.exec_())