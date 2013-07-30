# import sys
# from xml.dom.minidom import *
# import urllib
# import xml.etree.cElementTree as ET
# 
# xmlurl = 'http://www.uniprot.org/uniprot/'
# xmlpath = xmlurl + 'Q0ZHJ1.xml'
# try:
#     xml = urllib.urlopen(xmlpath)
#     tree = ET.ElementTree(xml)
#     root = tree.getroot()
#     for child_of_root in root:
#         print child_of_root
#         
# except Exception as e:
#     print(e)
#     sys.exit(0)

import sys
from PySide.QtGui import *
from PySide.QtWebKit import *

class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.loadFinished.connect(self._result_available)

    def _result_available(self, ok):
        frame = self.page().mainFrame()
        #print unicode(frame.toHtml()).encode('utf-8')
