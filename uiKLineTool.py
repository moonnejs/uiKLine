# -*- coding: utf-8 -*-
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
os.environ['QT_API'] = 'pyqt'
from uiBasicIO import uiBasicIO
from uiKLine import KLineWidget
# PyQt
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy import QtGui,QtCore


import pandas as pd



########################################################################
class uiKLineTool(uiBasicIO):
    """K线回测分析工具"""

    dbClient = None
    signal = QtCore.Signal(type({}))

    #----------------------------------------------------------------------
    def __init__(self,parent=None):
        """初始化函数"""
        super(uiKLineTool,self).__init__(parent,\
                    'json\\uiKLine_input.json',\
                    'json\\uiKLine_button.json')  # 输入配置文件,按钮配置文件

        # 用于计算因子的数据
        self.bars = []
        self.pdBars = pd.DataFrame()
        self.signals = []
        self.signalsOpen = []
        self.states = []
        self.stateData = {}
        
        self.datas = None
        self.vtSymbol = ""
        self.vtSymbol1 = ""
        self.mode = 'deal'

        self.canvas = KLineWidget()
        self.signal.connect(self.loadData)

        self.initUi()


    #-----------------------------------------------
    def loadData(self,data):
        """加载数据"""
        self.signals = data['deal']
        self.signalsOpen = data['dealOpen']
        kTool = self.canvas
        for sig in kTool.sigPlots:
            kTool.pwKL.removeItem(kTool.sigPlots[sig])
        kTool.sigData  = {}
        kTool.sigPlots = {}
        for sig in kTool.subSigPlots:
            kTool.pwOI.removeItem(kTool.subSigPlots[sig])
        kTool.subSigData  = {}
        kTool.subSigPlots = {}
        print u'正在准备回测结果数据....'
        self.canvas.clearData()
        self.pdBars = data[['open','close','low','high','volume','openInterest']]
        self.canvas.loadData(self.pdBars)
        self.canvas.updateSig(self.signals)
        barinfo = ['datetime','open','close','low','high','volume','openInterest','deal','dealOpen']
        allState = [k for k in data if not k in barinfo]
        self.stateData = data[allState].to_records()
        self.editDict['signalName'].clear()
        self.editDict['signalName'].addItems(allState) 
        print u'数据准备完成！'

    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        hbox = QHBoxLayout()
        hbox.addWidget(self.groupInput)
        hbox.addWidget(self.groupProcess)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)

    #----------------------------------------------------------------------
    def setSymbol(self, symbol):
        """设置合约信息"""
        self.vtSymbol = symbol

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
    ui = uiKLineTool()
    ui.show()
    app.exec_()
