import sys, os, socket, time
from threading import Thread

MEDIA_PORT = 55544
DELIMITER = b"$%^$"

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

def check_filename(path, filename):
    while os.path.isfile(path+"/"+filename):
        name, ext = os.path.splitext(filename)
        name = name+" copy"
        filename = name+ext
    return filename

def recv_media():
    self_ip = get_ip()

    media = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    media.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    media.bind((self_ip, MEDIA_PORT))
    media.listen(10)

    print(f"Listening for files on {self_ip}:{MEDIA_PORT}. Please specificed open port to receive files.")
    while True:
        conn, ip = media.accept()
        print(f'Request from {ip[0]}:{ip[1]}')
        data = conn.recv(256)
        try:
            signal, name, size = data.split(DELIMITER)
            size = int(size)
            name = name.decode('utf-8')
        except:
            print("Error splitting data")
        else:
            if signal == b'FILE':
                print(f'Get file: '+name)
                conn.send(b'OK')

                dir = "./downloads/"+ip[0]
                if not os.path.exists(dir):
                    os.makedirs(dir)
                name = check_filename(dir, name)

                wfi = open(dir+"/"+name, 'wb+')
                got_size = 0
                while got_size < size:
                    data = conn.recv(size)
                    wfi.write(data)
                    got_size += len(data)
                print("Finished")
                wfi.close()
                conn.close()



            # counter += 1

recv_media()