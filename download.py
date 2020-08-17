import sys, os, socket, tkinter, ctypes, PySimpleGUI as sg
from youtube_dl import YoutubeDL
from ytdl import PORT_NUM
from multiprocessing import Process, Event, Value


#  TODO: implement Pipe()(?)

ydl_agent = YoutubeDL()

def main(video_url):
    print(f"[YTDL] Parsing video: {video_url}")
    try:
        info = ydl_agent.extract_info(video_url, download=False)
        print(f"[YTDL] Valid video: {info['title']}")
    except:
        print("Error parsing video/video not found")
    else:
        if info['duration'] < 600:
            print(f"[YTDL] Sending {info['title']} to youtube-dl")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect(("localhost", PORT_NUM))
                    s.send(video_url.encode())
                except:
                    print("Can not connect to Youtube-dl")
                else:
                    print(f"'{info['title']}' sent to youtube-dl")
                finally:
                    s.close()

        else:
            print(f"[YTDL] Video {info['title']} longer than allowed duration")


def interface():
    worker = None
    sg_layout = [
        [sg.Text("Enter URL below")],
        [sg.InputText(size=(75,50))],
        [sg.Text("Run in terminal for status", key="status")],
        [sg.Button("Ok"), sg.Button("Exit")]
    ]
    print("[YTDL-GUI] Starting GUI...")
    window = sg.Window("YTDL", sg_layout)

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            print("[YTDL-GUI] Exiting...")
            if ytdl_mt:
                print("[YTDL-GUI] Stopping downloader...")          
                ytdl_mt.terminate()
            if worker:
                worker.terminate()
            break
        elif event == "Ok":
            if not worker or not worker.is_alive():
                worker = Process(target=main, args=(values[0],))
                worker.start()
            else:
                print("[YTDL-GUI] Already working on job!")

    window.close()



if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        import ytdl
        ytdl_mt = Process(target=ytdl.main)
        gui_mt = Process(target=interface)
        ytdl_mt.start()
        gui_mt.start()