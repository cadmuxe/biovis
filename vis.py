from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

import OpenGL


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import new

from mmLib import FileIO, Structure, Viewer, OpenGLDriver
from SPaintWidget import *
from GLPropertyBrowser import *

class GLWidget(QtOpenGL.QGLWidget, Viewer.GLViewer):
    def __init__(self, path, parent=None):
        
        self.parent = parent
        self.glstruct = None
        self.ready = False
                
        QtOpenGL.QGLWidget.__init__(self, self.parent)
        
        self.opengl_driver = OpenGLDriver.OpenGLDriver()
                
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        Viewer.GLViewer.__init__(self)
        
        gluPerspective(45.0, self.width()/self.height(), 0.0001, 1000)
        
        self.load_struct(path)

        ## install new draw method
        #self.install_draw_method({ "name":"lines",
        #      "func":                glal_draw_lines,
        #      "transparent":         False,
        #      "visible_property":    "lines",
        #      "recompile_action":    "recompile_lines" })
                    
    def load_struct(self, path = None):
                
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
                    
        return struct
    
    def setStatus(self):
        self.ready = True
    
    def getStruct(self):
        return self.glstruct
    
    # show property 
    def showEditor(self):
        self.prop_editor.show()
        
    def initializeGL(self):
        #glutInit(sys.argv)
        
        self.glv_init()

    def resizeGL(self, width, height):
        self.glv_resize(width, height)

    def paintGL(self):
        
        if not self.ready:
            return 1
        
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
        #self.update_fragment_id_list(fragment_id_list)
        #self.glv_redraw()
        # for frag in self.glstruct.iter_fragments():
        #     print frag  
        #print fragment_id_list
        for child in self.glstruct.glo_iter_children():
            if isinstance(child, Viewer.GLChain):    
                for frag in child.glal_iter_atoms():
                    print type(frag.get_fragment())
    
    def install_draw_method(self,method):
        for glstructure in self.glo_iter_children():
            for glchain in glstructure.glo_iter_children():
                if isinstance(glchain, Viewer.GLChain):
                    instancemethod = new.instancemethod(method["func"], glchain, Viewer.GLChain)
                    for i in glchain.gldl_draw_method_list:
                        # this method looks bad, but i have not other choice
                        if i["name"] == method["name"]:
                            i["func"] = instancemethod

class ListWidget(QtGui.QListWidget):
    def __init__(self,text, parent = None):
        QtGui.QListWidget.__init__(self, parent)
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

class ListWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, text , parent, frag_id=None):
        QtGui.QListWidgetItem.__init__(self, "%s (%i)" % (text, frag_id), parent)
        self.frag_name = text
        self.frag_id = frag_id
        self.__callback = {}
    def get_fragment_id(self):
        return self.frag_id
class ColorWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        hbox = QtGui.QHBoxLayout(self)
        pixmap = QtGui.QPixmap("data/color.png")
        lbl = QtGui.QLabel(self)
        lbl.setPixmap(pixmap)

        hbox.addWidget(lbl)
        self.setLayout(hbox)
        self.setWindowTitle('Coloring schemes')


def glal_draw_lines(self):
    """Draw a atom using bond lines only.
    """
    ## driver optimization
    glr_set_material_rgb = self.driver.glr_set_material_rgb
    glr_line             = self.driver.glr_line
    glr_cross            = self.driver.glr_cross
    ##

    self.driver.glr_lighting_disable()
    self.driver.glr_set_line_width(self.properties["line_width"])

    for atm1, pos1 in self.glal_iter_visible_atoms():
        glr_set_material_rgb(*self.glal_calc_color(atm1))

        if len(atm1.bond_list)>0:
            ## if there are bonds, then draw the lines 1/2 way to the
            ## bonded atoms
            print dir(atm1)
            print type(atm1)
            for bond in atm1.iter_bonds():
                atm2 = bond.get_partner(atm1)
                try:
                    pos2 = self.glal_visible_atoms_dict[atm2]
                except KeyError:
                    if self.glal_hidden_atoms_dict.has_key(atm2):
                        continue
                    else:
                        pos2 = self.glal_calc_position(atm2.position)

                end = pos1 + ((pos2 - pos1) / 2)
                glr_line(pos1, end)

        ## draw a cross for non-bonded atoms
        else:
            glr_cross(
                pos1,
                self.glal_calc_color(atm1),
                self.properties["line_width"])
