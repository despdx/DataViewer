#!/usr/bin/python3
'''
Data Analyser Helper

'''
#TODO translation
#TODO linear fit, view
#TODO NavigationToolbar2TkAgg depricated
#TODO scaling (unit conversion)
#TODO interpret data types, allow filtering
#TODO Fix doc strings
#TODO WIP: polymorphic load
#TODO multi-key HDF5 instead of many files
#TODO quadratic fit, view
#TODO WIP remove configuration
#TODO ML fits
#TODO GUI summary statistics
#TODO allow index to beselected in main view
#TODO Index Views

import pandas as pd
import numpy as np
import os
from sys import stderr
import pathlib
from logging import *
basicConfig(level=ERROR)
from warnings import warn as warnwarn
import configer
from numbers import Number

def _loadCSV(filename, *args, **kwargs) :
    return pd.read_csv(filename, *args, **kwargs)

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

def fixedTranslation(dfList, **kwargs) :
    """Fixed translation function."""
    newDFlist = list()
    xshift = kwargs['xTrans']
    yshift = kwargs['yTrans']
    for df in dfList :
        newSeriesList = list()
        labelVsTrans = zip(df.columns.unique().tolist(),[xshift,yshift])
        for label,trans in zip(df.columns.unique().tolist(),[xshift,yshift]) :
            #debug("Fixed Translation: label:{}, trans:{}".format(label,trans))
            newSeries = df[label] + trans
            #debug("Fixed Translation: new series: %s", newSeries.head())
            newSeriesList.append(newSeries)
        newDF = pd.concat( newSeriesList, axis=1 ) 
        #debug("Fixed Translation: new DF: %s",newDF.head() )
        newDFlist.append(newDF)
    return newDFlist

