from tkinter import *

import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog

import sys
if sys.version[0] != "3": sys.exit(3)
import os

try:
    import ctypes
    import time
    import pathlib
    import requests
    import pythread
    import zipfile
    import io
    import shutil
    import subprocess
    import atexit
    import js2py
    import PIL.Image
except ImportError:
    if os.path.isfile("requirements.txt"):
       os.system("pip install -r requirements.txt")
    else:
        packages = ["Pillow==8.4.0", "JS2Py==0.71", "pythread==1.0.2", "requests==2.26.0"]
        for package in packages:
            os.system(f"pip install {package}")

argv = sys.argv[0] if not " " in sys.argv[0] else '"' + sys.argv[0] + '"'

log = js2py.eval_js(
"""
function log(log){
    console.log(log);
}
"""
)

warning = js2py.eval_js(
"""
function warning(log){
    console.log('warning: ' + log);
}

"""
)

ctypes.windll.shcore.SetProcessDpiAwareness(1)

print("\033[32m")  
log("Plpyer | 제작: poolmanager | https://github.com/poolmanager")

if not sys.platform.startswith("win"):
    warning("윈도우에서만 작동합니다.")
    time.sleep(10)
    sys.exit(3)

def select_file():
    global _song_q, _song_q_n
    file = filedialog.askopenfilename(title="파일 선택하기")

    if file in _song_q: return messagebox.showwarning("경고", "이미 선택된 음악입니다.")
    if file == "": return None
    if not pathlib.Path(file).suffix in (".mp3", ".ogg", ".wav"): return messagebox.showwarning("경고", "음악 파일이 아닙니다.")

    _song_q.append(file)

    _song_q_n.clear()

    for song in _song_q:
        name = os.path.basename(
            str(song).replace("\\", os.sep).replace(pathlib.Path(song).suffix, "")
        )
        _song_q_n.append(name)
        print(f"{name}: {song}")

    return None

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
    global _ffplay, _song_q, log, _T_var
    for queue in _song_q:
        music = "Now playing: {0}".format(os.path.basename(str(queue).replace("\\", os.sep).replace(pathlib.Path(queue).suffix, "")))
        log(music)
        _T_var.set(music)
        subprocess.call([_ffplay, queue, "-nodisp", "-autoexit"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

play_wrapper = lambda: pythread.cTread("PlayWrapper", play)

def on_exit():
    global root
    subprocess.call("taskkill /f /im ffplay.exe")
    root.withdraw()
    sys.exit(0)

def on_exit_():
    global root
    subprocess.call("taskkill /f /im ffplay.exe")
    print("\033[37m")  
    root.destroy()

atexit.register(on_exit_)

def song_list_():
    global _song_q_n
    if len(_song_q_n) <= 0:
        return messagebox.showerror("오류", "선택된 음악이 없습니다.")

    _root = Tk()
    _root.resizable(False, False)
    _label = Label(_root, text="\n".join(_song_q_n))
    _label.pack()
    _root.mainloop()

def stop():
    global argv, _song_q
    subprocess.call("taskkill /f /im ffplay.exe")
    with io.open("saved.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(_song_q))
    os.execl(sys.executable, sys.executable, argv)

def skip():
    global _song_q, argv
    subprocess.call("taskkill /f /im ffplay.exe")
    with io.open("skip.txt", "a", encoding="utf-8") as f:
        _song_q.append(_song_q.pop(0))
        f.write("\n".join(_song_q))

    return os.execl(sys.executable, sys.executable, argv)

def load_skip():
    global _song_q
    if not os.path.isfile("skip.txt"):
        return None

    with io.open("skip.txt", "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f]
    
    _song_q.extend(lines)
    play_wrapper()
        
    return os.remove("skip.txt")

def load_save():
    global _song_q
    if not os.path.isfile("saved.txt"):
        return None

    with io.open("saved.txt", "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f]
    
    _song_q.extend(lines)

    return os.remove("saved.txt")

if not os.path.isdir("ext") & os.path.isfile("ext/ffplay.exe"):
    warning("FFplay를 설치 중입니다. 약간의 시간이 걸릴 수 있습니다.")
    install_ffplay()

root = Tk()
root_dpi = ctypes.windll.user32.GetDpiForWindow(root.winfo_id())
root_res = "265x265" if int(root_dpi) < 110 else "530x530"
root_res_bg = 265 if int(root_dpi) < 110 else 530
root_bg = "images/background.png" if int(root_dpi) < 110 else "images/background_high_dpi.png"
root.geometry(root_res)
root.resizable(False, False)
root.title("Plpyer")
_T_var = StringVar(value="재생중: 공기 소리")
 
_ffplay = f"{os.getcwd()}\\ext\\ffplay.exe"
_song_q = list() # _song_queue = []
_song_q_n = list() # _song_q_n = []
canvas = Canvas(root, bg="blue", height=root_res_bg, width=root_res_bg)
_img = PhotoImage(file=root_bg)
_bg = Label(root, image=_img)
_bg.place(x=0, y=0, relwidth=1, relheight=1)
_rgb_t = PIL.Image.open("images/background.png")
_rgb_img = _rgb_t.convert("RGB")
r, g, b = _rgb_img.getpixel((1, 1))

load_save()
load_skip()

select_btn = Button(root, text="음악 선택", command=select_file, bg="white", fg="black")
play_btn = Button(root, text="음악 재생", command=play_wrapper, bg="white", fg="black")
stop_btn = Button(root, text="음악 중지", command=stop, bg="white", fg="black")
list_btn = Button(root, text="목록 보기", command=song_list_, bg="white", fg="black")
skip_btn = Button(root, text="스킵 하기", command=skip, bg="white", fg="black")
song_lab = Label(root, textvariable=_T_var, bg=f"#{r:02x}{g:02x}{b:02x}", fg="white")

root.protocol("WM_DELETE_WINDOW", on_exit)

select_btn.pack()
play_btn.pack()
stop_btn.pack()
list_btn.pack()
skip_btn.pack()
song_lab.pack()
canvas.pack()
root.mainloop()
