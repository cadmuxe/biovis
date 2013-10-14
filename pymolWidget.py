from OpenGL.GL import *
from OpenGL.GLU import *
from PySide import QtGui
from PySide.QtOpenGL import *
from PySide.QtCore import Qt
from PySide import QtCore

import pymol2



residues_class = [('RRG','LYS','ASP','GLU'),
                  ('GLN','ASN','HIS','SER','THR','TYR','CYS','MET','TRP'),
                  ('ALA','ILE','LEU','PHE','VAL','PRO','GLY')]

def get_color(resn):
    colours = ['red', 'green', 'blue', 'yellow', 'violet', 'cyan',    \
            'salmon', 'lime', 'pink', 'slate', 'magenta', 'orange', 'marine', \
            'olive', 'purple', 'teal', 'forest', 'firebrick', 'chocolate',    \
            'wheat', 'white', 'grey' ]
    if resn in residues_class[0]:
        return 'olive'
    elif resn in residues_class[1]:
        return 'marine'
    else:
        return "firebrick"

def define_color(set_color):
    set_color("c1",[0.698, 0.094, 0.168])
    set_color("c2",[0.129, 0.4, 0.674])
    set_color("c3", [0.93, 0.541, 0.384])


class PymolQtWidget(QGLWidget):
    _buttonMap = {Qt.LeftButton:0,
                  Qt.MidButton:1,
                  Qt.RightButton:2}


    def __init__(self, parent, enableUi,File=""):
        f = QGLFormat()
        f.setStencil(True)
        f.setRgba(True)
        f.setDepth(True)
        f.setDoubleBuffer(True)
        QGLWidget.__init__(self, f, parent=parent)
        self.setMinimumSize(500, 500)
        self._enableUi=enableUi
        self.pymol = pymol2.PyMOL()# _pymolPool.getInstance()
        self.pymol.start()
        self.cmd = self.pymol.cmd
        # self.toPymolName = self.pymol.toPymolName ### Attribute Error
        self._pymolProcess()
        self.setFocusPolicy(Qt.ClickFocus)
        #self.Parser = self.

        if not self._enableUi:
            self.pymol.cmd.set("internal_gui",0)
            self.pymol.cmd.set("internal_feedback",1)
            self.pymol.cmd.button("double_left","None","None")
            self.pymol.cmd.button("single_right","None","None")

        self.pymol.cmd.load(File)
        self.cmd.show("cartoon")
        #self.cmd.cartoon("putty")
        self.cmd.set("cartoon_highlight_color", 1)
        self.cmd.hide("lines")
        #self.cmd.hide("chain ")
        self.color_obj(0)
        #self.cmd.color("marine")
        self.pymol.reshape(self.width(),self.height())
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._pymolProcess)
        self.resizeGL(self.width(),self.height())
        #globalSettings.settingsChanged.connect(self._updateGlobalSettings)
        self._updateGlobalSettings()
        define_color(self.cmd.set_color)

    def enableUI(self):
        #self.pymol.cmd.set("internal_gui",1)
        self.pymol.cmd.set("internal_feedback",1)
        self.pymol.cmd.button("double_left","None","None")
        self.pymol.cmd.button("single_right","None","None")
        self.resizeGL(self.width(),self.height())

    def disableUI(self):
        #self.pymol.cmd.set("internal_gui",0)
        self.pymol.cmd.set("internal_feedback",0)
        self.pymol.cmd.button("double_left","None","None")
        self.pymol.cmd.button("single_right","None","None")
        self.resizeGL(self.width(),self.height())

    def __del__(self):
        pass

    def pymol_feedback(self):
        pass
    def _updateGlobalSettings(self):
        #for k,v in globalSettings.settings.iteritems():
        #    self.pymol.cmd.set(k, v)
        #self.update()
        return

    def redoSizing(self):
        self.resizeGL(self.width(), self.height())

    def paintGL(self):
        glViewport(0,0,self.width(), self.height())
        bottom = self.mapToGlobal(QtCore.QPoint(0,self.height())).y()
        #self.pymol.cmd.set("_stencil_parity", bottom & 0x1)
        self._doIdle()
        self.pymol.draw()
    def keyPressEvent(self, ev):
        print ev.key()
        pymol2.PyMOL.parse(ev.key())
        pass
    
    def mouseMoveEvent(self, ev):
        self.pymol.drag(ev.x(), self.height()-ev.y(),0)
        self._pymolProcess()

    def mousePressEvent(self, ev):
        if not self._enableUi:
            self.pymol.cmd.button("double_left","None","None")
            self.pymol.cmd.button("single_right","None","None")
        self.pymol.button(self._buttonMap[ev.button()], 0, ev.x(),
self.height()-ev.y(),0)
        self._pymolProcess()
        #print self.pymol.cmd.get_names("all")
        #print self.pymol.cmd.get("scTIM", "active_selections")

    def mouseReleaseEvent(self, ev):
        self.pymol.button(self._buttonMap[ev.button()], 1, ev.x(),
self.height()-ev.y(),0)
        self._pymolProcess()
        self._timer.start(0)
        my_dict={"list":[]}
        self.cmd.iterate("(sele)","list.append((resi,resn))",space=my_dict)
        #print my_dict["list"]
        l=[]
        for i in my_dict["list"]:
            try:
                l.index(i)
            except ValueError:
                l.append(i)
        self._call_selected(l)

    def resizeGL(self, w, h):
        self.pymol.reshape(w,h, True)
        self._pymolProcess()

    def initializeGL(self):
        pass

    def _pymolProcess(self):
        self._doIdle()
        self.update()
    def _doIdle(self):
        if self.pymol.idle():
            self._timer.start(0)
    def register_callback(self, func):
        self._call_selected = func
    def setStatus(self):
        pass
    def show_resi(self, resi_id):
        self.cmd.show("sticks", "(resi %d)"%resi_id)
        self._pymolProcess()
        self.update()
    def get_all_resi(self):
        my_dict={"list":[]}
        n = self.cmd.get_names()
        self.cmd.iterate("(%s)"% n[0],"list.append((resi,resn))",space=my_dict)
        l=[]
        for i in my_dict["list"]:
            try:
                l.index(i)
            except ValueError:
                l.append(i)
        return l
    def color_obj(self,rainbow=0):
        """

AUTHOR

        Gareth Stockwell

USAGE

        color_obj(rainbow=0)

        This function colours each object currently in the PyMOL heirarchy
        with a different colour.  Colours used are either the 22 named
        colours used by PyMOL (in which case the 23rd object, if it exists,
        gets the same colour as the first), or are the colours of the rainbow

SEE ALSO

        util.color_objs()
        """

        # Process arguments
        rainbow = int(rainbow)

        # Get names of all PyMOL objects
        obj_list = self.cmd.get_names('objects')

        if rainbow:

            nobj = len(obj_list)

            # Create colours starting at blue(240) to red(0), using intervals
            # of 240/(nobj-1)
            for j in range(nobj):
                hsv = (240-j*240/(nobj-1), 1, 1)
                # Convert to RGB
                rgb = hsv_to_rgb(hsv)
                # Define the new colour
                self.cmd.set_color("col" + str(j), rgb)
                # Colour the object
                self.cmd.color("col" + str(j), obj_list[j])

        else:


           # List of available colours
            colours = ['red', 'green', 'blue', 'yellow', 'violet', 'cyan',    \
            'salmon', 'lime', 'pink', 'slate', 'magenta', 'orange', 'marine', \
            'olive', 'purple', 'teal', 'forest', 'firebrick', 'chocolate',    \
            'wheat', 'white', 'grey' ]
            ncolours = len(colours)
            all_residues = self.get_all_resi()
            # Loop over objects
            i = 0
            for obj in all_residues:
                self.cmd.color(get_color(obj[1]), "resi %s"%obj[0])
                i = i+1
                if(i == ncolours):
                    i = 0


