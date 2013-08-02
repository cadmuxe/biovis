import sys
from PySide import QtCore, QtGui

###############################################################################
### GLProperty Browser Components for browsing and changing GLViewer.GLObject
### properties
###

def markup_vector3(vector):
    return "<small>%7.4f %7.4f %7.4f</small>" % (
        vector[0], vector[1], vector[2])

def markup_matrix3(tensor):
    """Uses pango markup to make the presentation of the tensor
    look nice.
    """
    return "<small>%7.4f %7.4f %7.4f\n"\
                  "%7.4f %7.4f %7.4f\n"\
                  "%7.4f %7.4f %7.4f</small>" % (
               tensor[0,0], tensor[0,1], tensor[0,2],
               tensor[1,0], tensor[1,1], tensor[1,2],
               tensor[2,0], tensor[2,1], tensor[2,2])

class EnumeratedStringEntry(QtGui.QComboBox):
    """Allows the entry of a custom string or a choice of a list of
    enumerations.
    """
    def __init__(self, enum_list):
        QtGui.QComboBox.__init__(self)
        
        #self.entry.connect("activate", self.activate, None)
        self.activated['QString'].connect(self.activate)
        
        self.enum_list = enum_list[:]
        self.string    = None
        
    def activate(self, text):
        self.set_string(text)

    def set_string(self, string):
        self.string = string
        self.addItems(self.enum_list)
        self.setEditText(string)

    def get_string(self):
        #elf.activate(self.entry, None)
        return self.string

