#!/usr/bin/python3
""" DataView Application
Just helps looking at large data groups and finding useful bits, and separating
them out for easier analysis.
"""
#TODO Bug in phase calculation
#TODO chop exports current view in addition to full dataset
#TODO user defined plot scale/axes
#TODO quadratic fit
#TODO linear fit
#TODO WIP allow transform to change view axis titles.  Actually, this already works
#TODO why update runs twice: cause button release and button motion both call it?
#TODO refactor logger, subclass LogRecord, speed improvement
#TODO speed up update (without animation)
#TODO filter data types
#TODO save filters, named filters
#TODO pick window from figure
#TODO disable chop button until loaded
#TODO error when cancelling load
#TODO scale scales
#TODO LaTeX plots
#TODO My own plot style
#TODO WIP Alternate indexes, need to be able to change scales first
#TODO animation
#TODO fix doc strings
#TODO implement settings menu
#TODO save settings
#TODO transform/fit descriptions
#TODO start on start frame, show PageThree after load
#TODO better window and view widget layouts
#TODO use pymagic to detect file types
#TODO ? fix NotImplementedError class
#TODO show summary statistics for view in GUI
#TODO enabling disabled view should assume primary view

import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvas
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg as NavigationToolbar
#from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')
import os
import pathlib
from logging import *
basicConfig(level=ERROR)
from warnings import warn as warnwarn
from numbers import Number

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import configer

LARGE_FONT = ("Times", 12)
NORM_FONT = ("Times", 10)

from DataAnalyser.DataAnalyser import DataAnalyser
DA = DataAnalyser()

configDefault = {
        'figMark'          : {
            'default'   : 'bo-'
            ,'func'     : lambda p: isinstance(p,str)
            }
        ,'writeFormat'      : {
            'default'   : 'csv'
            ,'func'     : lambda fmt: fmt in ['csv','hdf']
            }
        ,'xscale'       : {
            'default'   : 1.0
            ,'func'      : lambda x: isinstance(x,float)
            }
        ,'yscale'       : {
            'default'   : 1.0
            ,'func'      : lambda x: isinstance(x,float)
            }
        ,'xlabel'       : {
            'default'   : None
            #'default'   : "Position X (mm)"
            ,'func'     : lambda x: (x is None) or isinstance(x,str)
            }
        ,'ylabel'       : {
            'default'   : None
            ,'func'     : lambda x: (x is None) or isinstance(x,str)
            }
        ,'chopOpts'     : {
            'default'   : {
                'fmt'       : 'csv'
                ,'dirpath'  : pathlib.PurePath(os.path.curdir)
                ,'hdfKey'   : 'chop'
                ,'prefix'   : 'chop'
                }
            ,'func'      : lambda c: isinstance(c,dict)
            }
        }