# You don't need anything below this
class PyMolWidgetDemo(QtGui.QMainWindow):
     def __init__(self):
         QtGui.QMainWindow.__init__(self)
         widget = PymolQtWidget(self,True,"../data/scTIM.pdb")
         self.setCentralWidget(widget)

if __name__ == '__main__':
     app = QtGui.QApplication(['PyMol Widget Demo'])
     window = PyMolWidgetDemo()
     window.show()
     app.exec_()

def hsv_to_rgb(hsv):
        h = float(hsv[0])
        s = float(hsv[1])
        v = float(hsv[2])

        if( s == 0 ) :
                #achromatic (grey)
                r = g = b = v

        else:
                # sector 0 to 5
                h = h/60.
                i = int(h)
                f = h - i                       # factorial part of h
                #print h,i,f
                p = v * ( 1 - s )
                q = v * ( 1 - s * f )
                t = v * ( 1 - s * ( 1 - f ) )

                if i == 0:
                        (r,g,b) = (v,t,p)
                elif i == 1:
                        (r,g,b) = (q,v,p)
                elif i == 2:
                        (r,g,b) = (p,v,t)
                elif i == 3:
                        (r,g,b) = (p,q,v)
                elif i == 4:
                        (r,g,b) = (t,p,v)
                elif i == 5:
                        (r,g,b) = (v,p,q)
                else:
                        (r,g,b) = (v,v,v)
                        print "error, i not equal 1-5"

        return [r,g,b]
