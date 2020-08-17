import base64, cv2, zmq, sys, time, math
from threading import Thread
from queue import Queue
input = None
ip = None

stopped = False

def stream(address='tcp://192.168.1.98:55544'):
    global stopped

    cap = Thread(target=capture, args=(input,))
    cap.daemon = True
    cap.start()
    
    time.sleep(1)

    while not stopped:
        try:
            data = q.get()
            if data:
                socket.send(data)
            else:
                continue
        except KeyboardInterrupt:
            break
    cap.join()
    socket.close()

def capture(input, address='tcp://192.168.1.98:55544'):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(address)
    camera = cv2.VideoCapture(input)
    if type(input) != int:
        wait = math.floor(1000/math.ceil(camera.get(cv2.CAP_PROP_FPS)))
    else:
        wait = 100
    print(wait)
    
    while camera.isOpened():
        try:
            ret, frame = camera.read()
            if not ret:
                break
            cv2.imshow('send', frame)
            cv2.waitKey(wait)
            frame = cv2.resize(frame, (320, 240))
            rend, img = cv2.imencode('.jpg', frame)
            if not rend:
                break

            data = base64.b64encode(img)
            socket.send(data)
        except KeyboardInterrupt:
            camera.release()
            cv2.destroyAllWindows()
            break



if __name__ == "__main__":
    try:
        input = int(sys.argv[1])
    except:
        input = str(sys.argv[1])
    ip = str(sys.argv[2])

    print(input,ip)
    try:
        capture(input, ip)
    except Exception as err:
        print(err)