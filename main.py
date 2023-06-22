import datetime
import time
import traceback
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QNetworkAccessManager
from PyQt5.QtCore import QDate, pyqtSlot, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QColor
from deepface import DeepFace
import sys

def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)

    text += ''.join(traceback.format_tb(tb))

    print(text)
    QtWidgets.QMessageBox.critical(None, 'Error', text)

    sys.exit()

sys.excepthook = log_uncaught_exceptions
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)


class InfoThread(QThread):
    dataThread = pyqtSignal(list)
    def __init__(self, img,parent):
        super(InfoThread,self).__init__(parent)
        self.img = img

    def run(self):
        try:
            obj = DeepFace.analyze(self.img)
        except:
            obj = []
        self.dataThread.emit(obj)


class Ui_MainWindow(QtWidgets.QMainWindow):

    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.cv_img = cv_img
        self.MainLabel.setPixmap(qt_img)
        self.update_info()
        # self.get_info(cv_img)
    def get_info(self,detail):
        if len(detail)!=0:
            detail = detail[0]
            status = 'Лицо найдено'
            age = detail['age']
            emotion = detail['dominant_emotion']
            gender = detail['dominant_gender']
            race = detail['dominant_race']
            self.LastTimeLabel.setText(datetime.datetime.now().strftime("%I:%M:%S"))
        else:
            status = 'Лицо не найдено'
            age = " - "
            emotion = ' - '
            gender = ' - '
            race = ' - '
        self.update_labels(status,gender,age,race,emotion)

    def update_labels(self,status,gender,age,race,emotion):
        self.StatusLabel.setText(f'Статус:{status}')
        self.GenderLabel.setText(f'Пол:{gender}')
        self.AgeLabel.setText(f'Возраст:{age}')
        self.RaceLabel.setText(f'Раса:{race}')
        self.EmotionLabel.setText(f'Эмоция:{emotion}')

    def analize(self):
        # obj = DeepFace.analyze(img_path=self.cv_img, enforce_detection=False)
        # print(obj)
        infoThread = InfoThread(self.cv_img,self)
        infoThread.dataThread.connect(self.get_info)
        print('before')
        infoThread.start()
        print('after')

    def update_info(self):
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M:%S")
        self.DateNameLabel.setText(f'Дата: {current_date}')
        self.TimeNameLabel.setText(f'Время: {current_time}')

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.width, self.height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(801, 601)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(540, 0, 261, 131))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.TimeLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.TimeLayout.setContentsMargins(0, 0, 0, 0)
        self.TimeLayout.setObjectName("TimeLayout")
        self.DateNameLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.DateNameLabel.setFont(font)
        self.DateNameLabel.setToolTipDuration(1)
        self.DateNameLabel.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.DateNameLabel.setObjectName("DateNameLabel")
        self.TimeLayout.addWidget(self.DateNameLabel, 0, 0, 1, 1)
        self.TimeNameLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.TimeNameLabel.setFont(font)
        self.TimeNameLabel.setToolTipDuration(1)
        self.TimeNameLabel.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.TimeNameLabel.setObjectName("TimeNameLabel")
        self.TimeLayout.addWidget(self.TimeNameLabel, 1, 0, 1, 1)
        self.InformationBox = QtWidgets.QGroupBox(self.centralwidget)
        self.InformationBox.setGeometry(QtCore.QRect(540, 140, 260, 340))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.InformationBox.setFont(font)
        self.InformationBox.setObjectName("InformationBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.InformationBox)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 40, 241, 271))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.StatusLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.StatusLabel.setFont(font)
        self.StatusLabel.setObjectName("StatusLabel")
        self.verticalLayout.addWidget(self.StatusLabel)
        self.GenderLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.GenderLabel.setFont(font)
        self.GenderLabel.setObjectName("GenderLabel")
        self.verticalLayout.addWidget(self.GenderLabel)
        self.AgeLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.AgeLabel.setFont(font)
        self.AgeLabel.setObjectName("AgeLabel")
        self.verticalLayout.addWidget(self.AgeLabel)
        self.RaceLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.RaceLabel.setFont(font)
        self.RaceLabel.setObjectName("RaceLabel")
        self.verticalLayout.addWidget(self.RaceLabel)
        self.EmotionLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.EmotionLabel.setFont(font)
        self.EmotionLabel.setObjectName("EmotionLabel")
        self.verticalLayout.addWidget(self.EmotionLabel)
        self.LastTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.LastTimeLabel.setGeometry(QtCore.QRect(550, 470, 239, 81))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.LastTimeLabel.setFont(font)
        self.LastTimeLabel.setObjectName("LastTimeLabel")
        self.MainLabel = QtWidgets.QLabel(self.centralwidget)
        self.MainLabel.setGeometry(QtCore.QRect(10, 40, 500, 400))
        self.MainLabel.setText("")
        self.MainLabel.setObjectName("MainLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.MainButton = QtWidgets.QPushButton(self.centralwidget)
        self.MainButton.setGeometry(QtCore.QRect(130, 460, 220, 90))
        self.MainButton.setText('Анализ')
        self.MainButton.setObjectName("MainButton")
        self.retranslateUi(MainWindow)
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime('%I:%M')
        self.DateNameLabel.setText(current_date)
        self.TimeNameLabel.setText(current_time)
        self.width, self.height = self.MainLabel.width(), self.MainLabel.height()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.pause = False
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.MainButton.clicked.connect(self.analize)
        self.thread.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.DateNameLabel.setText(_translate("MainWindow", "Дата:"))
        self.TimeNameLabel.setText(_translate("MainWindow", "Время:"))
        self.InformationBox.setTitle(_translate("MainWindow", "Информация"))
        self.StatusLabel.setText(_translate("MainWindow", "Статус:"))
        self.GenderLabel.setText(_translate("MainWindow", "Пол:"))
        self.AgeLabel.setText(_translate("MainWindow", "Возраст:"))
        self.RaceLabel.setText(_translate("MainWindow", "Раса:"))
        self.EmotionLabel.setText(_translate("MainWindow", "Эмоция:"))
        self.LastTimeLabel.setText(_translate("MainWindow", "Последнее время:"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
