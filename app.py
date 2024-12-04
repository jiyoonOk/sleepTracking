from flask import Flask, render_template, request, Response
from camera import gen_frames, get_camera
import atexit

app = Flask(__name__,
    template_folder='src/templates',    
    static_folder='src/static'          
)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/video_feed')
def video_feed():
    """비디오 스트리밍 라우트"""
    try:
        return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"비디오 피드 에러: {str(e)}")
        return "비디오 스트림을 시작할 수 없습니다.", 500

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@atexit.register
def cleanup():
    camera = get_camera()
    if camera:
        camera.cleanup()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
