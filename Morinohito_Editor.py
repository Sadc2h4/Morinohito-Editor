import os
import os.path
import tkinter as tk
from tkinter import filedialog,Toplevel,messagebox,ttk
from tkinter.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageDraw
import cv2
from moviepy.editor import *

# グローバル変数として定義
PREVIEW_W, PREVIEW_H = 120, 80
preview_canvas = None

# Pillow 10対応: ANTIALIAS 等は削除されたため互換定数を用意
try:
    RESAMPLE = Image.Resampling.LANCZOS  # Pillow >= 9.1
except Exception:
    RESAMPLE = getattr(Image, "LANCZOS", Image.BICUBIC)  # Pillow < 10 fallback

#ビデオ参照ボタンを押した際の処理
def show_video_dialog():
    # ファイルダイアログを表示し、ビデオファイルを選択
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4"),("gif Files", "*.gif"),("mkv Files", "*.mkv")])
    get_video_duration()
#=====================================================================
#ファイルがドラッグ&ドロップされた際の処理
def File_Drop(event):
    try:
        global video_path
        video_path = event.data
        video_path = video_path.replace('{', '').replace('}', '')
        
        video_name, video_extension = os.path.splitext(video_path)

        if video_extension == ".mp4":
            get_video_duration()
        elif video_extension == ".gif":
            get_video_duration()
        elif video_extension == ".mkv":
            get_video_duration()
        else:
            raise RuntimeError("ウワァ！ びっくりしたァ!?\nこのツールはmp4,gif,mkvにしか対応してないんだから\nもっと説明をよく見て使ってくれないかナ…")
    except Exception as e:
        messagebox.showerror("出力エラー", f"もう疲れちゃってェ…全然動けなくってェ…\n このエラーを直してほしいなぁって…\n\n{str(e)}")
        
#=====================================================================
#ビデオファイル参照共通処理
def get_video_duration():
    global capture,fps
    if video_path: 
        textBox1.delete(0, tk.END)# 既存のテキストを削除
        textBox1.insert(tk.END,video_path) #文字列更新

        wd = os.path.dirname(__file__)
        capture = cv2.VideoCapture(video_path)
        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        capture.release()

        #シークバーの最大値を更新
        scale.configure(to=duration)
        scale["state"]="normal" #シークバーをアクティブにする
        button2["state"]="normal" #選択フレーム参照ボタンをアクティブにする
        button3["state"]="normal" #開始時間に反映ボタンをアクティブにする
        button4["state"]="normal" #終了時間に反映ボタンをアクティブにする

        global preview_canvas
        try:
            if preview_canvas and preview_canvas.winfo_exists():
                preview_canvas.destroy()
                
                selected_value.set(0)
                label4.config(text=" 0")
                scale.set(0)                 # シークバー値も同期
                display_frame("0")           # 0 秒のフレームを描画
        except NameError:
            # まだ preview_canvas が作られていない初回起動などはパスする
            pass

#=====================================================================
#シークバーで選択された数値をラベルで表示
def display_frame(value):
    # ラベルと内部値を同期
    label4.config(text=f" {value}")
    selected_value.set(value)

    video_path = textBox1.get()
    cap = cv2.VideoCapture(video_path)
    if not cap or not cap.isOpened():
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    # Scaleの現在値からフレーム番号算出（valueは文字列のことがある）
    try:
        selected_second = float(scale.get())
    except Exception:
        selected_second = float(value)
    frame_number = max(0, int(selected_second * fps))

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret or frame is None:
        cap.release()
        return

    # プレビュー用に縮小
    frame = cv2.resize(frame, (PREVIEW_W, PREVIEW_H))

    # OpenCV(BGR) → PIL(RGB) → Tk画像
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    photo = ImageTk.PhotoImage(image=image)

    # 初回だけプレビュ－用ラベルを配置
    if not label6.winfo_ismapped():
        label6.place(x=480, y=20)

    # （プレースホルダCanvas方式なら）残っていたら消す
    try:
        if preview_canvas and preview_canvas.winfo_exists():
            preview_canvas.destroy()
    except NameError:
        pass

    # プレビュー画像を表示（参照保持も）
    label6.config(image=photo)
    label6.photo = photo

    cap.release()

