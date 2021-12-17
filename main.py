from tkinter import *

import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog

try:
    import subprocess, os, requests, zipfile, shutil, io, pathlib, pythread, atexit, sys
except:
    exit(2) 

def select_file():
    global _song_q, _song_var, _song_q_n
    file = filedialog.askopenfilename()

    if file in _song_q: return messagebox.showwarning("경고", "이미 선택된 음악입니다.")
    if file == "": return None

    _song_q.append(file)

    _song_q_n.clear()

    for song in _song_q:
        name = os.path.basename(
            str(song).replace("\\", os.sep).replace(pathlib.Path(song).suffix, "")
        )
        _song_q_n.append(name)
        print(f"{name}: {song}")

    _song_str = "\n".join(_song_q_n)

    return _song_var.set(f"Song List\n{_song_str}")

def install_ffplay():
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")

    if not os.path.isdir("ext"):
        os.mkdir("ext")

    res = requests.get("https://github.com/GyanD/codexffmpeg/releases/download/4.4.1/ffmpeg-4.4.1-essentials_build.zip")
    zip = zipfile.ZipFile(io.BytesIO(res.content))

    zip.extractall("tmp")

    shutil.move("tmp/ffmpeg-4.4.1-essentials_build/bin/ffplay.exe", "ext/ffplay.exe")
    shutil.rmtree("tmp")
    return None

def play():
    global _ffplay, _song_q
    for queue in _song_q:
        subprocess.call([_ffplay, queue, "-autoexit", "-nodisp"])

def on_exit():
    global root
    root.withdraw()
    sys.exit(0)

def on_exit_():
    global root
    os.system("taskkill /f /im ffplay.exe")    
    root.destroy()

atexit.register(on_exit_)

if not os.path.isdir("ext") & os.path.isfile("ext/ffplay.exe"):
    install_ffplay()

root = Tk()
root.geometry("265x265")
root.resizable(False, False)
root.title("Plpyer")

_song_var = StringVar(value="Song List")
_ffplay = f"{os.getcwd()}\\ext\\ffplay.exe"
_song_q = list() # _song_queue = []
_song_q_n = list() # _song_q_n = []

select_btn = Button(root, text="음악 선택하기", command=select_file)
play_btn = Button(root, text="음악 재생하기", command=lambda: pythread.cTread("play", play))
q_lab = Label(root, textvariable=_song_var)

root.protocol("WM_DELETE_WINDOW", on_exit)

select_btn.pack()
play_btn.pack()
q_lab.pack()
root.mainloop()
