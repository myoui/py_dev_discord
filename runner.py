import sys, os, time, bot, ytdl, tkinter, PySimpleGUI as sg
from multiprocessing import Process

def main(yt = 1):
    disc = Process(target=bot.main)
    disc.start()
    if yt:
        yt_dl = Process(target=ytdl.main)
        yt_dl.start()


def interface(yt = 1):
    sg_layout_toggle = [sg.Button("Bot ON", key='bot', size=(10,2))]
    if yt:
        sg_layout_toggle.append(sg.Button("YTDL ON", key='yt', size=(10,2)))
    sg_layout = [
        [sg.Text("Bot is operational")],
        sg_layout_toggle,
        [sg.Text("Run in terminal for logging")],
        [sg.Button("Exit")]
    ]
    window = sg.Window("JS BOT", sg_layout, element_justification="center")
    
    disc = Process(target=bot.main)
    disc.start()
    if yt:
        yt_dl = Process(target=ytdl.main)
        yt_dl.start()

    while True:

        event, values = window.read(timeout=100)

        if event in (sg.WINDOW_CLOSED, 'Exit'):
            print('[BOT] Exiting...')
            disc.terminate()
            if yt:
                yt_dl.terminate()
            break

        if event == 'bot':
            if disc.is_alive():
                print("Stopping Discord bot")
                disc.terminate()
                time.sleep(1)
                window['bot'].update('Bot OFF')
            else:
                print("Starting Discord bot")
                try:
                    disc = Process(target=bot.main)
                    disc.start()
                    window['bot'].update('Bot ON')
                except:
                    print("Discord bot is busy")

        if event == "yt":
            if yt_dl.is_alive():
                print("Stopping YTDL bot")
                time.sleep(1)
                yt_dl.terminate()
                window['yt'].update('YTDL OFF')
            else:
                print("Starting YTDL bot")
                try:
                    yt_dl = Process(target=ytdl.main)
                    yt_dl.start()
                    window['yt'].update('YTDL ON')
                except:
                    print("YTDL bot is busy")
    window.close()

if __name__ == "__main__":

    print("A BOT BY JS")
    try:
        if len(sys.argv) == 1:
            interface()
        elif sys.argv[1] in ("-n", "-nogui"):
            print("[BOT] No GUI")
            main()
        elif sys.argv[1] in ("-bn", "-botonly-nogui"):
            print("[BOT] Bot only + no GUI")
            main(yt=0)
        elif sys.argv[1] in ("-b", "-botonly"):    
            print("[BOT] Bot only")
            interface(yt=0)
    except KeyboardInterrupt:
        sys.exit()