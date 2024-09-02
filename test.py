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
from deep_sort_realtime.deepsort_tracker import DeepSort # DeepSort 임포트

MainWindow = uic.loadUiType("ui.ui")[0]

class WindowClass(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.yolo_thread = None #쓰레드 초기화

        #이벤트 연결
        self.pushButton.clicked.connect(self.start_detection)
        self.pushButton_2.clicked.connect(self.stop_detection)
        self.pushButton_3.clicked.connect(self.end_program)
        self.pushButton_4.clicked.connect(self.start_track_id)

        # QComboBox 초기값
        self.weights = 'yolov5s.pt'
        self.source = '0'
        self.device = 'cpu'
        
        # QLineEdit 초기값
        self.lineEdit.setText("(450,450)")
        self.lineEdit_3.setText("30")
        
        # QComboBox에 대한 이벤트 핸들러 연결
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.comboBox_2.currentIndexChanged.connect(self.on_combobox_changed)
        self.comboBox_3.currentIndexChanged.connect(self.on_combobox_changed)
        
        # DeepSort 객체 생성
        self.deepsort = DeepSort()
        # im0 초기화
        self.current_im0 = None
        
    def start_detection(self):
        if not self.yolo_thread or not self.yolo_thread.isRunning():
            # run(weights='yolov5s.pt', source=1, imgsz=(640, 640), conf_thres=0.25)
            
            resolution = self.lineEdit.text().strip() # QLineEdit 에서 읽어오기
            try:
            # 문자열 "(450,450)"을 튜플 (450, 450)로 변환
                imgsz = tuple(map(int, resolution.strip("()").split(",")))
            except ValueError:
                QMessageBox.warning(None, "Error", "Invalid resolution format. Please enter in the format (width,height).")
                return
            
            self.yolo_thread = yolov5(source=self.source, weights=self.weights, imgsz=imgsz, conf_thres=0.25, device=self.device)
            #self.yolo_thread.image_signal.connect(self.update_image)
            self.yolo_thread.im0_signal.connect(self.im0_signal)
            self.yolo_thread.det_signal.connect(self.det_signal)
            self.yolo_thread.start()
        else:
            QMessageBox.warning(None, "Warn!", "Detection is already in progress.")
        
    def stop_detection(self):
        if self.yolo_thread and self.yolo_thread.isRunning():
            self.yolo_thread.stop()
        else:
            QMessageBox.warning(None, "Warn!", "No detection in progress")
    
    def im0_signal(self, im0): #im0 시그널 처리
        #self.textBrowser.append(status)  # textBrowser에 정보 추가
        percent = int(self.lineEdit_3.text())
        height, width = im0.shape[:2] # im0에서 해상도 추출
        side_length = int(min(height, width) * (percent / 100)) # 정사각형의 변 길이 계산
        center_height, center_width = height // 2, width // 2 # 이미지 중앙 좌표 계산
        top_left_x = center_width - side_length // 2 # 정사각형의 좌상단 좌표와 우하단 좌표 계산
        top_left_y = center_height - side_length // 2
        bottom_right_x = center_width + side_length // 2
        bottom_right_y = center_height + side_length // 2
        cv2.rectangle(im0, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 2)
        qimage = self.numpy_to_qimage(im0) # np arrray to QImage
        pixmap = QPixmap.fromImage(qimage) # Create QPixmap from QImage
        self.label.setPixmap(pixmap) # 생성한 QImage를 label에 출력
    
        self.current_im0 = im0 # DeepSort의 프레임을 위함
    
    def det_signal(self, det):
        
        det_str = str(det)
        self.textBrowser_2.append(det_str)
        
        # DeepSort
        # bboxes = []
        # confidence = []
        # classes = []
        # frame = self.current_im0

        # # det의 구조를 확인하고 적절하게 값을 추출
        # for d in reversed(det):
        #     if len(d) >= 6:  # 필요한 값이 모두 있는지 확인
        #         *xyxy, conf, cls = d
        #         bboxes.append(tuple(xyxy))
        #         confidence.append(conf)
        #         classes.append(cls)
        
        # track_results = self.deepsort.update_tracks(bboxes, confidence, classes, frame) # DeepSort로 객체 추적
        # results_str = str(track_results)
        # self..textBrowser.append(results_str)
        
        if len(det) > 0:
            # det에서 필요한 값들 추출
            bbs = []  # DeepSort가 기대하는 형식으로 변환된 바운딩 박스 리스트

            for d in det:
                d = d.cpu().numpy()  # 텐서를 numpy 배열로 변환
                for detection in d:
                    if len(detection) >= 6:  # 필요한 값이 모두 있는지 확인
                        *xyxy, conf, cls = detection
                        # xyxy -> x1, y1, x2, y2로 나누기
                        x1, y1, x2, y2 = xyxy
                        # 좌표를 [left, top, w, h] 형식으로 변환
                        w = x2 - x1
                        h = y2 - y1
                        bbox = [x1, y1, w, h]  # [left, top, width, height] 형식
                        bbs.append((bbox, conf, int(cls)))  # 튜플 형태로 추가

            # 프레임이 유효한지 확인
            if self.current_im0 is None:
                self.textBrowser.append("Frame is not available")
                return

            # DeepSort로 객체 추적
            try:
                self.track_results = self.deepsort.update_tracks(bbs, frame=self.current_im0)
                if self.track_results is None:
                    self.textBrowser.append("No tracks available")
                else:
                    # Track 객체의 정보 추출 후 출력
                    for track in self.track_results:
                        track_info = (f"Track ID: {track.track_id}, "
                                    f"BBox: {track.to_tlwh()}, ")
                                    #f"Class ID: {track.class_id}")
                        self.textBrowser.append(track_info)
            except Exception as e:
                self.textBrowser.append(f"Error: {str(e)}")
        else:
            self.textBrowser.append("No detections")



    
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

    def start_track_id(self):
        target_track_id = self.lineEdit_2.text().strip()
        # Track ID가 target_track_id인 객체를 찾기
        target_track = None
        for track in self.track_results:
            if track.track_id == target_track_id:
                target_track = track
                break

        if target_track is not None:
            # 필요한 정보 추출
            track_id = target_track.track_id
            bbox = target_track.to_tlwh()
            #confidence = target_track.detection_confidence
            #class_id = target_track.class_id

            self.textBrowser_3.append(f"Track ID: {track_id}")
            self.textBrowser_3.append(f"BBox: {bbox}")
            #self.textBrowser_3.append(f"Confidence: {confidence}")
            #self.textBrowser_3.append(f"Class ID: {class_id}")
        else:
            self.textBrowser_3.append("Target track not found.")
    
    def on_combobox_changed(self):
        selected_weights = self.comboBox.currentIndex()
        selected_source = self.comboBox_2.currentIndex()
        selected_device = self.comboBox_3.currentIndex()
        
        if selected_weights == 0:
            self.weights = 'yolov5s.pt'
            
        if selected_source == 0:
            self.source = '0'
        elif selected_source == 1:
            self.source = '1'
        
        if selected_device == 0:
            self.device = 'cpu'
        elif selected_device == 1:
            self.device = '1'
        elif selected_device == 2:
            self.device = '2'
        
    # 프로그램 종료 함수
    def end_program(self):
            QApplication.quit()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())