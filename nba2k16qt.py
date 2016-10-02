from PySide.QtCore import *
from PySide.QtGui import *

# pymedia
# import pymedia.audio.acodec as acodec
# import pymedia.audio.sound as sound
# import pymedia.muxer as muxer

from vlc_player import Player
# from unused_stuff import PhononAudioPlayer


# external imports
from pygl_widgets import *
from myqmodels import *

# internal imports
import sys
import struct
import time
import threading
import gc
import pylzma
import os
import zlib
import webbrowser
from StringIO import StringIO
# from collections import OrderedDict
# from pylzma import compress
# from pysideuic.Compiler.qtproxies import QtGui
from _winreg import *
from nba2k16commonvars import *

# Import Custom Modules/Libraries
sys.path.append('../gk_blender_lib/modules')
from string_func import *
from scheduler import *
from parsing_functions import *


class dataInitiate:

    def __init__(self, msg, datalen):
        self.msg = msg
        self.datalen = datalen


class scheduleItem:  # not used keep thinking...

    def __init__(self, datadict):
        for key in datadict:
            setattr(self, key, datadict[key])


class x38header:

    def __init__(self, f):
        self.id0 = struct.unpack('<I', f.read(4))[0]
        self.id1 = struct.unpack('<I', f.read(4))[0]
        self.type = struct.unpack('<Q', f.read(8))[0]
        self.size = struct.unpack('<Q', f.read(8))[0]
        self.comp_type = struct.unpack('<Q', f.read(8))[0]
        self.start = struct.unpack('<Q', f.read(8))[0]
        self.stop = struct.unpack('<Q', f.read(8))[0]
        f.read(8)  # zeroes

    def write(self, f):
        f.write(struct.pack('<2I6Q', self.id0, self.id1, self.type,
                            self.size, self.comp_type, self.start, self.stop, 0))


class file_entry:

    def __init__(self, f, custom=False, offset=None, id0=None, id1=None, type=None, g_id=None, size=None, data=None):
        if not custom:
            self.off = f.tell()
            self.id0 = struct.unpack('<I', f.read(4))[0]
            self.id1 = struct.unpack('<I', f.read(4))[0]
            self.type = struct.unpack('<Q', f.read(8))[0]
            self.g_id = 0  # used later
            self.size = 0  # used later
            if self.type == 1:  # zlib or lzma data
                self.data = struct.unpack('<Q', f.read(8))
            elif self.type == 2:  # zip files
                self.data = struct.unpack('<2Q', f.read(16))
            elif self.type == 3:  # empty /separators?
                self.data = struct.unpack('<3Q', f.read(24))
            else:
                logging.info('unknown type: ', self.type)
            # data[1] contains the file offsets
        else:
            # Create Custom fileEntry
            self.off = offset
            self.id0 = id0
            self.id1 = id1
            self.type = type
            self.g_id = g_id
            self.size = size
            self.data = data


class cdf_file_entry:

    def __init__(self, f, custom=False, offset=None, id0=None, id1=None, type=None, g_id=None, size=None, data=None):
        if not custom:
            self.off = struct.unpack('<Q', f.read(8))[0]
            self.size = struct.unpack('<Q', f.read(8))[0]
            f.seek(0x8, 1)
            self.id0 = 0
            self.id1 = 0
            self.g_id = 0
            self.type = 0
            self.pad = struct.unpack('<Q', f.read(8))[0]  # used later
        else:
            # Create Custom fileEntry
            self.off = offset
            self.id0 = id0
            self.id1 = id1
            self.type = type
            self.g_id = g_id
            self.size = size
            self.data = data


class header16:

    def __init__(self, f):
        self.magic = struct.unpack('>I', f.read(4))[0]
        logging.info(hex(self.magic))
        # exceptions
        if self.magic == 0x7EA1CFBB:  # handle ogg  files
            f.seek(0x14, 1)
            f_size = struct.unpack(
                '<I', f.read(4))[0] + struct.unpack('<I', f.read(4))[0] - 8
            f.read(4)  # skipp 2048
            preentries_num = struct.unpack('<I', f.read(4))[0]
            f.read(4)  # skip zeroes
            preentries_size = preentries_num * 0x8
            f_size -= preentries_size
            f.read(preentries_size)
            self.file_entries = []
            self.file_entries.append((f.tell(), f_size))
            return
        elif self.magic == 0x00000000:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return
        elif self.magic in index_table:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return
        elif self.magic == 0x5A4C4942:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return
        elif self.magic == 0x504B0304:  # zip files
            f.seek(-4, 1)
            off = f.tell()
            subfile = sub_file(f, 'ZIP', stop - off)
            self.file_entries = []
            self.file_entries.append((off, stop - off))
            logging.info(self.file_entries)
            return
        # encrypted data
        elif self.magic in [0xC6B0581C, 0x4A50922A, 0xAAC40536]:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return

        if not self.magic in [0x305098F0, 0x94EF3BFF]:
            logging.info('unknown magic ', self.magic)
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return


