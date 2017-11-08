# encoding: UTF-8

import numba as nb
import numpy as np

@nb.autojit
#------------------------------------------------
def get_capital_np(markets,signals,size,commiRate,climit = 4, wlimit = 2, op=True):
    """使用numpy回测，标签的盈亏, op 表示是否延迟一个tick以后撮合"""
    postions    = np.zeros(len(signals))
    actions     = np.zeros(len(signals))
    costs       = np.zeros(len(signals))
    pnls        = np.zeros(len(signals))
    lastsignal  = 0
    lastpos     = 0
    lastcost    = 0
    num         = 0
    for num in range(1,len(signals)):
        postions[num]   = lastpos
        actions[num]    = 0
        costs[num]      = lastcost
        pnls[num]       = 0
        # 止盈止损
        if lastpos > 0 and \
            (markets[num,1]<=lastcost-climit or markets[num,1]>=lastcost+wlimit):
            postions[num]   = 0
            actions[num]    = -1
            costs[num]      = 0
            fee             = (markets[num,1]+lastcost)*size*commiRate
            pnls[num]       = (markets[num,1]-lastcost)*size-fee
        elif lastpos < 0 and \
            (markets[num,0]>=lastcost+climit or markets[num,0]<=lastcost-wlimit):
            postions[num]   = 0
            actions[num]    = 1
            costs[num]      = 0
            fee             = (markets[num,0]+lastcost)*size*commiRate
            pnls[num]       = (lastcost-markets[num,0])*size-fee 
        # 开仓
        if op:
            lastsignal      = signals[num]
        if lastsignal > 0 and lastpos == 0:
            postions[num]   = 1
            actions[num]    = 1
            costs[num]      = markets[num,0]
        elif lastsignal < 0 and lastpos == 0:
            postions[num]   = -1
            actions[num]    = -1
            costs[num]      = markets[num,1]
        lastpos     = postions[num]
        lastcost    = costs[num]
        lastsignal  = signals[num]
    return pnls,actions

