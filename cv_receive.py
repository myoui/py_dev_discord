import os, sys, socket, time, cv2 as cv, pickle
from multiprocessing import Process, Queue

VIDEO_PORT = 55545
DELIMITER = b"$%^$"

# cv.namedWindow('frame', cv.WINDOW_NORMAL)
# cv.resizeWindow('frame', 800, 600)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def recv_video(resize=None):
    self_ip = get_ip()
    media = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    media.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    media.bind((self_ip, VIDEO_PORT))
    media.listen(10)

    print(f"Listening for video on {self_ip}:{VIDEO_PORT}. Please open specificed port to receive files.")
    while True:
        conn, ip = media.accept()
        print(f'Request from {ip[0]}:{ip[1]}')
        data = conn.recv(64)
        try:
            print(data)
            signal, _ = data.split(DELIMITER)
        except:
            print("Error splitting data")
            continue
        else:
            if signal == b'STREAM':
                print('READY')
                conn.send(b'$READY$')

                timeout = 0
                print('Receiving...')

                while True:
                    frame = bytearray()
                    size = conn.recv(8)
                    if not size:
                        timeout += 1
                        print(f'...{timeout}')
                        time.sleep(1)
                        if timeout > 4:
                            print('Stream ended.')
                            break
                        continue
                    try:
                        size = int(size.rstrip(b'%'))
                    except:
                        continue
                    while len(frame) < size:
                        data = conn.recv(size - len(frame))
                        # print(len(data))
                        if not data:
                            timeout += 1
                            print(f'...{timeout}')
                            time.sleep(1)
                            if timeout > 4:
                                print('Timed out.')
                                break
                            continue
                        frame.extend(data)
                    try:
                        # print(len(frame))

                        img = pickle.loads(frame)
                        img = cv.imdecode(img, 1)
                        if resize: img = cv.resize(img, resize)
                        cv.imshow("Press 'Q' to end stream", img)
                        if cv.waitKey(15) & 0xFF == ord('q'):
                            break


                    except:
                        print('Pickle error')
                        continue
                cv.destroyAllWindows()
                conn.close()

def showimg():
    while True:
        if not q.empty():
            img = cv.imdecode(q.get(), 1)
            # img = cv.resize(img, (640,480))
            cv.imshow('recv', img)
            cv.waitKey(5)
        else:
            continue


if __name__ == "__main__":
    Process(target=recv_video, args=((640,480),)).start()
    ## Used