class header:

    def __init__(self, f):
        # self.main_offset=main_off
        self.magic = struct.unpack('>I', f.read(4))[0]
        # exceptions
        if self.magic == 0x7EA1CFBB:  # handle ogg  files
            f.seek(0x14, 1)
            f_size = struct.unpack(
                '<I', f.read(4))[0] + struct.unpack('<I', f.read(4))[0] - 8
            f.read(4)  # skipp 2048
            preentries_num = struct.unpack('<I', f.read(4))[0]
            f.read(4)  # skip zeroes
            preentries_size = preentries_num * 0x8
            f_size -= preentries_size
            f.read(preentries_size)
            self.file_entries = []
            self.file_entries.append((f.tell(), f_size))
            return
        elif self.magic == 0x00000000:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return
        elif self.magic in index_table:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return
        elif self.magic == 0x5A4C4942:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return
        elif self.magic == 0x504B0304:  # zip files
            f.seek(-4, 1)
            off = f.tell()
            subfile = sub_file(f, 'ZIP', stop - off)
            self.file_entries = []
            self.file_entries.append((off, stop - off))
            return
        # encrypted data
        elif self.magic in [0xC6B0581C, 0x4A50922A, 0xAAC40536]:
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return

        if not self.magic in [0x305098F0, 0x94EF3BFF]:
            logging.info('unknown magic ', self.magic)
            self.file_entries = []
            self.file_entries.append((f.tell() - 4, 0))
            return

        self.header_length = struct.unpack('<I', f.read(4))[0]
        self.next_off = struct.unpack('>I', f.read(4))[0]
        f.read(4)
        self.sub_head_count = struct.unpack(
            '<Q', f.read(8))[0]  # x38 headers counter
        s = struct.unpack('<Q', f.read(8))[0]
        self.x38headersOffset = s + f.tell() - 8 - 1
        # additional information on the header counter
        self.head_count = (s - 9) // 16
        self.file_count = struct.unpack('<Q', f.read(8))[0]
        self.sub_heads = []
        # self.sub_heads.append(f.tell()-self.main_offset +
        # struct.unpack('<Q',f.read(8))[0]-1)
        self.sub_heads.append(f.tell() + struct.unpack('<Q', f.read(8))[0] - 1)
        if self.magic == 0x305098F0 and self.head_count > 1:
            # self.sub_heads.append(f.tell()-self.main_offset + struct.unpack('<Q',f.read(8))[0]-1)
            # self.sub_heads.append(f.tell()-self.main_offset +
            # struct.unpack('<Q',f.read(8))[0]-1)
            self.sub_heads.append(
                f.tell() + struct.unpack('<Q', f.read(8))[0] - 1)
            self.sub_heads.append(
                f.tell() + struct.unpack('<Q', f.read(8))[0] - 1)

        f.seek(self.x38headersOffset)
        self.x38headers = []
        for i in range(self.sub_head_count):
            self.x38headers.append(x38header(f))
        # Fix x38headers start
        # for x38 in self.x38headers:
        #    x38.start+=main_off
        self.sub_heads_data = []
        self.file_entries = []
        self.file_name = None
        self.file_sizes = []

        # Store Basic Information (Included to all archives)

        # small_base=self.main_offset+f.tell()-1
        # small_base=f.tell()-1

        for x38 in self.x38headers:
            x38_file_entries = []
            x38_file_sizes = []
            logging.info('x38 Start: ', x38.start, 'x38 Type: ',
                         x38.type, 'x38 CompType: ', x38.comp_type)
            if x38.type == 1 and self.magic == 0x94EF3BFF:
                logging.info('IFF File Container')
                f.seek(self.sub_heads[0])
                small_base = self.sub_heads[0] - 1
                logging.info('File Description Offset Base: ',
                             small_base, 'file_count: ', self.file_count)

                templist = []
                small_base = 0
                for j in range(self.file_count):
                    templist.append(
                        struct.unpack('<Q', f.read(8))[0] + self.sub_heads[0] - 1 + small_base)
                    small_base += 8

                # logging.info(templist)
                # force file_count for another weird kind of archives
                # if self.sub_head_count==1 and self.x38headers[0].type==8:      I will check if it works without this
                #    self.file_count=1
                g_id = 0
                mode = 0
                for j in range(self.file_count):
                    f.seek(templist[j])

                    temp = file_entry(f)
                    temp.g_id = g_id

                    if not temp.type == 3:
                        if mode == 0:
                            temp.size = temp.data[0]
                        else:
                            temp.size = temp.data[1]
                        x38_file_entries.append(temp)
                    else:
                        if not temp.data[0]:
                            mode = 1
                        else:
                            mode = 0
                        g_id += 1

                # file sizes calculation and offsets
                stop = x38.stop

                # for j in range(len(self.file_entries) - 1):
                #    self.file_sizes.append(self.file_entries[j + 1].size - self.file_entries[j].size)
                # self.file_sizes.append(stop - self.file_entries[-1].size)  #
                # store the last item size

                for j in range(len(x38_file_entries) - 1):
                    x38_file_sizes.append(
                        x38_file_entries[j + 1].size - x38_file_entries[j].size)
                # store the last item size
                x38_file_sizes.append(stop - x38_file_entries[-1].size)

                for entry in x38_file_entries:  # fix offsets
                    # logging.info(entry.size,x38.start)
                    entry.size += x38.start
                    entry.off = entry.size
                    logging.info(entry.off)

                # Append Lists to Parent
                self.file_entries.extend(x38_file_entries)
                self.file_sizes.extend(x38_file_sizes)

                self.sub_heads_data.append(templist)  # Append templist
            elif x38.type == 0x10 or (x38.type == 0x08 and x38.comp_type in [0x05, 0x06]):
                logging.info('Zlib Section')
                temp = file_entry(f, custom=True, offset=x38.start, id0='ZLIB',
                                  id1=None, type=None, g_id=0, size=x38.stop, data=None)
                self.file_entries.append(temp)
                self.file_sizes.append(x38.stop)
            elif x38.type == 0x00 and x38.comp_type == 0x00:
                pass  # Empty Section
            elif x38.type == 0x08 and x38.comp_type == 0x00 and self.magic == 0x94EF3BFF:
                pass  # Empty Section
            elif x38.type == 0x01 and x38.comp_type == 0x00 and self.magic == 0x305098F0:
                logging.info('CDF File Container')
                # Omitting practically FUCKING USELESS First Section
                big_base = self.sub_heads[1] - 1
                f.seek(big_base + 1)

                logging.info('File Description Offset Base: ',
                             big_base, 'file_count: ', self.file_count)

                templist = []
                small_base = 0
                for j in range(self.file_count):
                    templist.append(
                        struct.unpack('<Q', f.read(8))[0] + big_base + small_base)
                    small_base += 8

                for j in range(self.file_count):
                    f.seek(templist[j])
                    self.file_entries.append(cdf_file_entry(f))

                # file sizes calculation and offsets
                for entry in self.file_entries:
                    self.file_sizes.append(entry.size)
                for entry in self.file_entries:
                    entry.off += x38.start  # fix offsets

                self.sub_heads_data.append(templist)  # Append templist

                # Parse CDF File Name
                f.seek(self.sub_heads[-1])
                self.file_name = read_string_2(f)
            else:
                logging.info('Unimplemented Type: ', x38.type)

        # if self.head_count>1 and self.head_count<4:
            # temp=[]
            # for j in range(self.file_count):
            #    temp.append(struct.unpack('<Q',f.read(8))[0]+small_base)
            # self.sub_heads_data.append(temp)
            # file sizes
            # self.file_sizes=[]
            # temp=[]
            # for j in range(self.file_count*self.sub_head_count):
            #    self.file_sizes.append(struct.unpack('<2Q',f.read(16)))
            # if self.sub_head_count>1:
            #    temp=self.file_sizes
            #    self.file_sizes=[]
            #    for j in range(self.file_count):
            #        self.file_sizes.append(temp[self.sub_head_count*j])


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('NBA2K16 Explorer v' + version)
        self.setWindowIcon(QIcon('./resources/tool_icon.ico'))
        self.setupUi()
        self.actionOpen.triggered.connect(self.open_file_table)
        self.actionExit.triggered.connect(self.close_app)
        self.actionApply_Changes.triggered.connect(self.runScheduler)
        self.actionPreferences.triggered.connect(self.preferences_window)
        self.actionSave_Comments.triggered.connect(self.save_comments)
        self.actionCreateManifest.triggered.connect(self.create_manifest)
        self.clipboard = QClipboard()

        self.prepareUi()

        self.pref_window = PreferencesWindow()  # preferences window
        self.iffEditorWindow = IffEditorWindow()
        # Assign Corresponding Action
        self.actionShowIffWindow.triggered.connect(self.iffEditorWindow.show)

        # self properties
        self._active_file = None
        self.list = []  # List that will contain all the game file info
        # List that will contain all the game file names
        self.list_names = {}
        # List that will contain all the game file allocation sizes
        self.alloc_table = {}
        self.comments = {}  # Initialize Comments
        self.parse_comments()
        # logging.info(self.comments.keys()

        self.about_dialog = AboutDialog()  # Create About Dialog

    def setupUi(self):
        # self.setObjectName("MainWindow")
        self.resize(1400, 800)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        # self.gridLayout = QGridLayout(self.centralwidget)
        self.mainSplitter = QSplitter()
        self.mainSplitter.setOrientation(QtCore.Qt.Horizontal)

        # splitter is the Left Part Splitter
        self.splitter = QSplitter(self.mainSplitter)
        self.splitter.setLineWidth(1)
        self.splitter.setOrientation(QtCore.Qt.Vertical)

        # groupBox_2 stores the top left treeview
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setTitle("2K Archive List")
        self.groupBox_2VLayout = QVBoxLayout(self.groupBox_2)
        # ArchiveTabs is the widget which will store all the
        # different archive contents
        # I'm adding treeviews in the tab programmaticaly
        self.archiveTabs = QTabWidget(self.groupBox_2)
        self.archiveTabs.setMinimumSize(QtCore.QSize(0, 264))
        self.archiveTabs.setTabPosition(QTabWidget.North)
        self.archiveTabs.setTabShape(QTabWidget.Rounded)
        self.archiveTabs.setObjectName("archiveTabs")
        self.groupBox_2VLayout.addWidget(self.archiveTabs)

        # Horizontal Layout stores the tab widgets search stuff
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.searchLabel = QLabel(self.groupBox_2)
        self.searchLabel.setText("Search:")
        self.horizontalLayout.addWidget(self.searchLabel)
        self.searchBar = QLineEdit(self.groupBox_2)
        self.horizontalLayout.addWidget(self.searchBar)
        self.groupBox_2VLayout.addLayout(self.horizontalLayout)

        # treeView_2 will hold the archive contents
        self.horizSplitter = QSplitter(self.splitter)
        self.horizSplitter.setOrientation(QtCore.Qt.Horizontal)

        self.groupBox = QGroupBox(self.horizSplitter)
        self.groupBox.setTitle("Archive File List")
        self.groupBoxVLayout = QVBoxLayout(self.groupBox)
        # treeView_2 is the File List Treeview Bottom Left
        self.treeView_2 = QTreeView(self.groupBox)
        self.treeView_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_2.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.treeView_2.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_2.setUniformRowHeights(True)
        self.treeView_2.setObjectName("treeView_2")
        self.groupBoxVLayout.addWidget(self.treeView_2)
        # self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        # Right TabWidget
        self.tabWidget = QTabWidget(self.horizSplitter)

        # Tools Tab
        self.tab = QWidget()
        sizePolicy = QSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        # self.tab.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.tab)

        self.tabWidget.addTab(self.tab, "AudioPlayer")
        # self.gridLayout.addWidget(self.splitter_4, 0, 1, 1, 1)

        self.setCentralWidget(self.mainSplitter)

        # Status Bar
        self.statusBar = QStatusBar(self)
        self.statusBar.setStatusTip("")
        self.statusBar.setSizeGripEnabled(True)
        self.setStatusBar(self.statusBar)

        # Define MenuBar
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1276, 21))
        # File Menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setTitle("File")
        # Options Menu
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setTitle("Options")

        self.actionOpen = QAction(self)
        self.actionOpen.setText("Load Archives")
        self.actionExit = QAction(self)
        self.actionExit.setText("Exit")
        self.actionPreferences = QAction(self)
        self.actionPreferences.setText("Preferences")
        self.actionApply_Changes = QAction(self)
        self.actionApply_Changes.setText("Apply Changes")
        self.actionSave_Comments = QAction(self)
        self.actionSave_Comments.setText("Save Comments")
        self.actionShowIffWindow = QAction(self)
        self.actionShowIffWindow.setText("Show Iff Editor")
        self.actionCreateManifest = QAction(self)
        self.actionCreateManifest.setText("Create Manifest")

        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionApply_Changes)
        self.menuFile.addAction(self.actionExit)
        self.menuOptions.addAction(self.actionPreferences)
        self.menuOptions.addAction(self.actionSave_Comments)
        self.menuOptions.addAction(self.actionSave_Comments)
        self.menuOptions.addAction(self.actionCreateManifest)

        self.menuOptions.addAction(self.actionShowIffWindow)

        # About Dialog
        about_action = QAction(self.menubar)
        about_action.setText("About")
        about_action.triggered.connect(self.about_window)

        # Add actions to menubar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(about_action)
        self.setMenuBar(self.menubar)

        self.tabWidget.setCurrentIndex(0)
        self.archiveTabs.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.archiveTabs, self.searchBar)
        self.setTabOrder(self.searchBar, self.treeView_2)
        self.setTabOrder(self.treeView_2, self.tabWidget)

    def prepareUi(self):
        self.main_viewer_sortmodels = []  # List for sortmodels storage
        self.current_sortmodel = None
        self.current_tableView = None
        self.current_tableView_index = None

        # Active File Data Attribs
        self._active_file_data = None
        self._active_file_handle = None
        self._active_file_path = None

        # ArchiveTabs Wigdet Functions
        self.archiveTabs.currentChanged.connect(self.set_currentTableData)

        # SearchBar Options
        self.searchBar.returnPressed.connect(self.mainViewerFilter)

        # Subfiles Treeview settings
        # self.treeView_2.doubleClicked.connect(self.read_subfile)

        self.treeView_2.setUniformRowHeights(True)
        self.treeView_2.header().setResizeMode(QHeaderView.Stretch)

        # Treeview 2 context menu
        # self.treeView_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.treeView_2.customContextMenuRequested.connect(self.ctx_menu)

        # Subfile Contents Treeview settings
        # self.treeView_3.clicked.connect(self.open_subfile)
        # self.treeView_3.entered.connect(self.open_subfile)

        # self.treeView_3.setUniformRowHeights(True)
        # self.treeView_3.header().setResizeMode(QHeaderView.Stretch)

        # GLWIDGET
        # self.glviewer = GLWidgetQ(self)
        # self.splitter_4.addWidget(self.glviewer)
        # self.glviewer.renderText(0.5, 0.5, "3dgamedevblog")
        # self.glviewer.changeObject()

        # self.glviewer.cubeDraw()

        # Media Widget
        self.sound_player = Player()
        soundPlayerLayout = QVBoxLayout()
        soundPlayerLayout.addWidget(QLabel('Audio Player'))
        soundPlayerLayout.addWidget(self.sound_player.widget)

        # self.tabWidget.addTab(self.sound_player, "Media Player") #  Vlc
        # Player
        tab = self.tabWidget.widget(0)  # Getting first tab
        tablayout = tab.layout()
        tablayout.addLayout(soundPlayerLayout)

        # Text Editor Tab
        # self.text_editor = QPlainTextEdit()
        # self.tabWidget.addTab(self.text_editor, "Text Editor")

        # Import Scheduler
        self.scheduler = QTreeView()
        self.scheduler.setUniformRowHeights(True)
        self.schedulerFiles = []
        # self.scheduler.header().setResizeMode(QHeaderView.Stretch)
        self.scheduler_model = None
        self.tabWidget.addTab(self.scheduler, 'Import Scheduler')

        # Statusbar
        self.progressbar = QProgressBar()
        self.progressbar.setMaximumSize(500, 19)
        self.progressbar.setAlignment(Qt.AlignRight)
        # self.main_viewer_model.progressTrigger.connect(self.progressbar.setValue)

        # 3dgamedevblog label
        # image_pix=QPixmap.fromImage(image)
        self.status_label = QLabel()
        # self.connect(self.status_label, SIGNAL('clicked()'), self.visit_url)
        self.status_label.setText(
            "<a href=\"https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=arianos10@gmail.com&lc=GR&item_name=3dgamedevblog&currency_code=EUR&bn=PP-DonationsBF:btn_donateCC_LG.gif:NonHosted\">Donate to 3dgamedevblog</a>")
        self.status_label.setTextFormat(Qt.RichText)
        self.status_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.status_label.setOpenExternalLinks(True)
        # self.status_label.setPixmap(image_pix)

        # self.statusBar.addPermanentWidget(self.progressbar)
        self.statusBar.addPermanentWidget(self.status_label)
        self.statusBar.showMessage('Ready')

        # Shortcuts
        # shortcut=QShortcut(QKeySequence(self.tr("Ctrl+F","Find")),self.treeView)
        # shortcut.activated.connect(self.find)

    def set_currentTableData(self, index):
        # Setting Current Sortmodel, to the Sortmodel of the TableView of the
        # Set active file
        if not self.archiveTabs.tabText(index) in self._active_file:
            try:
                self._active_file_handle.close()
            except:
                pass
            self._active_file = os.path.join(
                self.mainDirectory, self.archiveTabs.tabText(index))
            self._active_file_handle = open(self._active_file, 'rb')
        # Current Tab
        self.current_tableView = self.archiveTabs.widget(index)
        try:
            self.current_sortmodel = self.current_tableView.model()
            self.current_tableView_index = QModelIndex()
        except:
            logging.info('No Model in tableView')

    def mainViewerFilter(self):
        index = self.current_sortmodel.findlayer(self.searchBar.text())
        selmod = self.current_tableView.selectionModel()
        selmod.clear()
        selmod.select(index, QItemSelectionModel.Rows)
        self.current_tableView.setCurrentIndex(index)

    # Show Preferences Window
    def preferences_window(self):
        self.pref_window.show()

    # About Window
    def about_window(self):
        self.about_dialog.show()

    # Create Custom Manifest File
    def create_manifest(self):
        file_name = os.path.join(self.mainDirectory, 'manifest_g')
        f = open(file_name, 'w')
        for arch in self.list:
            if len(arch[3]) != 0:
                for i in range(len(arch[3])):
                    entry = arch[3][i]
                    f.write(arch[0] + '\t' + entry[0] +
                            ' ' + str(entry[6]) +
                            ' ' + str(entry[3]) +
                            ' ' + str(entry[7]) + '\n')
            else:
                f.write(arch[0] + '\t' + '[pad_file]' + ' ' +
                        str(arch[1]) + ' 1 \n')
        f.close()

    # Main Functions
    def visit_url(self):
        webbrowser.open('http:\\3dgamedevblog.com')

    def main_ctx_menu(self, position):
        '''CONTEXT MENU ON THE TOP-LEFT TABLEVIEW'''
        logging.info('Executing Main Context')
        selmod = self.current_tableView.selectionModel().selectedIndexes()
        arch_name = self.archiveTabs.tabText(self.archiveTabs.currentIndex())
        name = self.current_sortmodel.data(selmod[0], Qt.DisplayRole)
        off = self.current_sortmodel.data(selmod[1], Qt.DisplayRole)
        size = self.current_sortmodel.data(selmod[3], Qt.DisplayRole)
        oaname = self.current_sortmodel.data(selmod[5], Qt.DisplayRole)

        menu = QMenu()
        menu.addAction(self.tr("Copy Offset"))
        menu.addAction(self.tr("Copy Name"))
        menu.addAction(self.tr("Import Archive"))
        menu.addAction(self.tr("Export Archive"))

        res = menu.exec_(
            self.current_tableView.viewport().mapToGlobal(position))

        if not res:
            return

        if res.text() == 'Copy Offset':
            self.clipboard.setText(str(off))
            self.statusBar.showMessage('Copied ' + str(off) + ' to clipboard.')
        elif res.text() == 'Copy Name':
            self.clipboard.setText(str(name))
            self.statusBar.showMessage(
                'Copied ' + str(name) + ' to clipboard.')
        elif res.text() == 'Import Archive':
            logging.info('Importing iff File over: ', name, off, size)

            location = QFileDialog.getOpenFileName(
                caption='Select file', filter='2K16 Archive *.iff;;OGG Audio File *.ogg')

            if not location[0]:
                logging.info('Import Canceled')
                return
            t = open(location[0], 'rb')
            k = t.read()  # store file temporarily
            t.close()

            # Construct ogg
            if 'wav' in name:
                f = open(self._active_file, 'rb')
                f.seek(off)
                l = f.read(size)
                f.close()
                # Open the audio file right away
                self.sound_player.Stop()
                self.sound_player.OpenFile(location[0])
                k = constructOgg(l, k, self.sound_player.metadata)

            # Create Scheduler Entry
            sched = SchedulerEntry()
            # Scheduler Props

            sched.name = name
            sched.archName = arch_name
            sched.oaId = oaname.split('_')[-1]  # Storing just the number
            sched.localOffset = off
            sched.oldCompSize = size
            sched.newCompSize = len(k)
            sched.newData = k
            sched.type = name.split('.')[-1].upper()

            self.addToScheduler(sched)  # Add to Scheduler

        elif res.text() == 'Export Archive':
            location = QFileDialog.getSaveFileName(
                caption="Save File", dir=name, filter='*.iff')
            t = open(location[0], 'wb')
            f = open(self._active_file, 'rb')
            # Explicitly handle ogg files
            # if 'wav' in name:
            #    f.seek(off + 0x2C)
            # else:
            f.seek(off)
            t.write(f.read(size))
            f.close()
            t.close()
            self.statusBar.showMessage(
                'Exported .iff to : ' + str(location[0]))

    def test(self, rowMid):  # Sub Archive Reader
        # Check if Comments Section was Clicked
        if rowMid.column() == 4:
            self.tableview_edit_start(rowMid)
            return
        ''' THIS IS THE FUNCTION THAT PARSES THE SELECTED
            SUBARCHIVE AFTER CLICK ON THE MAIN TABLEVIEW '''
        selmod = self.current_tableView.selectionModel().selectedIndexes()
        '''Check Current Index'''
        if self.current_tableView_index == selmod[0].row():
            return
        arch_name = self.archiveTabs.tabText(self.archiveTabs.currentIndex())
        name = self.current_sortmodel.data(selmod[0], Qt.DisplayRole)
        off = self.current_sortmodel.data(selmod[1], Qt.DisplayRole)
        size = self.current_sortmodel.data(selmod[3], Qt.DisplayRole)

        if arch_name not in self._active_file:  # File not already opened
            try:
                if isinstance(self._active_file_handle, file):
                    self._active_file_handle.close()
                self._active_file = self.mainDirectory + os.sep +\
                    arch_name  # Get the New arhive file path
                self._active_file_handle = open(
                    self._active_file, 'rb')  # Opening File
            except:
                msgbox = QMessageBox()
                msgbox.setText(
                    "File Not Found\n Make sure you have selected the correct NBA 2K15 Installation Path")
                msgbox.exec_()
                return

        '''PARSING START'''
        self._active_file_handle.seek(off)
        t = StringIO()
        t.write(self._active_file_handle.read(size))
        t.seek(0)
        self._active_file_data = t

        logging.info(' '.join(map(str, ('Searching in : ', self._active_file))))
        logging.info(' '.join(map(str, ('Handle Path : ', self._active_file_handle.name))))

        gc.collect()

        '''Check for audio files'''
        if '.wav' in name:
            # Get to proper Offset
            self._active_file_data.seek(0x2C + 0x2214)
            t = open('temp.ogg', 'wb')
            t.write(self._active_file_data.read())
            t.close()
            self.sound_player.Stop()
            self.sound_player.OpenFile('temp.ogg')

            return

        ''' CALLING archive_parser TO PARSE THE SUBARCHIVE '''
        ''' LOC CONTAINS A FILE LIST WITH ALL THE SUBFILES DATA'''
        loc = archive_parser(self._active_file_data)
        if isinstance(loc, dataInitiate):
            # Answering Data Delivery Request
            # Getting the Data
            self._active_file_data.close()  # Closing the file
            self._active_file_handle.seek(off)  # Big archive already open
            t = StringIO()
            t.write(self._active_file_handle.read(loc.datalen))
            t.seek(0)
            self._active_file_data = t
            # Call archive parser again
            loc = archive_parser(self._active_file_data)

        '''self.file_list IS THE TREEMODEL THAT CONTAINS ALL THE
            FILES CONTAINED IN THE SUBARCHIVE'''
        self.file_list = SortModel()
        self.file_listModel = TreeModel(
            ("Name", "Offset", "Comp. Size", "Decomp. Size", "Type"))
        self.file_list.setSourceModel(self.file_listModel)

        # self.treeView_2.header().setResizeMode(QHeaderView.ResizeToContents)
        # self.treeView_2.header().setResizeMode(QHeaderView.Interactive)

        gc.collect()
        parent = self.file_listModel.rootItem
        for i in loc:
            # logging.info(i)
            item = TreeItem(i, parent)
            parent.appendChild(item)

        self.treeView_2.setModel(self.file_list)  # Update the treeview
        self.treeView_2.setSortingEnabled(True)  # enable sorting
        self.treeView_2.sortByColumn(
            1, Qt.SortOrder.AscendingOrder)  # sort by offset
        self.current_tableView_index = selmod[0].row()
        # Open File into the iff editor
        logging.info('Opening File in Iff Editor')
        self._active_file_data.seek(0)
        self.iffEditorWindow._file = self._active_file_data
        self.iffEditorWindow._fileProps.name = name
        self.iffEditorWindow.openFileData()
        # self.iffEditorWindow.show()

    def open_file_table(self):
        ''' FUNCTION THAT INITIATES THE FILE ARCHIVES LOADING
            ACTUAL PARSING IS DONE BY load_archive_database_tableview '''
        # Delete Current Tabs
        while self.archiveTabs.count():

            widg = self.archiveTabs.widget(self.archiveTabs.currentIndex())
            self.archiveTabs.removeTab(self.archiveTabs.currentIndex())
            try:
                widg.deleteLater()
            except:
                pass

        # Clear SortModels
        self.main_viewer_sortmodels = []

        gc.collect()
        # update mainDirectory
        self.mainDirectory = self.pref_window.mainDirectory
        file_name = self.mainDirectory + os.sep + '0A'
        logging.info(' '.join(map(str, (self.mainDirectory, file_name))))

        self._active_file = file_name  # set active file to 0A file
        self._0Afile = file_name
        self._active_file_handle = open(self._active_file, 'rb')

        self.statusBar.showMessage('Getting archives...')
        self.fill_archive_names()  # Fill Archive Names and Allocation Sizes
        self.fill_archive_list()  # Fill Archive List

        # Sort All File Entries
        for arch in self.list:
            arch[3] = sorted(arch[3], key=lambda s: s[1])

        try:
            num = self.load_archive_database_tableview()
        except:
            msgbox = QMessageBox()
            msgbox.setText(
                "File Not Found\n Make sure you have selected the correct NBA 2K16 Installation Path")
            msgbox.exec_()
            return

        # self.main_viewer_model=MyTableModel()

        '''SETUP SECONDARY BOTTOM-LEFT TABLEVIEW'''
        self.file_list = SortModel()
        self.file_listModel = TreeModel(
            ("Name", "Offset", "Comp. Size", "Decomp. Size", "Type"))
        self.file_list.setSourceModel(self.file_listModel)
        self.treeView_2.setModel(self.file_list)  # Update the treeview
        logging.info("Swapping Columns")
        self.treeView_2.header().swapSections(3, 4)
        self.treeView_2.header().swapSections(2, 3)

        self.treeView_2.header().setResizeMode(QHeaderView.Interactive)
        self.statusBar.showMessage(str(num) + ' archives detected.')
        gc.collect()

    def close_app(self):
        sys.exit(0)

    def fill_archive_names(self):
        file_name = os.path.join(self.mainDirectory, 'manifest_g')
        if not os.path.exists(os.path.join(self.mainDirectory, 'manifest_g')):
            file_name = os.path.join(self.mainDirectory, 'manifest')
            f = open(file_name, 'r')
            for line in f.readlines():
                archname = line.split('\t')[0]
                split = line.split('\t')[1].lstrip().split(' ')
                name = split[0]
                offset = int(split[1])
                if archname not in self.list_names.keys():
                    self.list_names[archname] = {}
                    self.alloc_table[archname] = {}
                self.list_names[archname][offset] = name
                self.alloc_table[archname][offset] = 0
            f.close()
        else:
            f = open(file_name, 'r')
            for line in f.readlines():
                archname = line.split('\t')[0]
                split = line.split('\t')[1].lstrip().split(' ')
                name = split[0]
                offset = int(split[1])
                allocsize = int(split[2])
                if archname not in self.list_names.keys():
                    self.list_names[archname] = {}
                    self.alloc_table[archname] = {}

                self.list_names[archname][offset] = name
                self.alloc_table[archname][offset] = allocsize
            f.close()

    def fill_alloc_table(self):
        file_name = os.path.join(self.mainDirectory, 'alloctable_g')
        if not os.path.exists(file_name):
            logging.info('not found alloctable_g, Creating One')
            self.write_alloc_table()
            return
        else:
            logging.info('found alloctable_g')

        t = StringIO()
        f = open(file_name, 'rb')
        t.write(f.read())
        f.close()

        for arch in self.list:
            for entry in arch[3]:
                oaIndex = int(entry[5].split('_')[-1])
                t.seek(0x8 * oaIndex)
                entry[7] = struct.unpack('<Q', t.read(0x8))[0]

        t.close()

    def write_alloc_table(self):
        logging.info('Creating Allocation Table')
        file_name = os.path.join(self.mainDirectory, 'alloctable_g')
        tFileCount = 0
        for arch in self.list:
            tFileCount += len(arch[3])
        logging.info(' ', join((TotalFileCount, tFileCount)))
        t = StringIO()
        t.write(b'\x00' * tFileCount * 8)
        logging.info('Wrote temp file')

        for arch in self.list:
            logging.info(' ', join(('Working on archive: ', arch[0])))
            for entry in arch[3]:
                oaIndex = int(entry[5].split('_')[-1])
                t.seek(oaIndex * 0x8)
                t.write(struct.pack('<Q', entry[7]))
        t.seek(0)

        # write file to disk
        f = open(file_name, 'wb')
        f.write(t.read())
        f.close()

    def fill_archive_list(self):
        f = self._active_file_handle
        f.seek(16)
        count_0 = struct.unpack('<I', f.read(4))[0]
        f.seek(12, 1)
        count_1 = struct.unpack('<I', f.read(4))[0]
        f.seek(12, 1)
        s = 0
        logging.info(' '.join(map(str, ('Counts: ', count_0, count_1))))
        self.list = []
        for i in range(count_0):
            size = struct.unpack('<Q', f.read(8))[0]
            f.read(8)
            name = read_string_1(f)
            f.read(13 + 16)
            # logging.info(name,hex(size),f.tell())
            # self.main_list.append(None,(name,s))
            self.list.append([name, s, size, []])
            logging.info(' '.join(map(str, (name, s, size))))
            archiveOffsets_list.append(s)
            s += size

        archiveOffsets_list.append(s)

        logging.info(' '.join(map(str, ('Total Size: ', s))))
        # Store archives data
        self.t = StringIO()
        self.t.write(f.read(0x18 * count_1))

        # Split worker jobs

        work_length = 50000
        work_last_length = count_1 % work_length
        work_count = count_1 // work_length

        # Call workers
        t0 = time.clock()
        threads = []
        subarch_id = 0  # keep the subarchive id
        for i in range(work_count):
            logging.info(' '.join(map(str, ('Starting Thread: ', i))))
            self.t.seek(i * work_length * 0x18)
            data = StringIO()
            data.write(self.t.read(0x18 * work_length))
            # thread=threading.Thread(target=self.worker,args=(data,work_length,count_0,))
            thread = threading.Thread(
                target=self.worker, args=(data, work_length, count_0, subarch_id,))
            thread.start()
            threads.append(thread)
            subarch_id += work_length
        for i in range(work_count):
            threads[i].join()

        # last worker
        self.t.seek(work_count * work_length * 0x18)
        data = StringIO()
        data.write(self.t.read(0x18 * work_last_length))
        thread = threading.Thread(
            target=self.worker, args=(data, work_last_length, count_0, subarch_id,))
        thread.start()
        thread.join()

        logging.info(
            ' '.join(map(str, ('Finished working. Total Time Elapsed: ', time.clock() - t0))))

    def load_archive_database_tableview(self):
        ''' PARSING SETTINGS, IDENTIFYING WHICH ARCHIVE FILES TO READ
            AND SETUP THE MAIN TOP-LEFT TABLEVIEW '''
        # Create Tabs according to the Settings
        logging.info('Parsing Settings')
        settings = self.pref_window.pref_window_buttonGroup
        selected_archives = []
        for child in settings.children():
            if isinstance(child, QCheckBox):
                if child.isChecked():
                    selected_archives.append(
                        archiveName_dict[child.text().split(' ')[0]])

        count = 0
        logging.info(' '.join(map(str, ('Creating ', len(selected_archives), ' Tabs'))))

        for i in selected_archives:
            # Create TableViewModel
            entry = self.list[i]
            sortmodel = MyTableModel(
                entry[3], ["Name", "Offset", "Type", "Size",
                           "Comments", "0A Id", "Global Offset",
                           "Allocated Size"])
            # Create the TableView and Assign Options
            table_view = MyTableView()
            table_view.setModel(sortmodel)
            table_view.horizontalHeader().setResizeMode(QHeaderView.Interactive)
            table_view.horizontalHeader().setMovable(True)

            table_view.setSortingEnabled(True)
            table_view.sortByColumn(1, Qt.AscendingOrder)
            table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
            table_view.setSelectionMode(QAbstractItemView.SingleSelection)
            table_view.setEditTriggers(QAbstractItemView.SelectedClicked)
            table_view.hideColumn(2)  # Type
            table_view.hideColumn(5)  # 0A Id
            table_view.hideColumn(6)  # Global Offset
            table_view.hideColumn(7)  # Allocation Sizes
            table_view.horizontalHeader().swapSections(3, 4)
            table_view.horizontalHeader().swapSections(1, 3)

            # Set Column Sizes
            lid = table_view.horizontalHeader().logicalIndex(0)
            table_view.horizontalHeader().resizeSection(lid, 400)
            lid = table_view.horizontalHeader().logicalIndex(1)
            table_view.horizontalHeader().resizeSection(lid, 700)
            lid = table_view.horizontalHeader().logicalIndex(2)
            table_view.horizontalHeader().resizeSection(lid, 60)
            table_view.horizontalHeader().setStretchLastSection(True)

            # Functions
            table_view.clicked.connect(self.test)
            # table_view.doubleClicked.connect(self.tableview_edit_start)
            # table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            table_view.customContextMenuRequested.connect(self.main_ctx_menu)

            count += len(entry[3])
            tabId = self.archiveTabs.addTab(table_view, entry[0])
            # Store the sortmodel handles
            self.main_viewer_sortmodels.append(sortmodel)
            # Debugging Testing Archive size
            # size = 0
            # for subentry in entry[3]:
            #    size += subentry[3]
            # logging.info('Estimated Archive %s size: %d' % (entry[0], size))

        return count

    def save_comments(self):
        logging.info('Saving Comments')

        f = open('NBA2K16_archiveComments.txt', 'w')
        f.write('//NBA2K16 ARCHIVE COMMENTS\n')
        f.write('//Created by NBA2K16 Explorer v' + version + '\n')
        for i in range(self.archiveTabs.count()):
            fname = str(self.archiveTabs.tabText(i))  # Write the archive name
            f.write('//' + fname + '\n')
            tmodel = self.archiveTabs.widget(i).model()  # Get tableview model
            for entry in tmodel.mylist:
                if entry[4]:
                    f.write(
                        entry[0] + '\t' + str(entry[4]) + '\n')
        f.close()

        # Immediately reload new comments in the database
        self.parse_comments()

    def parse_comments(self):
        logging.info('Parsing Comments')
        try:
            f = open('NBA2K16_archiveComments.txt')
            for line in f.readlines():
                if not line.startswith('//'):
                    split = line.rstrip().split('\t')
                    # logging.info(split[0], split[1])
                    self.comments[split[0]] = split[1]
            f.close()
        except:
            logging.info('No Comments File Exists')

    def tableview_edit_start(self, index):
        if index.column() == 4:
            self.current_tableView.edit(index)

    def worker(self, data, length, count_0, subarch_id):
        data.seek(0)
        # f=open('C:\\worker.txt','w')
        for i in range(length):
            sa = struct.unpack('<Q', data.read(8))[0]  # Size
            id0 = struct.unpack('<I', data.read(4))[0]
            sb = struct.unpack('<I', data.read(4))[0]  # Checksum???
            id1 = struct.unpack('<Q', data.read(8))[0]  # Global Offset
            # f.write(id1)
            for j in range(count_0 - 1, -1, -1):
                val = self.list[j][1]  # full archive calculated offset
                archname = self.list[j][0]
                if id1 >= val:
                    # self.main_list.append(it,('unknown_'+str(i),id1-val))
                    comm = ''
                    name = self.list_names[archname][id1]
                    oaname = 'unknown_' + str(subarch_id)

                    if self.alloc_table[archname][id1]:
                        allocsize = self.alloc_table[archname][id1]
                    else:
                        allocsize = sa

                    if name in self.comments.keys():
                        comm = self.comments[name]  # Try to load comment
                    # Saving iff size sa as the allocated size as well.
                    # This is fixed up later

                    self.list[j][3].append(
                        [name, id1 - val, sb, sa,  comm, oaname, id1, allocsize])
                    subarch_id += 1
                    break

    def open_subfile(self):
        selmod = self.treeView_3.selectionModel().selectedIndexes()[0].row()
        logging.info(self.subfile.files)
        name, off, size, type = self.subfile.files[selmod]
        logging.info('Opening ', name)
        t = self.subfile._get_file(selmod)  # getting file

        typecheck = struct.unpack('>I', t.read(4))[0]
        t.seek(0)
        try:
            type = type_dict[typecheck]
        except:
            # logging.info(type)
            type = 'UNKNOWN'

        logging.info(type)
        # binary files checking

    def fill_info_panel(self, info_dict):  # Not used anymore
        # setup info panel
        logging.info('Clearing Information Panel')
        for entry in self.groupBox_3.layout().children():
            self.clearLayout(entry)
        logging.info('Setting Up Information Panel')
        sub_layout = QFormLayout()
        for entry in info_dict:
            lab = QLabel()
            if not info_dict[entry]:
                lab.setText(
                    "<P><b><FONT COLOR='#000000' FONT SIZE = 4>" + str(entry) + "</b></P></br>")
            else:
                lab.setText(str(entry) + info_dict[entry])

            sub_layout.addWidget(lab)

        self.groupBox_3.layout().addLayout(sub_layout)
        gc.collect()

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

