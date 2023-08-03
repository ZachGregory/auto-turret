from flask import Flask, render_template, Response
import picamera
from picamera.array import PiRGBArray
import cv2
import socket
import io
import time

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(2)

app = Flask(__name__, template_folder='Templates')
print("penis")

@app.route('/')
def index():
	"""Video Streaming"""
	return render_template('index.html')
	
def gen():
	"""Video streaming generator function."""
	for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
		image = frame.array
		byteArray = cv2.imencode('.jpg', image)[1].tobytes()
		yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + byteArray + b'\r\n')
		rawCapture.truncate(0)
		
@app.route('/video_feed')
def video_feed():
	"""video streaming route. Put this in the src attrubyute of an img tag."""
	return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False, threaded=True)
