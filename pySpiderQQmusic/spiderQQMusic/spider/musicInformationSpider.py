from threading import Thread

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from multiprocessing import Pool,cpu_count,freeze_support
import sys, os,re,urllib,traceback
from time import *
import tkinter.messagebox as msg

from spiderQQMusic.spider.musicSpider import musicSpiderTogetInformation, pieAnalysis, Histogram


# 接收控制台上的信息
class Stream(QObject):
    """Redirects console output to text widget."""
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class Ui_Form(QtWidgets.QWidget):
    def __init__(self):
        super(Ui_Form,self).__init__()
        self.urls=[]
        self.nb_jobs=cpu_count()
        self.max_num=1000
        self.start_page=1
        self.dirname=''
        self.word=''
        sys.stdout = Stream(newText=self.onUpdateText) # 接收控制台信息
        pass
    # 更新显示信息
    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(500, 574)
        Form.setWindowIcon(QtGui.QIcon('./cat.ico'))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_key = QtWidgets.QLabel(Form)
        self.label_key.setAlignment(QtCore.Qt.AlignCenter)
        self.label_key.setWordWrap(False)
        self.label_key.setOpenExternalLinks(False)
        self.label_key.setObjectName("label_key")
        self.gridLayout.addWidget(self.label_key, 0, 0, 1, 1)
        self.edit_key = QtWidgets.QLineEdit(Form)
        self.edit_key.setObjectName("edit_key")
        self.gridLayout.addWidget(self.edit_key, 0, 1, 1, 3)
        self.bt_crawl = QtWidgets.QPushButton(Form)
        self.bt_crawl.setObjectName("bt_crawl")
        self.bt_crawl.clicked.connect(self.crawl)
        self.gridLayout.addWidget(self.bt_crawl, 0, 6, 1, 1)
        self.label_dir = QtWidgets.QLabel(Form)
        self.label_dir.setAlignment(QtCore.Qt.AlignCenter)
        self.label_dir.setObjectName("label_dir")
        self.gridLayout.addWidget(self.label_dir, 1, 0, 1, 1)
        self.edit_dir = QtWidgets.QLineEdit(Form)
        self.edit_dir.setObjectName("edit_dir")
        self.gridLayout.addWidget(self.edit_dir, 1, 1, 1, 3)
        self.bt_select = QtWidgets.QPushButton(Form)
        self.bt_select.setObjectName("bt_select")
        self.bt_select.clicked.connect(self.select_dir)
        self.gridLayout.addWidget(self.bt_select, 1, 6, 1, 1)
        self.label_start = QtWidgets.QLabel(Form)
        self.label_start.setAlignment(QtCore.Qt.AlignCenter)
        self.label_start.setObjectName("label_start")
        self.gridLayout.addWidget(self.label_start, 2, 0, 1, 1)
        # 复选框
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 2, 1, 1, 1)

        self.label_jobs = QtWidgets.QLabel(Form)
        self.label_jobs.setAlignment(QtCore.Qt.AlignCenter)
        self.label_jobs.setObjectName("label_jobs")
        self.gridLayout.addWidget(self.label_jobs, 2, 2, 1, 1)
        self.spin_jobs = QtWidgets.QSpinBox(Form)
        self.spin_jobs.setObjectName("spin_jobs")
        self.spin_jobs.setRange(1,100)
        self.spin_jobs.setValue(1)
        self.gridLayout.addWidget(self.spin_jobs, 2, 3, 1, 1)
        self.bt_auto_j = QtWidgets.QPushButton(Form)
        self.bt_auto_j.setObjectName("bt_auto_j")
        self.bt_auto_j.clicked.connect(self.auto_jobs)
        self.gridLayout.addWidget(self.bt_auto_j, 2, 6, 1, 1)
        # 列表
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 3, 0, 1, 7)
        self.textEdit.ensureCursorVisible()

        #饼状图分析按钮
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 5, 1, 1)
        self.pushButton.clicked.connect(self.analysis)

        # 柱状图分析按钮
        self.pushButton1 = QtWidgets.QPushButton(Form)
        self.pushButton1.setObjectName("pushButton1")
        self.gridLayout.addWidget(self.pushButton1, 1, 5, 1, 1)
        self.pushButton1.clicked.connect(self.analysisHis)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "QQMusic爬虫"))
        self.label_key.setText(_translate("Form", "关键词"))
        self.bt_crawl.setText(_translate("Form", "爬取"))
        self.label_dir.setText(_translate("Form", "保存目录"))
        self.bt_select.setText(_translate("Form", "选择"))
        self.label_start.setText(_translate("Form", "起始"))
        self.label_jobs.setText(_translate("Form", "线程数"))
        self.bt_auto_j.setText(_translate("Form", "自动选择"))
        self.comboBox.setItemText(0, _translate("Form", "全部"))
        self.comboBox.setItemText(1, _translate("Form", "内地"))
        self.comboBox.setItemText(2, _translate("Form", "港台"))
        self.comboBox.setItemText(3, _translate("Form", "欧美"))
        self.comboBox.setItemText(4, _translate("Form", "日本"))
        self.comboBox.setItemText(5, _translate("Form", "韩国"))
        self.pushButton.setText(_translate("Form", "饼状图展示"))
        self.pushButton1.setText(_translate("Form", "柱状图展示"))

#柱状图
    def analysisHis(self):
        Histogram()

    # 饼状图分析按钮链接：
    def analysis(self):
        pieAnalysis()

    def select_dir(self):
        path = QFileDialog.getExistingDirectory(self, '选择保存路径', (self.dirname if self.dirname else './'))
        self.edit_dir.setText(path)

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)


    def auto_jobs(self):
        self.spin_jobs.setValue(cpu_count())

    def crawl(self):
        # 创建 Thread 类的实例对象
        thread = Thread(
            # target 参数 指定 新线程要执行的函数
            # 注意，这里指定的函数对象只能写一个名字，不能后面加括号，
            # 如果加括号就是直接在当前线程调用执行，而不是在新线程中执行了
            target=self.crawls)
        thread.start()

    def crawls(self):
        self.dirname, self.word = self.edit_dir.text(), self.edit_key.text()
        if not self.dirname:
            print('请指定保存目录！')
            self.select_dir()
            if not self.word:
                print('请输入关键词！')
            return
        # mkdir(self.dirname)

        #计算程序运行时间
        begin_time=time()
        end_time=None
        run_time=None
        self.nb_jobs = self.spin_jobs.value()
        print(self.comboBox.currentText())
        if self.nb_jobs < 2:
            print('正在使用单线程下载')
            nb_succeed = musicSpiderTogetInformation(self.word ,self.comboBox.currentText(),  self.dirname,self.nb_jobs)
        else:
            print('正在使用{}线程下载'.format(self.nb_jobs))
            print(self.word,   self.dirname)
            nb_succeed = musicSpiderTogetInformation(self.word ,self.comboBox.currentText(),  self.dirname,self.nb_jobs)
        #
        # 程序运行时间计算
        end_time = time()
        run_time = end_time - begin_time
        print('爬取完毕！\n共爬取{s}首歌曲，保存到文件夹:{d}，运行时间为{time}'.format(s=nb_succeed,d=self.dirname,time=run_time))
        # msg = QMessageBox(QMessageBox.Information, '数据爬取成功!', '爬取完毕！\n共爬取{s}首歌曲，保存到文件夹:{d}，运行时间为{time}'.format(s=nb_succeed,d=self.dirname,time=run_time))  # 小窗口提示框
        # msg.exec_()

# 爬虫页面初始化
def musicInforSpiderFramInit():
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    musicInforSpiderFramInit()

