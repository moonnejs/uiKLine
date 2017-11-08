# encoding: UTF-8
"""
包含一些CTA因子的可视化函数
"""
import numpy as np
import pandas as pd
import seaborn as sns
#import matplotlib as mpl
#mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei"]#
#mpl.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt 
from calcFunction import get_capital_np

#----------------------------------------------------------------------
def plotSigCaps(signals,markets,climit=4,wlimit=2,size=1,rate=0.0001,op=True):
    """
    打印某一个信号的资金曲线
    """
    plt.close()
    pnls,poss = get_capital_np(markets,signals,size,rate,\
            climit=climit, wlimit=wlimit,op=op)
    caps = np.cumsum(pnls[pnls!=0])
    return caps,poss

#----------------------------------------------------------------------
def plotSigHeats(signals,markets,start=0,step=2,size=1,iters=6):
    """
    打印信号回测盈损热度图,寻找参数稳定岛
    """
    sigMat = pd.DataFrame(index=range(iters),columns=range(iters))
    for i in range(iters):
        for j in range(iters):
            climit = start + i*step
            wlimit = start + j*step
            caps,poss = plotSigCaps(signals,markets,climit=climit,wlimit=wlimit,size=size,op=False)
            sigMat[i][j] = caps[-1]
    sns.heatmap(sigMat.values.astype(np.float64),annot=True,fmt='.2f',annot_kws={"weight": "bold"})
    xTicks   = [i+0.5 for i in range(iters)]
    yTicks   = [iters-i-0.5 for i in range(iters)]
    xyLabels = [str(start+i*step) for i in range(iters)]
    _, labels = plt.yticks(yTicks,xyLabels)
    plt.setp(labels, rotation=0)
    _, labels = plt.xticks(xTicks,xyLabels)
    plt.setp(labels, rotation=90)
    plt.xlabel('Loss Stop @')
    plt.ylabel('Profit Stop @')
    return sigMat
