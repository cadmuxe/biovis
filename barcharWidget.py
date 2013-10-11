from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class barcharWidget(QtGui.QWidget):
    """
    generate a small multiple of barchar for a set of fragment 
    """
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.per_width = 0
        self.per_height = 0

        self.barchar_width = 15

        self.cal_size()

    def update_sequences(self, frag_id_from, frag_id_to, frags, barchar_data):
        """
        """
        # (frag_id, frag, barchar_data)
        self.frags = zip(range(frag_id_from, frag_id_to + 1), frags, barchar_data)
        self.cal_size()
        self.update()

    def cal_size(self):
        try:
            self.per_width = self.size().width() / len(self.frags)
            self.per_height = self.size().height() / 5.0
        except (AttributeError, ZeroDivisionError):
            pass

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        for i in range(len(self.frags)):
            x = i * self.per_width + 0.25 * self.per_width
            y = self.per_height * 0.5
            # draw frag_id
            painter.setPen(Qt.black)
            painter.drawText(x, y, self.per_width, self.per_height,
                    Qt.AlignCenter, str(self.frags[i][0]))

            # draw frag
            y+= self.per_height
            painter.drawText(x, y, self.per_width, self.per_height,
                    Qt.AlignCenter, self.frags[i][1])

            # draw barchar
            # draw outline
            y += self.per_height
            painter.setPen(Qt.black)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(x + 0.5*self.per_width - 0.5 *self.barchar_width, y, self.barchar_width, self.per_height * 2.0)
            # draw percent
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.blue)
            painter.drawRect(x + 0.5*self.per_width - 0.5 *self.barchar_width, y + self.per_height *2.0,
                    self.barchar_width, -self.per_height*self.frags[i][2]*2.0)
        painter.end()

    def resizeEvent(self, event):
        self.cal_size()


