import os, sys, time, tkinter, PySimpleGUI as sg
from youtube_dl import YoutubeDL
from multiprocessing import Queue, Process


DIRECTORY = '/home/oat/Videos/' # set output directory
MAX_DURATION = 900
FORMATS = {
    "480p" : 'bestvideo[height<=480]+bestaudio',
    "720p" : 'bestvideo[height<=720]+bestaudio',
    "1080p" : 'bestvideo[height<=1080]+bestaudio',
    "Best" : 'bestvideo+bestaudio',
}

# Communication Queues
# worker() gets instructions from q. interface() gets status updates from status.
q = Queue()
status = Queue()

SENTINEL = 'CLOSE THE GATES'


# Youtube-dl agent ---
def worker():
    ydl_opts = {
    # youtube-dl options.
    # See https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278
        'outtmpl' : DIRECTORY+'%(title)s_%(id)s.%(ext)s',
        'format' : FORMATS['1080p'],
    }
    ytdl = YoutubeDL(ydl_opts)

    print('Agent starting...')
    while True:
        if not q.empty(): # fetch from worker queue
            url = str(q.get())
            if url == SENTINEL: # Exit sentinel
                print('Agent exiting...')
                break
            elif url.startswith("$FORMAT:"): # Change format
                format = url.split(":")[1]
                ydl_opts['format'] = FORMATS[format]
                print(ydl_opts['format'])
                ytdl = YoutubeDL(ydl_opts)
            else: # Parse URL
                print(f"[YTDL] Parsing video: {url}")
                status.put("Parsing...")
                try: # Verifies video. Optional
                    info = ytdl.extract_info(url, download=False)
                    print(f"[YTDL] Valid video: {info['title']}")
                    status.put("Size: "+str(round(info['requested_formats'][0]['filesize']/1000000,2))+"Mb")
                except:
                    print("Error parsing video/video not found")
                    status.put("Error parsing video/video not found")
                else:
                    if info['duration'] <= MAX_DURATION:
                        status.put("Downloading video...")
                        ytdl.download([url]) # Only accepts a list(?)
                        status.put("Download complete.")
                    else:
                        print(f"[YTDL] Video {info['title']} longer than allowed duration")
                        status.put("Video is longer than allowed duration")
        else:
            time.sleep(1)

# GUI
def interface():
    sg_layout = [
        [sg.Text("Enter URL below")],
        [sg.InputText(size=(67,1), key='input'), sg.Button("Clear")],
        [sg.Text("Format:"), sg.DropDown(
            values=list(FORMATS.keys()), default_value='1080p',
            key='format', readonly=True, enable_events=True, pad=(0,5), size=(10,10))],
        [sg.Multiline("", disabled=True, autoscroll=True, key='history', size=(75,8))],
        [sg.Button("Download", bind_return_key=True, size=(10,1)), sg.Button("Exit", size=(5,1))]
    ]
    history = ""
    print("[YTDL-GUI] Starting GUI...")
    window = sg.Window("YTDL", sg_layout)

    while True:
        event, values = window.read(timeout=100)
        if not status.empty(): # Updates status window per read
            latest_status = status.get()
            history += latest_status+"\n"
            window['history'].update(history)
        
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            print("[YTDL-GUI] Exiting...")
            q.put(SENTINEL)
            break
        elif event == "Download":
            if not values['input'] or not values['input'].strip():
                print("No value!")
            elif q.empty():
                q.put(values['input'])
                history += values['input']+"\n"
                window['history'].update(history)
            else:
                status.put("A video is already in queue.")
        elif event == 'format':
            print(window['format'].get()+" selected, restarting agent.")
            q.put('$FORMAT:'+window['format'].get())
        elif event == "Clear":
            window['input'].update('')
    
    window.close()

if __name__ == "__main__":
    gui = Process(target=interface)
    agent = Process(target=worker)
    gui.start()
    agent.start()
    gui.join()
    agent.join()
    sys.exit()