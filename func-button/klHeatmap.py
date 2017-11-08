# coding: utf-8
"""
插入所有需要的库，和函数
"""
import numpy as np
from ctaFunction.calcFunction import *
from ctaFunction.visFunction import *

#----------------------------------------------------------------------
def klHeatmap(self):
    start    = self.getInputParamByName('wLimit')
    step     = self.getInputParamByName('cLimit')
    sLippage = self.getInputParamByName('sLippage')
    size     = self.getInputParamByName('size')
    tickers  = pd.DataFrame()
    tickers['bidPrice1'] = self.pdBars['open']-sLippage
    tickers['askPrice1'] = self.pdBars['open']+sLippage
    markets  = tickers.values
    signals  = np.array(self.signalsOpen)
    plotSigHeats(signals,markets,start=start,step=step,size=size,iters=6)
    plt.show()