class DataViewApp(tk.Tk):
    """ Data View Application Class
    """

    headerRow = 0
    windowType = 'index'

    def __init__(self, *args, **kwargs):
        """Initialize DataViewApp

        Position arguments:
        All positional arguments are passed to Tk() constructor.  None are used
        by DataAnalyser().

        Keyword arguments:
        All keyword arguments are passed to Tk() constructor. None are used by
        DataAnalyser().
        """

        tk.Tk.__init__(self, *args, **kwargs)
        """ Build the application (main) window """
        #tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Data Viewer")

        """ Load default configuration """
        self.DVconfig = configer.Configer(configDefault)
        
        """ Initialize Data Viewer """
        self.DA = DA

        """ Arrange "this" frame """
        self.minsize(640,480)
        #self.geometry("640x480")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        """ build a menu bar """
        menubar = tk.Menu(container)
        self.menubar = menubar

        """Create file menu"""
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save settings", command=lambda: popupmsg('Not supported just yet!'))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.filemenu = filemenu

        """Create Settings Menu"""
        self.addSettingsMenu()

        """Transform Menu"""
        self.transformMenu = tk.Menu(menubar, tearoff=0)            #create a menu
        self.transformOpts = self.DA.getTransformOptions()          #get dict of transforms from DA
        for key in self.transformOpts.keys():
            """Each key is a different transform capability.  Add a menu entry
            for it, and make the action to launch a dialog box. """
            transformConfig = self.transformOpts[key]
            transName = transformConfig['label']
            debug("Adding menu entry for translation %s:%s" % (key,transName))
            newBox = DVdialogHelper(self, transformConfig)
            self.transformMenu.add_command(label=transName,command=newBox.launch)
        menubar.add_cascade( label="Transform", menu=self.transformMenu)    #Finally, add new menu to main menubar

        """Curve Fit Menu"""
        self.addCurveFitMenu()

        """ Finish Menu bar """
        tk.Tk.config(self,menu=menubar)

        """ Make a dictionary of different frame types (classes) that
        we will use for the application.
        """
        self.frames = {}
        for newFrame in (StartPage, PageThree):

            frame = newFrame(container, self)

            self.frames[newFrame] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        """ Show the starting frame type on init """
        self.show_frame(PageThree)

    def addSettingsMenu(self):
        """Curve Fit Menu"""
        menubar = self.menubar
        self.settingsMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=self.settingsMenu)

    def addCurveFitMenu(self):
        """Curve Fit Menu"""
        menubar = self.menubar
        self.fitMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Curve Fit", menu=self.fitMenu)


    def launchDialog(self, dialogClass, parentForDialog, returnDict, **initDict):
        """Launch a dialog box and wait for it.

        Parameters:
        dialogClass: class name
        parentForDialog: reference to the TK parent of the dailog box to be
        launched.
        returnDict: dict to which new values from the dialog will be placed
        initDict: dict to pass to the constructor of dialogClass

        Returns: none
        """
        dialogWidget = dialogClass(parentForDialog, returnDict, **initDict) # dialog constructor
        parentForDialog.wait_window(dialogWidget.top)                       # pause the parent until window is destroyed

    def show_frame(self, cont):
        """ method for switching content
        """

        frame = self.frames[cont]
        frame.tkraise()
        #frame.updateEvent(None)

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree))
        button3.pack()

class labelSelWidgetFrame(tk.Frame):
    """Frame a labelled selector widget."""

    def __init__(self, parent, label='selector'):
        tk.Frame.__init__(self, parent)
        self.handler = None
        self.id = str(label)
        self.labelW = tk.Label(self, text=label, font=NORM_FONT)
        self.labelW.pack(side=tk.LEFT)
        self.tkStrVar = tk.StringVar(self)
        self.tkStrVar.traceID = None
        self.tkSelW = tk.OptionMenu(self, self.tkStrVar, "No Data")
        self.disable()
        self.tkSelW.pack(side=tk.LEFT)

    def get(self):
        return self.getSelValue()

    def getSelWidet(self):
        return self.tkSelW

    def getVariable(self):
        return self.tkStrVar

    def getSelValue(self):
        return self.tkStrVar.get()

    def setSelValue(self, value):
        self.unsetEventHandler()
        retval = self.tkStrVar.set(value)
        self.setEventHandler()

    def setEventHandler(self, func=None):
        """ Set a new event handler on the menu """
        newHandler = None
        if func is not None :
            """Use new handler, if we get one"""
            newHandler = func
        elif self.handler is not None :
            """Use old handler"""
            newHandler = self.handler

        self.handler = newHandler
        if self.isEnabled :
            """ Set new observer """
            self.tkStrVar.traceID = self.tkStrVar.trace('w', self.handler)
        else :
            debug(self.id+": setEventHandler: disabled, handler saved, but not setting until enabled.")

    def unsetEventHandler(self):
        """ Remove old obserers """
        obsList = self.tkStrVar.trace_info()            # get list of observers
        debug("Got list of traces:"+str(obsList))       #
        for pair in obsList :
            self.tkStrVar.trace_vdelete('u', pair[1])
        #if self.tkStrVar.traceID is not None :
        #    self.tkStrVar.trace_vdelete('u',self.tkStrVar.traceID)

    def setOptionsList(self, strList):
        self.unsetEventHandler()
        self.tkSelW['menu'].delete(0,tk.END)
        for name in strList:
            debug("Adding name to option menu:"+str(name))
            self.tkSelW['menu'].add_command( label=name, command=tk._setit(self.tkStrVar,name) )
        self.setEventHandler()

    def enable(self):
        if self.handler is not None :
            self.isEnabled = True
            self.setEventHandler(self.handler)
            self.tkSelW.configure(state='normal')
        else :
            error(self.id+": Cannot enable, set event handler first.")

    def disable(self):
        self.unsetEventHandler()
        self.tkSelW.configure(state='disable')
        self.isEnabled = False

    def configure(self, *args, **kwargs):
        if 'state' in kwargs.keys():
            self.tkSelW.configure(state=kwargs['state'])

