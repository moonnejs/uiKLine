# -*- coding: utf-8 -*-


# Qt相关和十字光标
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtGui,QtCore
from uiCrosshair import Crosshair
import pyqtgraph as pg
# 其他
import numpy as np
import pandas as pd
from functools import partial
from datetime import datetime,timedelta


# 字符串转换
#---------------------------------------------------------------------------------------
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

########################################################################
# 键盘鼠标功能
########################################################################
class KeyWraper(QtGui.QWidget):
    """键盘鼠标功能支持的元类"""
    #初始化
    #----------------------------------------------------------------------
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

    #重载方法keyPressEvent(self,event),即按键按下事件方法
    #----------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.onUp()
        elif event.key() == QtCore.Qt.Key_Down:
            self.onDown()
        elif event.key() == QtCore.Qt.Key_Left:
            self.onLeft()
        elif event.key() == QtCore.Qt.Key_Right:
            self.onRight()
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.onPre()
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.onNxt()

    #重载方法mousePressEvent(self,event),即鼠标点击事件方法
    #----------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.onRClick(event.pos())
        elif event.button() == QtCore.Qt.LeftButton:
            self.onLClick(event.pos())
        event.accept()

    #重载方法mouseReleaseEvent(self,event),即鼠标点击事件方法
    #----------------------------------------------------------------------
    def mouseRelease(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.onRRelease(event.pos())
        elif event.button() == QtCore.Qt.LeftButton:
            self.onLRelease(event.pos())
        self.releaseMouse()

    #重载方法wheelEvent(self,event),即滚轮事件方法
    #----------------------------------------------------------------------
    def wheelEvent(self, event):
        if event.delta() > 0:
            self.onUp()
        else:
            self.onDown()

    #重载方法dragMoveEvent(self,event),即拖动事件方法
    #----------------------------------------------------------------------
    def paintEvent(self, event):
        self.onPaint()

    # PgDown键
    #----------------------------------------------------------------------
    def onNxt(self):
        pass

    # PgUp键
    #----------------------------------------------------------------------
    def onPre(self):
        pass

    # 向上键和滚轮向上
    #----------------------------------------------------------------------
    def onUp(self):
        pass

    # 向下键和滚轮向下
    #----------------------------------------------------------------------
    def onDown(self):
        pass
    
    # 向左键
    #----------------------------------------------------------------------
    def onLeft(self):
        pass

    # 向右键
    #----------------------------------------------------------------------
    def onRight(self):
        pass

    # 鼠标左单击
    #----------------------------------------------------------------------
    def onLClick(self,pos):
        pass

    # 鼠标右单击
    #----------------------------------------------------------------------
    def onRClick(self,pos):
        pass

    # 鼠标左释放
    #----------------------------------------------------------------------
    def onLRelease(self,pos):
        pass

    # 鼠标右释放
    #----------------------------------------------------------------------
    def onRRelease(self,pos):
        pass

    # 画图
    #----------------------------------------------------------------------
    def onPaint(self):
        pass


########################################################################
# 选择缩放功能支持
########################################################################
class CustomViewBox(pg.ViewBox):
    #----------------------------------------------------------------------
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        # 拖动放大模式
        #self.setMouseMode(self.RectMode)
        
    ## 右键自适应
    #----------------------------------------------------------------------
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            self.autoRange()

    # 鼠标拖动        
    #----------------------------------------------------------------------
    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)


