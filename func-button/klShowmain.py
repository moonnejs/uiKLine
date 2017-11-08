# coding: utf-8
"""
插入所有需要的库，和函数
"""
import pandas as pd

#----------------------------------------------------------------------
def klShowmain(self):
    """信号分析报告"""   
    sigName = self.getInputParamByName('signalName')
    self.canvas.showSig({sigName:self.stateData[sigName]},True)

