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
        self.geometry("640x480")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ''' build a menu bar '''
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save settings", command=lambda: popupmsg('Not supported just yet!'))
        filemenu.add_command(label="Load", command=loadData)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)

        ''' Finish Menu bar '''
        tk.Tk.config(self,menu=menubar)

        ''' Make a dictionary of different frame types (classes) that
        we will use for the application.
        '''
        self.frames = {}
        for newFrame in (StartPage, PageThree):

            frame = newFrame(container, self)

            self.frames[newFrame] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        ''' Intialize Data Viewer '''
        self.DA = DA

        ''' Show the starting frame type on init '''
        self.show_frame(PageThree)

    def show_frame(self, cont):
        ''' method for switching content
        '''

        frame = self.frames[cont]
        frame.tkraise()
        frame.updateEvent(None)

    def loadData(self, event) :
        loadData()
        self.show_frame(PageThree)

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree))
        button3.pack()


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        data = ([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        self.fig = plt.figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(data[0], data[1], 'bo-')

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        #self.canvas.mpl_connect('
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        dataWindow = tk.Scale(self, from_=100, to=1000, resolution=1,
                orient="horizontal")
        dataWindow.bind("<ButtonRelease-1>", self.updateEvent)
        dataWindow.pack()

    def paintCanvasWithFigure(self, canvas, fig):
        self.canvas

    def updateEvent(self, event):
        global DA
        df = DA.getViewData()
        self.ax.clear()
        self.ax.plot(df[0].values, df[1].values, 'bo-')
        self.fig.canvas.show()

def loadData(event):
    global DA
    global labels

    name = filedialog.askopenfilename()
    print("Got filename:" +name)
    DA.load_csv(filename, header=self.headerRow)
    labels = DA.getLabels()
    return labels


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