class GLPropertyEditor(QtGui.QTabWidget):
    """Widget which generates a customized editing widget for a
    GLObject widget supporting GLProperties.
    """
    def __init__(self, gl_object):
        
        QtGui.QTabWidget.__init__(self)
        
        #self.set_scrollable(True)
        #self.connect("destroy", self.destroy)

        # gl render element
        self.gl_object = gl_object
        
        self.gl_object.glo_add_update_callback(self.properties_update_cb)

        ## property name -> widget dictionary
        self.prop_widget_dict = {}

        ## count the number of properties/pages to be displayed
        catagory_dict = self.catagory_dict_sort()
        
        ## sort pages: make sure Show/Hide is the first page
        catagories = catagory_dict.keys()
        if "Show/Hide" in catagories:
            #print "show hide"
            catagories.remove("Show/Hide")
            catagories.insert(0, "Show/Hide")
            
        ## add Notebook pages and tables
        for catagory in catagories:
            table = self.build_catagory_widgets(catagory, catagory_dict)
            self.addTab(table, catagory)

        self.properties_update_cb(self.gl_object.properties)

    def catagory_dict_sort(self):
        """Returns a tree of dictionaries/lists  catagory_dict[]->[prop list]
        """
        
        ## count the number of properties/pages to be displayed
        catagory_dict = {}
        
        for prop_desc in self.gl_object.glo_iter_property_desc():

            #print "prop_desc: " + prop_desc["name"]

            ## skip hidden properties
            if prop_desc.get("hidden", False)==True:
                #print "hidden"
                continue

            ## get the catagory name, default to "Misc"
            catagory = prop_desc.get("catagory", "Misc")
            try:
                catagory_dict[catagory].append(prop_desc)
            except KeyError:
                catagory_dict[catagory] = [prop_desc]

        return catagory_dict

    def build_catagory_widgets(self, catagory, catagory_dict):
        """Returns the Table widget will all the control widgets
        """
        prop_desc_list = catagory_dict[catagory]
        num_properties = len(prop_desc_list)

        ## create table widget
        table = QtGui.QTableWidget(num_properties, 2 , None)
        table.setStyleSheet("QTableWidget{ border-top-color: transparent; border-bottom-color: transparent; border-right-color: transparent; border-left-color: transparent;}")
        #table.horizontalHeader().setStretchLastSection(True)
                
        #table.verticalHeader().setVisible(False)
        #table.horizontalHeader().setVisible(False)
        #table.
        #table.set_border_width(5)
        #table.set_row_spacings(5)
        #table.set_col_spacings(10)

        ## size group widget to make the edit/display widgets
        ## in the right column all the same size
        #size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

        table_row  = 0

        ## boolean types first since the toggle widgets don't look good mixed
        ## with the entry widgets
        for prop_desc in prop_desc_list:
            
            name = prop_desc["name"]
            
            ## only handling boolean right now
            if prop_desc["type"]!="boolean":
                continue
            
            #print "name: " + name
                
            ## create the widget for this property
            edit_widget = self.new_property_edit_widget(prop_desc)

            ## add the widget to a class dict so property name->widget is
            ## easy to look up
            self.prop_widget_dict[name] = edit_widget 

            ## use a alignment widget in the table
            #align = gtk.Alignment(0.0, 0.5, 1.0, 0.0)
            #align.add(edit_widget)

            ## attach to table
            #print "table row: " + str(table_row)
            table.setCellWidget(table_row, 0, edit_widget)

            table_row += 1
        #print "exit boolean list"
        ## now create all the widgets for non-boolean types
        for prop_desc in prop_desc_list: 
            name = prop_desc["name"]
            
            ## boolean types were already handled
            if prop_desc["type"]=="boolean":
                continue

            ## create the labell widget for the property and attach
            ## it to the left side of the table
            label_widget = self.new_property_label_widget(prop_desc)
            #align = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
            #align.add(label_widget)
            
            #print "table row: " + str(table_row)
            table.setCellWidget(table_row, 0,
                         label_widget)

            ## create the edit widget
            edit_widget = self.new_property_edit_widget(prop_desc)
            self.prop_widget_dict[name] = edit_widget 

            ## use alignment widget in table
            #align = gtk.Alignment(0.0, 0.5, 1.0, 0.0)
            #align.add(edit_widget)

            ## add to size group and attach to table
            #size_group.add_widget(edit_widget)
            
            #table.setCellWidget(table_row, 1, edit_widget)

            table_row += 1

            #table.verticalHeader().setStretchLastSection(False)
            #table.resizeRowsToContents()
            #table.verticalHeader().setStretchLastSection(True)

        #table.show()
        
        rows = table.columnCount()
        cell = table.item(0,1)
        
        if rows > 1 and cell is None:
            table.removeColumn(1)
       
        #print cell
        
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #table.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        
        #table.resizeColumnsToContents()
        
        return table

    def destroy(self, widget):
        """Called after this widget is destroyed.  Make sure to remove the
        callback we installed to monitor property changes.
        """
        self.gl_object.glo_remove_update_callback(self.properties_update_cb)

    def markup_property_label(self, prop_desc, max_len=40):
        """
        """
        listx    = prop_desc.get("desc", prop_desc["name"]).split()
        strx     = ""
        line_len = 0
        
        for word in listx:
            new_line_len = line_len + len(word)
            if new_line_len>max_len:
                strx     += "\n" + word
                line_len = len(word)
            elif line_len==0:
                strx     += word
                line_len += len(word)
            else:
                strx     += " " + word
                line_len += len(word) + 1

        return "<small>%s</small>" % (strx)

    def new_property_label_widget(self, prop):
        """Returns the label widget for property editing.
        """
        label = QtGui.QLabel()
        label.setText(self.markup_property_label(prop))
        #label.set_alignment(0.0, 0.5)
        return label

    def new_property_edit_widget(self, prop):
        """Returns the editing widget for a property.
        """

        ## BOOLEAN
        if prop["type"]=="boolean":
            widget = QtGui.QCheckBox(prop.get("desc", prop["name"]))
            #widget.get_child().set_markup(
             #   self.markup_property_label(prop, max_len=50))

        ## INTEGER
        elif prop["type"]=="integer":
            if prop.get("read_only", False)==True:
                widget = QtGui.QLabel()
            else:
                if prop.get("range") is not None:
                    ## range format: min-max,step
                    min_max, step = prop["range"].split(",")
                    min, max      = min_max.split("-")

                    min  = int(min)
                    max  = int(max)
                    step = int(step)

                    widget = QtGui.QSlider(QtCore.Qt.Horizontal)
                    widget.setValue(0)
                    widget.setRange(float(min), float(max))
                    widget.setTickInterval(float(step))

                elif prop.get("spin") is not None:
                    ## range format: min-max,step
                    min_max, step = prop["spin"].split(",")
                    min, max      = min_max.split("-")
                    
                    min  = int(min)
                    max  = int(max)
                    step = int(step)

                    widget = QtGui.QSpinBox()
                    widget.setSingleStep(step)
                    widget.setValue(0)
                    widget.setRange(float(min), float(max))
                    #widget.set_increments(float(step), float(step*10))
                else:
                    widget = QtGui.QLineEdit()

        ## FLOAT
        elif prop["type"]=="float":
            if prop.get("read_only", False)==True:
                widget = QtGui.QLabel()
            else:
                if prop.get("range") is not None:
                    ## range format: min-max,step
                    min_max, step = prop["range"].split(",")
                    min, max      = min_max.split("-")

                    min  = float(min)
                    max  = float(max)
                    step = float(step)

                    widget = QtGui.QSlider(QtCore.Qt.Horizontal)
                    widget.setValue(1)
                    widget.setRange(min, max)
                    widget.setTickInterval(step)

                elif prop.get("spin") is not None:
                    ## range format: min-max,step
                    min_max, step = prop["spin"].split(",")
                    min, max      = min_max.split("-")
                    
                    min  = float(min)
                    max  = float(max)
                    step = float(step)

                    widget = QtGui.QSpinBox()
                    widget.setValue(1)
                    widget.setSingleStep(step)
                    widget.setRange(min, max)
                    #widget.set_increments(step, step*10.0)

                else:
                    widget = QtGui.QLineEdit()

        ## ARRAY(3)
        elif prop["type"]=="array(3)":
            widget = QtGui.QLabel()

        ## ARRAY(3,3)
        elif prop["type"]=="array(3,3)":
            widget = QtGui.QLabel()
            
        ## ENUMERATED STRING
        elif prop["type"]=="enum_string":
            widget = EnumeratedStringEntry(prop["enum_list"])
        
        ## WTF?
        else:
            text = str(self.gl_object.properties[prop["name"]])
            widget = QtGui.QLabel(text)

        return widget

    def properties_update_cb(self, updates={}, actions=[]):
        """Read the property values and update the widgets to display the
        values.
        """
        for name in updates:
            try:
                widget = self.prop_widget_dict[name]
            except KeyError:
                continue

            prop_desc = self.gl_object.glo_get_property_desc(name)
            
            #print "prop_desc"
            #print prop_desc
            
            if prop_desc["type"]=="boolean":
                if self.gl_object.properties[name]==True:
                    widget.setCheckState(QtCore.Qt.Checked)
                else:
                    widget.setCheckState(QtCore.Qt.Unchecked)

            elif prop_desc["type"]=="integer":
                if prop_desc.get("read_only", False)==True:
                    text = "<small>%d</small>" % (self.gl_object.properties[name])
                    widget.setText(text)
                else:
                    if prop_desc.get("range") is not None:
                        widget.setValue( float(self.gl_object.properties[name]))
                    elif prop_desc.get("spin") is not None:
                        widget.setValue(float(self.gl_object.properties[name]))
                    else:
                        text = str(self.gl_object.properties[name])
                        widget.setText(text)

            elif prop_desc["type"]=="float":
                if prop_desc.get("read_only", False)==True:
                    widget.setText("<small>%12.6f</small>" % (self.gl_object.properties[name]))
                else:
                    if prop_desc.get("range") is not None:
                        widget.setValue(self.gl_object.properties[name])
                    elif prop_desc.get("spin") is not None:
                        widget.setValue(self.gl_object.properties[name])
                    else:
                        text = str(self.gl_object.properties[name])
                        widget.setText(text)

            elif prop_desc["type"]=="array(3)":
                widget.setText(
                    markup_vector3(self.gl_object.properties[name]))

            elif prop_desc["type"]=="array(3,3)":
                widget.setText(markup_matrix3(self.gl_object.properties[name]))

            elif prop_desc["type"]=="enum_string":
                widget.set_string(self.gl_object.properties[name])

            else:
                widget.setText(str(self.gl_object.properties[name]))

    def update(self):
        """Read values from widgets and apply them to the gl_object
        properties.
        """
                
        update_dict = {}
        
        for prop in self.gl_object.glo_iter_property_desc():

            ## skip read_only properties
            if prop.get("read_only", False)==True:
                #print "read only: " + prop["name"]
                continue

            ## property name
            name = prop["name"]

            try:
                widget = self.prop_widget_dict[name]
            except KeyError:
                continue
            
            ## retrieve data based on widget type
            if prop["type"]=="boolean":
               # print "state"
                #print widget.isChecked()
                if widget.isChecked() == True:
                    update_dict[name] = True

                else:
                    update_dict[name] = False

            elif prop["type"]=="integer":
                if prop.get("range") is not None:
                    update_dict[name] = int(widget.value())
                elif prop.get("spin") is not None:
                    update_dict[name] = int(widget.value())
                else:
                    try:
                        update_dict[name] = int(widget.get_text())
                    except ValueError:  
                        pass
                    
            elif prop["type"]=="float":
                if prop.get("range") is not None:
                    update_dict[name] = float(widget.value())
                elif prop.get("spin") is not None:
                    update_dict[name] = float(widget.value())
                else:
                    try:
                        update_dict[name] = float(widget.text())
                    except ValueError:
                        pass

            elif prop["type"]=="enum_string":
                update_dict[name] = widget.get_string()
                
        #print "update dict"
        #print update_dict.keys()
        #print " "
        #print update_dict.values()
        self.gl_object.glo_update_properties(**update_dict)

