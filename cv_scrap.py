import sys, os
import pickle, time, math, socket, cv2 as cv
from multiprocessing import Queue, Process
from threading import Thread
from queue import Queue

DELIMITER = b"$%^$"
IP = '192.168.1.98'
PORT = 55544
INPUT = 'video2.mkv'
COMPRESSION = None
WAIT = 50
q = Queue(5)

class Streamer:
    def __init__(self, input, queue=128, compress=False):
        self.source = cv.VideoCapture(input)
        self.stopped = False
        self.compress = compress
        self.queue = Queue(queue)
        if type(input) != int:
            self.fps = self.source.get(cv.CAP_PROP_FPS)
        else:
            self.fps = None
    def get(self):
        while True:
            if self.stopped:
                return
            if not self.queue.full():
                ret, frame = self.source.read()
                if not ret:
                    self.stopped = True
                    return
                self.queue.put(frame)

    def start(self):
        worker = Thread(target=self.get)
        worker.daemon = True
        worker.start()
        return self

    def read(self):
        return self.queue.get()


def stream(input, compress=True, limit=50):
    vid = cv.VideoCapture(input)
    if input != 0: 
        limit = math.floor(1000/math.ceil(vid.get(cv.CAP_PROP_FPS)))
    else:
        limit = 50
    try:
        ret, frame = vid.read()
        size = len(pickle.dumps(frame))
        print(size)
    except Exception as err:
        print(err)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((IP, PORT))
        print(f"Connected")
    except Exception as err:
        print(err)

    s.send(b'STREAM'+DELIMITER+str(size).encode())
    response = s.recv(8)
    if response != b'$READY$':
        print("Error")
        s.close()
    else:
        while vid.isOpened():
            ret, frame = vid.read()
            if not ret:
                print('Stopped')
                break
            frame = cv.resize(frame, (320,240))    
            cv.imshow('sending', frame)
            cv.waitKey(limit)
            if compress:
                _, img = cv.imencode('.jpg', frame)
                data = pickle.dumps(img)
            else:
                data = pickle.dumps(frame)
            s.send(str(len(data)).encode().ljust(8, b'%'))
            s.sendall(data)


        vid.release()
        cv.destroyAllWindows()
        s.close()

def stream2():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((IP, PORT))
        print(f"Connected")
    except Exception as err:
        print(err)

    s.send(b'STREAM'+DELIMITER+b'STARTING')
    response = s.recv(8)
    if response != b'$READY$':
        print("Error")
        s.close()
    else:

        cap = Streamer(INPUT, queue=10, compress=True)
        cap.start()
        if cap.fps:
            wait = math.floor(1000/cap.fps)
        else:
            wait = 10
        while not cap.stopped:
            frame = cap.read()
            cv.imshow('Video', frame)
            cv.waitKey(wait)
            if cap.compress:
                frame = cv.imencode('.jpg', frame)
            data = pickle.dumps(frame)
            s.send(str(len(data)).encode().ljust(8, b'%'))
            s.sendall(data)



if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('APP [IP] [PORT] [SOURCE(0 for webcam)]')
    else:
        IP = str(sys.argv[1])
        PORT = int(sys.argv[2])
        try:
            INPUT = int(sys.argv[3])
        except:
            INPUT = str(sys.argv[3])
        try:
            WAIT = int(sys.argv[4])
        except:
            pass
    stream(INPUT)

