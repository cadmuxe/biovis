from PySide import QtCore, QtGui, QtOpenGL
from random import choice

class color(object):
    gray = QtCore.Qt.gray
    black = QtCore.Qt.black
    red = QtCore.Qt.red
    green = QtCore.Qt.green
    blue = QtCore.Qt.blue
    cyan = QtCore.Qt.cyan

    red1 = QtGui.QColor(128,35,41)
    red2 = QtGui.QColor(148,28,52)
    red3 = QtGui.QColor(193,61,105)
    red4 = QtGui.QColor(220,118,160)
    red5 = QtGui.QColor(236,168,200)

    c1 = QtGui.QColor(178, 24, 43)
    c2 = QtGui.QColor(33, 102, 172)
    c3 = QtGui.QColor(239, 138, 98)
    c4 = QtGui.QColor(103, 169, 207)
    c5 = QtGui.QColor(253, 219, 199)
    c6 = QtGui.QColor(209, 229, 240)

    white = QtGui.QColor(251, 255, 244)
    tetrad_red = QtGui.QColor(255, 49, 0)
    tetrad_yellow = QtGui.QColor(255, 135, 0)
    tetrad_blue = QtGui.QColor(7, 114, 161)
    tetrad_green = QtGui.QColor(0, 183, 74)
    pink = QtGui.QColor(253, 219, 199)




    @staticmethod
    def  random(not_color):
        """
        pick an random color which is not not_color
        """
        c = not_color
        while c == not_color:
            c = choice([color.green, color.blue, color.cyan])
        return c


class MyPaintWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setBackgroundRole(QtGui.QPalette.Base)

        # {id:[color], 1:[red,green, ...]}  id: sequences id, color: the color for each amino acid.
        self.sequences={"len":0, "max_len_frag":0}
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        # whether to redraw the cache
        self.__TIMs_redraw = True
        # mouse on which sequence and fragment
        self.on_sequences_id = 0
        self.on_frag_id = 0

        self.__callback={} # callback function,  mouse_click, mouse_over

        # current scroll postion 0-1.0
        self.__scroll_button_position = 0.0
        self.cursor_button = QtCore.Qt.MouseButton.NoButton

        self.__scroll_button_position_horA = 0.0
        self.__scroll_button_position_horB = 1.0
        self.__horizontal_selection_element_num = 5

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
        self.__TIMs_cache_width = self.__widget_width - self.__scrollbar_width

        # scrollbar is a thumbnail of TIMs image.
        self.__TIMs_cache_scrollbar = self.__TIMs_cache.scaled(self.__scrollbar_width,self.__scrollbar_height)
        self.__TIMs_cache = self.__TIMs_cache.scaled(self.__TIMs_cache_width,self.__TIMs_cache_height)

        # the height of scroll button is depend on the height of widget and the length of TIMs image
        self.__scroll_button_height = self.__widget_height * self.__widget_height/self.__TIMs_cache_height

        self.__scrollabr_button_width_hor = self.__horizontal_selection_element_num * self.__TIMs_cache_width / self.sequences["max_len_frag"]



    def paintEvent(self, event):
        self.paint_frag_heigh = 2
        # assume all the sequences have the same length
        self.paint_frag_width = event.rect().width() / self.sequences["max_len_frag"]   

        # cache the result (TIMs image)
        if self.__TIMs_redraw:
            self.__TIMs_cache = QtGui.QPixmap(self.paint_frag_width * self.sequences["max_len_frag"], self.sequences["len"]*self.paint_frag_heigh)
            self.__TIMs_cache.fill(QtCore.Qt.white)
            painter = QtGui.QPainter(self.__TIMs_cache)
            #painter.begin(self.__TIMs_cache)
            painter.setPen(QtCore.Qt.NoPen)
            for x in range(0,self.sequences["len"]):
                for y in range(0, len(self.sequences[x])):
                    painter.setBrush(self.sequences[x][y])
                    painter.drawRect(y * self.paint_frag_width, x*self.paint_frag_heigh,
                                     self.paint_frag_width, self.paint_frag_heigh)
            painter.end()
            self.__TIMs_redraw = False
            self.__update_size_info()

        painter = QtGui.QPainter(self)
        # draw TIMs
        painter.setOpacity(0.4)
        painter.drawPixmap(0,0,
                           self.__TIMs_cache,
                           0,(self.__TIMs_cache_height-self.__widget_height)*self.__scroll_button_position,
                           self.__widget_width, self.__widget_height)
        painter.setOpacity(1.0)
        # draw scroll bar
        painter.setOpacity(0.4)
        painter.drawPixmap(self.__scrollbar_postion_x, self.__scrollbar_postion_y, self.__TIMs_cache_scrollbar)
        painter.setOpacity(1)

        # draw scroll button
        # the parameters of drawPixmap are (position_x, position_y, pixmap, offest_x, offset_y, width, height).
        # offest: the start point of pixmap, from the top left
        painter.drawPixmap(self.__scrollbar_postion_x, 
                (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                self.__TIMs_cache_scrollbar,
                0, (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                self.__scrollbar_width, self.__scroll_button_height)

        # draw outline of scroll button
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtCore.Qt.green)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(self.__scrollbar_postion_x,
                (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position,
                self.__scrollbar_width,self.__scroll_button_height)

        # draw outline of horizontal scroll button
        # horA
        pen.setColor(QtCore.Qt.green)
        painter.setPen(pen)
        painter.drawRect((self.__TIMs_cache_width-self.__scrollabr_button_width_hor*0.5)*self.__scroll_button_position_horA, 0,
                self.__scrollabr_button_width_hor*0.5,self.__TIMs_cache_height)
        painter.drawPixmap((self.__TIMs_cache_width-self.__scrollabr_button_width_hor*0.5)*self.__scroll_button_position_horA, 0,
                self.__TIMs_cache,
               (self.__TIMs_cache_width-self.__scrollabr_button_width_hor*0.5)*self.__scroll_button_position_horA,
               (self.__TIMs_cache_height-self.__widget_height)*self.__scroll_button_position,
                self.__scrollabr_button_width_hor*0.5,self.__TIMs_cache_height)

        # horB
        pen.setColor(QtCore.Qt.blue)
        painter.setPen(pen)
        painter.drawRect((self.__TIMs_cache_width-self.__scrollabr_button_width_hor*0.5)*self.__scroll_button_position_horB, 0,
                self.__scrollabr_button_width_hor*0.5,self.__TIMs_cache_height)
        painter.drawPixmap((self.__TIMs_cache_width-self.__scrollabr_button_width_hor*0.5)*self.__scroll_button_position_horB, 0,
                self.__TIMs_cache,
               (self.__TIMs_cache_width-self.__scrollabr_button_width_hor*0.5)*self.__scroll_button_position_horB,
               (self.__TIMs_cache_height-self.__widget_height)*self.__scroll_button_position,
                self.__scrollabr_button_width_hor*0.5,self.__TIMs_cache_height)


        # draw a rectangle on current mouse position
        if self.on_sequences_id != None:
            painter.setPen(QtCore.Qt.NoPen)
            selection = QtGui.QPixmap(self.paint_frag_width * self.sequences["max_len_frag"], 10)
            selection.fill(QtCore.Qt.white)
            painter_s = QtGui.QPainter(selection)
            painter_s.setPen(QtCore.Qt.NoPen)
            for y in range(0, len(self.sequences[self.on_sequences_id])):
                painter_s.setBrush(self.sequences[self.on_sequences_id][y])
                painter_s.drawRect(y * self.paint_frag_width, 0,
                                 self.paint_frag_width, 10)
            painter_s.setPen(QtCore.Qt.white)
            painter_s.setBrush(QtCore.Qt.NoBrush)
            painter_s.drawRect(0,0,self.__TIMs_cache_width, 9)
            painter_s.end()
            new_selection = selection.scaled(self.__TIMs_cache_width,10)
            painter.drawPixmap(0,self.on_sequences_id * self.paint_frag_heigh- \
                    (self.__TIMs_cache_height-self.__widget_height)*self.__scroll_button_position, new_selection)
        painter.end()

    def mousePressEvent(self,event):
        x,y = event.x(),event.y()
        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()
        self.cursor_button = event.button()
        if self.cursor_button == QtCore.Qt.MouseButton.LeftButton:
            if (self.__TIMs_cache_width - self.__scrollabr_button_width_hor*0.5) * self.__scroll_button_position_horA < x \
                        < ((self.__TIMs_cache_width - self.__scrollabr_button_width_hor*0.5) * self.__scroll_button_position_horA + self.__scrollabr_button_width_hor*0.5) \
                and x < self.__scrollbar_postion_x:
                self.hit = "horA"
            elif (self.__TIMs_cache_width - self.__scrollabr_button_width_hor*0.5) * self.__scroll_button_position_horB < x \
                        < ((self.__TIMs_cache_width - self.__scrollabr_button_width_hor*0.5) * self.__scroll_button_position_horB + self.__scrollabr_button_width_hor*0.5) \
                and x < self.__scrollbar_postion_x:
                self.hit = "horB"
            # sequences selection
            else:
                self.hit = "seq"
            # sequence scrollbar
            if (self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position < y \
                        < ((self.__scrollbar_height- self.__scroll_button_height)*self.__scroll_button_position + self.__scroll_button_height) and \
                x > self.__scrollbar_postion_x:
                self.hit ="scr"

    def mouseReleaseEvent(self,event):
        if self.cursor_button == event.button():
            self.cursor_button = QtCore.Qt.MouseButton.NoButton
        self.hit = None

    def update_scroll(self,dy):
        self.__scroll_button_position +=dy
        if self.__scroll_button_position<0:
            self.__scroll_button_position = 0.0
        elif self.__scroll_button_position > 1.0:
            self.__scroll_button_position = 1.0
    def update_scroll_horA(self,dx):
        self.__scroll_button_position_horA +=dx
        if self.__scroll_button_position_horA<0:
            self.__scroll_button_position_horA = 0.0
        elif self.__scroll_button_position_horA > 1.0:
            self.__scroll_button_position_horA = 1.0
        print self.__scroll_button_position_horA,self.sequences["max_len_frag"]
    def update_scroll_horB(self,dx):
        self.__scroll_button_position_horB +=dx
        if self.__scroll_button_position_horB<0:
            self.__scroll_button_position_horB = 0.0
        elif self.__scroll_button_position_horB > 1.0:
            self.__scroll_button_position_horB = 1.0
        print self.__scroll_button_position_horB,self.sequences["max_len_frag"]

    def move_scroll_to_resi(self, resi_id):
        print (resi_id, self.sequences["max_len_frag"])
        d = resi_id/ float(self.sequences["max_len_frag"])
        self.__scroll_button_position_horB = d
        if self.__scroll_button_position_horB<0:
            self.__scroll_button_position_horB = 0.0
        elif self.__scroll_button_position_horB > 1.0:
            self.__scroll_button_position_horB = 1.0
        self.repaint()

        rAf = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horA)
        rAt = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horA + int(self.__horizontal_selection_element_num*0.5)+1)
        rBf = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horB)
        rBt = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horB + int(self.__horizontal_selection_element_num*0.5)+1)
        for f in self.__callback["barchar"]:
            f(rAf,rAt,rBf,rBt,self.on_sequences_id,self.on_frag_id)

    def mouseMoveEvent(self,event):
        x,y = event.x(),event.y()

        if self.cursor_button == QtCore.Qt.MouseButton.LeftButton:
            # fragment selection
            if self.hit == "horA":
                d = (x-self.cursor_pre_x) * 1.0 / self.__TIMs_cache_width
                self.update_scroll_horA(d)
            elif self.hit == "horB":
                d = (x-self.cursor_pre_x) * 1.0 / self.__TIMs_cache_width
                self.update_scroll_horB(d)
            # sequences selection
            elif self.hit == "seq":
                self.on_sequences_id = int(y+(self.__TIMs_cache_height-self.__widget_height)* \
                                           self.__scroll_button_position) / self.paint_frag_heigh
                paint_frag_width = float(self.__TIMs_cache_width)/ self.sequences["max_len_frag"]
                self.on_frag_id = int(x / paint_frag_width)
                if self.on_sequences_id >= self.sequences["len"]:
                    self.on_sequences_id = self.sequences["len"] - 1
                elif self.on_sequences_id < 0:
                    self.on_sequences_id = 0
                if self.on_frag_id >= len(self.sequences[self.on_sequences_id]):
                    self.on_frag_id = len(self.sequences[self.on_sequences_id]) -1
                elif self.on_frag_id < 0:
                    self.on_frag_id = 0
                if self.__callback.has_key("seq_name"):
                    for f in self.__callback["seq_name"]:
                        f(self.sequenceData[self.on_sequences_id].name)
            # sequence scrollbar
            elif self.hit =="scr":
                d =  (y - self.cursor_pre_y) * 1.0 / self.__scrollbar_height
                self.update_scroll(d)
                self.cursor_pre_x = x
                self.cursor_pre_y = y
            self.update()
        self.cursor_pre_x = x
        self.cursor_pre_y = y

        rAf = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horA)
        rAt = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horA + int(self.__horizontal_selection_element_num*0.5)+1)
        rBf = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horB)
        rBt = int((self.sequences["max_len_frag"]-self.__horizontal_selection_element_num*0.5)* self.__scroll_button_position_horB + int(self.__horizontal_selection_element_num*0.5)+1)
        for f in self.__callback["barchar"]:
            f(rAf,rAt,rBf,rBt,self.on_sequences_id,self.on_frag_id)



    def update_color(self,sequence_id, new_color_list):
        """
        update the color of a sequence.
        new_color_list: the color list describe the sequence.
        """
        self.sequences[sequence_id] = new_color_list
        self.sequences["len"] = len(self.sequences) - 2
        if self.sequences["max_len_frag"] < len(self.sequences[sequence_id]):
            self.sequences["max_len_frag"] = len(self.sequences[sequence_id])


    def update_frag_color(self, sequence_id, frag_id, color):
        if not self.sequences.has_key(sequence_id):
            self.sequences[sequence_id] = []
        try:
            self.sequences[sequence_id][frag_id] = color
        except IndexError:
            self.sequences[sequence_id].append(color)
        self.sequences["len"] = len(self.sequences) - 2
        if self.sequences["max_len_frag"] < len(self.sequences[sequence_id]):
            self.sequences["max_len_frag"] = len(self.sequences[sequence_id])

    def redraw_colors(self):
        self.__TIMs_redraw = True
        self.update()

    def clearColor(self):
        self.sequences={"len":0, "max_len_frag":0}
        self.redraw_colors()


    def registerClickCallBack(self, d):
        """
            register callback
            d: {"name":"name", "func":f}

            seq_name: get current sequence name
                     f(seq_name)
            frag_name: get current frag_name and id
                     f(frag_name, id)
            for seq_name and frag_name you can register more than one
            callback function

            barchar: using for updating the barchar.
        """
        if d["name"] not in self.__callback:
            self.__callback[d["name"]] = []
        self.__callback[d["name"]].append(d["func"])

    def resizeEvent(self, *args, **kwargs):
        self.__TIMs_redraw = True

    def set_sequenceData(self,sequence):
        self.sequenceData = sequence