class GLPropertyTreeControl(QtGui.QTreeView):
    """Hierarchical tree view of the GLObjects which make up
    the molecular viewer.  The purpose of this widget is to alllow
    easy navigation through the hierarchy.
    """
    def __init__(self, gl_object_root, glo_select_cb):
        
        self.gl_object_root = gl_object_root
        self.glo_select_cb  = glo_select_cb
        
        self.path_glo_dict  = {}
        
        # done in setupUI
        QtGui.QTreeView.__init__(self)
        
        self.model = QtGui.QStandardItemModel()
        self.setModel(self.model)
        
        self.connect(self.selectionModel(),  
            QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),  
            self.store_current_selection)
          
        # test data added to the tree
        self.root = self.model.invisibleRootItem()
        
        self.selection = self.root
        
        #self.get_selection().set_mode(gtk.SELECTION_BROWSE)
        
        #self.connect("row-activated", self.row_activated_cb)
        #self.connect("button-release-event", self.button_release_event_cb)
        
        # done in setupUI
        #self.model = gtk.TreeStore(gobject.TYPE_STRING)
        #self.set_model(self.model)
        
        # old and don't need    
        #cell = gtk.CellRendererText()
        #self.column = gtk.TreeViewColumn("Graphics Objects", cell)
        #self.column.add_attribute(cell, "text", 0)
        #self.append_column(self.column)
        #level2 = QtGui.QStandardItem('2nd item')    
        
        # name the column
        self.model.setHorizontalHeaderLabels(['Graphics Objects'])
        self.rebuild_gl_object_tree()
    
    def store_current_selection(self, newSelection, oldSelection):
        
        # current index 
        index = self.currentIndex()
        # current item
        self.selection = self.model.item(index.row(),index.column())
        
        #print self.selection
        #print self.currentIndex().row(), self.currentIndex().column()
        
        glo = self.get_gl_object(index.row() * self.model.rowCount() + index.column())
        self.glo_select_cb(glo) 
        
    # def row_activated_cb(self, tree_view, path, column):
    #     """Retrieve selected node, then call the correct set method for the
    #     type.
    #     """
    #     glo = self.get_gl_object(path)
    #     self.glo_select_cb(glo)

    # def button_release_event_cb(self, tree_view, bevent):
    #     """
    #     """
    #     x = int(bevent.x)
    #     y = int(bevent.y)
    # 
    #     try:
    #         (path, col, x, y) = self.get_path_at_pos(x, y)
    #     except TypeError:
    #         return False
    # 
    #     self.row_activated_cb(tree_view, path, col)
    #     return False

    def get_gl_object(self, path):
        """Return the GLObject from the treeview path.
        """
        glo = self.path_glo_dict[path]
        #print "click"
        #print glo
        return glo

    def rebuild_gl_object_tree(self):
            """Clear and refresh the view of the widget according to the
            self.struct_list
            """
            ## first get a refernence to the current selection
            ## so it can be restored after the reset if it hasn't
            ## been removed
            
            selected_glo = self.selection
            
            # #TODO get index and model path
            # model, miter = self.get_selection().get_selected()
            # if miter is not None:
            #     selected_glo = self.path_glo_dict[model.get_path(miter)]
            # else:
            #     selected_glo = None
    
            ## now record how the tree is expanded so the expansion
            ## can be restored after rebuilding
            # expansion_dict = {}
            
            # for path, glo in self.path_glo_dict.items():
            #     expansion_dict[glo] = self.row_expanded(path)
    
            ## rebuild the tree view using recursion
            self.path_glo_dict = {}
            #self.model.clear()
            
            item = None
            
            def redraw_recurse(parent, child, widget):
                                   
                gl_obj = None
                
                if child is None:
                    gl_obj = parent
                else:
                    gl_obj = child
              
                item = QtGui.QStandardItem( gl_obj.glo_name() )
                widget.appendRow(item)
                #item.setData(QVariant(glo))
                
                #path = self.model.get_path(miter)
                self.path_glo_dict[item.row() * self.model.rowCount() 
                    + item.column()] = gl_obj
                #self.model.set(miter, 0, glo.glo_name())
                
                for child in gl_obj.glo_iter_children():
                    #print "insert name"
                    #print child.glo_name()
                    redraw_recurse(gl_obj, child, item)
                    
            selected_glo = self.model.invisibleRootItem()
            redraw_recurse(self.gl_object_root, None, selected_glo)
    
            ## restore expansions and selections
            # for path, glo in self.path_glo_dict.items():
            #                 try:
            #                     expanded = expansion_dict[glo]
            #                 except KeyError:
            #                     continue
            #                 if expanded==True:
            #                     for i in xrange(1, len(path)):
            #                         self.expand_row(path[:i], False)
    
            #if selected_glo is not None:
             #   self.select_gl_object(selected_glo)

    # def select_gl_object(self, target_glo):
    #     """Selects a gl_object which must be a glo_root or a
    #     decendant of glo_root.
    #     """
    #     ## try to find and select target_glo
    #     for path, glo in self.path_glo_dict.items():
    #         if id(glo)==id(target_glo):
    #                             
    #             for i in xrange(1, len(path)):
    #                 self.expand_row(path[:i], False)
    # 
    #             self.glo_select_cb(glo)
    #             return
    # 
    #     ## unable to find target_glo, select the root
    #     self.select_gl_object(self.gl_object_root)
    #     self.glo_select_cb(self.gl_object_root)
    
