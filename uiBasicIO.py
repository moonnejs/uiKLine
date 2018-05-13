# -*- coding: utf-8 -*-
# PyQt
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy import QtGui,QtCore
# Others
import os
import imp
import sys
import json
import glob
from functools import partial
from collections import OrderedDict

# 导入按钮函数
#---------------------------------------------------------------------------------------
ALL_FUNC_BUTTON = []
funcBtnPath = os.getcwd() + '/func-button/'
allPath = glob.glob(funcBtnPath+r'*.py')
for path in allPath:
    fileName  = path.split("\\")[-1]
    modelName = fileName.split(".")[0]
    ALL_FUNC_BUTTON.append(modelName)
    imp.load_source('ctaFuncButttons',path)

BUTTON_FUNC  = {}
from ctaFuncButttons import *
for func_bt in ALL_FUNC_BUTTON:
    fn_obj = getattr(sys.modules['ctaFuncButttons'], func_bt)
    BUTTON_FUNC[func_bt]  = fn_obj

# 字符串转换
#---------------------------------------------------------------------------------------
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

########################################################################
class uiBasicIO(QWidget):
    """通过json文件，自动生成输入框和按钮的元类"""

    #----------------------------------------------------------------------
    def __init__(self,parent=None,inpFile='',btnFile=''):
        """初始化函数"""
        super(uiBasicIO,self).__init__(parent)

        # 输入框数据
        self.classDict    = OrderedDict()
        self.labelDict    = {}
        self.widthDict    = {}
        self.typeDict     = {}
        self.evalDict     = {}
        self.editDict     = {}
        # 按钮数据
        self.bClassDict   = OrderedDict()
        self.bWidthDict   = {}
        self.bFunDict     = {}
        self.buttonDict   = {}
        # 输入框和按钮
        self.groupInput   = None
        self.groupProcess = None
        # 输入框和按钮的配置文件
        self.inpFile      = inpFile
        self.btnFile      = btnFile

        self.loadInputSetting()
        self.loadButtonSetting()
        self.initBasicUi()

    #----------------------------------------------------------------------
    def getInputParamByName(self,name):
        """获得输入框参数值"""
        typeName = self.typeDict[name]
        editCell = self.editDict[name]
        val = str(editCell.currentText()) if typeName == 'List' else str(editCell.text())
        try:
            return (eval(val) if self.evalDict[name] else val)
        except:
            return val
 
    #----------------------------------------------------------------------
    def loadInputSetting(self):
        """载入输入框界面配置"""
        settingFile = self.inpFile
        with open(settingFile) as f:
            for setting in json.load(f):
                name        = setting['name']
                label       = setting['label']
                typeName    = setting['type']
                evalType    = setting['eval']
                width       = setting['width']
                className   = setting['class']
                default     = setting['default']
                # 标签
                self.labelDict[name] = QLabel(label)
                self.labelDict[name].setAlignment(QtCore.Qt.AlignCenter)
                # 宽度
                self.widthDict[name] = width
                # 输入框类型
                self.typeDict[name] = typeName
                self.evalDict[name] = evalType
                # 分类
                if className in self.classDict:
                    self.classDict[className].append(name)
                else:
                    self.classDict[className] = [name]
                # 输入框
                if typeName == 'Edit':
                    self.editDict[name] = QLineEdit()
                    self.editDict[name].setText(default)
                elif typeName == 'List':
                    self.editDict[name] = QComboBox()
                    self.editDict[name].addItems(eval(setting['ListVar']))

    #----------------------------------------------------------------------
    def loadButtonSetting(self):
        """载入按钮界面配置"""
        settingFile = self.btnFile
        with open(settingFile) as f:
            for setting in json.load(f):
                label       = setting['label']
                func        = setting['func']
                width       = setting['width']
                className   = setting['class']
                style       = setting['style']
                # 按钮
                self.buttonDict[func] = QPushButton(label)
                self.buttonDict[func].setObjectName(_fromUtf8(style))
                self.buttonDict[func].clicked.connect(partial(BUTTON_FUNC[func],self))
                # 宽度
                self.bWidthDict[func] = width
                # 分类
                if className in self.bClassDict:
                    self.bClassDict[className].append(func)
                else:
                    self.bClassDict[className] = [func]

    #----------------------------------------------------------------------
    def initBasicUi(self):
        """初始化界面"""
        # 根据配置文件生成输入框界面
        self.groupInput = QGroupBox()
        self.groupInput.setTitle(u'')
        gridup = QGridLayout()
        i = 0
        for className in self.classDict:
            classIndex = i
            # 标题和输入框
            for name in self.classDict[className]:
                width   = self.widthDict[name]
                qLabel  = self.labelDict[name]
                qEdit   = self.editDict[name]
                gridup.addWidget(qLabel, 1, i)
                gridup.addWidget(qEdit, 2, i)
                gridup.setColumnStretch(i, width)
                i+=1
            # 分类标题
            qcLabel = QLabel(className)
            qcLabel.setAlignment(QtCore.Qt.AlignCenter)
            qcLabel.setFont(QtGui.QFont("Roman times",10,QtGui.QFont.Bold))
            gridup.addWidget(qcLabel, 0, classIndex,1,i-classIndex)
            # 分隔符
            for j in xrange(0,3):
                qcSplit = QLabel(u'|')
                qcSplit.setAlignment(QtCore.Qt.AlignCenter)
                gridup.addWidget(qcSplit, j, i)
            i+=1
        self.groupInput.setLayout(gridup)

        # 根据配置文件生成按钮界面
        self.groupProcess = QGroupBox()
        self.groupProcess.setTitle(u'')
        griddown = QGridLayout()
        i = 0
        for className in self.bClassDict:
            classIndex = i
            # 标题和输入框
            for name in self.bClassDict[className]:
                width   = self.bWidthDict[name]
                qButton = self.buttonDict[name]
                griddown.addWidget(qButton, 1, i)
                griddown.setColumnStretch(i, width)
                i+=1
            # 分类标题
            qcLabel = QLabel(className)
            qcLabel.setAlignment(QtCore.Qt.AlignCenter)
            qcLabel.setFont(QFont("Roman times",10,QtGui.QFont.Bold))
            griddown.addWidget(qcLabel, 0, classIndex,1,i-classIndex)
            # 分隔符
            for j in xrange(0,2):
                qcSplit = QLabel(u'|')
                qcSplit.setAlignment(QtCore.Qt.AlignCenter)
                griddown.addWidget(qcSplit, j, i)
            i+=1
        self.groupProcess.setLayout(griddown)

