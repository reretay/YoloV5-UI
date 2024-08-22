import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox
import os
import subprocess
from detect2 import run

MainWindow = uic.loadUiType("ui.ui")[0]

class WindowClass(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        #이벤트 연결
        self.pushButton.clicked.connect(self.start_detect)
        
    def start_detect(self):
        run(weights='yolov5s.pt', source=1, imgsz=(640, 640), conf_thres=0.25)

        
        
    # 프로그램 종료 함수
    def end_program(self):
            QApplication.quit()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())