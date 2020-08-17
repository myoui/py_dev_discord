import sys, os, socket, json, time, select
from threading import Thread
from multiprocessing import Process

PORT_NUM = 55543
MSG_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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

myip = get_ip()
s.bind((myip, PORT_NUM))
s.listen(10)
clients = []
users = {}


def a_client(conn, ip):
    username = None
    conn.send(f"User connected.\n".encode())
    while True:
        try:
            msg = conn.recv(MSG_SIZE)
            if msg:
                msg = msg.decode("utf-8")
                if msg == "!help":
                    conn.send("[SYSTEM] Available commands: !nick !users !user !myip".encode())

                elif msg.startswith("!nick"):
                    if len(msg.split(" ")) == 2:
                        nick = msg.split()[1]
                        if nick in users.keys():
                            conn.send(f"[SYSTEM] The name '{nick}' is already taken.".encode())
                        else:
                            if username:
                                del users[username]
                                broadcast(username=username, mode='del')
                                broadcast(f"[SYSTEM] {ip[0]} changed nick from {username} to {nick}")
                            # else:
                            #     broadcast(f"[SYSTEM] {ip[0]} changed nick to {nick}")
                            username = nick
                            users[username] = (ip[0], ip[1])
                            # print(len(users))
                            conn.send(f"[SYSTEM] Your nickname is now {username}".encode())
                            time.sleep(0.1)
                            broadcast(username=username, ip=ip[0], mode='add')
                    else:
                        conn.send(b"[SYSTEM] Set your nickname with `!nick [username]`")

                elif msg == '!users':
                    conn.send(f'[SYSTEM] {len(clients)} users connected'.encode())

                elif msg.startswith("!user"):
                    if len(msg.split(" ")) == 2:
                        user = msg.split()[1]
                        if user in users.keys():
                            conn.send(f"[SYSTEM-user] {user} {users[user][0]}".encode())
                        else:
                            conn.send("[SYSTEM] user not found.".encode())
                    else:
                        conn.send("[SYSTEM] !user [username] to get a user's IP".encode())
                        
                elif msg == '!myip':
                    conn.send(
                        f'[SYSTEM] Your IP is: {users[username][0]+":"+str(users[username][1])}'
                        .encode())
                else:
                    text = f"{username if username else ip[0]} [{time.ctime()}]: {msg}"
                    broadcast(text, username=username, ip=ip[0])
            else:
                del_client(conn)
                del users[username]
                break
        except:
            time.sleep(0.2)
            continue

def broadcast(msg=None, username=None, ip=None, mode=None):
    def close(client):
        client.close()
        del_client(client)

    if msg and not mode: # Updates userlist every broadcast
        print(msg)
        for client in clients:
            try:
                client.send(msg.encode())
            except:
                close(client)
        time.sleep(0.1)
        if username and ip:          
            for client in clients:
                try:
                    client.send(f"$ni$ {username} {ip}".encode())
                except:
                    close(client)

    elif mode == "add" and username and ip:
        for client in clients:
            try:
                client.send(f"$ni$ {username} {ip}".encode())
            except:
                close(client)

    elif mode == "del" and username:
        for client in clients:
            try:
                client.send(f"$nid$ {username}".encode())
            except:
                close(client)
                
    time.sleep(0.1)


def del_client(conn):
    clients.remove(conn)

def main():
    print(f"Starting Server {myip}")
    while True:
        conn, ip = s.accept()
        clients.append(conn)
        print(f'{ip[0]}:{ip[1]} connected')
        Thread(target=a_client, args=(conn, ip)).start()

Process(target=main).start()