#!/usr/bin/python3
''' DataView Application
Just helps looking at large data groups and finding useful bits, and separating
them out for easier analysis.
'''
#TODO chop
#TODO wider sliders
#TODO animation
#TODO configuration

import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

LARGE_FONT = ("Times", 12)

filename = "No File Loaded"
from DataAnalyser.DataAnalyser import DataAnalyser
DA = DataAnalyser()
#DA.load_csv('data.csv', index_col=0)
#print("DA has data member: " + str(DA.data) )
#data = ([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
#labels = ['x','y']
#figMain = plt.figure(figsize=(5,4), dpi=100)
#axMain1 = figMain.add_subplot(111)

class DataViewApp(tk.Tk):
    ''' Data View Application Class
    '''

    headerRow = 0
    windowType = 'index'

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        ''' Build the application (main) window
        '''
        #tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Data Viewer")
        
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

        ''' Intialize Data Viewer '''
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


class PageThree(tk.Frame):

    #TODO : organize default values

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) # call class parent

        ''' Initialize data members '''
        self.DA = DA
        self.isSafeToUpdate = False

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

    def addDataView(self) :
        ''' Data View Index  '''
        #TODO 
        ''' Data View X Widget '''
        self.xViewSel = tk.StringVar(self)
        self.xViewSel.set("No data") # default value
        self.dataViewXwidget = tk.OptionMenu(self, self.xViewSel, "No Data" )
        self.dataViewXwidget.configure(state="disabled")
        self.dataViewXwidget.pack()
        self.xViewSel.trace('w', self.viewChangeTrace) # set up event
        ''' Data View Y Widget '''
        self.yViewSel = tk.StringVar(self)
        self.yViewSel.set("No data") # default value
        self.dataViewYwidget = tk.OptionMenu(self, self.yViewSel, "No Data" )
        self.dataViewYwidget.configure(state="disabled")
        self.dataViewYwidget.pack()
        self.yViewSel.trace('w', self.viewChangeTrace) # set up event

    def addDataWindow(self) :
        ''' Data Window Size Widget '''
        self.dataWindowSizeWidget = tk.Scale(self, from_=1, to=10, resolution=1,
                orient="horizontal")
        self.dataWindowSizeWidget.bind("<ButtonRelease-1>", self.updateEvent)
        self.dataWindowSizeWidget.pack()
        ''' Data Window Start Widget '''
        self.dataWindowStartWidget = tk.Scale(self, from_=0, to=10, resolution=1,
                orient="horizontal")
        self.dataWindowStartWidget.bind("<ButtonRelease-1>", self.updateEvent)
        self.dataWindowStartWidget.pack()

    def addMainFigure(self) :
        ''' Add main figure area '''
        self.fig = plt.figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('No data')
        self.fig.canvas.show()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        #TODO animation
        #self.canvas.mpl_connect('
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def postLoad(self) :
        ''' Things to run after loading a new DataAnalyser object.
        '''
        self.updateLabels() # get new data types from data loaded
        view = self.DA.getView() # retrieve the default view after load
        self.setView(view) # configure GUI to reflect new data
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

    def load(self,*args,**kwargs) :
        ''' catch all load method
        Currently, the only implemented mode is CSV file data.
        '''
        self.isSafeToUpdate = False
        self.loadFileData()

    def loadFileData(self) :
        ''' Show a dialog to select a file and load it.
        '''
        name = filedialog.askopenfilename()
        print("Got filename:" +name)
        loadData(name)
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
        ''' Relabel the drop down menus'''
        for label in newLabels :
            #print("DEBUG: adding label to option menu:",label)
            self.dataViewXwidget['menu'].add_command( label=label, command=tk._setit(self.xViewSel,label) )
            self.dataViewYwidget['menu'].add_command( label=label, command=tk._setit(self.yViewSel,label) )
            #self.dataViewXwidget['menu'].add_command( label=label, command=lambda : self.xViewSel.set(label) ) # wrong!
            #self.dataViewYwidget['menu'].add_command( label=label, command=lambda : self.yViewSel.set(label) ) # wrong!
        ''' re-enable widgets '''
        self.dataViewXwidget.configure(state="normal") # enable widget
        self.dataViewYwidget.configure(state="normal") # enable widget

    def viewChangeTrace(self, *args):
        #print("DEBUG: viewChange: isSafeToUpdate", self.isSafeToUpdate)
        if not self.isSafeToUpdate :
            #print("DEBUG: viewChangeTrace: not safe, returning")
            return
        newx, newy = ( self.xViewSel.get(), self.yViewSel.get() )
        #print("DEBUG: viewChangeTrace: new selection:",str((newx,newy)) )
        self.updateEvent(None)

    def setView(self, view) :
        ''' Set the GUI representation of the current data view
        Takes a "view" object and sets the GUI so that it matches.
        '''
        self.isSafeToUpdate = False
        #print("DEBUG: DataViewApp: setView: "+str(view))
        self.xViewSel.set(view[0])
        self.yViewSel.set(view[1])
        # TODO Set active value in pulldown

    def updateEvent(self, event):
        ''' Change/Update data view when user requests a change.
        Call this whenever the user makes a change to view values.
        '''
        if not self.DA.isLoaded :
            return DataNotLoaded()
        DA = self.DA
        newWinSize = self.dataWindowSizeWidget.get()
        newWinStart = self.dataWindowStartWidget.get()
        limitDict=self.DA.getIndexLimits()
        #print("DEBUG: updateEvent: got limits: "+str(limitDict))
        maxSize, minVal = ( limitDict['max'] , limitDict['min'] )
        self.setWindow( minVal=minVal, start=newWinStart,
                        maxSize=maxSize, size=newWinSize )

        ''' set view '''
        xSel = self.xViewSel.get()
        ySel = self.yViewSel.get()
        newView = [ xSel,ySel ]
        #print("DEBUG: updateEvent: newView: "+str(newView))

        DA.setView( view=newView, windowStart=newWinStart, windowSize=newWinSize,
                windowType='index' )

        df = DA.getViewData()
        #print("DEBUG: updateEvent: got updated data:", df.colums.tolist())
        self.ax.clear()
        self.ax.plot(df[xSel].values, df[ySel].values, 'bo-')
        self.fig.canvas.show()

class DataNotLoaded(Exception) :
    def __init__(self,*args,**kwargs) :
        Exception.__init__(self,*args,**kwargs)

def loadData(filename):
    global DA
    #print("DEBUG: DataViewer: loadData: loading data")
    DA.load_csv(filename)

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

app = DataViewApp()
app.protocol("WM_DELETE_WINDOW", quitHandler)
app.mainloop()
