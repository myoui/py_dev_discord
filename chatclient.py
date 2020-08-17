import sys, os, socket, time, tkinter, PySimpleGUI as sg
from multiprocessing import Process, Queue
from threading import Thread
from cv_send import VideoStream
from cv_receive import recv_video

IP_ADDR = None
IP_PORT = 55543
MEDIA_PORT = 55544
VIDEO_PORT = 55545
DELIMITER = b"$%^$"

NICK = ''

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
status = Queue()

users = {}
def add_user(username, ip):
    users[username] = (ip, MEDIA_PORT)

def get_ip(): # Get own IP helper
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

# Send data and tools ---
def media_send(filename:str, ip:str, data=None):
    if data and type(data) != bytes:
        print('data input must be in bytes')
        return False
    else:
        try:
            with open(filename, "rb") as fi:
                data = fi.read()
        except:
            print(f"Error opening file: {filename}.")
            status.put(f"Error opening file: {filename}.")
            return False
    size = len(data)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, MEDIA_PORT))
        print(f"Connected to {ip}")
        status.put(f"Connected to {ip}")
    except Exception as err:
        print("Connection error")
        status.put("Connection error")
        return False
    
    s.send(b'FILE'+DELIMITER+filename.split("/")[-1].encode()+DELIMITER+str(size).encode())
    response = s.recv(8)
    if response == b'OK':
        print(f'Sending {filename.split("/")[-1]}')
        status.put(f'Sending {filename.split("/")[-1]}')
        s.sendall(data)
    else:
        print("Response error")
        return False
    print("Finished sending file.")
    status.put("Finished sending file.")
    return

# Receive data and tools ---
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
        status.put(f'[FILE] Request from {ip[0]}:{ip[1]}')
        data = conn.recv(256)
        print(data)
        try:
            signal, name, size = data.split(DELIMITER)
            size = int(size)
            name = name.decode('utf-8')
        except:
            print("Error splitting data")
            status.put("[FILE] Error splitting data")
        else:
            if signal == b'FILE':
                print(f'Get file: '+name)
                status.put(f'[FILE] Get file: '+name)
                conn.send(b'OK')

                dir = "./downloads/"+ip[0]
                if not os.path.exists(dir):
                    os.makedirs(dir)
                name = check_filename(dir, name)

                wfi = open(dir+"/"+name, 'wb+')
                got_size = 0
                while got_size < size:
                    data = conn.recv(4096)
                    wfi.write(data)
                    got_size += len(data)
                print("Finished")
                status.put("[FILE] Finished")
                wfi.close()
                conn.close()
# ---
    
def get_msg():
    print("Listening")
    while True:
        try:
            msg = c.recv(1024)
            if msg:
                msg = msg.decode('utf-8')
                print(msg)
                status.put(msg)
        except:
            time.sleep(.5)
            continue

def send_msg(msg):
    try:
        c.send(msg.encode())
    except:
        print("ERR: Failed to send msg")
        status.put("Failed to send msg")
        c.close()


