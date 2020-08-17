import os, socket
from youtube_dl import YoutubeDL

PORT_NUM = 55543 # set port number
DIRECTORY = '/home/oat/Videos/' # set output directory
FORMAT = 'bestvideo[height<=1080]+bestaudio' # set format 

ydl_opts = { # youtube-dl options. See: https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278
    'outtmpl' : DIRECTORY+'%(title)s_%(id)s.%(ext)s',
    'format' : FORMAT,
}

def main():
    
    ydl = YoutubeDL(ydl_opts)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('localhost', PORT_NUM))
    except:
        print("[YTDL] Port in use. Is another instance running?")
        return
    else:
        pass
    s.listen()
    print("[YTDL] Youtube-dl started")

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        video_url = data.decode('utf-8')
        try:
            print(f"[YTDL] Downloading {video_url}")
            ydl.download([video_url])
        except:
            print("[YTDL] Error parsing video/video not found")
        else:
            print(f"[YTDL] Downloaded '{video_url}' to local storage.")
        conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
