import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox
import os
import subprocess
from detect2 import yolov5

import cv2 # OpenCV, np 어레이를 QImage로 변환
import numpy as np # for np array

MainWindow = uic.loadUiType("ui.ui")[0]

class WindowClass(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.yolo_thread = None #쓰레드 초기화

        #이벤트 연결
        self.pushButton.clicked.connect(self.start_detection)
        
    def start_detection(self):
        # run(weights='yolov5s.pt', source=1, imgsz=(640, 640), conf_thres=0.25)
        self.yolo_thread = yolov5(source=1, weights='yolov5s.pt', imgsz=(450,450), conf_thres=0.25)
        #self.yolo_thread.image_signal.connect(self.update_image)
        self.yolo_thread.im0_signal.connect(self.im0_signal)
        self.yolo_thread.det_signal.connect(self.det_signal)
        self.yolo_thread.start()
        
    def im0_signal(self, im0): #im0 시그널 처리
        #self.textBrowser.append(status)  # textBrowser에 정보 추가
        qimage = self.numpy_to_qimage(im0) # np arrray to QImage
        pixmap = QPixmap.fromImage(qimage) # Create QPixmap from QImage
        self.label.setPixmap(pixmap) # 생성한 QImage를 label에 출력
    
    def det_signal(self, det):
        det_str = str(det)
        self.label_2.setText(det_str)
    
    def numpy_to_qimage(self, image: np.ndarray) -> QImage:
        """Convert a numpy array to QImage."""
        if len(image.shape) == 3:
            if image.shape[2] == 3:  # RGB
                # Convert BGR to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                q_format = QImage.Format_RGB888
            elif image.shape[2] == 4:  # RGBA
                q_format = QImage.Format_RGBA8888
            else:
                raise ValueError("Unsupported number of channels in the image")
            bytes_per_line = 3 * image.shape[1] if image.shape[2] == 3 else 4 * image.shape[1]
            q_image = QImage(image.data, image.shape[1], image.shape[0], bytes_per_line, q_format)
            return q_image
        elif len(image.shape) == 2:  # Grayscale
            q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Grayscale8)
            return q_image
        else:
            raise ValueError("Unsupported image format")

    
    # 프로그램 종료 함수
    def end_program(self):
            QApplication.quit()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())