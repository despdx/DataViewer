#!/usr/bin/python3
'''
Data Analyser Helper

'''
#(done?)TODO cross-platform files
#TODO remove configuration
#TODO scaling (unit conversion)
#TODO interpret data types, allow filtering
#TODO linear fit, view
#TODO polymorphic load
#TODO multi-key HDF5 instead of many files
#TODO quadratic fit, view
#TODO Summary statistics
#TODO ML fits

import pandas as pd
import numpy as np
import os
from sys import stderr
import pathlib
from logging import *
basicConfig(level=ERROR)
from warnings import warn as warnwarn
import configer

def _loadCSV(filename, *args, **kwargs) :
    return pd.DataFrame.from_csv(filename, *args, **kwargs)

def _loadHDF(filename, *args, **kwargs) :
    warnwarn('HDF loading not yet implemented.')
    #store = HDFStore(filename)
    #store[self.config['hdfKey']]

def _loadRAND(*args, **kwargs) :
    x = np.arange(100)
    y = np.random.rand(100)
    return pd.DataFrame( {'x':x, 'y':y} )

def _writeCSV(pandasDF, filename, *args, **kwargs) :
    pandasDF.to_csv(filename, *args, **kwargs)

def _writeHDF(pandasDF, filename, *args, **kwargs) :
    pandasDF.to_hdf(filename, *args, **kwargs)