#=====================================================================
def get_video_frame():
    video_path = textBox1.get()

    # --- 現在のフレームをメモリ上で取得 ---
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    target_second = scale.get()         # 現在選択中の秒
    target_frame = int(fps * target_second)
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        messagebox.showerror("エラー", "選択フレームの取得に失敗しました。")
        return

    # OpenCV(BGR) → PIL(RGB) に直接変換（ディスクに書かない）
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # --- サブウィンドウ生成 ---
    subwindow = Toplevel(window)
    subwindow.title("トリミングエリア指定")
    substatus_bar_var = tk.StringVar(value="")
    substatus_bar = tk.Label(subwindow, textvariable=substatus_bar_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    substatus_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # 表示倍率（1/2チェック）
    global magnification
    magnification = 2 if var1.get() else 1
    w, h = image.size
    w //= magnification
    h //= magnification
    image = image.resize((w, h), RESAMPLE)
    
    # キャンバス＆画像表示
    tk_img = ImageTk.PhotoImage(image, master=subwindow)
    info_label = tk.Label(subwindow, text="※マウスで画面をドラッグするとメインウィンドウに座標が取得・記載されます", font=("MSゴシック", 10, "bold"))
    info_label.place(x=10, y=0)

    canvas = tk.Canvas(subwindow, width=w, height=h)
    canvas.place(x=10, y=20)
    canvas.create_image(w//2, h//2, image=tk_img, anchor=tk.CENTER)
    canvas.image = tk_img           # << 参照保持（重要）
    subwindow.geometry(f"{w+20}x{h+50}")

    # グリッド描画
    def draw_grid(event=None):
        if not var2.get():
            return
        canvas.delete("grid")
        for i in range(0, w, 10):
            canvas.create_line(i, 0, i, h, fill="gray", stipple="gray50", tags="grid")
        for i in range(0, h, 10):
            canvas.create_line(0, i, w, i, fill="gray", stipple="gray50", tags="grid")

    # ドラッグで矩形取得
    start = {"x": 0, "y": 0}
    def on_press(e):
        # 以前の矩形があれば消す
        lecval = label5.cget('text')
        if lecval != '--':
            try:
                canvas.delete(int(lecval))
            except Exception:
                pass
        start["x"], start["y"] = e.x, e.y

    def on_release(e):
        sx, sy = start["x"], start["y"]
        ex, ey = e.x, e.y
        # 10の位へ丸めて、左上右下に正規化
        sx, sy, ex, ey = [round(v, -1) for v in (sx, sy, ex, ey)]
        if ex <= sx: sx, ex = ex, sx
        if ey <= sy: sy, ey = ey, sy

        rect_id = canvas.create_rectangle(sx, sy, ex, ey, outline="red", fill="red", stipple="gray50")
        label9.config(text=f'X: {sx * magnification}, Y: {sy * magnification}')
        label11.config(text=f'X: {ex * magnification}, Y: {ey * magnification}')
        label5.config(text=str(rect_id))

        # 以降のcropで使う座標をグローバルに保存（表示は1/2だが値は実座標に換算）
        global rnd_start_x, rnd_start_y, rnd_end_x, rnd_end_y
        rnd_start_x, rnd_start_y, rnd_end_x, rnd_end_y = sx, sy, ex, ey

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<ButtonRelease-1>", on_release)
    canvas.bind("<Configure>", draw_grid)
    draw_grid()  # 初期描画

    # ※ ここで subwindow のみを開く。二重 mainloop は回さない！
    # subwindow.transient(window)  # （任意）親ウィンドウの前面に
    # subwindow.grab_set()         # （任意）モーダル化したい場合

#=====================================================================
#読込動画をトリミングして出力
def Create_Trimming_Video():
    video_path = textBox1.get()
    filename = video_path.split('/')[-1]
    filename, file_extension = os.path.splitext(filename)
    filename = os.path.basename(filename)
    directory = os.path.dirname(video_path)
    
    save_path = directory + '\\' + filename + "trimed_" + textBox2.get() + "to" + textBox3.get() + ".mp4"

    try:
        #1の桁が0以外の場合、VideoFileClip処理がなぜかうまく機能しないので注意
        #1/2表示の際は実際よりも2倍の数値にして出力させる
        if label9.cget('text') == '--':
            #座標指定なしの場合はそのままトリミングを開始
            video = (VideoFileClip(video_path)
            .subclip(int(textBox2.get()), int(textBox3.get()) )
            )
        else:
            video = (VideoFileClip(video_path)
            .subclip(int(textBox2.get()), int(textBox3.get()) )
            .crop(x1=rnd_start_x*magnification, y1=rnd_start_y*magnification, x2=rnd_end_x*magnification, y2=rnd_end_y*magnification)
            )
        video.write_videofile(save_path, fps=fps, logger=None) #保存
        messagebox.showinfo("処理完了", "出力完了!")

    except Exception as e:
        messagebox.showerror("出力エラー", f"もう疲れちゃってェ…全然動けなくってェ…\n このエラーを直してほしいなぁって…\n\n{str(e)}")


#=====================================================================
#選択中のフレームの数字を開始時間テキストボックスに反映
def set_start_time():
    textBox2.delete(0, tk.END)  # テキストボックスの内容をクリア
    textBox2.insert(0,scale.get())
    button5["state"]="normal" #時間を指定しないと処理開始ボタンがをアクティブにしない
    
    status_bar_var.set('')  #記載内容を一旦削除
    
#=====================================================================
#選択中のフレームの数字を終了時間テキストボックスに反映
def set_end_time():
    textBox3.delete(0, tk.END)  # テキストボックスの内容をクリア
    textBox3.insert(0,scale.get())
    status_bar_var.set('') 
    
    if int(textBox3.get()) - int(textBox2.get()) <= 0:
        textBox3.delete(0, tk.END)
        status_bar_var.set('開始時間より早い時間を指定することは出来ないよｫ…')
        button5["state"]="disabled" 
        return

    button5["state"]="normal" #時間を指定しないと処理開始ボタンがをアクティブにしない

#=====================================================================
#左右のキーでシークバーを操作する為の処理
def on_key(event):
    # キーイベントからキーの名前を取得
    key = event.keysym

    # 左キーが押された場合、Scaleの値を減少
    if key == 'Left':
        current_value = scale.get()
        scale.set(current_value - 1)

    # 右キーが押された場合、Scaleの値を増加
    elif key == 'Right':
        current_value = scale.get()
        scale.set(current_value + 1)
    
    #左右以外の場合はスルーする
    else:
        return

    #ラベルに現在選択中の数値を反映する
    label4.config(text=f" {current_value}")
    selected_value.set(current_value)  # 変数に選択された値を格納

#=====================================================================
def resource_path(rel_path: str) -> str:
    # PyInstaller: _MEIPASS（onefile の一時展開先 or onedir のルート）
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)
    # 通常のスクリプト実行時
    return os.path.join(os.path.dirname(__file__), rel_path)

#=====================================================================
# UIを作成
# https://flytech.work/blog/16310/
cwd = os.path.dirname(__file__)
window = TkinterDnD.Tk()

window.title('Morinohito Editor')
window.geometry('620x200')

iconfile = resource_path("Kolog_icon.ico")
window.iconbitmap(default=iconfile)

#----------------------------------------------
#動画ファイル参照エリア
label1 = tk.Label(text='※対応拡張子はmp4,gif,mkvです．参照後に確認するフレームを選択してください．')
label1.place(x= 10, y=5)

label2 = tk.Label(text='参照動画ファイルを選択：')
label2.place(x= 10, y=28)

textBox1 = tk.Entry(width=48)
textBox1.place(x= 140, y=30)

button1 = tk.Button(window, text="選択", command=show_video_dialog)
button1.place(x= 430, y=26)
#----------------------------------------------

#----------------------------------------------
#シークバー表示エリア
#https://daeudaeu.com/tkinter-scale/

label3 = tk.Label(text='フレーム(秒)の指定：')
label3.place(x= 10, y=60)

# 変数を作成して初期値を設定
selected_value = tk.IntVar()
selected_value.set(0)  # 初期値を0に設定

#シークバーを作成して操作時に[display_frame]の処理を実行、プレビューに画像を表示
scale = tk.DoubleVar()
scale = tk.Scale(window, 
                from_=0, 
                to=0, 
                orient="horizontal", 
                showvalue=False,
                variable=scale ,
                length=293 ,
                command=display_frame,
                state="disabled"
                )
scale.place(x= 137, y=60)

# シークバーの選択中数値表示を作成
label4 = tk.Label(window, text=" 0",font=("MSゴシック", "14", "bold"))
label4.place(x= 430, y=57)
#label3.config(text=f" {xxxx}") #ラベルの表示更新方法テンプレート
#https://office54.net/python/tkinter/python-tkinter-label

label5 = tk.Label(text='--')
label5.place(x= 480, y=20)

# プレースホルダ（Unloaded）をコードで描画：四角＋文字

# プレースホルダ Canvas（四角＋文字）
preview_canvas = tk.Canvas(
    window, width=PREVIEW_W, height=PREVIEW_H,
    bg="lightslategray", highlightthickness=0  # ← 外枠を消す
)
preview_canvas.place(x=480, y=20)
preview_canvas.create_rectangle(1, 1, PREVIEW_W-2, PREVIEW_H-2,
                                outline="gray")
preview_canvas.create_text(PREVIEW_W//2, PREVIEW_H//2,
                            text="Unloaded",
                            font=("MSゴシック", 10, "bold"),
                            fill="linen")

# プレビュー画像用ラベルは作るだけ（まだ置かない）
label6 = tk.Label(window, bd=0, highlightthickness=0)

# フレーム指定ボタン
button2 = tk.Button(window, text="選択フレームを参照", command=get_video_frame,state="disabled")
button2.place(x= 140, y=85)


#----------------------------------------------

#----------------------------------------------
#座標・時間指定エリア
label8 = tk.Label(text='始点座標：')
label8.place(x= 140, y=120)

label9 = tk.Label(text='--')
label9.place(x= 205, y=120)

label10 = tk.Label(text='終端座標：')
label10.place(x= 140, y=145)

label11 = tk.Label(text='--')
label11.place(x= 205, y=145)

label12 = tk.Label(text='トリミング開始時間：')
label12.place(x= 290, y=120)

label13 = tk.Label(text='トリミング終了時間：')
label13.place(x= 290, y=145)

# チェックボックス1の状態を格納する変数
var1 = tk.BooleanVar()
# チェックボックス1を作成
checkbox1 = tk.Checkbutton(window, text="1/2サイズで表示", variable=var1)
checkbox1.place(x= 250, y=85)

# チェックボックスの状態を格納する変数
var2 = tk.BooleanVar()
# サブウィンドウチェックボックスを作成
subcheckbox1 = tk.Checkbutton(window, text="グリッド有で表示", variable=var2)
subcheckbox1.place(x= 360, y=85)

#トリミング時間指定
textBox2 = tk.Entry(width=5)
textBox2.insert(tk.END,'0') #文字列更新
textBox2.place(x= 395, y=120)

textBox3 = tk.Entry(width=5)
textBox3.insert(tk.END,'0') #文字列更新
textBox3.place(x= 395, y=145)

button3 = tk.Button(window, text="反映", command=set_start_time,state="disabled")
button3.place(x= 430, y=116)

button4 = tk.Button(window, text="反映", command=set_end_time,state="disabled")
button4.place(x= 430, y=141)

#トリミング開始処理ボタン
button5 = tk.Button(window, text="トリミング開始", fg="red" ,width=15, height=2,command=Create_Trimming_Video,state="disabled")
button5.place(x= 483, y=115)

#----------------------------------------------
# ステータスバー用の変数を作成
status_bar_var = tk.StringVar()
status_bar_var.set("")
# ステータスバーを作成
status_bar = tk.Label(window, textvariable=status_bar_var, fg="red", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

#画面上でのイベント設定
window.bind("<KeyPress>", on_key)

#ドラッグ&ドロップ設定
window.drop_target_register(DND_FILES)
window.dnd_bind('<<Drop>>', File_Drop)

# UIを表示
window.mainloop()