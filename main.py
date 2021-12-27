from tkinter import *
from tkinter import filedialog

from urllib import request
from zipfile import ZipFile
from contextlib import closing

import sys, shutil, os, subprocess, atexit

ctypes = None
windows = False
high_dpi = False
dpi = 100

queue = list()

if sys.platform.startswith("win"):
    import ctypes 
    windows = True

root = Tk()
if windows:
    dpi = ctypes.windll.user32.GetDpiForWindow(root.winfo_id())
    
if dpi >= 101:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    high_dpi = True

root.geometry("265x265" if not high_dpi else "530x530")
root.resizable(False, False)
root.title("플레이어")

def install_external():
    request.urlretrieve("https://github.com/GyanD/codexffmpeg/releases/download/4.4.1/ffmpeg-4.4.1-essentials_build.zip", "ffmpeg.zip")
    os.mkdir("temp")
    with closing(ZipFile("ffmpeg.zip", "r")) as f:
        f.extractall("temp")

    shutil.move("temp\\ffmpeg-4.4.1-essentials_build\\bin\\ffplay.exe", "ffplay.exe")
    shutil.rmtree("temp")
    os.remove("ffmpeg.zip")

if not os.path.isfile("ffplay.exe"):
    install_external()

def restart(executable, argv, queue):
    at_exit()
    with closing(open("saved_restart.txt", "w")) as f:
        f.write("\n".join(queue))

    os.execl(executable, executable, argv)

def load_save(queue, root):
    with closing(open("saved_restart.txt", "r")) as f:
        queue.extend(f.read().splitlines())

    play(queue, root)

def select(queue):
    file = filedialog.askopenfilename()

    if file in queue:
        return print("어? 이미 추가한 곡을 고르셨어요!")

    queue.append(file)

def play(queue, root):
    root.withdraw()
    for song in queue:
        subprocess.call(
            [f"{os.getcwd()}\\ffplay.exe", song]
        )

def at_exit():
    global root
    root.quit()
    subprocess.Popen("taskkill /f /im ffplay.exe")

atexit.register(at_exit)

def at_destroy():
    subprocess.Popen("taskkill /f /im ffplay.exe")
    exit()

if os.path.isfile("saved_restart.txt"):
    load_save(queue, root)

select_button = Button(root, text="음악 추가", command=lambda: select(queue))
play_button = Button(root, text="음악 재생", command=lambda: play(queue, root))
restart_button = Button(root, text="음악 다시 재생하기", command=lambda: restart(sys.executable, f'"{sys.argv[0]}"', queue))

root.protocol("WM_DELETE_WINDOW", at_destroy)

select_button.pack(side=TOP, anchor=SW)
play_button.pack(side=TOP, anchor=SW)
restart_button.pack(side=TOP, anchor=SW)

root.mainloop()
