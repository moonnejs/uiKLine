# coding: utf-8
"""
插入所有需要的库，和函数
"""

#----------------------------------------------------------------------
def klSigmode(self):
    """查找模式"""   
    if self.mode == 'deal':
        self.canvas.updateSig(self.signalsOpen)
        self.mode = 'dealOpen'
    else:
        self.canvas.updateSig(self.signals)
        self.mode = 'deal'

