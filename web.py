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
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

class Browser(QWebView):

    def __init__(self, PDB, FASTA):
        
        QWebView.__init__(self)
        
        self.PDB = PDB
        self.FASTA = FASTA
        
        print self.PDB + " " + self.FASTA
        
        self.loadFinished.connect(self._result_available)

    def _result_available(self, ok):
        frame = self.page().mainFrame()
        #print unicode(frame.toHtml()).encode('utf-8')

    def contextMenuEvent(self, event):  
        
        self.me = QMenu(self)
        
        url = self.url().toString()
        
        actionPDB = QAction('PDB', self)
        actionPDB.triggered.connect( self.on_item_clicked )
        
        if url[:23] == "http://www.rcsb.org/pdb":
            actionPDB.setDisabled(True)
        
        actionUni = QAction('UniProt', self)
        actionUni.triggered.connect( self.on_item_clicked ) 
        
        if url[:22] == "http://www.uniprot.org":
            actionUni.setDisabled(True)
        
        actionMod = QAction('ModBase', self)
        actionMod.triggered.connect( self.on_item_clicked )
        
        if url[:7] == "modbase":
            actionMod.setDisabled(True)
        
        self.me.addAction(actionUni)
        self.me.addAction(actionPDB)
        self.me.addAction(actionMod)
        
        self.me.exec_(self.mapToGlobal(QPoint(event.x(),event.y())))
    
    def on_item_clicked(self):
        selected = self.sender().text()
        
        if selected == "PDB":
            self.setUrl("http://www.rcsb.org/pdb/explore/explore.do?structureId=" + self.PDB)
        elif selected == "UniProt":
            self.setUrl("http://www.uniprot.org/uniprot/" + self.FASTA )
        elif selected == "ModBase":
            self.setUrl("http://salilab.org/modbase-cgi/model_search.cgi?searchkw=name&kword=" + self.FASTA)
        