# coding: utf-8
"""
插入所有需要的库，和函数
"""
#----------------------------------------------------------------------
def klClearSig(self):
    kTool = self.canvas
    for sig in kTool.sigPlots:
        kTool.pwKL.removeItem(kTool.sigPlots[sig])
    kTool.sigData  = {}
    kTool.sigPlots = {}
    for sig in kTool.subSigPlots:
        kTool.pwOI.removeItem(kTool.subSigPlots[sig])
    kTool.subSigData  = {}
    kTool.subSigPlots = {}
