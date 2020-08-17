import cv2
import zmq
import base64
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind('tcp://192.168.1.98:55544')
socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
print('Running')
while True:
    try:
        data = socket.recv_string()
        print(len(data))
        raw_image = base64.b64decode(data)

        image = np.frombuffer(raw_image, dtype=np.uint8)
        frame = cv2.imdecode(image, 1)



        cv2.imshow("frame", frame)
        cv2.waitKey(5)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break