#!/usr/bin/python3
'''
Data Analyser Helper

'''
#TODO add chop capability
#TODO configuration
#TODO polymorphic load
#TODO multi-key HDF5 instead of many files
#TODO linear fit, view
#TODO quadratic fit, view
#TODO ML fits

import pandas as pd
import numpy as np

filetypes = {
        'csv': pd.DataFrame.from_csv ,
        }


class DataAnalyser(object):
    '''
    Helper object for reading some common data types and exploring them.
    '''

    isLoaded = False
    configDefault = {
            "chopDirectory"         : '.'
            ,"chopFilenamePrefix"    : 'chop'
            ,"hdfKey"                : 'chop'
            }

    def __init__(self, initObj=None, *args, **kwargs):
        self.config = self.configDefault
        if initObj :
            ''' Try to initialize the data object with the first passed argument '''
            self.df = pd.DataFrame(initObj)
            self.isLoaded = True
            self.__setDefaultView()
        else :
            ''' Otherwise, empty'''
            pass
        if kwargs is not None :
            for key,val in kwargs.items() :
                self.config[key] = val

    def __setDefaultView(self):
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: __setDefaultView: no data loaded")
        self.windowStart = 0
        self.windowSize = self.df.shape[0]
        self.windowType = 'index'
        self.altIndexCol = 'index'
        ''' Create a default view of the fist column only.  One column is
        technically okay, but, rest of implementation may assume otherwise.
        '''
        columns = self.df.columns
        self.currentView = columns[0:1].tolist()
        if columns.size > 1 :
            self.currentView = columns[0:2].tolist()

    def loadRandomData(self) :
        x = np.arange(100)
        y = np.random.rand(100)
        self.df = pd.DataFrame( {'x':x, 'y':y} )
        self.isLoaded = True
        self.__setDefaultView()

    def load_csv(self, *args, **kwargs):
        data = pd.DataFrame.from_csv(*args, **kwargs)
        columns = data.columns.tolist()
        self.df = data
        self.isLoaded = True
        self.cleanData()
        self.__setDefaultView()

##    def load(self, filetype='csv', filename=None, *args, **kwargs)##:
##        self.df = None
##        ''' Determine which file to load '''
##        if filename == None :
##            if self.filename == None :
##                raise Exception('No Filename Given')
##        else :
##            self.filename = filename
##
##        ''' Load the file with Pandas '''
##        loadFunc = filetypes[filetype]
##        self.df = loadFunc(path=filename, args, kwargs)

    def cleanData(self) :
        #data.dropna(inplace=True)
        #data.reset_index(drop=True)
        print("Not yet implemented.")

    def getColumnList(self) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: getColumnList: no data loaded")
        return self.getLabels()

    def getLabels(self):
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: getLabels: no data loaded")
        return self.df.columns

    def setAltIndexColumn(self, value):
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: setAltIndexColumn: no data loaded")
        if value not in self.df.columns :
            raise Exception('Invalid Column Name')
        self.altIndexCol = value

    def setView(self, view=None, windowStart = None, windowSize=None, windowType=None) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: no data loaded")
        goodLabels = self.getLabels()
        if view is not None :
            for item in view :
                if item not in goodLabels :
                    raise TypeError("ERROR: '"+item+"' not a valid label")
            self.currentView = view
        if windowStart is not None :
            self.windowStart = windowStart
        if windowSize is not None :
            self.windowSize = windowSize
        if windowType is not None :
            if not windowType == 'index' :
                print("WARNING: cannot set index type: " +str(windowType))
                print("The only supported index type is: index.")
            #self.windowType = windowType

    def getIndexLimits(self) :
        #TODO use alternative index
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: no data loaded")
        return {    'max' : self.df.index.max(),
                    'min' : self.df.index.min() }

    def getView(self) :
        return self.currentView

    def getViewLimits(self) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: getWindowLimits: no data loaded")
        x,y = self.view
        return {    'xmin' : self.df[x].min(),
                    'ymin' : self.df[y].min(),
                    'xmax' : self.df[x].max(),
                    'ymax' : self.df[y].max() }

    def setWindow(self, start, size) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: setWindow: no data loaded")
        self.windowStart = start
        self.windowSize = size

    def getWindow(self) :
        return (self.windowStart, self.windowSize)

    def getWindow(self) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: getView: no data loaded")
        return ( self.windowStart , self.windowSize )
    
    def getViewData(self) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: getViewData: no data loaded")
        if self.windowType == 'index' :
            start = self.windowStart
            end = self.windowStart + self.windowSize
            mySlice = slice(start,end)
            df = self.df[mySlice]
            #print("DEBUG: currentView:"+ str(self.currentView))
            df = df[ self.currentView ]
            return df
        else:
            raise Exception('DataAnalyser window type ' + self.windowType + ' not implemented')

    def get2DData(self) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: get2DData: no data loaded")
        return (self.df[self.altIndexCol].values,
                self.df[self.currentView[0].values],
                self.df[self.currentView[1].values]
                )

    def getAxes(self) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: no data loaded")
        xColName = self.currentView[0]
        yColName = self.currentView[1]
        axMain = data.plot(x=xColName,y=yColName)
        axTwo = None
        axThree = None
        if isinstance(self.currentView, list) :
            axTwo = data[labelTwo].plot(x=self.altIndexCol, y=labelTwo)
            if len(self.currentView) > 1 :
                axThree = data[labelThree].plot(x=self.altIndexCol, y=labelThree)
        return (axMain, axTwo, axThree)

    def chop(self) :
        if not self.isLoaded :
            raise DataNotLoaded("ERROR: DataAnalyser: no data loaded")
        view = self.currentView
        xLabel = view[0]
        hdfKey = self.config[ 'hdfKey' ]
        xMin, xMax = (self.windowStart, self.windowStart + self.windowSize)
        prefix = self.config['chopFilenamePrefix']
        filename = "{0}_{1}:{2:d}:{3:d}.{4}".format(prefix,xLabel,xMin,xMax,"hdf5")
        print("DEBUG: DataAnalyser: chop: writing to file:",filename)
        self.df.to_hdf( filename, mode='w', key=hdfKey, data_columns = view )

class DataNotLoaded(Exception) :
    def __init__(self,*args,**kwargs) :
        Exception.__init__(self,*args,**kwargs)