class viewWidgetGroupFrame(tk.Frame):
    """Frame showing the data view widgets."""

    def __init__(self, parent, label="Enable"):
        tk.Frame.__init__(self, parent)
        self.handler = None
        """ A check button for on/off of this view """
        self.var = tk.IntVar()
        self.checkButton = tk.Checkbutton(self, text=label
                ,variable=self.var
                ,command=self._checkChangeHandler
                ,offvalue=0,onvalue=1)
        self.checkButton.pack()
        self.xViewSelFrame = labelSelWidgetFrame(self, label='Abscissa')
        self.xViewSelFrame.pack()
        self.yViewSelFrame = labelSelWidgetFrame(self, label='Ordinate')
        self.yViewSelFrame.pack()
        """Set default state"""
        self.isEnabled = False
        self._disable()
        self.id = str(label)            # debug id

    def enable(self):
        """Programmatically enable this frame, causes change event just
        like changing it from the GUI.
        """
        debug(self.id+": enable: called")
        #self.isEnabled = True
        self.checkButton.select()
        self._enable()

    def _enable(self):
        """Internally enable this frame."""
        self.xViewSelFrame.enable()
        self.yViewSelFrame.enable()
        self.isEnabled = True

    def disable(self):
        """Programmatically disable this frame, causes a button event just like
        changing it from the GUI.
        """
        debug(self.id+": disable: called")
        #self.isEnabled = False
        self.checkButton.deselect()
        self._disable()

    def _disable(self):
        """Internally disable this frame."""
        self.isEnabled = False
        self.xViewSelFrame.disable()
        self.yViewSelFrame.disable()

    def setEventHandler(self, func):
        self.handler = func
        self.xViewSelFrame.setEventHandler(func)
        self.yViewSelFrame.setEventHandler(func) 

    def setView(self, view):
        self.xViewSelFrame.setSelValue(view[0])
        self.yViewSelFrame.setSelValue(view[1])

    def getView(self):
        debug(self.id+": getView: isEnabled:"+str(self.isEnabled))
        retval = None
        if self.isEnabled :
            xSel = self.xViewSelFrame.getSelValue()
            ySel = self.yViewSelFrame.getSelValue()
            retval = (xSel,ySel)
            debug(self.id+": getView: (xSel,ySel):"+str(retval))
        return retval

    def setOptionsList(self, newList):
        """ Update list of options in menu list """
        self.xViewSelFrame.setOptionsList(newList)
        self.yViewSelFrame.setOptionsList(newList)

    def _checkChangeHandler(self):
        if 1 == self.var.get():
            """ Check box was enabled. """
            debug(self.id+": Check button was enabled.")
            self._enable()
        elif 0 == self.var.get():
            """ Check box was disabled. """
            debug(self.id+": Check button was disabled.")
            self._disable()
        else :
            raise TypeError("Cannot interpret check button value"+str(self.var.get()))
        """Call external handler, too."""
        if self.handler is not None :
            self.handler(None)

