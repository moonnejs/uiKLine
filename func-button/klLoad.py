# coding: utf-8
"""
插入所有需要的库，和函数
"""
import pandas as pd

#----------------------------------------------------------------------
def klLoad(self,bars=None):
    """载入合约数据"""   
    bars = pd.DataFrame.from_csv('datasig.csv')
    kTool = self.canvas
    for sig in kTool.sigPlots:
        kTool.pwKL.removeItem(kTool.sigPlots[sig])
    kTool.sigData  = {}
    kTool.sigPlots = {}
    for sig in kTool.subSigPlots:
        kTool.pwOI.removeItem(kTool.subSigPlots[sig])
    kTool.subSigData  = {}
    kTool.subSigPlots = {}
    self.loadData(bars)

