from flask import Flask, render_template, Response
import cv2
import threading
import numpy as np

#initialize HOG
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

app = Flask(__name__, template_folder='Templates')
url = "http://192.168.0.168:5000/video_feed"
cap = cv2.VideoCapture(url)
lock = threading.Lock()
frame = None

#output video
out = cv2.VideoWriter(
    'output.avi',
    cv2.VideoWriter_fourcc(*'MJPG'),
    15.,
    (360,360)
)


@app.route('/')
def index():
    return render_template('index.html', coords=gen())

def gen():
    """Process the image through the HOG Algorithm and output the correction coordinates"""
    global frame

    lock.acquire()
    #process image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    boxes, weights = hog.detectMultiScale(gray, winStride=(2,2), padding=(10,10), scale=1.02)
    boxes = np.array([[x,y, x+w, y+h] for (x, y, w, h) in boxes])

    coordinates = dict()
    for i, (xA, yA, xB, yB) in enumerate(boxes):
        if weights[i] < 0.30:
            continue
        else:
            #display
            ysum = int(yA)+((int(yB)-int(yA))/2)-180
            xsum = int(xA)+((int(xB)-int(xA))/2)-240
            coordinates[abs(xsum)+abs(ysum)] = (xsum,ysum) #dictionary entry as Sum distance from center = (x,y)
            cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

    coords = sorted(coordinates)
    #cv2.imshow("live", frame)
    lock.release()
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    if len(coords) > 0:
        return coordinates[coords[0]]
    else:
        return 0

def thread_read_frames():
    global frame
    lock.acquire()
    ret, frame = cap.read()
    lock.release()
    while True:
        lock.acquire()
        cv2.imshow("live", frame)
        ret, frame = cap.read()
        frame = cv2.resize(frame, (480, 360))
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        """gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes, weights = hog.detectMultiScale(gray, winStride=(2,2), padding=(10,10), scale=1.02)
        boxes = np.array([[x,y, x+w, y+h] for (x, y, w, h) in boxes])
        for i, (xA, yA, xB, yB) in enumerate(boxes):
            if weights[i] < 0.45:
                continue
            else:
                #display
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
        cv2.imshow("live", frame)"""
        lock.release()
        if cv2.waitKey(5) > 0:
            break 

if __name__ == '__main__':
    x = threading.Thread(target=thread_read_frames)
    x.start()
    app.run(host='0.0.0.0', debug=False, threaded=True)