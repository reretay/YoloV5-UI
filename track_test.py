import os
import sys
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class track(QThread):
    
    # 작업 완료 시그널
    finished = pyqtSignal()
    # 상태 업데이트 시그널
    status_updated = pyqtSignal(str)

    
    def __init__(self, center_height, center_width, bbox):
        super().__init__()
        center_height = self.center_height
        center_width = self.center_width
        bbox = self.bbox
    
    def run(self):
        # top_left_x, top_left_y, width, height
        top_left_x = self.bbox[0]
        top_left_y = self.bbox[1]
        width = self.bbox[2]
        height = self.bbox[3]

        # 중앙 좌표 계산
        center_x = top_left_x + width / 2
        center_y = top_left_y + height / 2
        
    def stop(self):
        # 스레드 강제 종료
        if self.isRunning():
            self.terminate()  # QThread의 terminate 메서드로 강제 종료
            self.wait()  # 스레드가 종료될 때까지 대기 (필요에 따라)