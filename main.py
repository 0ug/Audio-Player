from tkinter import *
from tkinter import filedialog, messagebox

import winsound, os, subprocess, pythread, sys, shutil

from io import BytesIO
from requests import get
from zipfile import ZipFile

def purge():
    global root
    root.withdraw()

    winsound.PlaySound(None, winsound.SND_FILENAME)
    exit()

def install_ffmpeg():
    if not os.path.isdir("external"):
        os.mkdir("external")
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")
    response = get("https://github.com/GyanD/codexffmpeg/releases/download/4.4.1/ffmpeg-4.4.1-essentials_build.zip")
    zipper = ZipFile(BytesIO(response.content))
    zipper.extractall("tmp")
    shutil.move("tmp/ffmpeg-4.4.1-essentials_build/bin/ffmpeg.exe", "external/ffmpeg.exe")
    shutil.rmtree("tmp")

if not os.path.isfile("external/ffmpeg.exe"):
    install_ffmpeg()

if not sys.platform.startswith("win"):
    raise RuntimeError("Windows가 아닌 다른 플랫폼에서는 사용할 수 없습니다.")

root = Tk()
root.resizable(False, False)
root.geometry("480x480")
root.title("오디오 재생기")

def select_file():
    global queue, queue_list
    not_queue = []
    not_queue.append(queue)
    file = filedialog.askopenfilename()

    if file == "":
        return

    if not file.endswith("mp3") or file.endswith("wav"):
        return messagebox.showerror("오류", "확장자는 mp3와 wav 파일만 지원합니다.")

    if file in queue:
        return messagebox.showerror("오류", "이미 목록에 있습니다.")

    if not queue_list.get(0, END) == ():
        queue_list.delete(0, END)

    queue.append(file)
    for files in queue:
        for i in range(len(not_queue)):
            queue_list.insert(i, files)
    
    return not_queue.clear()

def play_audio():
    global queue, now_playing
    
    if os.path.isdir("Converted"):
        shutil.rmtree("Converted")

    number = 0

    while True:
        if number >= len(queue):
            break

        if str(queue[number]).endswith(".mp3"):
            if not os.path.isdir("Converted"):
                os.mkdir("Converted")

            dest = os.getcwd() + "\\Converted\\" + os.path.basename(str(queue[number]).replace("\\", os.sep).replace("mp3", "wav"))
            path = os.getcwd() + "\\external\\ffmpeg.exe"
            if not os.path.isfile(dest):
                subprocess.call(
                    [path, "-i", queue[number], dest]
                )

            number += 1

    queue.clear()
    for files in os.listdir("Converted"):
        if files.endswith(".wav"):
            queue.append(os.getcwd() + "\\Converted\\" + files)
    
    for x in queue:
        now_playing.set("Now playing: " + os.path.basename(str(x).replace("\\", os.sep)))
        try:
            winsound.PlaySound(x, winsound.SND_ASYNC)
        except PermissionError: pass

queue = []
now_playing = StringVar(value="Now playing: None")

btn_select = Button(root, text="파일 선택하기", command=select_file)
btn_play = Button(root, text="재생하기", command=lambda: pythread.cTread("play", play_audio))
queue_list = Listbox(root, width=50, height=20)
now_play_lab = Label(root, textvariable=now_playing)

root.protocol("WM_DELETE_WINDOW", purge)
btn_play.pack()
btn_select.pack()
queue_list.pack()
now_play_lab.pack()
root.mainloop()
