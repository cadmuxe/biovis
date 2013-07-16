__author__ = 'cadmuxe'
from PySide import QtCore, QtGui, QtOpenGL

class color(object):
    gray = QtCore.Qt.gray
    black = QtCore.Qt.black
    red = QtCore.Qt.red
    gree = QtCore.Qt.green
    def __getattribute__(self, item):
        return self.item


class MyPaintWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setBackgroundRole(QtGui.QPalette.Base)

        # {id:[color], 1:[red,green, ...]}  id: sequences id, color: the color for each amino acid.
        self.sequences={"len":0, "max_len_freg":0}
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        # whether to redraw the cache
        self.__TIMs_redraw = True
        # mouse on which sequence and fregment
        self.on_sequences_id = None
        self.on_freg_id = None

        self.__callback={} # callback function,  mouse_click, mouse_over

        # current scroll postion 0-1.0
        self.__scroll_button_position = 0.0

    def __update_size_info(self):
        """
        update size information which will used for drawing
        """
        # Original TIMs QPixmap size

        self.__wiget_height = self.size().height()
        self.__wiget_width = self.size().width()

        self.__scrollbar_width = 40
        self.__scrollbar_height = self.__wiget_height
        self.__scrollbar_postion_x = self.__wiget_width -  self.__scrollbar_width
        self.__scrollbar_postion_y = 0 # not really used


        self.__TIMs_cache_height = self.__TIMs_cache.size().height()
        self.__TIMs_cache_width = self.__TIMs_cache.size().width() - self.__scrollbar_width

        self.__TIMs_cache_scrollbar = self.__TIMs_cache.scaled(self.__scrollbar_width,self.__scrollbar_height)
        self.__TIMs_cache = self.__TIMs_cache.scaled(self.__TIMs_cache_width,self.__TIMs_cache_height)


        self.__scroll_button_height = self.__wiget_height * self.__wiget_height/self.__TIMs_cache_height



    def paintEvent(self, event):
        self.paint_freg_heigh = 2
        self.paint_freg_width = event.rect().width() / self.sequences["max_len_freg"]   # assume all the sequences have the same length

        # cache the result
        if self.__TIMs_redraw:
            self.__TIMs_cache = QtGui.QPixmap(event.rect().width(), self.sequences["len"]*self.paint_freg_heigh)
            self.__TIMs_cache.fill(QtCore.Qt.white)
            painter = QtGui.QPainter(self.__TIMs_cache)
            #painter.begin(self.__TIMs_cache)
            painter.setPen(QtCore.Qt.NoPen)
            for x in range(0,self.sequences["len"]):
                for y in range(0, len(self.sequences[x])):
                    painter.setBrush(self.sequences[x][y])
                    painter.drawRect(y * self.paint_freg_width, x*self.paint_freg_heigh,
                                     self.paint_freg_width, self.paint_freg_heigh)
            painter.end()
            self.__TIMs_redraw = False
            self.__update_size_info()

        painter = QtGui.QPainter(self)
        #painter.begin(self)
        painter.drawPixmap(0,0, self.__TIMs_cache)

        # draw scroll bar
        painter.setOpacity(0.5)
        painter.drawPixmap(self.__scrollbar_postion_x, self.__scrollbar_postion_y, self.__TIMs_cache_scrollbar)
        painter.setOpacity(1)

        # draw scroll button
        painter.drawPixmap(self.__scrollbar_postion_x, (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                           self.__TIMs_cache_scrollbar,
                           0, (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                           self.__scrollbar_width, self.__scroll_button_height)
        print((self.__scrollbar_postion_x, (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                           0, (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                           self.__scrollbar_width,self.__scroll_button_height))


        if self.on_sequences_id != None:
            painter.setPen(QtCore.Qt.NoPen)
            for y in range(0, len(self.sequences[self.on_sequences_id])):
                painter.setBrush(self.sequences[self.on_sequences_id][y])
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
        """
        update the color of a sequence.
        new_color_list: the color list describe the sequence.
        """
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