from flask import Response
import cv2
import threading
import time

class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)  # 웹캠 초기화
        if not self.camera.isOpened():
            raise RuntimeError('카메라를 열 수 없습니다.')
            
        # 카메라 설정
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        # Haar Cascade 분류기 로드
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        if self.face_cascade.empty() or self.eye_cascade.empty():
            raise RuntimeError('Haar Cascade 파일을 로드할 수 없습니다.')

    def get_frame(self):
        success, frame = self.camera.read()
        if not success:
            return None
            
        # 그레이스케일 변환
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 얼굴 감지
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # 눈 감지
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
        
        # JPEG로 인코딩
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def __del__(self):
        self.camera.release()

# 전역 카메라 객체
camera = None

def get_camera():
    global camera
    if camera is None:
        try:
            camera = Camera()
        except Exception as e:
            print(f"카메라 초기화 에러: {str(e)}")
    return camera

def gen_frames():
    global camera
    if camera is None:
        camera = get_camera()
    
    while True:
        try:
            frame = camera.get_frame()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                print("프레임을 가져올 수 없습니다.")
                time.sleep(0.1)
        except Exception as e:
            print(f"프레임 생성 중 에러: {str(e)}")
            time.sleep(0.1)
            continue