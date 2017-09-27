# encoding: UTF-8
import sys,os
import pyqtgraph as pg
import datetime as dt          
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point

########################################################################
# 十字光标支持
########################################################################
class Crosshair(object):
    """
    此类给pg.PlotWidget()添加crossHair功能,PlotWidget实例需要初始化时传入
    """
    #----------------------------------------------------------------------
    def __init__(self,parent,master):
        """Constructor"""
        self.__view = parent
        self.master = master
        super(Crosshair, self).__init__()

        self.xAxis = 0

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
        self.__textDate = pg.TextItem('date')
        self.__textInfo = pg.TextItem('lastBarInfo')   
        self.__textVolume = pg.TextItem('lastBarVolume',anchor=(1,0))   

        self.__textDate.setZValue(2)
        self.__textInfo.setZValue(2)
        self.__textVolume.setZValue(2)
        
        for i in range(3):
            self.textPrices[i].setZValue(2)
            self.vLines[i].setPos(0)
            self.hLines[i].setPos(0)
            self.views[i].addItem(self.vLines[i])
            self.views[i].addItem(self.hLines[i])
            self.views[i].addItem(self.textPrices[i])
        
        self.views[2].addItem(self.__textDate, ignoreBounds=True)
        self.views[0].addItem(self.__textInfo, ignoreBounds=True)     
        self.views[1].addItem(self.__textVolume, ignoreBounds=True)     
        self.proxy = pg.SignalProxy(self.__view.scene().sigMouseMoved, rateLimit=60, slot=self.__mouseMoved)        
        
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
    def textPriceSetY(self,yAxis):
        """价格位置设置"""
        for i in range(3):
            if self.showHLine[i]:
                rightAxis = self.views[i].getAxis('right')
                rightAxisWidth = rightAxis.width()
                topRight = self.views[i].vb.mapSceneToView(QtCore.QPointF(self.rects[i].right()-rightAxisWidth,self.rects[i].top()))
                self.textPrices[i].setHtml(
                         '<div style="text-align: right">\
                             <span style="color: yellow; font-size: 24px;">\
                               %0.3f\
                             </span>\
                         </div>'\
                        % (yAxis if i==0 else self.yAxises[i]))   
                self.textPrices[i].setPos(topRight.x(),yAxis if i==0 else self.yAxises[i])
            else:
                topRight = self.views[i].vb.mapSceneToView(QtCore.QPointF(self.rects[i].right(),self.rects[i].top()))
                self.textPrices[i].setPos(topRight.x(),topRight.y()+abs(topRight.y()))


    #----------------------------------------------------------------------
    def moveTo(self,xAxis,yAxis):
        self.rects  = [self.views[i].sceneBoundingRect() for i in range(3)]
        if not xAxis or not yAxis:
            return
        self.xAxis = xAxis
        self.vhLinesSetXY(xAxis,yAxis)
        self.textPriceSetY(yAxis)
        self.tickDatetimeSetX(xAxis) 
        
    #----------------------------------------------------------------------
    def tickDatetimeSetX(self,xAxis):
        """
        默认计算方式，用datetimeNum标记x轴
        根据某个view中鼠标所在位置的x坐标获取其所在tick的time，xAxis可以是index，也可是一datetime转换而得到的datetimeNum
        return:str
        """        
        yAxis = 0
        tickDatetime = xAxis
        yAxis = self.datas.iloc[int(xAxis)]['close'] if not self.datas is None else 0

        if self.master.axisTime:
            axisTime = self.master.axisTime
            self.plotInfo(xAxis)        
    
    #----------------------------------------------------------------------
    def plotInfo(self,xAxis):        
        """
        被嵌入的plotWidget在需要的时候通过调用此方法显示lastprice和lasttime
        比如，在每个tick到来的时候
        """
        tickDatetime    = self.datas.iloc[int(xAxis)].name
        volume          = self.datas.iloc[int(xAxis)]['volume']
        openInterest    = self.datas.iloc[int(xAxis)]['openInterest']
        openPrice       = self.datas.iloc[int(xAxis)]['open']
        closePrice      = self.datas.iloc[int(xAxis)]['close']
        highPrice       = self.datas.iloc[int(xAxis)]['high']
        lowPrice        = self.datas.iloc[int(xAxis)]['low']
        preClosePrice   = self.datas.iloc[int(xAxis)-1]['close']
        
        if(isinstance(tickDatetime,dt.datetime)):
            datetimeText = dt.datetime.strftime(tickDatetime,'%Y-%m-%d %H:%M:%S')
            dateText     = dt.datetime.strftime(tickDatetime,'%Y-%m-%d')
            timeText     = dt.datetime.strftime(tickDatetime,'%H:%M:%S')
        else:
            datetimeText = "not set."
            dateText     = "not set."
            timeText     = "not set."

        openText  = "%.3f" % openPrice
        closeText = "%.3f" % closePrice
        highText  = "%.3f" % highPrice
        lowText   = "%.3f" % lowPrice
        cOpen     = 'red' if openPrice  > preClosePrice else 'green'
        cClose    = 'red' if closePrice > preClosePrice else 'green'
        cHigh     = 'red' if highPrice  > preClosePrice else 'green'
        cLow      = 'red' if lowPrice   > preClosePrice else 'green'
            
        self.__textInfo.setHtml(
                            u'<div style="text-align: center; background-color:#000; border:2px solid #FFFFFF;">\
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
                                <span style="color: yellow; font-size: 16px;">%f</span><br>\
                                <span style="color: white;  font-size: 16px;">仓差</span><br>\
                                <span style="color: yellow; font-size: 16px;">%f</span><br>\
                            </div>'\
                                % (dateText,timeText,cOpen,openText,cHigh,highText,cLow,lowText,cClose,closeText,volume,openInterest))             
        self.__textDate.setHtml(
                            '<div style="text-align: center">\
                                <span style="color: yellow; font-size: 24px;">%s</span>\
                            </div>'\
                                % (datetimeText))   

        self.__textVolume.setHtml(
                            '<div style="text-align: right">\
                                <span style="color: white; font-size: 20px;">VOL : %.3f</span>\
                            </div>'\
                                % (volume))   

        leftAxis = self.views[0].getAxis('left')
        leftAxisWidth = leftAxis.width()
        topLeft = self.views[0].vb.mapSceneToView(QtCore.QPointF(self.rects[0].left()+leftAxisWidth,self.rects[0].top()))
        x = topLeft.x()
        y = topLeft.y()
        self.__textInfo.setPos(x,y)           

        rightAxis = self.views[1].getAxis('right')
        rightAxisWidth = rightAxis.width()
        topRight = self.views[1].vb.mapSceneToView(QtCore.QPointF(self.rects[1].right()-rightAxisWidth,self.rects[1].top()))
        x = topRight.x()
        y = topRight.y()
        self.__textVolume.setPos(x,y)           

        rectTextDate = self.__textDate.boundingRect()         
        rectTextDateHeight = rectTextDate.height()
        bottomAxis = self.views[2].getAxis('bottom')            
        bottomAxisHeight = bottomAxis.height()
        bottomRight = self.views[2].vb.mapSceneToView(QtCore.QPointF(self.rects[2].width(),\
                self.rects[2].bottom()-(bottomAxisHeight+rectTextDateHeight)))
        if xAxis > self.master.index:
            self.__textDate.anchor = Point((1,0))
        else:
            self.__textDate.anchor = Point((0,0))
        self.__textDate.setPos(xAxis,bottomRight.y())

