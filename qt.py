#!/usr/bin/env python -W ignore::DeprecationWarning
import sys

from web import Browser
from vis import * # includes QT and openGL imports
from sequenceSet import sequenceSet
from barcharWidget import barcharWidget
import MySQLdb as mdb
import dbinfo as DB
from pymolWidget import PymolQtWidget

# Class that handles the mouse event filters 
# to link the views
class MyEventFilter(QtCore.QObject):

    # mouse press event
    pressed  = QtCore.Signal(QtCore.QEvent)
    # mouse move event
    moved    = QtCore.Signal(QtCore.QEvent)
    # mouse wheel event
    wheeled  = QtCore.Signal(QtCore.QEvent)
    # context menu event for Viewer
    context = QtCore.Signal(Viewer.GLViewer, QtCore.QPoint)
    
    def __init__(self):
        super(MyEventFilter, self).__init__()
        self.press = 0

    def hit(self):
        self.press = 1

    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.ContextMenu:
            self.context.emit(obj, QtGui.QCursor.pos())
            
        return super(MyEventFilter,self).eventFilter(obj, event)

class MainWindow(QtGui.QMainWindow):
    
    __key = None
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)#, None, QtCore.Qt.WindowStaysOnTopHint)
            
        self.setWindowTitle("2013 BioVis Contest")
        #self.resize(1280, 1024)
        self.resize(640, 512)
        
        info = DB.getInfo()
        self.db = None
        
        try:
            # Open database connection
            self.db = mdb.connect( info["host"], info["username"],
                info["password"], info["dbName"])
            # 
            # prepare a cursor object using cursor() method
            self.cursor = self.db.cursor()
            # 
            # sql = """SELECT l.FASTA FROM lookup l WHERE l.PDB ='2YPI' """
            # self.cursor.execute(sql)
            # fasta = self.cursor.fetchone()
            
            self.PDB = "2YPI"
            self.FASTA = "P00942" #fasta[0]
            
        except mdb.Error, e:
            print e
            exit(1)
        
        self.centralWidget = QtGui.QWidget(self)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        
        #self.glWidgetSC = GLWidget("./data/C7JHB8_ACEP3.B99990002.pdb", self.centralWidget)
        self.glWidgetSC = PymolQtWidget(self.centralWidget, False, File="./data/C7JHB8_ACEP3.B99990002.pdb")
        #self.glWidgetD = GLWidget("./data/scTIM.pdb", self.centralWidget)
        self.glWidgetD = PymolQtWidget(self.centralWidget, False,File="./data/scTIM.pdb")

        self.dTIMList = ListWidget(self.centralWidget)
        self.scTIMList = ListWidget(self.centralWidget)
        self.TIMs = MyPaintWidget(self.centralWidget)
        self.barchar = barcharWidget(self.centralWidget)

        self.dTIMLabel = QtGui.QLabel("dTIM")
        self.scTIMlabel = QtGui.QLabel("scTIM")
        
        self.view1 = QtGui.QTabWidget(self)
        self.browser1 = Browser(self.PDB, self.FASTA)
        self.browser1.load( 'http://www.rcsb.org/pdb/explore/explore.do?structureId=2YPI' )
        
        self.view2 = QtGui.QTabWidget(self)
        self.browser2 = Browser(self.PDB, self.FASTA)
        self.browser2.load( 'http://www.rcsb.org/pdb/explore/explore.do?structureId=2YPI' )
        
        #settings = QtWebKit.QWebSettings.globalSettings()
        #settings.setFontFamily(QtWebKit.QWebSettings.StandardFont, 'Times New Roman')
        #self.browser.settings().setFontSize(QtWebKit.QWebSettings.DefaultFontSize, 8)
        
        self.view1.addTab(self.glWidgetSC,"scTIM")
        self.view1.addTab( self.browser1,"dTIM Ref.")
        
        self.view2.addTab(self.glWidgetD,"dTIM")
        self.view2.addTab( self.browser2,"scTIM Ref.")
        
        self.gridlayout.addWidget(self.view1, 0, 1, 2, 1)
        self.gridlayout.addWidget(self.view2, 0, 0, 2, 1)

        self.gridlayout.addWidget(self.dTIMLabel, 0, 2, 1, 1)
        self.gridlayout.addWidget(self.dTIMList, 1, 2, 1, 1)

        self.gridlayout.addWidget(self.scTIMlabel, 0, 3, 1, 1)
        self.gridlayout.addWidget(self.scTIMList, 1, 3, 1, 1)

        self.gridlayout.addWidget(self.TIMs, 2, 0, 1, 4)
        self.gridlayout.addWidget(self.barchar, 3, 0, 1, 4)

        self.gridlayout.setColumnStretch(0,15)
        self.gridlayout.setColumnStretch(1,15)
        self.gridlayout.setColumnStretch(2,1)
        self.gridlayout.setColumnStretch(3,1)

        self.gridlayout.setRowStretch(0,0)
        self.gridlayout.setRowStretch(1,4)
        self.gridlayout.setRowStretch(2,3)
        self.gridlayout.setRowStretch(3,1)

        self.setCentralWidget(self.centralWidget)
        
        # create the event filter
        #self.myEF = MyEventFilter()
         
        # link  to each widgets mouse events
        #self.myEF.pressed.connect(self.pressEvent)
        #self.myEF.moved.connect(self.moveEvent)
        #self.myEF.wheeled.connect(self.myWheelEvent)
        
        # link event filter to context menu
        #self.glWidgetSC.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.glWidgetD.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        #self.myEF.context.connect(self.on_context_menu)
        
        # install the new event filter
        #self.glWidgetSC.installEventFilter(self.myEF)
        #self.glWidgetD.installEventFilter(self.myEF)

        self.color_scheme = ColorWidget()
        self.initActions()
        self.initListWidget()
        self.initTIMs()
        self.initMenus()
        self.barchar.update_sequences(zip(range(9), "ADGDEDSFE",[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] ), 5,4)
        
        self.TIMs.registerClickCallBack({"name":"barchar","func":self.barchar_update})
        
        def print_name(name):
            self.selected_sequence_name =  name
            self.updateStatusBar()
        
        self.TIMs.registerClickCallBack({"name":"seq_name", "func":print_name})
        
        self.TIMs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.TIMs, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_TIM_menu)
        
    def ready(self):
        # ready to render
        self.glWidgetSC.setStatus()
        self.glWidgetD.setStatus()
    
    def on_TIM_menu(self, point):
        
        fasta =  self.selected_sequence_name[:6]
        model = 0
        
        sql = "SELECT l.PDBCode, l.ModelID FROM modbase l WHERE l.FASTA = "
        sql += """'""" + fasta + """'"""
        
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
                
        # create context menu content
        timMenu = QtGui.QMenu(self)
        
        for row in result:
            if int(row[1]) > 0:
                model = 1
                
        if model > 0:
                
            options = QtGui.QAction('View 3D Model', self)
            options.triggered.connect( self.on_tim_clicked ) 
            timMenu.addAction(options)
            
            self.selected_PDB = row[0]
            
        else:
            options = QtGui.QAction('No Model Generated', self)
            options.triggered.connect( self.on_tim_clicked ) 
            options.setDisabled(True)
            
            timMenu.addAction(options)
        
        timMenu.exec_(QtGui.QCursor.pos())
            
    def on_context_menu(self, obj, point):
        
        # create context menu content
        self.popMenu = QtGui.QMenu(self)
        options = QtGui.QAction('Show Menu', self)
        options.triggered.connect( self.on_item_clicked ) 
        self.popMenu.addAction(options)
        # self.popMenu.addSeparator()
        
        self.me = obj
        
        # show context menu
        self.popMenu.exec_(point)
        
        return
    
    # when an item in the menu is clicked
    def on_item_clicked(self):
        self.me.showEditor()
        return
    
    def on_tim_clicked(self):
       
        name = "./data/PDB/P56076_2JGQ.pdb"#str(self.selected_sequence_name[:6]) + "_" + str(self.selected_PDB) + ".pdb"
        self.PDB = "2JGQ"
        self.FASTA = "P56076"
        
        #self.glWidgetSC = None
        #self.view1.removeTab(0)
        
        self.glWidgetSC.load_struct(name)
       # glWidgetSC.
        #self.view1.insertTab(0,self.glWidgetSC, "scTIM")
        self.browser2.load( 'http://www.rcsb.org/pdb/explore/explore.do?structureId=2JGQ' )
        
        return
        
    # mouse actions
    def pressEvent(self, event):

        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()
        self.cursor_button = event.button()

    def moveEvent(self, event):

        # why the fuck is this even a thing!?
        if type(event) == QtGui.QMoveEvent:
            return

        self.cursor_pre_x = event.x()
        self.cursor_pre_y = event.y()

    def myWheelEvent(self, event):

     # why the fuck is this even a thing!?
        if type(event) == QtGui.QMoveEvent:
            return


    # keyboard actions
        
    def keyPressEvent(self,event):
        self.__key = event.key()
        
    def keyReleaseEvent(self,event):
        self.__key = None
    
    # window actions    
                                  
    def initActions(self):
        self.exitAction = QtGui.QAction('Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), self.close)
        self.glWidgetD.register_callback(self.update_dTIM_select_pymol)

    def initListWidget(self):
        # scTIMList
        self.scTIMList.itemSelectionChanged.connect(self.update_scTIM_select)
        self.scTIMList.verticalScrollBar().valueChanged.connect(self.dTIMList.verticalScrollBar().setValue)

        self.dTIMList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.dTIMList.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.dTIMList.verticalScrollBar().valueChanged.connect(self.scTIMList.verticalScrollBar().setValue)

    def update_scTIM_select(self):
        id_list =[]
        for item in self.scTIMList.selectedItems():
            id_list.append(item.get_fragment_id())
        for item in self.dTIMList.selectedItems():
            self.dTIMList.setCurrentItem(item, QtGui.QItemSelectionModel.Clear)
        for i in id_list:
            self.dTIMList.setCurrentRow(i-1,QtGui.QItemSelectionModel.Select)

    def update_dTIM_select_pymol(self,l):
        for item in l:
            self.dTIMList.setCurrentRow(int(item[0])-1,QtGui.QItemSelectionModel.Select)
            self.scTIMList.setCurrentRow(int(item[0])-1,QtGui.QItemSelectionModel.Select)
            self.glWidgetSC.show_resi(int(item[0]))
            self.glWidgetD.show_resi(int(item[0]))

        self.TIMs.move_scroll_to_resi(int(l[-1][0]))

    def initMenus(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')

        sortingMenu = menuBar.addMenu("&Sorting")
        action_frequency = sortingMenu.addAction("&Residue frequency")
        action_edit_dist = sortingMenu.addAction("&Edit distance")
        action_weighted_edit_dist = sortingMenu.addAction("&Weighted edit distance")
        action_common_resi_with_scTIM = sortingMenu.addAction("&Common residues with scTIM")
        action_normalized_common_resi_with_scTIM = sortingMenu.addAction("&Common residues with scTIM(Normalized)")
        action_number_common_resi_with_scTIM_without_posi = sortingMenu.addAction("&Common resi. with scTIM without position")
        action_percent_common_resi_with_scTIM_without_posi = sortingMenu.addAction("&Common resi. with scTIM without position%")
        action_selection = sortingMenu.addAction("Sorting and coloring by selected scTIM fragment")

        self.connect(action_frequency, QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(0))
        self.connect(action_edit_dist, QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(1))
        self.connect(action_weighted_edit_dist, QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(2))
        self.connect(action_common_resi_with_scTIM , QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(3))
        self.connect(action_normalized_common_resi_with_scTIM , QtCore.SIGNAL("triggered()"),
                     lambda: self.set_sorting(4))
        self.connect(action_number_common_resi_with_scTIM_without_posi, QtCore.SIGNAL("triggered()"),
                     lambda: self.set_sorting(5))
        self.connect(action_percent_common_resi_with_scTIM_without_posi , QtCore.SIGNAL("triggered()"),
                     lambda: self.set_sorting(6))
        self.connect(action_selection, QtCore.SIGNAL("triggered()"), lambda: self.set_sorting(7))

        coloringMenu = menuBar.addMenu("&Coloring")
        action_color_scheme = coloringMenu.addAction("&Coloring schemes")
        action_frequency_color = coloringMenu.addAction("&Frequency coloring")
        action_general_chemical = coloringMenu.addAction("&General chemical coloring")
        action_side_chain_polarity = coloringMenu.addAction("&Side-chain polarity coloring")
        action_side_chain_charge = coloringMenu.addAction("&Side-chain charge coloring(pH7.4)")
        action_side_chain_solvent = coloringMenu.addAction("&Side-chain polar solvent")
        action_common_with_scTIM = coloringMenu.addAction("&Common fragment with scTIM")

        self.connect(action_frequency_color, QtCore.SIGNAL("triggered()"), lambda: self.set_coloring(1))
        self.connect(action_general_chemical, QtCore.SIGNAL("triggered()"), lambda: self.set_coloring(2))
        self.connect(action_side_chain_polarity, QtCore.SIGNAL("triggered()"), lambda: self.set_coloring(3))
        self.connect(action_side_chain_charge, QtCore.SIGNAL("triggered()"), lambda: self.set_coloring(4))
        self.connect(action_side_chain_solvent, QtCore.SIGNAL("triggered()"), lambda: self.set_coloring(5))
        self.connect(action_common_with_scTIM, QtCore.SIGNAL("triggered()"), lambda:self.set_coloring(6))
        self.connect(action_color_scheme, QtCore.SIGNAL("triggered()"), lambda:self.color_scheme.show())

        viewMenu = menuBar.addMenu("&View")
        showUI = viewMenu.addAction("&Show Menu")
        hideUI = viewMenu.addAction("&Hide Menu")
        self.connect(showUI, QtCore.SIGNAL("triggered()"), self.showUI)
        self.connect(hideUI, QtCore.SIGNAL("triggered()"), self.hideUI)


        self.setMenuBar(menuBar)
    def showUI(self):
        self.glWidgetD.enableUI()
        self.glWidgetSC.enableUI()
    def hideUI(self):
        self.glWidgetD.disableUI()
        self.glWidgetSC.disableUI()

    def set_sorting(self, n):
        if n == 0:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_frag_frequency
            self.current_sortting["name"] = "Residues frequency"
        elif n == 1:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_edit_dist
            self.current_sortting["name"] = "Edit distance"
        elif n == 2:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_weighted_edit_dist
            self.current_sortting["name"] = "Weighted edit distance"
        elif n == 3:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_num_of_common_residues_with_scTIM
            self.current_sortting["name"] = "Common residues with scTIM"
        elif n == 4:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_num_of_common_residues_with_scTIM_norm
            self.current_sortting["name"] = "Common residues with scTIM(Normalized)"
        elif n == 5:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_number_of_common_residues_with_scTIM_without_position
            self.current_sortting["name"] = "Common residues number with scTIM without consider the position"
        elif n == 6:
            self.current_sortting["func"] = self.__sequenceSet.sort_by_percent_of_common_residues_with_scTIM_without_position
            self.current_sortting["name"] = "Common residues percentage with scTIM without consider the position"
        elif n == 7:
            s = self.scTIMList.selectedItems()
            selections = {}
            for item in s:
                selections[item.frag_id] = item.frag_name
            self.__sequenceSet.sort_by_selection(selections)
            self.__sequenceSet.color_selection(selections)
            self.current_sortting["name"] = "Based on selected scTIM fragment"
            self.current_coloring["name"] = "Common with selected scTIM fragment"
            self.updateStatusBar()
            self.__sequenceSet.updateColor(self.TIMs)
            return
        self.current_sortting["func"]()
        self.current_coloring["func"]()
        self.updateStatusBar()
        self.__sequenceSet.updateColor(self.TIMs)

    def set_coloring(self, n):
        if n == 0:
            self.current_coloring["func"] = self.__sequenceSet.basicColor
            self.current_coloring["name"] = "Basic coloring(residues are colored by gray)"
        elif n == 1:
            self.current_coloring["func"] = self.__sequenceSet.frequencyColor
            self.current_coloring["name"] = "Frequency coloring(most frequency residue in same column colored by red)"
        elif n == 2:
            self.current_coloring["func"] = self.__sequenceSet.color_general_chemical
            self.current_coloring["name"] = "Based on general chemical characteristics of their R groups"
        elif n == 3:
            self.current_coloring["func"] = self.__sequenceSet.color_side_chain_polarity
            self.current_coloring["name"] = "Based on side-chain polarity"
        elif n == 4:
            self.current_coloring["func"] = self.__sequenceSet.color_side_chain_charge
            self.current_coloring["name"] = "Based on side-chain charge(pH7.4)"
        elif n == 5:
            self.current_coloring["func"] = self.__sequenceSet.color_side_chain_solvent
            self.current_coloring["name"] = "Based on the propensity of a side chain to be in contact with polar solvent like water"
        elif n == 6:
            self.current_coloring["func"] = self.__sequenceSet.color_common_with_scTim
            self.current_coloring["name"] = "Common fragment with scTIM"

        self.current_coloring["func"]()
        self.updateStatusBar()
        self.__sequenceSet.updateColor(self.TIMs)

    def updateStatusBar(self):
        if hasattr(self, 'selected_sequence_name'):
            self.statusBar().showMessage("Selected sequence:%s, Sorting(%s), Coloring(%s) " % (self.selected_sequence_name,self.current_sortting["name"], self.current_coloring["name"]))
        else:
            self.statusBar().showMessage("Sorting(%s), Coloring(%s) " % (self.current_sortting["name"], self.current_coloring["name"]))


    # Create the lists in the right panel
    def initTIMs(self):
         
        # read dTIM
        f = open("data/dTIM.fa")
        line = f.readline()
        f.close()
        # add each element to a list
        dTIM = [frag for frag in line]

        # read scTIM
        f = open("data/scTIM.fa")
        line = f.readline()
        f.close()
        # add each element to a list
        scTIM =[frag for frag in line]

        # create one list of both TIMs
        frag_id = range(1,300)
        items = zip(frag_id,dTIM,scTIM)
        self.__different_frag_id=set()

        # iterate and find the similarities, then color them accordingly
        for item in items:
            item_d = ListWidgetItem(item[1], self.dTIMList, item[0])
            item_sc = ListWidgetItem(item[2], self.scTIMList, item[0])
            if(item[1] != item[2]):
                self.__different_frag_id.add(item[0])
                item_d.setBackground(QtGui.QBrush(QtGui.QColor(204,204,255)))
                item_sc.setBackground(QtGui.QBrush(QtGui.QColor(204,204,255)))

        # load TIMs, and coloring them and update for darwing
        self.__sequenceSet = sequenceSet("data/cTIM_core_align.fa")
        self.__sequenceSet.loadscTIMFromFile("data/scTIM.fa")
        self.current_sortting={"func":"", "name":"Haven't been sorted"}
        self.current_coloring ={"func":self.__sequenceSet.frequencyColor, "name":"Frequency coloring"}
        self.__sequenceSet.frequencyColor()                 # could use other coloring method
        self.__sequenceSet.updateColor(self.TIMs)
        self.updateStatusBar()
        self.TIMs.set_sequenceData(self.__sequenceSet)

    def close(self):
        QtGui.qApp.quit()

    def barchar_update(self, selection_f, selection_t,fB,tB, seqid, fragid):
        seq = self.__sequenceSet[seqid].seq
        #frag_from, frag_to = selection_f, selection_t
        def helper(x):
            if x>len(seq):
                x = len(seq)-1
            if x<0:
                x =0
            return x
        frag_from, frag_to = selection_f - 5, selection_t + 5
        ffb, ftb = fB-5, tB+5
        frag_to = helper(frag_to)
        frag_from =helper(frag_from)
        ftb = helper(ftb)
        ffb = helper(ffb)

        Aids = range(frag_from,frag_to+1)
        Bids = range(ffb, ftb+1)

        Aresi = [seq[i] for i in Aids]
        Bresi = [seq[i] for i in Bids]

        Afre = [self.__sequenceSet.frag_frequency[i][seq[i]]/float(len(self.__sequenceSet)) if seq[i] !='-' else 0.0   for i in Aids]
        Bfre = [self.__sequenceSet.frag_frequency[i][seq[i]]/float(len(self.__sequenceSet)) if seq[i] !='-' else 0.0   for i in Bids]

        
        self.barchar.update_sequences(zip(Aids+Bids, Aresi+Bresi, Afre+Bfre), len(Aids), len(Bids))

app = QtGui.QApplication(sys.argv)

win = MainWindow()
win.show()


win.ready()

sys.exit(app.exec_())
