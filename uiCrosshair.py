# encoding: UTF-8
import sys,os
import PyQt4
import pyqtgraph as pg
import datetime as dt          
import numpy as np
import traceback

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point

########################################################################
# 十字光标支持
########################################################################
class Crosshair(PyQt4.QtCore.QObject):
    """
    此类给pg.PlotWidget()添加crossHair功能,PlotWidget实例需要初始化时传入
    """
    signal = QtCore.pyqtSignal(type(tuple([])))
    #----------------------------------------------------------------------
    def __init__(self,parent,master):
        """Constructor"""
        self.__view = parent
        self.master = master
        super(Crosshair, self).__init__()

        self.xAxis = 0
        self.yAxis = 0

        self.datas = None

        self.yAxises    = [0 for i in range(3)]
        self.leftX      = [0 for i in range(3)]
        self.showHLine  = [False for i in range(3)]
        self.textPrices = [pg.TextItem('',anchor=(1,1)) for i in range(3)]
        self.views      = [parent.centralWidget.getItem(i+1,0) for i in range(3)]
        self.rects      = [self.views[i].sceneBoundingRect() for i in range(3)]
        self.vLines     = [pg.InfiniteLine(angle=90, movable=False) for i in range(3)]
        self.hLines     = [pg.InfiniteLine(angle=0,  movable=False) for i in range(3)]
        
        #mid 在y轴动态跟随最新价显示最新价和最新时间
        self.__textDate   = pg.TextItem('date')
        self.__textInfo   = pg.TextItem('lastBarInfo')   
        self.__textSig    = pg.TextItem('lastSigInfo',anchor=(1,0))   
        self.__textVolume = pg.TextItem('lastBarVolume',anchor=(1,0))   

        self.__textDate.setZValue(2)
        self.__textInfo.setZValue(2)
        self.__textSig.setZValue(2)
        self.__textVolume.setZValue(2)
        self.__textInfo.border = pg.mkPen(color=(230, 255, 0, 255), width=1.2)
        
        for i in range(3):
            self.textPrices[i].setZValue(2)
            self.vLines[i].setPos(0)
            self.hLines[i].setPos(0)
            self.views[i].addItem(self.vLines[i])
            self.views[i].addItem(self.hLines[i])
            self.views[i].addItem(self.textPrices[i])
        
        self.views[0].addItem(self.__textInfo, ignoreBounds=True)     
        self.views[0].addItem(self.__textSig, ignoreBounds=True)     
        self.views[1].addItem(self.__textVolume, ignoreBounds=True)     
        self.views[2].addItem(self.__textDate, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.__view.scene().sigMouseMoved, rateLimit=60, slot=self.__mouseMoved)        
        # 跨线程刷新界面支持
        self.signal.connect(self.update)

    #----------------------------------------------------------------------
    def update(self,pos):
        """刷新界面显示"""
        xAxis,yAxis = pos
        xAxis,yAxis = (self.xAxis,self.yAxis) if xAxis is None else (xAxis,yAxis)
        self.moveTo(xAxis,yAxis)
        
    #----------------------------------------------------------------------
    def __mouseMoved(self,evt):
        """鼠标移动回调"""
        pos = evt[0]  
        self.rects = [self.views[i].sceneBoundingRect() for i in range(3)]
        for i in range(3):
            self.showHLine[i] = False
            if self.rects[i].contains(pos):
                mousePoint = self.views[i].vb.mapSceneToView(pos)
                xAxis = mousePoint.x()
                yAxis = mousePoint.y()    
                self.yAxises[i] = yAxis
                self.showHLine[i] = True
                self.moveTo(xAxis,yAxis)

    #----------------------------------------------------------------------
    def moveTo(self,xAxis,yAxis):
        xAxis,yAxis = (self.xAxis,self.yAxis) if xAxis is None else (xAxis,yAxis)
        self.rects  = [self.views[i].sceneBoundingRect() for i in range(3)]
        if not xAxis or not yAxis:
            return
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.vhLinesSetXY(xAxis,yAxis)
        self.plotPrice(yAxis)
        self.plotInfo(xAxis) 

    #----------------------------------------------------------------------
    def vhLinesSetXY(self,xAxis,yAxis):
        """水平和竖线位置设置"""
        for i in range(3):
            self.vLines[i].setPos(xAxis)
            if self.showHLine[i]:
                self.hLines[i].setPos(yAxis if i==0 else self.yAxises[i])
            else:
                topLeft = self.views[i].vb.mapSceneToView(QtCore.QPointF(self.rects[i].left(),self.rects[i].top()))
                self.hLines[i].setPos(topLeft.y()+abs(topLeft.y()))

    #----------------------------------------------------------------------
    def plotPrice(self,yAxis):
        """价格位置设置"""
        for i in range(3):
            if self.showHLine[i]:
                rightAxis = self.views[i].getAxis('right')
                rightAxisWidth = rightAxis.width()
                topRight = self.views[i].vb.mapSceneToView(QtCore.QPointF(self.rects[i].right()-rightAxisWidth,self.rects[i].top()))
                self.textPrices[i].setHtml(
                         '<div style="text-align: right">\
                             <span style="color: yellow; font-size: 20px;">\
                               %0.3f\
                             </span>\
                         </div>'\
                        % (yAxis if i==0 else self.yAxises[i]))   
                self.textPrices[i].setPos(topRight.x(),yAxis if i==0 else self.yAxises[i])
            else:
                topRight = self.views[i].vb.mapSceneToView(QtCore.QPointF(self.rects[i].right(),self.rects[i].top()))
                self.textPrices[i].setPos(topRight.x(),topRight.y()+abs(topRight.y()))


    #----------------------------------------------------------------------
    def plotInfo(self,xAxis):        
        """
        被嵌入的plotWidget在需要的时候通过调用此方法显示K线信息
        """
        if self.datas is None:
            return
        try:
            # 获取K线数据
            tickDatetime    = self.datas[int(xAxis)]['datetime']
            openPrice       = self.datas[int(xAxis)]['open']
            closePrice      = self.datas[int(xAxis)]['close']
            lowPrice        = self.datas[int(xAxis)]['low']
            highPrice       = self.datas[int(xAxis)]['high']
            volume          = self.datas[int(xAxis)]['volume']
            openInterest    = self.datas[int(xAxis)]['openInterest']
            preClosePrice   = self.datas[int(xAxis)-1]['close']
        except Exception, e:
            print(u'回测策略出错：%s' %e)
            print 'traceback.print_exc():'; traceback.print_exc()
            return
            
        if(isinstance(tickDatetime,dt.datetime)):
            datetimeText = dt.datetime.strftime(tickDatetime,'%Y-%m-%d %H:%M:%S')
            dateText     = dt.datetime.strftime(tickDatetime,'%Y-%m-%d')
            timeText     = dt.datetime.strftime(tickDatetime,'%H:%M:%S')
        else:
            datetimeText = ""
            dateText     = ""
            timeText     = ""

        # 显示所有的主图技术指标
        html = u'<div style="text-align: right">'
        for sig in self.master.sigData:
            val = self.master.sigData[sig][int(xAxis)]
            col = self.master.sigColor[sig]
            html+= u'<span style="color: %s;  font-size: 20px;">&nbsp;&nbsp;%s：%.2f</span>' %(col,sig,val)
        html+=u'</div>' 
        self.__textSig.setHtml(html)

        
        # 和上一个收盘价比较，决定K线信息的字符颜色
        openText  = "%.3f" % openPrice
        closeText = "%.3f" % closePrice
        highText  = "%.3f" % highPrice
        lowText   = "%.3f" % lowPrice
        cOpen     = 'red' if openPrice  > preClosePrice else 'green'
        cClose    = 'red' if closePrice > preClosePrice else 'green'
        cHigh     = 'red' if highPrice  > preClosePrice else 'green'
        cLow      = 'red' if lowPrice   > preClosePrice else 'green'
            
        self.__textInfo.setHtml(
                            u'<div style="text-align: center; background-color:#000">\
                                <span style="color: white;  font-size: 16px;">日期</span><br>\
                                <span style="color: yellow; font-size: 16px;">%s</span><br>\
                                <span style="color: white;  font-size: 16px;">时间</span><br>\
                                <span style="color: yellow; font-size: 16px;">%s</span><br>\
                                <span style="color: white;  font-size: 16px;">开盘</span><br>\
                                <span style="color: %s;     font-size: 16px;">%s</span><br>\
                                <span style="color: white;  font-size: 16px;">最高</span><br>\
                                <span style="color: %s;     font-size: 16px;">%s</span><br>\
                                <span style="color: white;  font-size: 16px;">最低</span><br>\
                                <span style="color: %s;     font-size: 16px;">%s</span><br>\
                                <span style="color: white;  font-size: 16px;">收盘</span><br>\
                                <span style="color: %s;     font-size: 16px;">%s</span><br>\
                                <span style="color: white;  font-size: 16px;">成交量</span><br>\
                                <span style="color: yellow; font-size: 16px;">%.3f</span><br>\
                            </div>'\
                                % (dateText,timeText,cOpen,openText,cHigh,highText,\
                                    cLow,lowText,cClose,closeText,volume))             
        self.__textDate.setHtml(
                            '<div style="text-align: center">\
                                <span style="color: yellow; font-size: 20px;">%s</span>\
                            </div>'\
                                % (datetimeText))   

        self.__textVolume.setHtml(
                            '<div style="text-align: right">\
                                <span style="color: white; font-size: 20px;">VOL : %.3f</span>\
                            </div>'\
                                % (volume))   
        
        # K线子图，左上角显示
        leftAxis = self.views[0].getAxis('left')
        leftAxisWidth = leftAxis.width()
        topLeft = self.views[0].vb.mapSceneToView(QtCore.QPointF(self.rects[0].left()+leftAxisWidth,self.rects[0].top()))
        x = topLeft.x()
        y = topLeft.y()
        self.__textInfo.setPos(x,y)           

        # K线子图，右上角显示
        rightAxis = self.views[0].getAxis('right')
        rightAxisWidth = rightAxis.width()
        topRight = self.views[0].vb.mapSceneToView(QtCore.QPointF(self.rects[0].right()-rightAxisWidth,self.rects[0].top()))
        x = topRight.x()
        y = topRight.y()
        self.__textSig.setPos(x,y)           
        
        # 成交量子图，右上角显示
        rightAxis = self.views[1].getAxis('right')
        rightAxisWidth = rightAxis.width()
        topRight = self.views[1].vb.mapSceneToView(QtCore.QPointF(self.rects[1].right()-rightAxisWidth,self.rects[1].top()))
        x = topRight.x()
        y = topRight.y()
        self.__textVolume.setPos(x,y)           

        # X坐标时间显示
        rectTextDate = self.__textDate.boundingRect()         
        rectTextDateHeight = rectTextDate.height()
        bottomAxis = self.views[2].getAxis('bottom')            
        bottomAxisHeight = bottomAxis.height()
        bottomRight = self.views[2].vb.mapSceneToView(QtCore.QPointF(self.rects[2].width(),\
                self.rects[2].bottom()-(bottomAxisHeight+rectTextDateHeight)))
        # 修改对称方式防止遮挡
        if xAxis > self.master.index:
            self.__textDate.anchor = Point((1,0))
        else:
            self.__textDate.anchor = Point((0,0))
        self.__textDate.setPos(xAxis,bottomRight.y())