# Scheduler Functions
# Since 2K16 Scheduler should be working just with iffs

    def addToScheduler(self, sched):
        if not self.scheduler_model:
            self.scheduler_model = TreeModel(("SubName", "0A ID", "SubOffset",
                                              "SubOldSize", "SubNewSize",
                                              "SubType", "Archive"))
            self.scheduler.setModel(self.scheduler_model)

        parent = self.scheduler_model.rootItem
        item = TreeItem((sched.name, sched.oaId, sched.localOffset,
                         sched.oldCompSize, sched.newCompSize,
                         sched.type, sched.archName),
                        parent)
        parent.appendChild(item)

        self.schedulerFiles.append(sched.newData)

    def runScheduler(self):
        parent = self.scheduler_model.rootItem
        rowCount = parent.childCount()
        # logging.info(rowCount)

        for i in range(rowCount):
            item = parent.child(i)
            name, oaname, off, oldSize, newSize, subType, archName = [item.data(0),
                                                                      item.data(1), item.data(2), item.data(3), item.data(4), item.data(5), item.data(6)]

            logging.info(
                ' ', join((name, oaname, off, oldSize, newSize, subType, archName)))

            diff = newSize - oldSize
            logging.info(' ', join(('Size Difference: ', diff)))

            self._active_file_handle.close()  # Close opened files
            if archName not in self._active_file:  # check archive name
                self._active_file = os.path.join(self.mainDirectory, archName)
            logging.info(self._active_file)

            f = open(self._active_file, 'r+b')  # open big archive
            f.seek(off)  # seek to iff offset
            data = self.schedulerFiles[i]
            # Locate index in database
            dbIndex = 0
            for i in range(len(self.list[archiveName_dict[archName]][3])):
                entry = self.list[archiveName_dict[archName]][3][i]
                if entry[5] == 'unknown_' + oaname:
                    dbIndex = i
                    allocsize = entry[7]
                    break

            if newSize <= allocsize:
                logging.info('Enough Space for File')
                f.write(data)  # enough space for writing
                # Change allocated memory value to table
                # oaIndex = int(oaname.split('_')[-1])
                # for entry in self.list[archiveName_dict[archName]][3]:
                #    if entry[5].split('_')[-1] == oaname:
                #        entry[7] += diff
                #        logging.info('Changed Allocation Value')
                #        break
                f.close()

                logging.info('Saving New Size to 0A')
                f = open(self.mainDirectory + '\\' + '0A', 'r+b')
                f.read(0x10)
                arch_num = struct.unpack('<I', f.read(4))[0]
                f.seek((arch_num + 1) * 0x30)  # seeking to archive definitions
                f.seek(int(oaname) * 0x18, 1)  # Seek to subarchive
                f.write(struct.pack('<Q', newSize))  # update its size
                f.close()

            else:
                f.seek(oldSize, 1)  # Seek to end of original file
                # Save big file tail to disk
                tailPath = os.path.join(self.mainDirectory, 'tail')
                tail = open(tailPath, 'wb')

                buf = 1
                while buf:
                    buf = f.read(1024 * 1024 * 1024)
                    logging.info(len(buf))
                    tail.write(buf)
                tail.close()
                logging.info("Done Writing tail - TESTING")

                # Write actual data to archive
                f.seek(off)
                f.write(data)

                logging.info("Writing back tail to big archive - TESTING")
                # Writing back the tail
                tail = open(tailPath, 'rb')
                buf = 1
                while buf:
                    buf = tail.read(1024 * 1024 * 1024)
                    f.write(buf)
                tail.close()
                os.remove(tailPath)  # Delete Tail File
                f.close()

                # Updating 0A database
                f = open(self.mainDirectory + '\\' + '0A', 'r+b')
                f.read(0x10)
                arch_num = struct.unpack('<I', f.read(4))[0]
                f.read(0xC)
                file_count = struct.unpack('<I', f.read(4))[0]
                f.read(0xC)
                # seeking to archive definition position
                f.seek(archiveName_dict[archName] * 0x30, 1)
                s = struct.unpack('<Q', f.read(8))[0]
                f.seek(-8, 1)
                logging.info('Writing ' + str(archName) + ' size to ', str(f.tell()))
                f.write(struct.pack('<Q', s + diff))

                f.seek((arch_num + 1) * 0x30)  # seeking to archive definitions
                data_off = f.tell()  # store the data offset

                # get global file id
                subarch_id = int(oaname)
                f.seek(subarch_id * 0x18, 1)
                logging.info('Found subarchive entry in ', f.tell())
                s = struct.unpack('<Q', f.read(8))[0]
                f.seek(-8, 1)
                f.write(struct.pack('<Q', s + diff))  # update its size
                f.seek(8, 1)
                sub_arch_full_offset = struct.unpack('<Q', f.read(8))[0]

                # Update size in database
                logging.info(' ', join(('Prev Size: ', self.list[
                             archiveName_dict[archName]][3][dbIndex][7])))
                self.list[archiveName_dict[archName]][3][dbIndex][7] = s + diff
                self.list[archiveName_dict[archName]][3][dbIndex][3] = s + diff
                logging.info(' ', join(('New Size: ', self.list[
                             archiveName_dict[archName]][3][dbIndex][7])))

                # Update next file offsets
                for arch in self.list:
                    logging.info('Seeking in: ', arch[0], arch[1], arch[2])
                    for subarch in arch[3]:
                        # find all siblings with larger offset
                        test_val = subarch[1] + arch[1]
                        if test_val > sub_arch_full_offset:
                            subarch_name = subarch[5]
                            subarch_id = int(subarch_name.split('_')[-1])
                            f.seek(data_off + subarch_id * 0x18)
                            f.seek(8 + 4 + 4, 1)
                            # Changing id1 aka the offset
                            s = struct.unpack('<Q', f.read(8))[0]
                            f.seek(-8, 1)
                            f.write(struct.pack('<Q', s + diff))
                            # Change the database as well
                            subarch[6] += diff
                            subarch[1] += diff
                f.close()

            self.schedulerFiles.pop()
            self.scheduler_model.rootItem.childItems.pop()
            logging.info('Scheduled Files left', len(self.schedulerFiles))

        self.scheduler.setModel(None)
        gc.collect()
        self.statusBar.showMessage('Import Completed')
        self.create_manifest()
        logging.info('Reloading Table')
        self.open_file_table()  # reload archives


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
