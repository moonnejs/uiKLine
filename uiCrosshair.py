# encoding: UTF-8
import sys,os
import qtpy
import pyqtgraph as pg
import datetime as dt          
import numpy as np
import traceback

#from pyqtgraph.Qt import QtGui, QtCore
from qtpy import QtGui, QtCore
from pyqtgraph.Point import Point

########################################################################
# 十字光标支持
########################################################################
class Crosshair(QtCore.QObject):
    """
    此类给pg.PlotWidget()添加crossHair功能,PlotWidget实例需要初始化时传入
    """
    signal = QtCore.Signal(type(tuple([])))
    signalInfo = QtCore.Signal(float,float)
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
        self.__textDate   = pg.TextItem('date',anchor=(1,1))
        self.__textInfo   = pg.TextItem('lastBarInfo')   
        self.__textSig    = pg.TextItem('lastSigInfo',anchor=(1,0))   
        self.__textSubSig = pg.TextItem('lastSubSigInfo',anchor=(1,0))   
        self.__textVolume = pg.TextItem('lastBarVolume',anchor=(1,0))   

        self.__textDate.setZValue(2)
        self.__textInfo.setZValue(2)
        self.__textSig.setZValue(2)
        self.__textSubSig.setZValue(2)
        self.__textVolume.setZValue(2)
        self.__textInfo.border = pg.mkPen(color=(230, 255, 0, 255), width=1.2)
        
        for i in range(3):
            self.textPrices[i].setZValue(2)
            self.vLines[i].setPos(0)
            self.hLines[i].setPos(0)
            self.vLines[i].setZValue(0)
            self.hLines[i].setZValue(0)
            self.views[i].addItem(self.vLines[i])
            self.views[i].addItem(self.hLines[i])
            self.views[i].addItem(self.textPrices[i])
        
        self.views[0].addItem(self.__textInfo, ignoreBounds=True)     
        self.views[0].addItem(self.__textSig, ignoreBounds=True)     
        self.views[1].addItem(self.__textVolume, ignoreBounds=True)     
        self.views[2].addItem(self.__textDate, ignoreBounds=True)
        self.views[2].addItem(self.__textSubSig, ignoreBounds=True)     
        self.proxy = pg.SignalProxy(self.__view.scene().sigMouseMoved, rateLimit=360, slot=self.__mouseMoved)        
        # 跨线程刷新界面支持
        self.signal.connect(self.update)
        self.signalInfo.connect(self.plotInfo)

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
        xAxis,yAxis = (self.xAxis,self.yAxis) if xAxis is None else (int(xAxis),yAxis)
        self.rects  = [self.views[i].sceneBoundingRect() for i in range(3)]
        if not xAxis or not yAxis:
            return
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.vhLinesSetXY(xAxis,yAxis)
        self.plotInfo(xAxis,yAxis)
        self.master.volume.update()

    #----------------------------------------------------------------------
    def vhLinesSetXY(self,xAxis,yAxis):
        """水平和竖线位置设置"""
        for i in range(3):
            self.vLines[i].setPos(xAxis)
            if self.showHLine[i]:
                self.hLines[i].setPos(yAxis if i==0 else self.yAxises[i])
                self.hLines[i].show()
            else:
                self.hLines[i].hide()

    #----------------------------------------------------------------------
    def plotInfo(self,xAxis,yAxis):        
        """
        被嵌入的plotWidget在需要的时候通过调用此方法显示K线信息
        """
        if self.datas is None:
            return
        try:
            # 获取K线数据
            data            = self.datas[xAxis]
            lastdata        = self.datas[xAxis-1]
            tickDatetime    = data['datetime']
            openPrice       = data['open']
            closePrice      = data['close']
            lowPrice        = data['low']
            highPrice       = data['high']
            volume          = int(data['volume'])
            openInterest    = int(data['openInterest'])
            preClosePrice   = lastdata['close']
            tradePrice      = abs(self.master.listSig[xAxis])
        except Exception as e:
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
            val = self.master.sigData[sig][xAxis]
            col = self.master.sigColor[sig]
            html+= u'<span style="color: %s;  font-size: 18px;">&nbsp;&nbsp;%s：%.2f</span>' %(col,sig,val)
        html+=u'</div>' 
        self.__textSig.setHtml(html)

        # 显示所有的主图技术指标
        html = u'<div style="text-align: right">'
        for sig in self.master.subSigData:
            val = self.master.subSigData[sig][xAxis]
            col = self.master.subSigColor[sig]
            html+= u'<span style="color: %s;  font-size: 18px;">&nbsp;&nbsp;%s：%.2f</span>' %(col,sig,val)
        html+=u'</div>' 
        self.__textSubSig.setHtml(html)

        
        # 和上一个收盘价比较，决定K线信息的字符颜色
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
                                <span style="color: white;  font-size: 16px;">价格</span><br>\
                                <span style="color: %s;     font-size: 16px;">(开) %.3f</span><br>\
                                <span style="color: %s;     font-size: 16px;">(高) %.3f</span><br>\
                                <span style="color: %s;     font-size: 16px;">(低) %.3f</span><br>\
                                <span style="color: %s;     font-size: 16px;">(收) %.3f</span><br>\
                                <span style="color: white;  font-size: 16px;">成交量</span><br>\
                                <span style="color: yellow; font-size: 16px;">(量) %d</span><br>\
                                <span style="color: white;  font-size: 16px;">成交价</span><br>\
                                <span style="color: yellow; font-size: 16px;">(价) %.3f</span><br>\
                            </div>'\
                                % (dateText,timeText,cOpen,openPrice,cHigh,highPrice,\
                                    cLow,lowPrice,cClose,closePrice,volume,tradePrice))             
        self.__textDate.setHtml(
                            '<div style="text-align: center">\
                                <span style="color: yellow; font-size: 18px;">%s</span>\
                            </div>'\
                                % (datetimeText))   

        self.__textVolume.setHtml(
                            '<div style="text-align: right">\
                                <span style="color: white; font-size: 18px;">VOL : %.3f</span>\
                            </div>'\
                                % (volume))   
        # 坐标轴宽度
        rightAxisWidth = self.views[0].getAxis('right').width()
        bottomAxisHeight = self.views[2].getAxis('bottom').height()           
        offset = QtCore.QPointF(rightAxisWidth,bottomAxisHeight)

        # 各个顶点
        tl = [self.views[i].vb.mapSceneToView(self.rects[i].topLeft()) for i in range(3)]
        br = [self.views[i].vb.mapSceneToView(self.rects[i].bottomRight()-offset) for i in range(3)]

        # 显示价格
        for i in range(3):
            if self.showHLine[i]:
                self.textPrices[i].setHtml(
                        '<div style="text-align: right">\
                             <span style="color: yellow; font-size: 18px;">\
                               %0.3f\
                             </span>\
                         </div>'\
                        % (yAxis if i==0 else self.yAxises[i]))   
                self.textPrices[i].setPos(br[i].x(),yAxis if i==0 else self.yAxises[i])
                self.textPrices[i].show()
            else:
                self.textPrices[i].hide()

        
        # 设置坐标
        self.__textInfo.setPos(tl[0])           
        self.__textSig.setPos(br[0].x(),tl[0].y())           
        self.__textSubSig.setPos(br[2].x(),tl[2].y())           
        self.__textVolume.setPos(br[1].x(),tl[1].y())           

        # 修改对称方式防止遮挡
        self.__textDate.anchor = Point((1,1)) if xAxis > self.master.index else Point((0,1))
        self.__textDate.setPos(xAxis,br[2].y())