def interface():
    # Main window layout
    menu_layout = [
        ['&Menu',['&Send File', '&Change Nickname','&Exit']],
    ]
    right_click_menu = ['&Menu',["___",'&Send File', '&Start Chat']]
    int_layout = [
        [sg.Menu(menu_layout)],
        [sg.Multiline("", size=(100,20), autoscroll=True, disabled=True, key='history'),
        sg.Listbox([],size=(20,19), key='users_col', enable_events=True,
            select_mode="LISTBOX_SELECT_MODE_SINGLE", right_click_menu=right_click_menu)],
        [sg.InputText("", size=(90,1), key='input'),
        sg.Button("Send", bind_return_key=True)],
        [sg.StatusBar("", size=(100,1), key="status_bar", background_color='grey', text_color='white')]
    ]

    # Needs factory for popups because layouts can only be used once (??)
    def make_nick_layout():
        nick_layout = [
            [sg.Text("Change your nickname. No spaces allowed!")],
            [sg.InputText("", key='nick_text')],
            [sg.Button("Ok", key='nick_submit', bind_return_key=True)]
        ]
        return nick_layout

    selected_user = None

    def make_send_layout():
        send_layout = [
            [sg.Text("Send a file to another user. Use command '!user [username]' to populate list.")],
            [sg.InputText(freeze_selected, disabled=True, key="to_user")],
            [sg.InputText("", key='file_location'), sg.FileBrowse()],
            [sg.Button("Ok", key='file_send')]
        ]
        return send_layout

    def make_chat_layout():
        chat_layout = [
            [sg.Text("Chat with another user. Use command '!user [username]' to populate list.")],
            [sg.InputText(freeze_selected, disabled=True, key="to_user")],
            [sg.Button('Start Chat', key='chat_init'), sg.Button('End Chat', key='chat_end')],
        ]
        return chat_layout

    history = ""

    # Start subroutines
    
    listen = Thread(target=get_msg)
    listen.daemon = True
    listen.start()

    try:
        media = Process(target=recv_media)
        media.start()
    except Exception as err:
        print(err)
        pass

    status_bar_text = f"Chat server IP: {IP_ADDR}"
    window = sg.Window("Client", int_layout)
    
    # Window statuses

    nick_win_open = False
    send_file_open = False
    chat_win_open = False

    while True:
        #Main window

        event, values = window.read(timeout=100)
        window['status_bar'].update(status_bar_text)
        if not status.empty(): # Updates status window per read
            latest_status = status.get()
            # Add user ip
            if latest_status.startswith("$ni$"):
                _, username, ip = latest_status.split()
                users[username] = ip
                print(f'Added user {username}')
                print(users)
            # Del user ip
            elif latest_status.startswith("$nid$"):
                _, username = latest_status.split()
                try:
                    del users[username]
                    print(f"{username} deleted.")
                except Exception as err:
                    print(err)
            else:
                history += latest_status+"\n"
                window['history'].update(history)
            window['users_col'].update(list(users.keys()))
        if event in (sg.WINDOW_CLOSED, 'Exit'):

            ### MULTIPROCESS
            # listen.terminate()
            try:
                media.terminate()
            except Exception as err:
                print(err)

            break
        if event == "Send":
            send_msg(values['input'])
            window['input'].update('')
            window['input'].set_focus()
        
        # Change nickname popup

        if event == "Change Nickname" and not nick_win_open:
            print("Open change nick window")
            nick_win_open = True
            nick_win = sg.Window('Change Nickname', make_nick_layout())
        if nick_win_open:
            event, values = nick_win.read(timeout=100)
            if event == sg.WINDOW_CLOSED:
                nick_win_open = False
                nick_win.close()
            if event == "nick_submit":
                send_msg(f"!nick {values['nick_text']}")
                nick_win_open = False
                nick_win.close()

        if event == "users_col":
            selected_user = values['users_col'][0]
            print(selected_user+" selected")

        # Send file window

        if event == "Send File" and not send_file_open:
            if selected_user == None:
                sg.Popup("No user selected", title="Warning", line_width=200)
            else:
                send_file_open = True
                freeze_selected = str(selected_user)
                send_file_win = sg.Window('Send File', make_send_layout())
        if send_file_open:
            event, values = send_file_win.read(timeout=100)
            if event == sg.WINDOW_CLOSED:
                send_file_open = False
                del freeze_selected
                send_file_win.close()
            if event == 'file_send':
                if not values['file_location']:
                    continue
                else:
                    file_location = values['file_location']
                    toip = users[values['to_user']]
                    print(f"Send file {file_location} to {toip}")
                    send_file_open = False
                    del freeze_selected
                    send_file_win.close()
                    # TODO send function
                    worker = Process(target=media_send, args=(file_location, toip))
                    worker.start()

        # Chat window

        if event == "Start Chat" and not chat_win_open:
            if selected_user == None:
                sg.Popup("No user selected", title="Warning", line_width=200)
            else:
                chat_win_open = True
                freeze_selected = str(selected_user)
                video = Process(target=recv_video, args=((640,480),))
                video.start()
                chat_win = sg.Window('Video Chat', make_chat_layout())
        if chat_win_open:
            event, values = chat_win.read(timeout=100)
            if event in (sg.WIN_CLOSED, 'chat_end'):
                video.terminate()
                chat_win_open = False
                del freeze_selected
                chat_win.close()
            if event == 'chat_init':
                print(f'Starting chat with {freeze_selected}..')
                camera = Process(target=VideoStream, kwargs={
                    'input':'video2.mkv', 'ip':users[freeze_selected], 'resize':(320,240),
                    })
                camera.start()
                camera.join()

            




if __name__ == "__main__":
    if len(sys.argv) == 4:
        IP_ADDR = str(sys.argv[1])
        IP_PORT = int(sys.argv[2])
        NICK = str(sys.argv[3])
    else:
        login_layout = [
            [sg.Text("Server IP:", size=(15,1)), sg.InputText("", key='ip', size=(20,1))],
            [sg.Text("Server Port:", size=(15,1)), sg.InputText(str(IP_PORT), key='port', disabled=True ,size=(20,1))],
            [sg.Text("Username:", size=(15,1)), sg.InputText("", key='username', size=(20,1))],
            
            [sg.Button("Login", bind_return_key=True), sg.Button("Exit")]
        ]
        window = sg.Window("Login", login_layout)
        while True:
            event, values = window.Read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                sys.exit()
            if event == 'Login':
                if not values['ip'] or not values['username']:
                    continue
                else:
                    IP_ADDR = values['ip']
                    try:
                        IP_PORT = int(values['port'])
                    except:
                        pass
                    NICK = values['username']
                    break
        window.close()

    print(IP_ADDR, NICK)

    inter = Thread(target=interface)
    inter.start()

    retrycount = 1
    while True:
        try:
            c.connect((IP_ADDR, IP_PORT))
            c.send(f'!nick {NICK}'.encode())
            break
        except:
            if retrycount < 5:
                print(f"Cannot connect to {NICK}@{IP_ADDR}:{IP_PORT}, retrying in 5s...{retrycount}")
                status.put(f"Cannot connect to {NICK}@{IP_ADDR}:{IP_PORT}, retrying in 5s...{retrycount}")
                retrycount += 1
                time.sleep(5)
            else:
                print("Cannot connect to server. Please try again later.")
                status.put("Cannot connect to server. Please try again later.")
                break

    if not inter.is_alive():
        sys.exit()