class DataAnalyser(object):
    '''
    Helper object for reading some common data types and exploring them.
    '''

    __readTypes = {
            'csv'       : _loadCSV
            ,'hdf5'     : _loadHDF
            ,'hdf'      : _loadHDF
            ,'rand'     : _loadRAND
            }

    __writeTypes = {
            'csv'   : _writeCSV
            ,'hdf'  : _writeHDF
            ,'hdf5' : _writeHDF
            }

    configDef = { # Configuration Definition
            'chopDirectory'         : {
                'default'   : pathlib.PurePath(os.path.curdir)
                ,'func'     : lambda p: isinstance(p,pathlib.PurePath)
                }
            ,'chopFilenamePrefix'   : {
                'default'   : 'chop'
                ,'func'     : lambda p: isinstance(p,str) and (len(p) >= 1 and len(p) <= 256)
                }
            ,'hdfKey'       : {
                'default'   : 'chop'
                ,'func'     : lambda p: isinstance(p,str) and (len(p) >= 1 and len(p) <= 64)
                }
            ,'chopFileFormat'   : {
                'default'   : 'csv'
                ,'func'     : lambda p: isinstance(p,str) and (p in DataAnalyser.getSupprtedFormats())
                }
            }

    def getDefaultConfig(self) :
        defaultDict = dict()
        for key in self.configDef :
            defaultDict[key] = self.configDef[key]['default']
        debug("DataAnalyser: getDefaultConfig: "+str(defaultDict))
        return defaultDict

    @staticmethod
    def getSupprtedFormats() :
        """ Get a list of supported file extensions that DataAnalyser can read
        and write.
        """
        return DataAnalyser.__readTypes.keys()

    def __init__(self, initObj=None, *args, **kwargs):
        self.isLoaded = False
        self.__config = configer.Configer(DataAnalyser.configDef)
        if initObj :
            ''' Initialize the data object with the first passed argument '''
            self.df = pd.DataFrame(initObj)
            self.isLoaded = True
            self.__setDefaultView()
        else :
            ''' Otherwise, empty'''
            pass
        if kwargs is not None :
            for key,val in kwargs.items() :
                self.__config[key] = val

    def __setDefaultView(self):
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: __setDefaultView: no data loaded")
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

    def getConfig(self) :
        return self.__config.getConfig()

    def load(self, *args, filetype='csv', filename=None, **kwargs):
        ''' Determine which file to load '''
        if filename == None :
            raise Exception('No filename provided.')
        else :
            self.filename = filename

        ''' Load the file '''
        loadFunc = DataAnalyser.__readTypes[filetype]
        self.df = loadFunc(filename, *args, **kwargs)
        self.isLoaded = True
        self.cleanData()
        self.__setDefaultView()

    def cleanData(self) :
        #data.dropna(inplace=True)
        #data.reset_index(drop=True)
        info("Not yet implemented.")

    def getColumnList(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: getColumnList: no data loaded")
        return self.getLabels()

    def getLabels(self):
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: getLabels: no data loaded")
        return self.df.columns

    def isValidColumn(self, name):
        return name in self.df.columns

    def isIndexable(self, name):
        """ Determine whether or not the given column can be used as an index. """
        retVal = False
        if isValidColumn(name):
            series = self.df[name]
            """ is it numeric ? """
            try :
                series.min()
            except Exception as e:
                warnwarn('Column is not usable as an index:'+str(name))
            """ Are all values unique? """
            if series.duplicated().any():
                """ Are the values ordered? """
                #TODO sort it?
                retVal = True
        return retVal

    def setAltIndexColumn(self, value):
        debug('setAltIndexColumn: got new index name:'+str(value))
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: setAltIndexColumn: no data loaded")
        """ Check for special option, index """
        if value is 'index' :
            self.altIndexCol = 'index'
            return
        """ Otherwise, check value. """
        if not self.isValidColumn(value):
            raise Exception('Invalid column name:'+str(value))

        self.altIndexCol = value

    def setView(self, view=None, windowStart = None, windowSize=None, windowType=None) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: no data loaded")
        goodLabels = self.getLabels()
        if view is not None :
            for item in view :
                if item not in goodLabels :
                    raise TypeError("ERROR: '"+str(item)+"' not a valid label")
            self.currentView = view
        if windowStart is not None :
            self.windowStart = windowStart
        if windowSize is not None :
            self.windowSize = windowSize
        if windowType is not None :
            if not windowType == 'index' :
                warnwarn("Cannot set index type: " +str(windowType))
                warnwarn("The only supported index type is: index.")
            #self.windowType = windowType

    def getIndexLimits(self) :
        #TODO use alternative index
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: no data loaded")
        return {    'max' : self.df.index.max(),
                    'min' : self.df.index.min() }

    def getView(self) :
        return self.currentView

    def getViewLimits(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: getWindowLimits: no data loaded")
        x,y = self.view
        return {    'xmin' : self.df[x].min(),
                    'ymin' : self.df[y].min(),
                    'xmax' : self.df[x].max(),
                    'ymax' : self.df[y].max() }

    def setWindow(self, start, size) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: setWindow: no data loaded")
        self.windowStart = start
        self.windowSize = size

    def getWindow(self) :
        return (self.windowStart, self.windowSize)

    def getWindow(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: getView: no data loaded")
        return ( self.windowStart , self.windowSize )
    
    def getViewData(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: getViewData: no data loaded")
        if self.windowType == 'index' :
            start = self.windowStart
            end = self.windowStart + self.windowSize
            mySlice = slice(start,end)
            df = self.df[mySlice]
            #debug("currentView:"+ str(self.currentView))
            df = df[ self.currentView ]
            return df
        else:
            raise Exception('DataAnalyser window type ' + self.windowType + ' not implemented')

    def get2DData(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: get2DData: no data loaded")
        return (self.df[self.altIndexCol].values,
                self.df[self.currentView[0].values],
                self.df[self.currentView[1].values]
                )

    def getAxes(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: no data loaded")
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

    def chop(self, dirpath=pathlib.PurePath(os.path.curdir), fmt='csv'
            ,hdfKey='chop', prefix='chop', **kwargs) :
        if not self.isLoaded :
            raise _DataNotLoaded("Data not loaded.")
        xMin, xMax = (self.windowStart, self.windowStart + self.windowSize)
        filename = "{0}_{1:d}:{2:d}.{3}".format(prefix,xMin,xMax,fmt)
        chopFilePath = os.path.join( dirpath , filename )
        if fmt not in self.__writeTypes.keys() :
            raise TypeError('Unsupported data format: '+str(fmt))
        writeFunc = self.__writeTypes[fmt]
        debug("DataAnalyser: chop: writing to file:"+chopFilePath)
        df = self.df
        altIndex = self.altIndexCol
        try :
            if altIndex == 'index' :
                writeFunc(df[xMin:xMax+1], chopFilePath, **kwargs)
            else :
                writeFunc( df[ (df[altIndex] >= xMin)and(df[altIndex] <= xMax) ]
                        ,chopFilePath, **kwargs)
        except Exception as e :
            error("ERROR: DataAnalyser: chop: failed writing to file:"+chopFilePath)
            print(e)

class _DataNotLoaded(Exception) :
    """ Specialized error class for DataAnalyser

    This error is only raised when DA is asked to perform a function that requires
    an active data set but one has not yet been loaded.
    """
    def __init__(self,*args,**kwargs) :
        Exception.__init__(self,*args,**kwargs)