class PageThree(tk.Frame):
    """Frame showing Data View and chop capabilities
    """

    def __init__(self, parent, controller, **kwargs):
        tk.Frame.__init__(self, parent) # call class parent

        """ Initialize data members """
        self.DA = DA
        self.isSafeToUpdate = False
        self.numViews = 2
        self.deactList = list()

        self.DVconfig = controller.DVconfig

        """ Create label for frame """
        #label = tk.Label(self, text="Data View", font=LARGE_FONT)
        #label.pack(pady=10,padx=10)

        """ Create button to go back to other frame """
        #button1 = ttk.Button(self, text="Back to Home",
        #                    command=lambda: controller.show_frame(StartPage))
        #button1.pack()

        """ Add menu item to load data """
        filemenu = controller.filemenu
        filemenu.insert_command(index=1,label="Load", command=self.load)

        self.addMainFigure()    # Add main figure area to frame
        self.addDataWindow()    # Add widgets for setting data window
        self.addDataView()      # Add widgets for setting data view
        self.addChop()          # Add chop button

    def addDeactivateList(self, listLike) :
        """ Keep a list of deactivate-able widgets """
        if isinstance(listLike, list) or isinstance(listLike, tuple) :
            for item in listLike :
                self.deactList.append(item)
        else :
            self.deactList.append(listLike)

    def deactivateWidgets(self) :
        for widget in self.deactList :
            widget.configure(state='disabled')

    def activateWidgets(self) :
        if not self.DA.isLoaded :
            return DataNotLoaded()
        for widget in self.deactList :
            widget.configure(state='normal')

    def addDataView(self) :
        """ Add widgets that control the view """
        self.viewList = list(('No Data','No Data'))

        """ Add View Widget Sub-Frames """
        self.dataViewSubFrameList = list()              # list of "subframes"
        for frameNum in range(0,self.numViews) :
            subFrame = viewWidgetGroupFrame(self, label="Data View "+str(frameNum))
            subFrame.setEventHandler(self.viewChangeTrace)
            subFrame.pack()
            self.dataViewSubFrameList.append(subFrame)

        """ Data View Index Selection """
        self.altIdxSel = tk.StringVar(self)
        self.altIdxSel.set("No data") # default value
        """
        self.altIdxSelW = tk.OptionMenu(self, self.altIdxSel, "No Data" )
        self.altIdxSelW.configure(state="disabled")
        self.altIdxSelW.pack()
        self.altIdxSel.trace('w', self.viewChangeTrace) # set up event
        self.addDeactivateList(self.altIdxSelW)
        """

    def addDataWindow(self) :
        """ Data Window Size Widget """
        self.dataWindowSizeWidgetLabel = tk.Label(self, text='View Size')
        self.dataWindowSizeWidgetLabel.pack()
        self.dataWindowSizeWidget = tk.Scale(self, from_=1, to=10, resolution=1,
                orient="horizontal")
        self.dataWindowSizeWidget.bind("<ButtonRelease-1>", self.updateEvent)
        self.dataWindowSizeWidget.bind("<Button1-Motion>", self.updateEvent)
        self.dataWindowSizeWidget.pack(fill=tk.X,expand=1)
        """ Data Window Start Widget """
        self.dataWindowStartWidgetLabel = tk.Label(self, text='View Start')
        self.dataWindowStartWidgetLabel.pack()
        self.dataWindowStartWidget = tk.Scale(self, from_=0, to=10, resolution=1,
                orient="horizontal")
        self.dataWindowStartWidget.bind("<ButtonRelease-1>", self.updateEvent)
        self.dataWindowStartWidget.bind("<Button1-Motion>", self.updateEvent)
        self.dataWindowStartWidget.pack(fill=tk.X,expand=1)

    def addMainFigure(self) :
        """ Add main figure area """
        self.fig = plt.figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('No data')
        self.fig.canvas.draw()

        self.canvas = FigureCanvas(self.fig, self)
        """ Set up callback from canvas draw events, i.e. pan/zoom """
        #self.cid1 = self.fig.canvas.mpl_connect('draw_event', self.updateFromCavas)
        #self.cid1 = self.fig.canvas.mpl_connect('button_release_event', self.updateFromCavas)
        #TODO animation
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def addChop(self) :
        chopBW = tk.Button(self, text="Chop", command=self.doChop)
        chopBW.pack()
        self.chopButtonW = chopBW

    def postLoad(self) :
        """ Things to run after loading a new DataAnalyser object.  """
        debug("postLoad: get current view from DA...")
        viewList = self.DA.getView()                    # retrieve the default view after load
        debug("postLoad: get labels from DA...")
        self.updateLabels()                             # get new data types from data loaded
        self.setAltIndex('index')
        self.setView(viewList)                          # configure GUI to reflect new data
        self.isSafeToUpdate = True
        debug("postLoad: isSafeToUpdate:"+str(self.isSafeToUpdate))
        """ now, set the window """
        #TODO use data values instead of index values
        limitDict=self.DA.getIndexLimits()
        maxSize, minVal = ( limitDict['max'] , limitDict['min'] )
        #print( "DEBUG: postLoad: maxSize: "+str(maxSize) )
        #print( "DEBUG: postLoad: minValue: "+str(minVal) )
        self.setWindow( minVal=minVal, start=0,
                        maxSize=maxSize, size=int(maxSize/2)) # reset the GUI window
        self.updateEvent(None)      # update GUI

    def setWindow(self, minVal=0, start=0, maxSize=10, size=10) :
        """ set the GUI values that correspond to the window """
        debug("DEBUG: setWindow: %s, start: %s, maxSize: %s, size: %s"
                ,minVal, start, maxSize, size )
        self.dataWindowSizeWidget.config(from_=1, to=maxSize-start+1)
        self.dataWindowSizeWidget.set(size)
        self.dataWindowStartWidget.config(from_=minVal, to=maxSize-size+1)
        self.dataWindowStartWidget.set(start)

    def load(self, *args, **kwargs) :
        """ catch all load method
        Currently, the only implemented mode is CSV file data.
        """
        self.isSafeToUpdate = False
        name = filedialog.askopenfilename()
        self.loadFileData(path=name, *args, **kwargs)

    def loadFileData(self, path=None, *args, **kwargs) :
        """ Show a dialog to select a file and load it.  """
        if path is None:
            raise TypeError("loadFileData: path option is required")
        print("Got filename:" +path)
        loadData(path, *args, **kwargs)
        self.postLoad()

    def updateLabels(self) :
        """ Update labels from the DataAnalyser object
        Call whenever DA is loaded/changed.
        """
        #print("DEBUG: updateLabels: isSafeToUpdate:", self.isSafeToUpdate)
        if not self.DA.isLoaded :
            return DataNotLoaded()
        newLabels = DA.getLabels()
        #debug("DEBUG: got label list from DA: "+str(newLabels))
        for viewSubFrame in self.dataViewSubFrameList:
            viewSubFrame.setOptionsList(newLabels)

        """ re-enable widgets """
        self.activateWidgets()

    def updateFromCavas(self, event) :
        """ Called when view is changed using figure canvas area. """
        """ Get the figure axis limits """
        figMinX, figMaxX = self.ax.get_xlim()
        debug('Got interval from MPL axis:'+str((figMinX,figMaxX)))
        """ Set the current window to match """
        #TODO

    def viewChangeTrace(self, *args):
        """View is changed, make proper updates downward."""
        debug("viewChange: isSafeToUpdate:"+str(self.isSafeToUpdate))
        if not self.isSafeToUpdate :
            #print("DEBUG: viewChangeTrace: not safe, returning")
            return
        """Do other updates"""
        self.updateEvent(None)

    def setView(self, viewList) :
        """ Set the GUI representation of the current data view
        Takes a "view" object and sets the GUI so that it matches.
        """
        self.isSafeToUpdate = False
        self.viewList = viewList
        for view,subFrame in zip(viewList,self.dataViewSubFrameList) :
            print("DEBUG: DataViewApp: setView: "+str(view))
            subFrame.disable()
            subFrame.setView(view)
            subFrame.enable()

    def setAltIndex(self, newIdx):
        """ Set the GUI presentation of alt index """
        self.isSafeToUpdate = False
        self.altIdxSel.set(newIdx)

    def updateEvent(self, event):
        """ Change/Update data view when user requests a change.
        Call this whenever the user makes a change to view values.
        """
        debug("updateEvent: called, event:"+str(event))
        if not self.DA.isLoaded :
            return DataNotLoaded()
        DA = self.DA

        """ Set window from interface settings """
        newWinSize = self.dataWindowSizeWidget.get()
        newWinStart = self.dataWindowStartWidget.get()
        limitDict=self.DA.getIndexLimits()
        debug("DEBUG: updateEvent: got limits: "+str(limitDict))
        maxSize, minVal = ( limitDict['max'] , limitDict['min'] )
        self.setWindow( minVal=minVal, start=newWinStart,
                        maxSize=maxSize, size=newWinSize )

        """ Set views from interface settings """
        newViewList = list()
        for subFrame in self.dataViewSubFrameList :
            newView = subFrame.getView()
            debug("updateEvent: newView: "+str(newView))
            if newView is not None :
                """If view frame returns None, don't add to list."""
                newViewList.append(newView)

        """ set index """
        try :
            pass
            #DA.setAltIndexColumn(self.altIdxSel.get())
            #TODO
        except Exception as e:
            warn('updateEvent: Failed to set altnernate index, ignoring selection')
            print(e)
        else :
            """ just leave it set to index """
            pass

        DA.setView( viewList=newViewList, windowStart=newWinStart, windowSize=newWinSize,
                windowType='index' )

        """Redraw the plot"""
        dfList = self.DA.getViewData()
        #print("DEBUG: updateEvent: got updated data:", df.colums.tolist())
        ax = self.ax
        ax.clear()
        xlabelList, ylabelList = list(), list()
        for df in dfList :
            """draw all df data as x,y data"""
            (xlabel, ylabel) = df.columns.tolist()
            ax.plot(df[xlabel].values, df[ylabel].values, 'o-')
            """store labels"""
            xlabelList.append(xlabel)
            ylabelList.append(ylabel)

        """Set labels"""
        newXlabel, newYlabel = str(), str()
        xlabelOverride = self.DVconfig.get('xlabel')
        ylabelOverride = self.DVconfig.get('ylabel')
        """Remember, configer doesn't hold native objects"""
        debug("Plotting: xlabelOverride: %s" % xlabelOverride)
        debug("Plotting: xlabelOverride eq None: %s" % (xlabelOverride == None))
        if (xlabelOverride == None) or (ylabelOverride == None) :
            """Write the labels for all data"""
            debug("Plotting: Label overrides OFF")
            sep = "\n"
            newXlabel = sep.join( xlabelList )
            newYlabel = sep.join( ylabelList )
            debug("new xlabel: %s" % newXlabel)
        else :
            """the labels"""
            debug("Plotting: Label overrides ON")
            newXlabel = xlabelOverride
            newYlabel = ylabelOverride
        ax.set_xlabel(newXlabel)
        ax.set_ylabel(newYlabel)
        self.fig.canvas.draw()

        """ Show Statistics """
        self.showStats()

    def showStats(self):
        """ Get and report statsistics for the current view """
        statsList = self.DA.getStats()
        for stats in statsList:
            print("Data View Statistics:")
            print(stats)

    def doChop(self) :
        directory=pathlib.PurePath(os.path.curdir)
        chopConf = self.DVconfig.get('chopOpts')
        debug('chopConf:'+str(chopConf))
        debug('dict(chopConf):'+str(dict(chopConf)))
        self.DA.chop(dirpath=directory, **dict(chopConf))

