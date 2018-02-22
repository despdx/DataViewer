#!/usr/bin/python3

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
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        self.DA = DA

        ''' Add menu item to load data '''
        filemenu = controller.filemenu
        filemenu.insert_command(index=1,label="Load", command=self.loadFileData)

        self.fig = plt.figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        #df = DA.getViewData()
        #defViewX = DA.currentView[0]
        #defViewY = DA.currentView[1]
        #print("DEBUG: defalt view: "+str([defViewX,defViewY]))
        #x = df[defViewX]
        #y = df[defViewY]
        #self.ax.plot(x, y, 'bo-')
        self.ax.set_title('No data')
        self.fig.canvas.show()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        #self.canvas.mpl_connect('
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
        ''' Data View Index  '''
        ''' Data View X Widget '''
        self.xViewSel = tk.StringVar(self)
        self.xViewSel.set("No data") # default value
        self.dataViewXwidget = tk.OptionMenu(self, self.xViewSel, "No Data" )
        self.dataViewXwidget.configure(state="disabled")
        self.dataViewXwidget.pack()
        ''' Data View Y Widget '''
        self.yViewSel = tk.StringVar(self)
        self.yViewSel.set("No data") # default value
        self.dataViewYwidget = tk.OptionMenu(self, self.xViewSel, "No Data" )
        self.dataViewYwidget.pack()
        self.dataViewYwidget.configure(state="disabled")

    def postLoad(self) :
        self.updateLabels() # get new data types from data loaded
        view = self.DA.getView() # retrieve the default view after load
        self.setView(view) # configure GUI to reflect new data

    def loadFileData(self) :
        name = filedialog.askopenfilename()
        print("Got filename:" +name)
        loadData(name)
        self.postLoad()

    def updateLabels(self) :
        if not self.DA.isLoaded :
            return DataNotLoaded()
        newLabels = DA.getLabels()
        print("DEBUG: got label list from DA: "+str(newLabels))
        ''' Delete old options from menu '''
        self.dataViewXwidget['menu'].delete(0, tk.END)
        self.dataViewYwidget['menu'].delete(0, tk.END)
        ''' Relabel the drop down menus'''
        for label in newLabels :
            self.dataViewXwidget['menu'].add_command( label=label, command=lambda : self.xViewSel.set(label) )
            self.dataViewYwidget['menu'].add_command( label=label, command=lambda : self.yViewSel.set(label) )
        ''' re-enable widgets '''
        self.dataViewXwidget.configure(state="normal") # enable widget
        self.dataViewYwidget.configure(state="normal") # enable widget

    def updateListWidget(self, listWidget, listValues ) :
        END = tk.END
        for item in listValues :
            listWidget.insert(END,item)

    def setView(self, view) :
        ''' Set the GUI representation of the current data view '''
        self.xViewSel.set(view[0])
        #self.dataViewXwidget.pack()
        self.yViewSel.set(view[1])
        #self.dataViewYwidget.pack()

    def updateEvent(self, event):
        if not self.DA.isLoaded :
            return DataNotLoaded()
        DA = self.DA
        newWinSize = self.dataWindowSizeWidget.get()
        newWinStart = self.dataWindowStartWidget.get()
        lastIndex = DA.getLastIndex()
        lastStart = lastIndex - newWinSize

        ''' set view '''
        xSel = self.xViewSel.get()
        ySel = self.yViewSel.get()
        newView = [ xSel,ySel ]
        print("DEBUG: newView: "+str(newView))

        DA.setView( view=None, windowStart=newWinStart, windowSize=newWinSize,
                windowType='index' )

        df = DA.getViewData()
        self.ax.clear()
        self.ax.plot(df[xSel].values, df[ySel].values, 'bo-')
        self.fig.canvas.show()

class DataNotLoaded(Exception) :
    def __init__(self,*args,**kwargs) :
        Exception.__init__(self,*args,**kwargs)

def loadData(filename):
    global DA
    print("DEBUG: DataViewer: loadData: loading data")
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
    quit()

app = DataViewApp()
app.protocol("WM_DELETE_WINDOW", quitHandler)
app.mainloop()