class GLPropertyBrowserDialog(QtGui.QDialog):
    """Dialog for manipulating the properties of a GLViewer.
    """
    
    def setupUi(self, GLPropertyBrowserDialog):

          GLPropertyBrowserDialog.setWindowModality(QtCore.Qt.WindowModal)
          GLPropertyBrowserDialog.resize(1024, 768)
          GLPropertyBrowserDialog.setModal(False)

          #initialize layouts
          self.vbox = QtGui.QVBoxLayout(GLPropertyBrowserDialog)
          self.hbox = QtGui.QHBoxLayout()

          # tree view for model components
          self.gl_tree_ctrl = GLPropertyTreeControl(self.gl_object_root, 
              self.gl_tree_ctrl_selected)
          
          # tab view for model properties
          self.tabWidget = QtGui.QTabWidget(GLPropertyBrowserDialog)

          # button layouts
          self.hpane2 = QtGui.QHBoxLayout()
          self.verticalLayout = QtGui.QVBoxLayout()

          # spacer
          spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
          
          # buttons
          self.abtn = QtGui.QPushButton("Apply", GLPropertyBrowserDialog)
          self.cbtn = QtGui.QPushButton("Close", GLPropertyBrowserDialog)
          
          self.abtn.clicked.connect(self.response_cb)
          self.cbtn.clicked.connect(self.Close )
          
          # assign widgets
          self.hpane2.addItem(spacerItem)
          
          self.verticalLayout.addWidget(self.abtn)
          self.hpane2.addLayout(self.verticalLayout)
          self.hpane2.addWidget(self.cbtn)

          # add items to layout(s)
          self.hbox.addWidget(self.gl_tree_ctrl)
          self.hbox.addWidget(self.tabWidget)
          self.vbox.addLayout(self.hbox)
          self.vbox.addLayout(self.hpane2)
          
          return
    def Close(self):
          self.close()
          
    def __init__(self, **args):
        
        self.gl_object_root = args["glo_root"]
        
        self.view_list = []

        #title = "Visualization Properties"
        #gl_object_root.glo_set_name(title)

        # super
        QtGui.QDialog.__init__(self)
        
        #setup UI
        self.setupUi(self)
         
        # don't think i need?       
        #self.view_load_file()

        ## widgets
        #self.hpaned = gtk.HPaned()
        #self.vbox.pack_start(self.hpaned, True, True, 0)
        #self.hpaned.set_border_width(3)

        ## property tree control
        #self.sw1 = gtk.ScrolledWindow()
        #self.hpaned.add1(self.sw1)
        #self.sw1.set_size_request(175, -1)
        #self.sw1.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
                
        #self.sw1.add(self.gl_tree_ctrl)

        ## always start with the root selected
        self.gl_prop_editor = None
        #self.select_gl_object(self.gl_object_root)

        #self.show()
    
    # def view_jump_cb(self, button, junk1, junk2):
    #     """Callback for Jump Button.
    #     """
    #     vname = self.view_combo.entry.get_text()
    #     for vdict in self.view_list:
    #         if vname==vdict["vname"]:
    #             self.select_view(vdict)
    #             break
    # 
    # def view_delete_cb(self, button, junk1, junk2):
    #     """Callback for Delete button.
    #     """
    #     vname = self.view_combo.entry.get_text()
    #     vname = vname.strip()
    #     
    #     for vdict in self.view_list:
    #         if vname==vdict["vname"]:
    #             self.view_list.remove(vdict)
    #             self.view_save_file()
    #             self.view_combo_refresh()
    #             break
                
    def select_view(self, vdict):
        """Applies the view dictionary (vdict) to the current
        viewer.
        """ 
        if vdict["vtype"]=="orientation":
            glo = self.gl_tree_ctrl.gl_object_root
            glo.properties.update(**vdict)

        elif vdict["vtype"]=="view":
            prop_list = []
            for path, val in vdict.items():
                n = path.count("/")
                prop_list.append((n, path, val))
            prop_list.sort()
            
            glo = self.gl_tree_ctrl.gl_object_root
            for n, path, val in prop_list:
                ## crude filter
                if path in ["vtype","vname","width","height"]:
                    continue
                glo.glo_update_properties_path(path, val)

    # def view_save_file(self, filename="view.dat"):
    #     import cPickle
    #     data = cPickle.dumps(self.view_list)
    # 
    #     try:
    #         fil = open(filename, "wb")
    #         fil.write(data)
    #         fil.close()
    #     except IOError:
    #         return
               
    def make_vdict_orientation(self):
        """Return a vdict for the current view.
        """
        glo = self.gl_tree_ctrl.gl_object_root

        vdict = {}
        vdict["vtype"] = "orientation"
        vdict["R"]     = glo.properties["R"].copy()
        vdict["cor"]   = glo.properties["cor"].copy()
        vdict["far"]   = glo.properties["far"]
        vdict["near"]  = glo.properties["near"]
        vdict["zoom"]  = glo.properties["zoom"]

        return vdict

    def make_vdict_view(self):
        """Return a vdict for the current view.
        """
        import copy, string
        
        glo = self.gl_tree_ctrl.gl_object_root

        vdict = {}
        vdict["vtype"] = "view"

        def save_props(glox):
            path = []
            for gloxx in glox.glo_get_path():
                path.append(gloxx.glo_get_properties_id())
            path = path[1:]

            paths = "/".join(path)
            if len(paths)>0:
                paths += "/"
            
            for key, val in glox.properties.items():
                vdict[paths+key] = copy.deepcopy(val)

        save_props(glo)
        for glo_child in glo.glo_iter_preorder_traversal():
            save_props(glo_child)

        return vdict
        
    def view_combo_refresh(self):
        old_vname = self.view_combo.entry.get_text()
        old_vname = old_vname.strip()

        vname_list = []
        for vdict in self.view_list:
            vname_list.append(vdict["vname"])
        self.view_combo.set_popdown_strings(vname_list)

        if len(old_vname) and old_vname in vname_list:
            self.view_combo.entry.set_text(old_vname)
        else:
            self.view_combo.entry.set_text("")
    
    def response_cb(self):
        
        #print "apply"
        #print self.gl_prop_editor
        if self.gl_prop_editor is not None:
            #print "update in response"
            self.gl_prop_editor.update()    

    def rebuild_gl_object_tree(self):
        """Rebuilds the GLObject tree view.
        """
        self.gl_tree_ctrl.rebuild_gl_object_tree()

    def gl_tree_ctrl_selected(self, glo):
        """Callback invoked by the GLPropertyTreeControl when a
        GLObject is selected
        """
        
        #print "gl_tree_ctrl_selected"
        
        ## remove the current property editor if there is one
        if self.gl_prop_editor is not None:
            if self.gl_prop_editor.gl_object==glo:
                return

            self.hbox.removeWidget(self.gl_prop_editor)
            self.gl_prop_editor = None

        ## create new property editor
        if self.tabWidget is not None:
            self.hbox.removeWidget(self.tabWidget)
            self.tabWidget = None
            
        self.gl_prop_editor = GLPropertyEditor(glo)
        self.hbox.addWidget(self.gl_prop_editor)
        self.gl_prop_editor.show()

    def select_gl_object(self, glo):
        """Selects the given GLObject for editing by
        simulating a selection through the GLPropertyTreeControl.
        """
        self.gl_tree_ctrl.select_gl_object(glo)