class DataNotLoaded(Exception) :
    def __init__(self,*args,**kwargs) :
        Exception.__init__(self,*args,**kwargs)

def loadData(filename, *args, **kwargs):
    global DA
    #print("DEBUG: DataViewer: loadData: loading data")
    kwargs['index_col'] = False #force DA to always generate it's own index
    DA.load(*args
            ,filetype='csv' # force CSV for now
            ,filename=filename
            , **kwargs)

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

def quitHandler():
    print("Quitting...")
    #TODO Call root window.quit()
    quit()

class LabelEntryFrame(tk.Frame):
    """Frame holding a label and a entry widget horizontally aligned"""

    def __init__(self, parent, label, strValue):
        debug("got label:{}; string:{}".format(label,strValue))
        tk.Frame.__init__(self, parent)
        labelW = tk.Label(self, text=str(label), font=NORM_FONT)
        labelW.pack(side=tk.LEFT,padx=5)
        entryW = tk.Entry(self)
        entryW.pack(side=tk.LEFT,padx=5)
        entryW.delete(0,tk.END)
        entryW.insert(0,str(strValue))
        self.entryW = entryW

    def get(self):
        return self.entryW.get()

class LabelCheckFrame(tk.Frame):
    """Frame holding a label and a checkbox widget horizontally aligned"""

    def __init__(self, parent, boolVal):
        debug("got boolval:{}".format(boolVal))
        tk.Frame.__init__(self, parent)
        var = tk.BooleanVar()
        checkBoxW = tk.Checkbutton(self, text="Enabled", variable=var
                ,onvalue=True, offvalue=False)
        checkBoxW.pack(side=tk.LEFT,padx=5)
        self.var = var
        self.checkBoxW = checkBoxW

        if boolVal :
            self.enable()
        else :
            self.disable()

    def get(self):
        return bool(self.var.get())

    def enable(self):
        self.checkBoxW.select()

    def disable(self):
        self.checkBoxW.deselect()


