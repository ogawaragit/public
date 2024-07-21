import tkinter as tk
from PIL import Image, ImageTk
import cv2
from pyzbar import pyzbar
import os


# QRコードデータの処理を行う関数
def process_qr_data(qr_data):
    global current_file, current_splits, total_splits
    try:
        header, *data = qr_data.splitlines()
        file_name, split_info = header.split(' ')
        split_index, split_total = map(int, split_info.split('/'))

        # 適切なQRコードの場合のみ処理
        if file_name and split_index <= split_total:
            # 最初のQRコードを受け入れる
            if current_file is None and split_index == 1:
                accept_qr_data(file_name, split_index, split_total, data)
            # 次の分割番号のQRコードを受け入れる
            elif file_name == current_file and split_index == max(current_splits) + 1:
                accept_qr_data(file_name, split_index, split_total, data)
    except ValueError:
        # QRコードのデータが期待される形式でない場合は無視
        return


# QRコードデータを受け入れる関数
def accept_qr_data(file_name, split_index, split_total, data):
    global current_file, current_splits, total_splits
    if split_index == 1:
        # 分割番号が1の場合、新しいファイルを生成（または上書き）
        current_file = file_name
        current_splits = {split_index}
        total_splits = split_total
        save_file(file_name, data, mode='w')  # 新規作成または上書き
    else:
        # 分割番号が連続する場合、ファイルに追記
        current_splits.add(split_index)
        save_file(file_name, data, mode='a')  # 追記
    update_listbox(file_name, split_index)
    if len(current_splits) == total_splits:
        reset_reading()
        status_label.config(text=f"ファイル '{file_name}' の読み込みが完了し保存されました")


# ファイルを保存する関数
def save_file(file_name, data, mode='w'):
    save_directory = 'Saved_Files'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    file_path = os.path.join(save_directory, file_name)
    with open(file_path, mode, encoding='shift_jis') as file:
        file.write('\n'.join(data) + '\n')


# リストボックスを更新する関数
def update_listbox(file_name, split_index):
    listbox.insert(tk.END, f"{file_name} {split_index}/{total_splits}")
    listbox.see(tk.END)


# カメラから映像を更新する関数
def update_video():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
        decoded_objects = pyzbar.decode(frame)
        for obj in decoded_objects:
            try:
                qr_data = obj.data.decode('shift_jis')  # Shift-JISとしてデコード
                process_qr_data(qr_data)
            except UnicodeDecodeError:
                try:
                    qr_data = obj.data.decode('utf-8')  # utf-8としてデコード
                    process_qr_data(qr_data)
                except UnicodeDecodeError:
                    status_label.config(
                        text="デコードに失敗しました。QRコードを再スキャンしてください。")
            break
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
    root.after(10, update_video)


# 読み取りをリセットする関数
def reset_reading():
    global current_file, current_splits, total_splits
    current_file = None
    current_splits.clear()
    total_splits = 0
    listbox.delete(0, tk.END)
    status_label.config(text="QRコードのスキャンをリセットしました。")


# ウィンドウの初期化
root = tk.Tk()
root.title("QR Code Scanner")

# カメラデバイスの初期化
cap = cv2.VideoCapture(0)

# データリストの初期化
current_file = None
current_splits = set()
total_splits = 0

# ラベルとリストボックスの初期化
lbl_video = tk.Label(root)
lbl_video.pack()

listbox = tk.Listbox(root, width=40, height=15)
listbox.pack()

# ステータスラベルの初期化
status_label = tk.Label(root, text="QRコードをスキャンしてください。")
status_label.pack()

# 読み取りリセットボタンの初期化
reset_button = tk.Button(root, text="読み取りをリセットする", command=reset_reading)
reset_button.pack()

# 映像更新の開始
update_video()

# ウィンドウのメインループ
root.mainloop()

# ウィンドウが閉じられたらカメラリリース
cap.release()
