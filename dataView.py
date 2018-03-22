#!/usr/bin/python3
''' DataView Application
Just helps looking at large data groups and finding useful bits, and separating
them out for easier analysis.
'''
#TODO show more than one relation
#TODO linear fit
#TODO fix doc strings
#TODO speed up update (without animation)
#TODO filter data types
#TODO pick window from figure
#TODO disable chop button until loaded
#TODO secondary views
#TODO scale scales
#TODO WIP Alternate indexes, need to be able to change scales first
#TODO animation
#TODO start on start frame, show PageThree after load
#TODO better window and view widget layouts
#TODO use pymagic to detect file types
#TODO ? fix NotImplementedError class
#TODO show summary statistics for view in GUI

import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
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
    ''' Data View Application Class
    '''

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
        ''' Build the application (main) window
        '''
        #tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Data Viewer")

        """ Load default configuration """
        self.DVconfig = configer.Configer(configDefault)
        self.testValue = 'hi there'
        
        ''' Arrange "this" frame '''
        self.minsize(640,480)
        #self.geometry("640x480")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ''' build a menu bar '''
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save settings", command=lambda: popupmsg('Not supported just yet!'))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.menubar = menubar
        self.filemenu = filemenu

        ''' Finish Menu bar '''
        tk.Tk.config(self,menu=menubar)

        ''' Initialize Data Viewer '''
        self.DA = DA

        ''' Make a dictionary of different frame types (classes) that
        we will use for the application.
        '''
        self.frames = {}
        for newFrame in (StartPage, PageThree):

            frame = newFrame(container, self)

            self.frames[newFrame] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        ''' Show the starting frame type on init '''
        self.show_frame(PageThree)

    def show_frame(self, cont):
        ''' method for switching content
        '''

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
        self.labelW = tk.Label(self, text=label, font=NORM_FONT)
        self.labelW.pack(side=tk.LEFT)
        self.tkStrVar = tk.StringVar(self)
        self.tkSelW = tk.OptionMenu(self, self.tkStrVar, "No Data")
        self.disable()
        self.tkSelW.pack(side=tk.LEFT)

    def getSelWidet(self):
        return self.tkSelW

    def getVariable(self):
        return self.tkStrVar

    def getSelValue(self):
        return self.tkStrVar.get()

    def setSelValue(self, value):
        return self.tkStrVar.set(value)

    def setEventHandler(self, func):
        """ Set a new event handler on the menu """
        """ Remove old obserers """
        obsList = self.tkStrVar.trace_info()            # get list of observers
        debug("Got list of traces:"+str(obsList))       #
        for pair in obsList :                           # each pair of observer identifiers
            self.tkStrVar.remove(pair)                  # remove this observer
        """ Set new observer """
        self.tkStrVar.trace('w', func)

    def setOptionList(self, strList):
        self.tkselW['menu'].delete(0,tk.END)
        for name in strList:
            debug("Adding name to option menu:"+str(name))
            self.tkSelW['menu'].add_command( label=name, command=tk._setit(self.tkStrVar,name) )
        self.enable()

    def enable(self):
        self.tkSelW.configure(state='normal')

    def disable(self):
        self.tkSelW.configure(state='disable')

    def configure(self, *args, **kwargs):
        if 'state' in kwargs.keys():
            self.tkSelW.configure(state=kwargs['state'])

class viewWidgetGroupFrame(tk.Frame):
    """Frame showing the data view widgets."""

    def __init__(self, parent, label="Enable"):
        tk.Frame.__init__(self, parent)
        """ A check button for on/off of this view """
        self.var = tk.IntVar()
        self.checkButton = tk.Checkbutton(self, text=label, variable=self.var)
        self.checkButton.pack()
        self.var.trace('w', self._checkChangeHandler)
        self.xViewSelFrame = labelSelWidgetFrame(self, label='Abscissa')
        self.xViewSelFrame.pack()
        self.yViewSelFrame = labelSelWidgetFrame(self, label='Ordinate')
        self.yViewSelFrame.pack()

    def enable(self):
        self.xViewSelFrame.enable()
        self.yViewSelFrame.enable()

    def disable(self):
        self.xViewSelFrame.disable()
        self.yViewSelFrame.disable()

    def setEventHandler(self, func):
        self.xViewSelFrame.setEventHandler(func)
        self.yViewSelFrame.setEventHandler(func) 

    def setView(self, view):
        self.xViewSelFrame.setSelValue(view[0])
        self.yViewSelFrame.setSelValue(view[1])

    def getView(self):
        xSel = self.xViewSelFrame.getSelValue()
        ySel = self.yViewSelFrame.getSelValue()
        return list(xSel,ySel)

    def _checkChangeHandler(self, event):
        if 1 == self.var.get():
            """ Check box was enabled. """
            debug("Check button was enabled.")
            self.enable()
        elif 0 == self.var.get():
            """ Check box was disabled. """
            debug("Check button was disabled.")
            self.disable()
        else :
            raise TypeError("Cannot interpret check button value"+str(self.var.get()))

