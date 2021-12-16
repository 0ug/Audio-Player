from tkinter import *
from tkinter import filedialog, messagebox

import winsound, os, subprocess, pythread, sys, platform

print("플랫폼: {0}".format(platform.platform()))

if not sys.platform.startswith("win"):
    raise RuntimeError("Windows가 아닌 다른 플랫폼에서는 사용할 수 없습니다.")

root = Tk()
root.resizable(False, False)
root.geometry("480x480")
root.title("오디오 재생기")

def close_thread_and_exit():
    global root
    root.destroy()

    try:
        pythread.sTread("play")
    except:
        pass

    exit(1)

def select_file():
    global queue, root
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
    
    not_queue.clear()
    return print(queue)

def play_audio():
    global root, playing_text

    for files in queue:
        if str(files).endswith(".mp3"):
            if not os.path.isdir("Converted"):
                os.mkdir("Converted")
            target_file = files
            _dest = os.getcwd() + "\\Converted\\" + os.path.basename(str(files).replace("\\", os.sep).replace("mp3", "wav"))
            path = os.getcwd() + "\\external\\ffmpeg.exe"
            if not os.path.isfile(_dest):
                subprocess.call(
                    [path, "-i", files, _dest]
                )
                
            queue.remove(target_file)
            queue.append(_dest)

    for queue_ in queue:
        winsound.PlaySound(queue_, winsound.SND_FILENAME)
        playing_text.set("Now playing: {0}".format(os.path.basename(str(queue_).replace("\\", os.sep).replace(".wav", ""))))

queue = []
now_playing = ""
playing_text = StringVar(value="Now playing: None")

btn_select = Button(root, text="파일 선택하기", command=select_file)
btn_play = Button(root, text="재생하기", command=lambda: pythread.cTread("play", play_audio))
queue_list = Listbox(root, width=50, height=20)
play_label = Label(root, textvariable=playing_text)

root.protocol("WM_DELETE_WINDOW", lambda: close_thread_and_exit())
btn_play.pack()
btn_select.pack()
queue_list.pack()
play_label.pack()
root.mainloop()