########################################################################
# 时间序列，横坐标支持
########################################################################
class MyStringAxis(pg.AxisItem):
    """时间序列横坐标支持"""
    
    # 初始化 
    #----------------------------------------------------------------------
    def __init__(self, xdict, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.minVal = 0 
        self.maxVal = 0
        self.x_values = np.asarray(xdict.keys())
        self.x_strings = xdict.values()
        self.setPen(color=(255, 255, 255, 255), width=0.8)
        self.setStyle(tickFont = QFont("Roman times",10,QFont.Bold),autoExpandTextSpace=True)

    # 更新坐标映射表
    #----------------------------------------------------------------------
    def update_xdict(self, xdict):
        self.x_values = np.asarray(xdict.keys())
        self.x_strings = xdict.values()

    # 将原始横坐标转换为时间字符串,第一个坐标包含日期
    #----------------------------------------------------------------------
    def tickStrings(self, values, scale, spacing):
        strings = []
        for v in values:
            vs = v * scale
            if vs in self.x_values:
                vstr = self.x_strings[np.abs(self.x_values-vs).argmin()]
                vstr = vstr.strftime('%Y-%m-%d %H:%M:%S')
            else:
                vstr = ""
            strings.append(vstr)
        return strings

########################################################################
# K线图形对象
########################################################################
class CandlestickItem(pg.GraphicsObject):
    """K线图形对象"""

    # 初始化
    #----------------------------------------------------------------------
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data                # 数据格式: [ (time, open, close, low, high),...]
        w = 0.4
        # 画笔和画刷
        self.bPen   = pg.mkPen(color=(0, 240, 240, 255), width=w*2)
        self.bBrush = pg.mkBrush((0, 240, 240, 255))
        self.rPen   = pg.mkPen(color=(255, 60, 60, 255), width=w*2)
        self.rBrush = pg.mkBrush((255, 60, 60, 255))
        self.rBrush.setStyle(Qt.NoBrush)
        # 刷新K线
        self.generatePicture(self.data)          

    # 重画K线
    #----------------------------------------------------------------------
    def generatePicture(self,data=None):
        # 提高调用速度
        bPen   = self.bPen
        bBrush = self.bBrush
        rPen   = self.rPen
        rBrush = self.rBrush
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        w = 0.4
        for (t, open0, close0, low0, high0) in data:
            # 下跌蓝色（实心）, 上涨红色（空心）
            pen,brush,pmin,pmax = (bPen,bBrush,close0,open0)\
                if open0 > close0 else (rPen,rBrush,open0,close0)
            p.setPen(pen)  
            p.setBrush(brush)
            # 画K线方块和上下影线
            p.drawRect(QtCore.QRectF(t-w, open0, w*2, close0-open0))
            if pmin  > low0:
                p.drawLine(QtCore.QPointF(t,low0), QtCore.QPointF(t, pmin))
            if high0 > pmax:
                p.drawLine(QtCore.QPointF(t,pmax), QtCore.QPointF(t, high0))
        p.end()

    # 自动重画
    #----------------------------------------------------------------------
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    # 定义边界
    #----------------------------------------------------------------------
    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


########################################################################
class KLineWidget(KeyWraper):
    """用于显示价格走势图"""

    # 保存K线数据的列表和Numpy Array对象
    listBar  = []
    listVol  = []
    listHigh = []
    listLow  = []
    listSig  = []
    listOpenInterest = []
    arrows   = []

    # 是否完成了历史数据的读取
    initCompleted = False
    
    #----------------------------------------------------------------------
    def __init__(self,parent=None):
        """Constructor"""
        self.parent = parent
        super(KLineWidget, self).__init__(parent)

        # 当前序号
        self.index    = None    # 下标
        self.countK   = 60      # 显示的Ｋ线范围

        # 缓存数据
        self.datas    = pd.DataFrame()
        self.signals  = pd.DataFrame()
        self.listBar  = []
        self.listVol  = []
        self.listHigh = []
        self.listLow  = []
        self.listSig  = []
        self.listOpenInterest = []
        self.arrows   = []

        # 所有K线上信号图
        self.sigPlots = {}

        # 初始化完成
        self.initCompleted = False

        # 调用函数
        self.initUi()

    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(u'K线工具')
        # 主图
        self.pw = pg.PlotWidget()
        # 界面布局
        self.lay_KL = pg.GraphicsLayout(border=(100,100,100))
        self.lay_KL.setContentsMargins(10, 10, 10, 10)
        self.lay_KL.setSpacing(0)
        self.lay_KL.setBorder(color=(255, 255, 255, 255), width=0.8)
        self.lay_KL.setZValue(0)
        self.KLtitle = self.lay_KL.addLabel(u'')
        self.pw.setCentralItem(self.lay_KL)
        # 设置横坐标
        xdict = {}
        self.axisTime = MyStringAxis(xdict, orientation='bottom')
        # 初始化子图
        self.initplotKline()
        self.initplotVol()  
        self.initplotOI()
        # 注册十字光标
        self.crosshair = Crosshair(self.pw,self)
        # 设置界面
        self.vb = QtGui.QVBoxLayout()
        self.vb.addWidget(self.pw)
        self.setLayout(self.vb)
        # 初始化完成
        self.initCompleted = True    

    # Y坐标自适应,数据使用pd.DataFrame格式 cols : datetime, open, close, low, high
    #----------------------------------------------------------------------
    def resignData(self,datas):
        """更新数据，用于Y坐标自适应"""
        self.crosshair.datas = datas
        def viewXRangeChanged(low,high,self):
            if len(datas)>0:
                vRange = self.viewRange()
                xmin = max(0,int(vRange[0][0]))
                xmax = max(0,int(vRange[0][1]))
                xmax = min(xmax,len(datas))
                ymin = min(datas.iloc[xmin:xmax][low])
                ymax = max(datas.iloc[xmin:xmax][high])
                self.setRange(yRange = (ymin,ymax))
            else:
                self.setRange(yRange = (0,1))

        view = self.pwKL.getViewBox()
        view.sigXRangeChanged.connect(partial(viewXRangeChanged,'low','high'))

        view = self.pwVol.getViewBox()
        view.sigXRangeChanged.connect(partial(viewXRangeChanged,'volume','volume'))

        view = self.pwOI.getViewBox()
        view.sigXRangeChanged.connect(partial(viewXRangeChanged,'openInterest','openInterest'))

    #----------------------------------------------------------------------
    def clearData(self):
        """清空数据"""
        # 清空数据，重新画图
        self.time_index = []
        self.listBar = []
        self.listVol = []
        self.listLow = []
        self.listHigh = []
        self.listOpenInterest = []
        self.listSig = []
        self.arrows = []
        self.datas = None

    #----------------------------------------------------------------------
    def makePI(self,name):
        """生成PlotItem对象"""
        vb = CustomViewBox()
        plotItem = pg.PlotItem(viewBox = vb, name=name ,axisItems={'bottom': self.axisTime})
        plotItem.setMenuEnabled(False)
        plotItem.setClipToView(True)
        plotItem.hideAxis('left')
        plotItem.showAxis('right')
        plotItem.setDownsampling(mode='peak')
        plotItem.setRange(xRange = (0,1),yRange = (0,1))
        plotItem.getAxis('right').setWidth(60)
        plotItem.getAxis('right').setStyle(tickFont = QFont("Roman times",10,QFont.Bold))
        plotItem.getAxis('right').setPen(color=(255, 255, 255, 255), width=0.8)
        plotItem.showGrid(True,True)
        plotItem.hideButtons()
        return plotItem

    #----------------------------------------------------------------------
    def initplotVol(self):
        """初始化成交量子图"""
        self.pwVol  = self.makePI('PlotVol')
        self.volume = CandlestickItem(self.listVol)
        self.pwVol.addItem(self.volume)
        self.pwVol.setMaximumHeight(150)
        self.pwVol.setXLink('PlotKL')
        self.pwVol.hideAxis('bottom')

        self.lay_KL.nextRow()
        self.lay_KL.addItem(self.pwVol)

    #----------------------------------------------------------------------
    def initplotKline(self):
        """初始化K线子图"""
        self.pwKL = self.makePI('PlotKL')
        self.candle = CandlestickItem(self.listBar)
        self.pwKL.addItem(self.candle)
        self.pwKL.hideAxis('bottom')

        self.lay_KL.nextRow()
        self.lay_KL.addItem(self.pwKL)

    #----------------------------------------------------------------------
    def initplotOI(self):
        """初始化持仓量子图"""
        self.pwOI = self.makePI('PlotOI')
        self.pwOI.setXLink('PlotKL') 
        self.curveOI = self.pwOI.plot()

        self.lay_KL.nextRow()
        self.lay_KL.addItem(self.pwOI)

    #----------------------------------------------------------------------
    def plotVol(self):
        """重画成交量子图"""
        if self.initCompleted:
            self.volume.generatePicture(self.listVol)   # 画成交量子图

    #----------------------------------------------------------------------
    def plotKline(self):
        """重画K线子图"""
        if self.initCompleted:
            self.candle.generatePicture(self.listBar)   # 画K线
            self.plotMark()                             # 显示开平仓信号位置

    #----------------------------------------------------------------------
    def plotOI(self):
        """重画持仓量子图"""
        if self.initCompleted:
            self.curveOI.setData(self.listOpenInterest, pen='w', name="OpenInterest")


    #----------------------------------------------------------------------
    def addSig(self,sig):
        """新增信号图"""
        if sig in self.sigPlots:
            self.pwKL.removeItem(self.sigPlots[sig])
        self.sigPlots[sig] = self.pwKL.plot()

    #----------------------------------------------------------------------
    def showSig(self,datas):
        """刷新信号图"""
        for sig in datas:
            self.sigPlots[sig].setData(datas[sig] , pen=(255, 255, 255), name=sig)

    #----------------------------------------------------------------------
    def refresh(self):
        """刷新三个子图"""   
        datas   = self.datas
        minutes = int(self.countK/2)
        xmin    = max(0,self.index-minutes)
        xmax    = xmin+2*minutes
        self.pwKL.setRange(xRange = (xmin,xmax))

    #----------------------------------------------------------------------
    def onNxt(self):
        """跳转到下一个开平仓点"""
        if len(signals)>0 and not self.index is None:
            datalen = len(self.signals)-1
            while self.signals[self.index] == 0 and self.index < datalen:
                self.index+=1
            self.refresh()

    #----------------------------------------------------------------------
    def onPre(self):
        """跳转到上一个开平仓点"""
        if  len(signals)>0 and not self.index is None:
            while self.signals[self.index] == 0 and self.index > 1:
                self.index-=1
            self.refresh()

    #----------------------------------------------------------------------
    def onDown(self):
        """放大显示区间"""
        self.countK = min(len(self.datas),int(self.countK*1.2)+1)
        self.refresh()
        if len(self.datas)>0:
            x = self.index-self.countK/2+2 if int(self.crosshair.xAxis)<self.index-self.countK/2+2 else int(self.crosshair.xAxis)
            x = self.index+self.countK/2-2 if x>self.index+self.countK/2-2 else x
            y = self.datas.iloc[x]['close']
            self.crosshair.moveTo(x,y)

    #----------------------------------------------------------------------
    def onUp(self):
        """缩小显示区间"""
        self.countK = max(3,int(self.countK/1.2)-1)
        self.refresh()
        if len(self.datas)>0:
            x = self.index-self.countK/2+2 if int(self.crosshair.xAxis)<self.index-self.countK/2+2 else int(self.crosshair.xAxis)
            x = self.index+self.countK/2-2 if x>self.index+self.countK/2-2 else x
            y = self.datas.iloc[x]['close']
            self.crosshair.moveTo(x,y)

    #----------------------------------------------------------------------
    def onLeft(self):
        """向左移动"""
        if len(self.datas)>0:
            x = int(self.crosshair.xAxis)-1
            y = self.datas.iloc[x]['close']
            if x <= self.index-self.countK/2+2 and self.index > 1:
                self.index -= 1
                self.refresh()
            self.crosshair.moveTo(x,y)

    #----------------------------------------------------------------------
    def onRight(self):
        """向右移动"""
        if len(self.datas)>0:
            x = int(self.crosshair.xAxis)+1
            y = self.datas.iloc[x]['close']
            if x >= self.index+int(self.countK/2)-2:
                self.index += 1
                self.refresh()
            self.crosshair.moveTo(x,y)
    
    #----------------------------------------------------------------------
    def onRClick(self,pos):
        """右键单击回调"""
        pass

    #----------------------------------------------------------------------
    def onPaint(self):
        """界面刷新回调"""
        view = self.pwKL.getViewBox()
        vRange = view.viewRange()
        xmin = max(0,int(vRange[0][0]))
        xmax = max(0,int(vRange[0][1]))
        self.index  = int((xmin+xmax)/2)+1

    #----------------------------------------------------------------------
    def plotMark(self):
        """显示开平仓信号"""
        # 检查是否有数据
        if len(self.datas)==0:
            return
        for arrow in self.arrows:
            self.pwKL.removeItem(arrow)
        # 画买卖信号
        for i in range(len(self.listSig)):
            # 无信号
            if self.listSig[i] == 0:
                continue
            # 买信号
            elif self.listSig[i] > 0:
                arrow = pg.ArrowItem(pos=(i, self.datas.iloc[i]['low']),  angle=90, brush=(255, 0, 0))
            # 卖信号
            elif self.listSig[i] < 0:
                arrow = pg.ArrowItem(pos=(i, self.datas.iloc[i]['high']), angle=-90, brush=(0, 255, 0))
            self.pwKL.addItem(arrow)
            self.arrows.append(arrow)

    # 载入数据，pd.DataFrame格式，cols : datetime, open, close, low, high
    #----------------------------------------------------------------------
    def loadData(self, datas):
        """载入pandas.DataFrame数据"""
        self.datas = datas
        # 设置中心点时间，更新横坐标映射，更新Y轴自适应函数，更新十字光标映射
        self.index = 0
        xdict = dict(enumerate(datas.index.tolist()))
        self.axisTime.update_xdict(xdict)
        self.resignData(datas)
        # 更新画图用到的数据
        datas['time_int']     = np.array(range(len(datas.index)))
        self.listBar          = datas[['time_int','open','close','low','high']].values
        self.listOpen         = datas['open'].values
        self.listClose        = datas['close'].values
        self.listHigh         = datas['high'].values
        self.listLow          = datas['low'].values
        self.listOpenInterest = datas['openInterest'].values
        # 成交量颜色和涨跌同步，K线方向由涨跌决定
        datas0 = pd.DataFrame()
        datas0['time_int'] = datas['time_int']
        datas0['v0'] = datas.apply(lambda x:0 if x['close'] >= x['open'] else x['volume'],axis=1)  
        datas0['v1'] = datas.apply(lambda x:0 if x['close'] <  x['open'] else x['volume'],axis=1) 
        self.listVol = datas0[['time_int','v0','v1','v0','v1']].values
        # 调用画图函数
        self.plotKline()     # K线图
        self.plotVol()       # K线副图，成交量
        self.plotOI()        # K线副图，持仓量
        self.pwKL.setLimits(xMin=0,xMax=len(self.listBar))
        self.refresh()

########################################################################
# 功能测试
########################################################################
import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 界面设置
    cfgfile = QtCore.QFile('css.qss')
    cfgfile.open(QtCore.QFile.ReadOnly)
    styleSheet = cfgfile.readAll()
    styleSheet = unicode(styleSheet, encoding='utf8')
    app.setStyleSheet(styleSheet)
    # K线界面
    ui = KLineWidget()
    ui.show()
    ui.KLtitle.setText('rb1701',size='20pt')
    ui.loadData(pd.DataFrame.from_csv('data.csv'))
    app.exec_()