class PageThree(tk.Frame):
    """Frame showing Data View and chop capabilities
    """

    def __init__(self, parent, controller, **kwargs):
        tk.Frame.__init__(self, parent) # call class parent

        ''' Initialize data members '''
        self.DA = DA
        self.isSafeToUpdate = False
        self.numViews = 2
        self.deactList = list()

        self.DVconfig = controller.DVconfig

        ''' Create label for frame '''
        label = tk.Label(self, text="Data View", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        ''' Create button to go back to other frame '''
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        ''' Add menu item to load data '''
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
        #self.viewList = list(('No Data','No Data'),('No Data','No Data'))
        self.viewList = list(('No Data','No Data'))
        self.dataViewWidgetDict = dict()

        """ Add View Widget Sub-Frames """
        self.dataViewSubFrameList = list()              # list of "subframes"
        for frameNum in range(0,self.numViews) :
            subFrame = viewWidgetGroupFrame(self, label="Data View "+str(frameNum))
            subFrame.setEventHandler(self.viewChangeTrace)
            subFrame.pack()
            self.dataViewSubFrameList.append(subFrame)
        self.dataViewSubFrameList[0].enable()

        """ Data View Index Selection """
        """
        self.altIdxSel = tk.StringVar(self)
        self.altIdxSel.set("No data") # default value
        self.altIdxSelW = tk.OptionMenu(self, self.altIdxSel, "No Data" )
        self.altIdxSelW.configure(state="disabled")
        self.altIdxSelW.pack()
        self.altIdxSel.trace('w', self.viewChangeTrace) # set up event
        self.addDeactivateList(self.altIdxSelW)
        """

    def addDataWindow(self) :
        ''' Data Window Size Widget '''
        self.dataWindowSizeWidgetLabel = tk.Label(self, text='View Size')
        self.dataWindowSizeWidgetLabel.pack()
        self.dataWindowSizeWidget = tk.Scale(self, from_=1, to=10, resolution=1,
                orient="horizontal")
        self.dataWindowSizeWidget.bind("<ButtonRelease-1>", self.updateEvent)
        self.dataWindowSizeWidget.bind("<Button1-Motion>", self.updateEvent)
        self.dataWindowSizeWidget.pack(fill=tk.X,expand=1)
        ''' Data Window Start Widget '''
        self.dataWindowStartWidgetLabel = tk.Label(self, text='View Start')
        self.dataWindowStartWidgetLabel.pack()
        self.dataWindowStartWidget = tk.Scale(self, from_=0, to=10, resolution=1,
                orient="horizontal")
        self.dataWindowStartWidget.bind("<ButtonRelease-1>", self.updateEvent)
        self.dataWindowStartWidget.bind("<Button1-Motion>", self.updateEvent)
        self.dataWindowStartWidget.pack(fill=tk.X,expand=1)

    def addMainFigure(self) :
        ''' Add main figure area '''
        self.fig = plt.figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('No data')
        self.fig.canvas.show()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        """ Set up callback from canvas draw events, i.e. pan/zoom """
        #self.cid1 = self.fig.canvas.mpl_connect('draw_event', self.updateFromCavas)
        #self.cid1 = self.fig.canvas.mpl_connect('button_release_event', self.updateFromCavas)
        #TODO animation
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def addChop(self) :
        chopBW = tk.Button(self, text="Chop", command=self.doChop)
        chopBW.pack()
        self.chopButtonW = chopBW

    def postLoad(self) :
        ''' Things to run after loading a new DataAnalyser object.
        '''
        self.updateLabels() # get new data types from data loaded
        viewList = self.DA.getView() # retrieve the default view after load
        self.setView(viewList) # configure GUI to reflect new data
        self.setAltIndex('index')
        self.isSafeToUpdate = True
        #print("DEBUG: postLoad: isSafeToUpdate", self.isSafeToUpdate)
        ''' now, set the window '''
        #TODO use data values instead of index values
        limitDict=self.DA.getIndexLimits()
        maxSize, minVal = ( limitDict['max'] , limitDict['min'] )
        #print( "DEBUG: postLoad: maxSize: "+str(maxSize) )
        #print( "DEBUG: postLoad: minValue: "+str(minVal) )
        self.setWindow( minVal=minVal, start=0,
                        maxSize=maxSize, size=int(maxSize/2)) # reset the GUI window
        self.updateEvent(None)      # update GUI

    def setWindow(self, minVal=0, start=0, maxSize=10, size=10) :
        ''' set the GUI values that correspond to the window '''
        #print("DEBUG: setWindow:"+str(minVal)
        #        +", start:"+str(start)
        #        +", maxSize:"+str(maxSize)
        #        +", size"+str(size) )
        self.dataWindowSizeWidget.config(from_=1, to=maxSize-start)
        self.dataWindowSizeWidget.set(size)
        self.dataWindowStartWidget.config(from_=minVal, to=maxSize-size)
        self.dataWindowStartWidget.set(start)

    def load(self, *args, **kwargs) :
        ''' catch all load method
        Currently, the only implemented mode is CSV file data.
        '''
        self.isSafeToUpdate = False
        name = filedialog.askopenfilename()
        self.loadFileData(path=name, *args, **kwargs)

    def loadFileData(self, *args, path=None, **kwargs) :
        ''' Show a dialog to select a file and load it.
        '''
        print("Got filename:" +path)
        loadData(path, *args, **kwargs)
        self.postLoad()

    def updateLabels(self) :
        ''' Update labels from the DataAnalyser object
        Call whenever DA is loaded/changed.
        '''
        #print("DEBUG: updateLabels: isSafeToUpdate:", self.isSafeToUpdate)
        if not self.DA.isLoaded :
            return DataNotLoaded()
        newLabels = DA.getLabels()
        #print("DEBUG: got label list from DA: "+str(newLabels))
        ''' Delete old options from menu '''
        self.dataViewXwidget['menu'].delete(0, tk.END)
        self.dataViewYwidget['menu'].delete(0, tk.END)
        self.altIdxSelW['menu'].delete(0, tk.END)
        self.altIdxSelW['menu'].add_command( label='index', command=tk._setit(self.altIdxSel,'index') )
        ''' Relabel the drop down menus'''
        for label in newLabels :
            debug("Adding label to option menu:"+str(label))
            self.dataViewXwidget['menu'].add_command( label=label, command=tk._setit(self.xViewSel,label) )
            self.dataViewYwidget['menu'].add_command( label=label, command=tk._setit(self.yViewSel,label) )
            self.altIdxSelW['menu'].add_command( label=label, command=tk._setit(self.altIdxSel,label) )
        ''' re-enable widgets '''
        self.activateWidgets()

    def updateFromCavas(self, event) :
        """ Called when view is changed using figure canvas area. """
        """ Get the figure axis limits """
        figMinX, figMaxX = self.ax.get_xlim()
        debug('Got interval from MPL axis:'+str((figMinX,figMaxX)))
        """ Set the current window to match """
        #TODO

    def viewChangeTrace(self, *args):
        #print("DEBUG: viewChange: isSafeToUpdate", self.isSafeToUpdate)
        if not self.isSafeToUpdate :
            #print("DEBUG: viewChangeTrace: not safe, returning")
            return
        newx, newy = ( self.xViewSel.get(), self.yViewSel.get() )
        #print("DEBUG: viewChangeTrace: new selection:",str((newx,newy)) )
        self.updateEvent(None)

    def setView(self, viewList) :
        """ Set the GUI representation of the current data view
        Takes a "view" object and sets the GUI so that it matches.
        """
        self.isSafeToUpdate = False
        for view,subFrame in zip(viewList,self.dataViewSubFrameList) :
            print("DEBUG: DataViewApp: setView: "+str(view))
            subFrame.setView(view)
            # TODO Set active value in pulldown

    def setAltIndex(self, newIdx):
        """ Set the GUI presentation of alt index """
        self.isSafeToUpdate = False
        self.altIdxSel.set(newIdx)

    def updateEvent(self, event):
        """ Change/Update data view when user requests a change.
        Call this whenever the user makes a change to view values.
        """
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

        DA.setView( view=newView, windowStart=newWinStart, windowSize=newWinSize,
                windowType='index' )

        df = self.DA.getViewData()
        #print("DEBUG: updateEvent: got updated data:", df.colums.tolist())
        self.ax.clear()
        self.ax.plot(df[xSel].values, df[ySel].values, 'bo-')
        self.ax.set_xlabel(xSel)
        self.ax.set_ylabel(ySel)
        self.fig.canvas.show()

        """ Show Statistics """
        self.showStats()

    def showStats(self):
        """ Get and report statsistics for the current view """
        statString = self.DA.getStats()
        print(statString)

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

if __name__ == "__main__" :
    app = DataViewApp()
    app.protocol("WM_DELETE_WINDOW", quitHandler)
    app.mainloop()
