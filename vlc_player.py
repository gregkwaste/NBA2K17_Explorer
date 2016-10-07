import sys
import user
import vlc
import gc
from PySide import QtGui, QtCore


class Player():
    """A simple Media Player using VLC and Qt
    """

    def __init__(self, master=None):
        #QtGui.QWidget.__init__(self, master)
        #self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.isPaused = False
        self.metadata = {'length': 0}

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget()
        # self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        # if sys.platform == "darwin": # for MacOS
        #    self.videoframe = QtGui.QMacCocoaViewContainer(0)
        # else:
        #    self.videoframe = QtGui.QFrame()
        #self.palette = self.videoframe.palette()
        # self.palette.setColor (QtGui.QPalette.Window,
        #                       QtGui.QColor(0,0,0))
        # self.videoframe.setPalette(self.palette)
        # self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self.widget)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.widget.connect(self.positionslider,
                            QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.widget.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                            self.PlayPause)

        self.stopbutton = QtGui.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.widget.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                            self.Stop)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self.widget)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.widget.connect(self.volumeslider,
                            QtCore.SIGNAL("valueChanged(int)"),
                            self.setVolume)

        self.vboxlayout = QtGui.QVBoxLayout()
        # self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

        open = QtGui.QAction("&Open", self.widget)
        self.widget.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)
        exit = QtGui.QAction("&Exit", self.widget)
        self.widget.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        #menubar = self.menuBar()
        #filemenu = menubar.addMenu("&File")
        # filemenu.addAction(open)
        # filemenu.addSeparator()
        # filemenu.addAction(exit)

        self.timer = QtCore.QTimer(self.widget)
        self.timer.setInterval(200)
        self.widget.connect(self.timer, QtCore.SIGNAL("timeout()"), self.updateUI)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            try:
                self.mediaplayer.play()
            except:
                raise Exception("Error while playing")
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def OpenFile(self, filename='temp.ogg'):
        # Always open the temporary ogg file"
        # create the media
        try:
            self.media = self.instance.media_new(filename)
        except:
            return
        gc.collect()
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        # self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        # if sys.platform == "linux2": # for Linux using the X Server
        #    self.mediaplayer.set_xwindow(self.videoframe.winId())
        # elif sys.platform == "win32": # for Windows
        #    self.mediaplayer.set_hwnd(self.videoframe.winId())
        # elif sys.platform == "darwin": # for MacOS
        #    self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.PlayPause()
        val = -1
        while val <= 0:
            val = self.mediaplayer.get_length()
            self.metadata['length'] = self.mediaplayer.get_length()
            if val==0:
                val=0.01 #Explicitly set length of 0.01 in case the audio has no proper length metadata
            self.metadata['length'] = val
            


    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)
        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    player = Player()
    player.widget.show()
    player.widget.resize(640, 480)
    if sys.argv[1:]:
        player.OpenFile(sys.argv[1])
    sys.exit(app.exec_())