def fitLinear(pandasDF, **kwargs) :
    pass

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
            ,'indexSpecialName' : {
                'default'   : 'Internal Index'
                ,'func'     : lambda s: isinstance(s,str) and (len(s) >= 1 and len(s) <= 32)
                }
            }

    """Transformation Options"""
    __transforms = {
            'fixed'         : {
                'label'         : 'Fixed Translation Transform'
                ,'xTrans'       : 0.0
                ,'yTrans'       : 0.0
                ,'Enabled'      : False
                ,'func'         : fixedTranslation
                }
            }

    """ Curve Fit Options """
    __fits = {
            'linear'        : {
                'label'         : 'Linear Curve Fit'
                ,'Enabled'      : False
                ,'func'         : fitLinear
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

    @staticmethod
    def getFitOptions() :
        return DataAnalyser.__fits

    @staticmethod
    def getTransformOptions() :
        return DataAnalyser.__transforms

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
        self.indexName = self.__config['indexSpecialName']

    def __setDefaultView(self):
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: __setDefaultView: no data loaded")
        self.windowStart = 0
        self.windowSize = self.df.shape[0]
        self.windowType = 'index'
        self.altIndexCol = 'index'

        """ Create a default view of the fist column only.  One column is
        technically okay, but, rest of implementation may assume otherwise.
        """
        """At minimum, there must be and index and one column, so we know
        that a good default is:"""
        currentView = [ [self.indexName, self.plotColumns[0] ] ]
        """If there is more than one plot-able column, choose the first two"""
        if len(self.plotColumns) > 2 :
            currentView = [self.plotColumns[0:2] ]
        """Keep forgetting the view is a list of lists!"""
        assert(isinstance(currentView[0],list))
        self.currentView = currentView

    def getConfig(self) :
        return self.__config.getConfig()

    def load(self, *args, filetype='csv', filename=None, **kwargs):
        """ Determine which file to load """
        if filename == None :
            raise Exception('No filename provided.')
        else :
            self.filename = filename

        ''' Load the file '''
        loadFunc = DataAnalyser.__readTypes[filetype]
        self.df = loadFunc(filename, *args, **kwargs)
        debug("load:Loaded new data file: head:"+str(self.df.head()))
        self.indexCol = kwargs['index_col']
        self.isLoaded = True
        self.cleanData()
        self.__setDefaultView()
        debug("load:default view:"+str(self.currentView))

    def cleanData(self) :
        #data.dropna(inplace=True)
        #data.reset_index(drop=True)
        """Pull out column names for plot-able column data"""
        #self.plotColumns = self.df.columns[ self.columnDataIsPlotable(e) for e in self.df.columns.tolist() ]
        self.plotColumns = list()
        for label in self.df.columns.tolist() :
            """For each lable, check against function, store"""
            if self.columnDataIsPlotable(label):
                self.plotColumns.append(label)
        debug("Got {} plot-able columns: {}".format(len(self.plotColumns),self.plotColumns))
        info("Not yet fully implemented.")

    def getColumnList(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: getColumnList: no data loaded")
        return self.getLabels()

    def getLabels(self):
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: getLabels: no data loaded")
        return self.plotColumns

    def columnDataIsPlotable(self, name):
        """Check data in the column named 'name' to make sure we can plot it
        Cannot plot anything but ints and floats.
        """
        return isinstance(self.df[name].iloc[0], Number)

    def isValidColumn(self, name):
        """Check if 'name' is in the DataFrame."""
        return (name in self.df.columns.tolist())

    def isIndexable(self, name):
        """ Determine whether or not the given column can be used as an index. """
        retVal = False
        if isValidColumn(name):
            series = self.df[name]
            """ Are all values unique? """
            if series.duplicated().any():
                """ Are the values ordered? """
                #TODO sort it?
                retVal = True
        return retVal

    def setAltIndexColumn(self, value):
        warn('DataAnalyser:setAltIndexColumn: Not implemented.')
        return
        debug("setAltIndexColumn: got new index name:'"+str(value)+"'")
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: setAltIndexColumn: no data loaded")
        """ Check for special option, index """
        if str(value) == str('index') :
            self.altIndexCol = 'index'
            return
        """ Otherwise, check value. """
        if not self.isValidColumn(value):
            raise Exception('Invalid column name:'+str(value))

        self.altIndexCol = value

    def validateView(self, viewList):
        """TODO Move view validation code here"""
        pass

    def setView(self, viewList=None, windowStart = None, windowSize=None, windowType=None) :
        """ Set the analyser view

        Parameters:
        viewList : list of views, each view is a tuple of x,y data columns/names
        """
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: no data loaded")
        debug("Got new view list:"+str(viewList))
        goodLabels = self.getLabels()
        if viewList is not None :
            """ Okay, this is real data """
            newViewList = list()
            if isinstance(viewList, list) or isinstance(viewList,tuple) :
                for view in viewList:
                    debug("new view:"+str(view))
                    debug("new view type:"+str(type(view)))
                    if isinstance(view, list) or isinstance(view,tuple) :
                        """ viewList must be a list of lists """
                        validView = True
                        for item in view :
                            """ Validate each name in new view """
                            if item not in goodLabels :
                                warnwarn("View contains invalid labels for this data set, ignoring")
                                validView = False
                            else :
                                debug("item okay:"+str(item))
                        """ Okay, new view is validated, set currentview if passed."""
                        if validView :
                            newViewList.append(view)
                        else :
                            error("Was passed invalid view, ignoring it:"+str(view))
                    elif view is None :
                        """View maybe none if input not sanitized.  Fine, just
                        ignore it."""
                        warnwarn("View is 'None', ignoring.")
                    else :
                        raise TypeError("view must be a list or tuple, also.")
            else :
                raise TypeError("viewList must be a list or tuple.")
            """At this point, the new views have been validated."""
            """Accept the current view list, unless it's empty!"""
            if len(newViewList) < 1 :
                """New views failed validation"""
                debug("setView: All requested views failed validation.")
                if len(self.currentView) >= 1 :
                    """Old views exist, so, just keep that"""
                    debug("setView: Keeping old views:"+str(self.currentView))
                else :
                    raise TypeError("New view did not pass validation:"+str(viewList))
            else :
                """Okay, we can accept the new views that have passed validation"""
                self.currentView = newViewList
                debug("setView: Views updated: "+str(self.currentView))
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
        viewLimitDictList = list()
        for view in self.view :
            x,y = self.view
            viewDict = {'xmin' : self.df[x].min(),
                        'ymin' : self.df[y].min(),
                        'xmax' : self.df[x].max(),
                        'ymax' : self.df[y].max() }
            viewLimitDictList.append(viewDict)
        return viewLimitDictList

    def setWindow(self, start, size) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: setWindow: no data loaded")
        self.windowStart = start
        self.windowSize = size

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
            dfList = list()
            debug("currentView:"+ str(self.currentView))
            """Make a list of DF Views to sent back to caller"""
            for viewpair in self.currentView :
                """Create DF views to return to caller"""
                df = self.df[ list(viewpair) ]      # make view
                df = df[mySlice]                    # get slice of the data requested
                dfList.append(df)
            """Now, pass all views through transforms"""
            newDFlist = self.doTransforms(dfList)
            """Now, pass all views through fitter"""
            #newDFlist = self.doFits(dfList)
            return newDFlist
        else:
            raise Exception('DataAnalyser window type ' + self.windowType + ' not implemented')

    def doTransforms(self, dfList):
        """Run all active transforms on the given DataFrame"""
        newDFlist = dfList
        #debug("doTransforms: available transforms: %s" , self.__transforms.keys())
        for transName in self.__transforms.keys():
            transConfig = self.__transforms[transName]
            if not transConfig['Enabled']:
                continue
            debug("Running transformation type: "+str(transName))
            transFunc = transConfig['func']
            newDFlist = transFunc(newDFlist, **transConfig)
            #debug("Got tranformation back: %s", newDFlist[0].head())
        return newDFlist

    def get2DData(self) :
        if not self.isLoaded :
            raise _DataNotLoaded("ERROR: DataAnalyser: get2DData: no data loaded")
        raise Exception('Not implemented yet.')

    def chop(self, dirpath=pathlib.PurePath(os.path.curdir), fmt='csv'
            ,hdfKey='chop', prefix='chop', **kwargs) :
        if not self.isLoaded :
            raise _DataNotLoaded("Data not loaded.")
        xMin, xMax = (self.windowStart, self.windowStart + self.windowSize)
        filename = "{0}_{1:d}-{2:d}.{3}".format(prefix,xMin,xMax,fmt)
        chopFilePath = os.path.join( dirpath , filename )
        if fmt not in self.__writeTypes.keys() :
            raise TypeError('Unsupported data format: '+str(fmt))
        writeFunc = self.__writeTypes[fmt]
        info("DataAnalyser: chop: writing to file:"+chopFilePath)
        df = self.df
        altIndex = self.altIndexCol
        #TODO finish alternative indexes
        try :
            if altIndex == 'index' :
                writeFunc(df[xMin:xMax+1], chopFilePath, **kwargs)
            else :
                dfView = df[ (df[altIndex] >= xMin) & (df[altIndex] <= xMax) ]
                writeFunc( dfView ,chopFilePath, **kwargs)
        except Exception as e :
            error("ERROR: DataAnalyser: chop: failed writing to file:"+chopFilePath)
            print(e)

    def getStats(self):
        dfList = self.getViewData()
        statList = list()
        for df in dfList :
            statList.append( df.describe() )
        return statList

class _DataNotLoaded(Exception) :
    """ Specialized error class for DataAnalyser

    This error is only raised when DA is asked to perform a function that requires
    an active data set but one has not yet been loaded.
    """
    def __init__(self,*args,**kwargs) :
        Exception.__init__(self,*args,**kwargs)
