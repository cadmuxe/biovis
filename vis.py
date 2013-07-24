from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

import OpenGL

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from mmLib import FileIO, Structure, Viewer, OpenGLDriver
from SPaintWidget import *

class GLWidget(QtOpenGL.QGLWidget, Viewer.GLViewer):
    def __init__(self, parent=None):
        
        self.parent = parent
        self.glstruct = None
                
        QtOpenGL.QGLWidget.__init__(self, self.parent)
        
        self.opengl_driver = OpenGLDriver.OpenGLDriver()
                
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
        
        # self.prop_editor = GLPropertyBrowserDialog(
        #     glo_root      = self.glstruct )
        # 
        # self.prop_editor.show()
        
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
                    
        self.glv_render_one(self.opengl_driver)
        glFlush()

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
