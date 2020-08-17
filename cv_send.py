import sys, os, math, cv2 as cv, socket, pickle, time
from threading import Thread
from queue import Queue

VIDEO_PORT = 55545
DELIMITER = b"$%^$"
class VideoStream:
    def __init__(
        self,
        input, 
        ip=None, 
        port=VIDEO_PORT,
        resize=0,
        webcamfps=15,
        debug=False,
        autostart=True
        ):
        
        ## Initializes video source and parameters.
        self.DELIMITER = DELIMITER
        self.input = input
        self.source = cv.VideoCapture(input)
        self._done = False
        self._debug = debug
        self._addr = None
        self._resize = resize

        self.ip = (ip, port)
        self.resize = resize

        ## Webcam may return 0 fps. Use fps to set waitKey value.

        if self.source.get(cv.CAP_PROP_FPS) > 0:
            self.fps = self.source.get(cv.CAP_PROP_FPS)
            print(f'Video fps: {self.fps}')
            self._queue = Queue(16)
        else:
            self.fps = webcamfps
            self._queue = Queue(8)
        
        self._wait = math.floor(1000/self.fps) # wait value is int in ms

        ## Test if the input is valid.

        ret, frame = self.source.read()
        if not ret:
            print("[INPUT] Could not read video or camera!")
            self._done = True
        if autostart:
            self.start()
    ## v v v Utility functions v v v

    # Resets object

    def reinit(self):
        self.__init__(
            input=self.input, 
            ip=self._addr[0], 
            resize=self._resize,
            webcamfps=15,
        )


    def done(self):
        if self._done:
            print("Stream is finished.")
            return True
        else:
            return False

    # Adjust resize value

    @property
    def resize(self):
        return self._resize
    
    @resize.setter
    def resize(self, resolution):
        if resolution == 0:
            self._resize = None
            print('Resize disabled')
        elif isinstance(resolution, tuple) and len(resolution) == 2:
            if isinstance(resolution[0], int) and isinstance(resolution[1], int):
                self._resize = resolution
                print(f'Resize resolution set to {self._resize[0]}x{self._resize[1]}')
            else:
                print('Tuple values must be int type')
        else:
            print("[ERROR] Resolution must be in tuple '(width, height)' or 0 to disable resize")


    # Set target IP and port

    @property
    def ip(self):
        return self._addr
    
    @ip.setter
    def ip(self, ip):
        if isinstance(ip[0], str) and isinstance(ip[1], int):
            self._addr = ip
        else:
            print('Invalid IP and/or port number.')

    def connect(self):
        if not self._addr:
            print('Target IP not set.')
            return
        print(f'Connecting to {self._addr}')
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect(self._addr)
        except Exception as err:
            print(err)
            self._socket.close()
            del self._socket
            self._connected = False
        else:
            print('Connected')
            self._connected = True

    def disconnect(self):
        if self._connected:
            self._socket.close()
        self._connected = False            

    ## v v v Processing functions v v v

    def show(self):
        print("Showing Video")
        while True:
            if self.done():
                break
            ret, frame = self.source.read()
            if not ret:
                break
            if self._resize:
                frame = cv.resize(frame, self._resize)
            cv.imshow('Video', frame)
            if cv.waitKey(self._wait) & 0xFF == ord('q'):
                break
            if  not self._queue.full(): 
                self._queue.put(cv.imencode('.jpg', frame)[1]) # !! imencode returns (bool, img)
            if self._debug: time.sleep(1)

        self.source.release()
        cv.destroyAllWindows()
        self._done = True

    def send(self):
        if not self._connected:
            print('Not connected.')
            return

        self._socket.send(b'STREAM'+self.DELIMITER+b'STARTING')
        response = self._socket.recv(8)
        if response == b'$READY$':
            timeout = 0
            print('Streaming video')
            while True:
                if self._done:
                    print('Stopped sending')
                    break
                if not self._queue.empty():
                    img = pickle.dumps(self._queue.get())
                    if self._debug: print(len(img))
                    try:
                        self._socket.send(str(len(img)).encode().ljust(8, b'%'))
                        self._socket.sendall(img)
                    except Exception as err:
                        print(err)
                        break
            print('Done sending')
            self._done = True
        else:
            print('Bad response from destination.')
        
        self.disconnect()


    # Start Video streaming
    def start(self):
        # if self._done:
        #     self.reinit()

        self.connect()
        if not self._connected:
            return
        print(f'Streaming to {self.ip}')
        reader = Thread(target=self.show)
        reader.daemon = True
        reader.start()
        
        sender = Thread(target=self.send)
        sender.start()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('APP [IP] [SOURCE(0 for webcam)]')
    else:
        try:
            source = int(sys.argv[2])
        except:
            source = sys.argv[2]

        v = VideoStream(input=source, resize=(320,240), debug=False, ip=sys.argv[1])
        # v.show()
