#!/usr/bin/python3
'''
Data Analyser Helper

'''

import pandas as pd
import numpy as np

filetypes = {
        'csv': pd.DataFrame.from_csv ,
        }


class DataAnalyser(object):
    '''
    Helper object for reading some common data types and exploring them.
    '''

    def __init__(self, initObj=None, *args, **kwargs):
        if initObj :
            ''' Try to initialize the data object with the first passed argument '''
            self.df = pd.DataFrame(initObj)
        else :
            ''' Otherwise, just create a bogus one'''
            self.df = pd.DataFrame( [[1,2],[2,4],[3,6]] )
        self.currentView = [0,1]
        self.windowStart = 0
        self.windowSize = 100
        self.windowType = 'index'
        self.altIndexCol = 0

    def load_csv(self, *args, **kwargs):
        data = pd.DataFrame.from_csv(args, kwargs)
        data = data.dropna()
        self.currentView = [0]
        if len(data.columns) > 2 :
            self.currentView = [0,1]
        self.df = data

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

    def getColumnList(self) :
        return self.getLabels()

    def getLabels(self):
        return self.df.columns

    def setAltIndexColumn(self, value):
        if value not in self.df.columns :
            raise Exception('Invalid Column Name')
        self.altIndexCol = value

    def setView(self, view=[0,1], windowStart = 0, windowSize=100, windowType='index') :
        self.currentView = view
        self.windowStart = windowStart
        self.windowSize = windowSize
        self.windowType = windowType
    
    def getViewData(self) :
        if self.windowType == 'index' :
            start = self.windowStart
            end = self.windowStart + self.windowSize
            mySlice = slice(start,end)
            df = self.df[ [self.currentView[0], self.currentView[1]] ]
            return df[mySlice]
        else:
            raise Exception('DataAnalyser window type ' + self.windowType + ' not implemented')

    def get2DData(self) :
        return (self.df[self.altIndexCol].values,
                self.df[self.currentView[0].values],
                self.df[self.currentView[1].values]
                )

    def getAxes(self) :
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
