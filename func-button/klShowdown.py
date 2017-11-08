# coding: utf-8
"""
插入所有需要的库，和函数
"""
import pandas as pd
import numpy as np

#----------------------------------------------------------------------
def klShowdown(self):
    """信号曲线"""   
    sigName = self.getInputParamByName('signalName')
    self.canvas.listOpenInterest = self.stateData[sigName]
    self.canvas.datas['openInterest'] = np.array(self.stateData[sigName])
    self.canvas.plotOI(0,len(self.stateData[sigName]))
    self.canvas.showSig({sigName:self.stateData[sigName]},False)
