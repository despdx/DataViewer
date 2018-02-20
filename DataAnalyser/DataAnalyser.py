#!/usr/bin/python3
'''
Data Analyser Helper

'''

import pandas as pd
import numpy as np

filetypes = {
        'csv': pd.DataFrame.from_csv ,
        }

class DataAnalyser:
    '''
    Helper object for reading some common data types and exploring them.
    '''

    data = None
    currentView = None
    windowStart = 0
    windowSize = 100
    windowType = 'index'
    altIndexCol = 0

    def __init__(self):
        self.data = None
        self.currentView = [0,1]

    def load_csv(self, *args, **kwargs):
        data = pd.DataFrame.from_csv(args, kwargs)
        data = data.dropna()
        self.currentView = [0]
        if len(data.columns) > 2 :
            self.currentView = [0,1]
        self.data = data

##    def load(self, filetype='csv', filename=None, *args, **kwargs)##:
##        self.data = None
##        ''' Determine which file to load '''
##        if filename == None :
##            if self.filename == None :
##                raise Exception('No Filename Given')
##        else :
##            self.filename = filename
##
##        ''' Load the file with Pandas '''
##        loadFunc = filetypes[filetype]
##        self.data = loadFunc(path=filename, args, kwargs)

    def getColumnList(self) :
        return self.getLabels()

    def getLabels(self):
        return self.data.columns

    def setAltIndexColumn(self, value):
        if value not in self.data.columns :
            raise Exception('Invalid Column Name')
        self.altIndexCol = value

    def setView(self, columnList=[0,1], windowStart = 0, windowSize=100, windowType='index') :
        self.columnList = columnList
        self.windowStart = windowStart
        self.windowSize = windowSize
        self.windowType = windowType
    
    def getViewData(self) :
        start = self.windowStart
        end = self.windowStart + self.windowSize
        df = self.data[ (self.columnList[0], self.columnList[1]) ]
        if self.windowType = 'index' :
            selector = [df[0] > start and df[0] < end ]
            return df[selector]
        else:
            raise Exception('DataAnalyser window type ' + self.windowType + ' not implemented')

    def get2DData(self) :
        return (self.data[self.altIndexCol].values,
                self.data[self.columnList[0].values],
                self.data[self.columnList[1].values]
                )

    def getAxes(self) :
        xColName = self.columnList[0]
        yColName = self.columnList[1]
        axMain = data.plot(x=xColName,y=yColName)
        axTwo = None
        axThree = None
        if isinstance(self.currentView, list) :
            axTwo = data[labelTwo].plot(x=self.altIndexCol, y=labelTwo)
            if len(self.currentView) > 1 :
                axThree = data[labelThree].plot(x=self.altIndexCol, y=labelThree)
        return (axMain, axTwo, axThree)
