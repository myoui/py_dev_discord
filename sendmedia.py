import sys, os, socket, time

def media_send(filename:str, ip:str, data=None):
    DELIMITER = b"$%^$"
    if data and type(data) != bytes:
        print('data input must be in bytes')
        return False
    else:
        try:
            with open(filename, "rb") as fi:
                data = fi.read()
        except:
            print(f"Error opening file: {filename}.")
            return False
    size = len(data)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, 55544))
        print(f"Connected to {ip}")
    except Exception as err:
        print(err)
        return False
    
    s.send(b'FILE'+DELIMITER+filename.split("/")[-1].encode()+DELIMITER+str(size).encode())
    response = s.recv(8)
    if response == b'OK':
        print(f'Sending {filename.split("/")[-1]}')
        s.sendall(data)
    else:
        print("Response error")
        return False
    print("Finished sending file.")

media_send("/home/oat/Desktop/Untitled Folder/Form W-9 (Rev. October 2018)-signed.pdf", "192.168.1.68")