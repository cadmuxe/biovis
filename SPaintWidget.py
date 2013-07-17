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
        self.cursor_button = QtCore.Qt.MouseButton.NoButton

    def __update_size_info(self):
        """
        update size information which will used for drawing
        """
        # Original TIMs QPixmap size

        self.__widget_height = self.size().height()
        self.__widget_width = self.size().width()

        self.__scrollbar_width = 40
        self.__scrollbar_height = self.__widget_height
        self.__scrollbar_postion_x = self.__widget_width -  self.__scrollbar_width
        self.__scrollbar_postion_y = 0 # not really used

        # used for scaling, let the TIMs image become a little small, so that have enough space for scrollbar
        self.__TIMs_cache_height = self.__TIMs_cache.size().height()
        self.__TIMs_cache_width = self.__TIMs_cache.size().width() - self.__scrollbar_width

        # scrollbar is a thumbnail of TIMs image.
        self.__TIMs_cache_scrollbar = self.__TIMs_cache.scaled(self.__scrollbar_width,self.__scrollbar_height)
        self.__TIMs_cache = self.__TIMs_cache.scaled(self.__TIMs_cache_width,self.__TIMs_cache_height)

        # the height of scroll button is depend on the height of widget and the length of TIMs image
        self.__scroll_button_height = self.__widget_height * self.__widget_height/self.__TIMs_cache_height



    def paintEvent(self, event):
        self.paint_freg_heigh = 2
        self.paint_freg_width = event.rect().width() / self.sequences["max_len_freg"]   # assume all the sequences have the same length

        # cache the result (TIMs image)
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
        # draw TIMs
        painter.drawPixmap(0,0,
                           self.__TIMs_cache,
                           0,(self.__TIMs_cache_height-self.__widget_height)*self.__scroll_button_position,
                           self.__widget_width, self.__widget_height)

        # draw scroll bar
        painter.setOpacity(0.5)
        painter.drawPixmap(self.__scrollbar_postion_x, self.__scrollbar_postion_y, self.__TIMs_cache_scrollbar)
        painter.setOpacity(1)

        # draw scroll button
        # the parameters of drawPixmap are (position_x, position_y, pixmap, offest_x, offset_y, width, height).
        # offest: the start point of pixmap, from the top left
        painter.drawPixmap(self.__scrollbar_postion_x, (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                           self.__TIMs_cache_scrollbar,
                           0, (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                           self.__scrollbar_width, self.__scroll_button_height)

        # draw outline of scroll button
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtCore.Qt.green)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(self.__scrollbar_postion_x,(self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                         self.__scrollbar_width,self.__scroll_button_height)

        # draw a rectangle on current mouse position
        if self.on_sequences_id != None:
            painter.setPen(QtCore.Qt.NoPen)
            selection = QtGui.QPixmap(self.__widget_width, 10)
            selection.fill(QtCore.Qt.white)
            painter_s = QtGui.QPainter(selection)
            painter_s.setPen(QtCore.Qt.NoPen)
            for y in range(0, len(self.sequences[self.on_sequences_id])):
                painter_s.setBrush(self.sequences[self.on_sequences_id][y])
                painter_s.drawRect(y * self.paint_freg_width, 0,
                                 self.paint_freg_width, 10)
            painter_s.setPen(QtCore.Qt.white)
            painter_s.setBrush(QtCore.Qt.NoBrush)
            painter_s.drawRect(0,0,self.__TIMs_cache_width, 9)
            painter_s.end()
            new_selection = selection.scaled(self.__TIMs_cache_width,10)
            painter.drawPixmap(0,self.on_sequences_id * self.paint_freg_heigh-(self.__TIMs_cache_height-self.__widget_height)*self.__scroll_button_position, new_selection)
        painter.end()

    def mousePressEvent(self,event):
        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()
        self.cursor_button = event.button()

    def mouseReleaseEvent(self,event):
        if self.cursor_button == event.button():
            self.cursor_button = QtCore.Qt.MouseButton.NoButton

    def update_scroll(self,dy):
        self.__scroll_button_position +=dy
        if self.__scroll_button_position<0:
            self.__scroll_button_position = 0.0
        elif self.__scroll_button_position > 1.0:
            self.__scroll_button_position = 1.0

    def mouseMoveEvent(self,event):
        x,y = event.x(),event.y()

        # draw selection rectangle
        if x < self.__scrollbar_postion_x:
            self.on_sequences_id = int(y+(self.__TIMs_cache_height-self.__widget_height)*self.__scroll_button_position) / self.paint_freg_heigh
            self.on_freg_id = x / self.paint_freg_width
            if self.on_sequences_id >= self.sequences["len"]:
                self.on_sequences_id = self.sequences["len"] - 1
            if self.on_freg_id >= len(self.sequences[self.on_sequences_id]):
                self.on_freg_id = len(self.sequences[self.on_sequences_id]) -1
            print (self.on_sequences_id,self.on_freg_id)

        elif self.cursor_button == QtCore.Qt.MouseButton.LeftButton:
            if (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position < y \
                        < ((self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position + self.__scroll_button_height):
                d =  (y - self.cursor_pre_y) /150.0
                print d
                self.update_scroll(d)
                self.cursor_pre_x = x
                self.cursor_pre_y = y

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

    def redraw_colors(self):
        self.__TIMs_redraw = True
        self.update()


    def registerClickCallBack(self, d):
        self.__callback[d["name"]] = d["func"]
    def resizeEvent(self, *args, **kwargs):
        self.__TIMs_redraw = True