class DVdialogHelper:
    """Helper class for tkinter dialog boxes.  This class is safe to create before
    it's needed/used.  When you want to pop it up, call the .launch method.
    """

    def __init__(self, parent, returnDict):
        debug("Createing new DVdialog")
        self.parent = parent
        self.retDict = returnDict
        self.label=returnDict['label']
        self.entryWidgetDict = dict()
        self.restoreValFunc = dict()

    def launch(self, **kwargs):
        """Create window"""
        top = self.top = tk.Toplevel(self.parent)
        tk.Label(top, text=self.label).pack()
        """Create most elements of the dialog from kwargs"""
        self._buildEntryWidgets(**self.retDict)
        """Show all the elements created before"""
        for key in self.entryWidgetDict.keys():
            self.entryWidgetDict[key].pack()
        """Finally, add button"""
        b = tk.Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def _buildEntryWidgets(self, **kwargs):
        for key in kwargs.keys():
            if key not in ('label','func'):             # don't expose these as options
                debug("Adding dialog option:"+str(key))
                """For each key, make a widget for display and recording of the value."""
                currentValue = kwargs[key]
                if isinstance(currentValue, bool) :
                    """Boolean value; use check box widget."""
                    checkBoxFrame= LabelCheckFrame(self.top,currentValue)
                    self.entryWidgetDict[key] = checkBoxFrame
                    self.restoreValFunc[key] = self.toBool
                elif isinstance(currentValue, (Number, str)) :
                    """Number or string value; use entry widget."""
                    entryFrame = LabelEntryFrame(self.top, key, kwargs[key])
                    self.entryWidgetDict[key] = entryFrame
                    self.restoreValFunc[key] = self.toNumber
                elif isinstance(currentValue,(list,tuple)):
                    """List value; use option list."""
                    optListFrame = labelSelWidgetFrame(self.top,label=key)
                    self.entryWidgetDict[key] = optListFrame
                    self.restoreValFunc[key] = self.toString
                else :
                    error("Cannot make widget for variable type: {}".format(currentValue))

    def toBool(self, element):
        """Enterpret the current value of the widget as a boolean"""
        return bool(element.get())

    def toNumber(self, element):
        """Enterpret the current value of the widget as a number"""
        return float(element.get())

    def toList(self, element):
        """Enterpret the current value of the widget as a list"""
        return list(element.get())

    def toString(self, element):
        """Enterpret the current value of the widget as a string"""
        return str(element.get())

    def _extractEntryValues(self):
        """Go through all entry widgets, get new values, store in return
        dictionary provided by caller"""
        for key in self.entryWidgetDict.keys():
            e = self.entryWidgetDict[key]
            func = self.restoreValFunc[key]
            newVal = func(e)
            self.retDict[key] = newVal
            debug("DVdialog: setting %s=%s", key, newVal)
        debug("DVdialog: retDict: %s", self.retDict)

    def ok(self):
        self._extractEntryValues()
        self.top.destroy()

def convertBack(strValue):
    """Take a value and try to convert it to the most restrictive data type.
    Parameters:
    value: *string* value to convert to a numerical type, if possible.

    Returns:
    Int, if possible; otherwise float, or, if that is not possible, either, a
    string.
    """
    try :
        retVal = int(value)
    except ValueError:
        try :
            retVal = float(value)
        except ValueError:
            retVal = str(value)

    return retVal 

'''
def dictToMenu(menu, dct):
    for key in dct.keys():
        menu.add_command(label=dct['label'], command=pass)
'''


if __name__ == "__main__" :
    app = DataViewApp()
    app.protocol("WM_DELETE_WINDOW", quitHandler)
    app.mainloop()
