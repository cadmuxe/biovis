from OpenGL.GL import *
from OpenGL import GL
from PySide.QtOpenGL import *
from PySide.QtCore import Qt
from PySide import QtCore, QtGui, QtOpenGL
import sys
import __main__
__main__.pymol_argv = [ 'pymol', '-qc'] # Quiet and no GUI
import pymol

 
class PyMolWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self)
        self._enableUi = True
        self.pymol = pymol
        #pymol.finish_launching()
        pymol._init_internals(self)
        self._COb = self.pymol._cmd._get_global_C_object(self)
        self.pymol._cmd._start(self._COb, self.pymol.cmd)
        self.pymol.cmd.load("../data/scTIM.pdb")
        self.resize(400,300)

 
    def paintGL(self):
        glViewport(0,0,self.width(), self.height())
        self.pymol._cmd._draw(self._COb)
        #self.pymol.cmd.draw(400,300)

    def resizeGL(self, width, height):
        self.pymol._cmd._reshape(self._COb,width,height, 0)

 

app = QtGui.QApplication(sys.argv)
window = PyMolWidget()
window.show()
sys.exit(app.exec_())
