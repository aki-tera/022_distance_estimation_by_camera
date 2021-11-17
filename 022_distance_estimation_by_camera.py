import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font

import cv2
import numpy as np

import json


class Model:
    """Webcam related

    1. load webcams's config which is setting.json.
    2. set up config in the webcam.
    3. get webcam image.
    4. compute and measure.
    5. release webcam resource

    """

    def __init__(self):
        """load webcams's config which is setting.json.

        1. load setting.json.
        2. create instance variables.

        """
        # 本ソフトの設定ファイル読み込み
        self.camera_setting = json.load(open("setting.json", "r", encoding="utf-8"))
        self.camera_id = self.camera_setting["CAM"]["ID"]
        self.camera_fps = self.camera_setting["DISPLAY_RATE"]["RATE"]
        self.distance_mark = self.camera_setting["BASE_DISTANCE"]["LENGTH"]

        # カメラ設定用
        self.camera_info_parameter = [
            "", "", "", "カメラの横幅", "カメラの縦幅", "カメラのFPS", "形式",
            "", "", "", "カメラの明るさ", "カメラのコントラスト", "カメラの彩度",
            "カメラの色相", "カメラのゲイン", "カメラの露出"]
        self.camera_info_results = [999] * len(self.camera_info_parameter)

        self.distance_x = 999.0
        self.distance_y = 999.0
        self.distance_xy = 999.0

    def open_camera(self):
        """set up config in the webcam.

        1. create dictionary about AR marker DICT_4X4_50.
        2. open webcam.
        3. get webcam information.

        """
        # カメラ起動
        self.aruco = cv2.aruco
        self.dictionary = self.aruco.getPredefinedDictionary(self.aruco.DICT_4X4_50)

        # CAP_DSHOWを設定すると、終了時のterminating async callbackのエラーは出なくなる
        # ただし場合によっては、フレームレートが劇遅になる可能性あり
        # self.cap = cv2.VideoCapture(self.camera_setting["CAM"]["ID"], cv2.CAP_DSHOW)
        self.cap = cv2.VideoCapture(self.camera_setting["CAM"]["ID"])

        # self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

        # カメラのステータス確認
        for i, label in enumerate(self.camera_info_parameter):
            if label:
                self.camera_info_results[i] = self.cap.get(i)

    def release_caremra(self):
        """release webcam resource.

        """
        # カメラリソース解放
        self.cap.release()

    def compute_camera_infomations(self):
        """compute and measure.

        1. get image from webcam.
        2. detect AR markers and display id of AR markers.
        3. cut the image using four AR markers.
        4. mesure from id0 to id1

        """
        # cv2の処理をすべて実施

        # ビデオキャプチャから画像を取得
        ret, frame = self.cap.read()

        # sizeを取得
        # (縦、横、色)
        Height, Width = frame.shape[:2]

        # 処理できる形に変換
        img1 = cv2.resize(frame, (int(Width), int(Height)))

        # マーカーの検出
        corners, ids, rejectedImgPoints = self.aruco.detectMarkers(img1, self.dictionary)

        # 検出したマーカに描画する
        # イメージをコピーする
        self.img2 = np.copy(img1)
        self.aruco.drawDetectedMarkers(self.img2, corners, ids, (0, 255, 0))

        # マーカー付きの画像を小さくする
        self.img2 = cv2.resize(self.img2, (int(400), int(400 * Height / Width)))

        # ラインを引く準備
        m = np.empty((4, 2))
        x_start, y_start = 0, 0
        x_end, y_end = 0, 0

        if ids is None:
            # マーカーが無い場合
            self.img_trans = cv2.resize(frame, (600, 600))
            self.distance_x = 0.0
            self.distance_y = 0.0
            self.distance_xy = 0.0

        elif np.count_nonzero((2 <= ids) & (ids <= 6)) == 4:
            # マーカーの数が適正な場合：4個（但し、id0とid1は除く）
            for i, c in zip(ids, corners):
                # マーカーの赤丸位置を基準としている
                if 2 <= i <= 6:
                    m[i - 2] = c[0][0]

            # 変形後の画像サイズ
            trans_width, trans_height = (600, 600)

            # 変換前の座標
            # 射影変換する際、ndarrayはfloat32にする必要あり
            marker_coordinates = np.float32(m)
            # 変換後の座標ポイント
            true_coordinates = np.float32([[0, 0], [trans_width, 0], [trans_width, trans_height], [0, trans_height]])
            # 射影変換の実施して変換行列を生成
            trans_mat = cv2.getPerspectiveTransform(marker_coordinates, true_coordinates)
            # 変換行列を使って画像を変換する
            self.img_trans = cv2.warpPerspective(img1, trans_mat, (trans_width, trans_height))

            if np.count_nonzero((0 <= ids) & (ids <= 1)) == 2:
                # 変換後の画像でid検索
                corners_trans, ids_trans, rejectedImgPoints_trans = self.aruco.detectMarkers(self.img_trans, self.dictionary)
                # id(0と1)の抽出
                if ids_trans is not None:
                    for number, corner in zip(ids_trans, corners_trans):
                        if number == 0:
                            x_start, y_start = int(corner[0][0][0]), int(corner[0][0][1])
                        elif number == 1:
                            x_end, y_end = int(corner[0][0][0]), int(corner[0][0][1])
                    # id(0と1)の距離を表示
                    self.distance_x, self.distance_y = (x_end - x_start) * self.distance_mark / 600.0, (y_end - y_start) * self.distance_mark / 600.0
                    self.distance_xy = ((self.distance_x * self.distance_x + self.distance_y * self.distance_y) ** 0.5)
                    # id0とid1の間にラインを引く
                    self.img_trans = cv2.line(self.img_trans, (x_start, y_start), (x_end, y_end), (0, 0, 255), 1)
        else:
            # マーカーが0～3個場合（但し、id0とid1は除く）
            self.img_trans = cv2.resize(frame, (600, 600))
            self.distance_x = 0.0
            self.distance_y = 0.0
            self.distance_xy = 0.0


class View:
    """tkinter related

    """

    def __init__(self, master, model):
        """create widget objects

        1. setiing of font
        2. create menu objects
        3. create frames objects and others
        4. use grid()

        Args:
            master (class): main window
            model (class): Webcam related
        """
        # インスタンス化
        self.master = master
        self.model = model

        # フォントの設定
        # メニュー用
        self.font_menu = font.Font(family="Meiryo UI", size=15, weight="bold")
        # ラベルフレーム用
        self.font_frame = font.Font(family="Meiryo UI", size=15, weight="normal")
        # ラベル用
        self.font_label = font.Font(family="Meiryo UI", size=15, weight="bold")
        # ボタン用
        self.font_buttom = font.Font(family="Meiryo UI", size=20, weight="bold")

        # メニューの表示
        self.menu_bar = tk.Menu()

        # メニューの展開先の設定
        self.menu_file = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_file.add_command(label=f"カメラID:{self.model.camera_id}", font=self.font_menu)
        self.menu_file.add_command(label=f"フレームレート:{self.model.camera_fps}[FPS]", font=self.font_menu)
        self.menu_file.add_command(label=f"マーク間の距離:{self.model.distance_mark}[mm]", font=self.font_menu)
        self.menu_file.add_separator()

        # カメラ情報分
        self.menu_list_numbers = 3
        for i, label in enumerate(self.model.camera_info_parameter):
            if label:
                self.menu_file.add_command(label=f"{label}:{self.model.camera_info_results[i]}", font=self.font_menu)
                self.menu_list_numbers += 1
        
        # メニューのルート設定
        self.menu_bar.add_cascade(label="カメラ情報", menu=self.menu_file)
        # メニューの表示
        self.master.config(menu=self.menu_bar)
        # フレーム設定
        self.frame1 = tk.LabelFrame(self.master, text="元画像", font=self.font_frame)
        self.frame2 = tk.LabelFrame(self.master, text="計測距離", font=self.font_frame)
        self.frame3 = tk.Frame(self.master)
        self.frame4 = tk.LabelFrame(self.master, text="変換画像", font=self.font_frame)
        
        # c=左, r=上, s=全方向に伸ばす, p=10の隙間
        self.frame1.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N, padx=10, pady=10)
        # c=左, r=中, s=全方向に伸ばす, p=10の隙間
        self.frame2.grid(column=0, row=1, sticky=tk.E + tk.W + tk.S + tk.N, padx=10, pady=10)
        # c=左, r=下, p=10の隙間
        self.frame3.grid(column=0, row=2, padx=10, pady=10)
        # c=右, r=上, rp=3個連結, p=10の隙間
        self.frame4.grid(column=1, row=0, rowspan=3, padx=10, pady=10)
        
        # フレーム1：オリジナル画像
        self.canvas1 = tk.Canvas(self.frame1, width=400, height=300)
        # フレーム２：距離関連
        self.label211 = tk.Label(self.frame2, text=" X方向 ", font=self.font_label)
        self.label212 = tk.Label(self.frame2, text=f" {self.model.distance_x:5.1f} ", font=self.font_label)
        self.label213 = tk.Label(self.frame2, text="mm", font=self.font_label)
        self.label221 = tk.Label(self.frame2, text=" Y方向 ", font=self.font_label)
        self.label222 = tk.Label(self.frame2, text=f" {self.model.distance_y:5.1f} ", font=self.font_label)
        self.label223 = tk.Label(self.frame2, text="mm", font=self.font_label)
        self.label231 = tk.Label(self.frame2, text="  距離", font=self.font_label)
        self.label232 = tk.Label(self.frame2, text=f" {self.model.distance_xy:5.1f} ", font=self.font_label)
        self.label233 = tk.Label(self.frame2, text="mm", font=self.font_label)
        # フレーム３：ボタン
        self.button31 = tk.Button(self.frame3, text="開始", font=self.font_buttom)
        self.button32 = tk.Button(self.frame3, text="終了", font=self.font_buttom)
        # フレーム４：変換画像
        self.canvas4 = tk.Canvas(self.frame4, width=600, height=600)
        
        self.canvas1.grid(pady=20)
        # c=左1, r=上
        self.label211.grid(column=0, row=0)
        # c=左2, r=上
        self.label212.grid(column=1, row=0)
        # c=左3, r=上
        self.label213.grid(column=2, row=0)
        # c=左1, r=下
        self.label221.grid(column=0, row=1)
        # c=左2, r=下
        self.label222.grid(column=1, row=1)
        # c=左3, r=下
        self.label223.grid(column=2, row=1)
        # c=右1, r=上下
        self.label231.grid(column=3, row=0, rowspan=2)
        # c=右2, r=上下
        self.label232.grid(column=4, row=0, rowspan=2)
        # c=右3, r=上下
        self.label233.grid(column=5, row=0, rowspan=2)
        self.button31.grid(column=0, row=0, padx=20)
        self.button32.grid(column=1, row=0, padx=20)
        self.canvas4.grid()

    def update_menu_infomation(self):
        """update menu

        1. delete menu
        2. recreate menu

        """
        # メニューの更新
        # 現状のメニューを一旦削除
        self.menu_file.delete(0, self.menu_list_numbers)

        # メニューを再表示
        self.menu_file.add_command(label=f"カメラID:{self.model.camera_id}", font=self.font_menu)
        self.menu_file.add_command(label=f"フレームレート:{self.model.camera_fps}[FPS]", font=self.font_menu)
        self.menu_file.add_command(label=f"マーク間の距離:{self.model.distance_mark}[mm]", font=self.font_menu)
        self.menu_file.add_separator()
        
        for i, label in enumerate(self.model.camera_info_parameter):
            if label:
                self.menu_file.add_command(label=f"{label}:{self.model.camera_info_results[i]}", font=self.font_menu)

    def display_distance_value(self):
        """display values

        1. get values from Model class
        2. redisplay values

        """
        # 更新された距離を表示する

        # X方向
        self.label212 = tk.Label(self.frame2, text=f" {self.model.distance_x:5.1f} ", font=self.font_label)
        # Y方向
        self.label222 = tk.Label(self.frame2, text=f" {self.model.distance_y:5.1f} ", font=self.font_label)
        # 合成距離
        self.label232 = tk.Label(self.frame2, text=f" {self.model.distance_xy:5.1f} ", font=self.font_label)

        # グリッド
        self.label212.grid(column=1, row=0)
        self.label222.grid(column=1, row=1)
        self.label232.grid(column=4, row=0, rowspan=2)

    def display_image_original(self):
        """display image of original

        1. color conversion(BGR to RGB)
        2. redisplay image

        """
        # マーク付きのオリジナル画像を表示する
        self.img1 = cv2.cvtColor(self.model.img2, cv2.COLOR_BGR2RGB)
        # 複数のインスタンスがある場合、インスタンをmasterで指示しないとエラーが発生する場合がある
        # エラー内容：image "pyimage##" doesn't exist
        self.im1 = ImageTk.PhotoImage(image=Image.fromarray(self.img1), master=self.frame1)
        self.canvas1.create_image(0, 0, anchor='nw', image=self.im1)

    def display_image_translation(self):
        """display image of translation

        1. color conversion(BGR to RGB)
        2. redisplay image

        """

        # マーク内の変換画像を表示する
        self.img4 = cv2.cvtColor(self.model.img_trans, cv2.COLOR_BGR2RGB)
        # 複数のインスタンスがある場合、インスタンをmasterで指示しないとエラーが発生する場合がある
        # エラー内容：image "pyimage##" doesn't exist
        self.im4 = ImageTk.PhotoImage(image=Image.fromarray(self.img4), master=self.frame4)
        self.canvas4.create_image(0, 0, anchor='nw', image=self.im4)


class Controller():
    """controller related

    """
    def __init__(self, master, model, view):
        """create instances

        Args:
            master (class): main window
            model (class): Webcam related
            view (class): tkinter related
        """
        # インスタンス化
        self.master = master
        self.model = model
        self.view = view

        # カメラの起動有無のフラグ設定
        self.is_open_camera = False

    def request_camera_open(self):
        """start webcam

        1. open webcam
        2. start to get image
        3. redisplay webcam information

        """
        # カメラの起動
        self.model.open_camera()
        # カメラ起動のON
        self.is_open_camera = True

        # メニューの更新
        self.view.update_menu_infomation()

    def request_camera_results(self):
        """control to display images and others

        1. compute webcam image
        2. display values and images
        3. execute after method

        """
        # 各種の表示をここで一括して行う

        # カメラ処理（画像取得、距離取得）の実施
        # Moldeクラス
        self.model.compute_camera_infomations()

        # 数値出力
        # Viewクラス
        self.view.display_distance_value()

        # 画像取得
        # Viewクラス
        self.view.display_image_original()
        self.view.display_image_translation()

        # 繰り返し動作
        self.master.after(int(1000 / self.model.camera_fps), self.request_camera_results)

    def press_start_button(self):
        """when start button is pressed

        1. don't execute if it's the second time and later.

        """
        # 初回のみカメラを起動
        # 初回のみ結果取得を実行して、あとはafterメソッドで対応する
        if self.is_open_camera is False:
            self.request_camera_open()
            # カメラの結果を取得
            self.request_camera_results()

    def press_close_button(self):
        """Terminate all

        1. destroy widgets
        2. relase webcam resource

        """
        # 終了処理

        # ウイジェットの終了
        self.master.destroy()
        # カメラリソース解放
        if self.is_open_camera is True:
            self.model.release_caremra()


class Application(tk.Frame):
    """main routine

    1. create tkinter
    2. set window
    3. create class object
    4. set buttom command

    Args:
        tk (class): root of tkinter

    """
    def __init__(self, master):
        """start instance

        Args:
            master  (class): main
        """
        # tkinterの定型文
        super().__init__(master)
        self.grid()
        
        # インスタンス化
        self.model = Model()
        
        master.geometry()
        master.title("カメラによる計測アプリ")

        # ウインドウサイズの変更不可
        master.resizable(width=False, height=False)

        # インスタンス化
        self.view = View(master, self.model)
        self.controller = Controller(master, self.model, self.view)

        # ボタンのコマンド設定
        self.view.button31["command"] = self.controller.press_start_button
        self.view.button32["command"] = self.controller.press_close_button


def main():
    win = tk.Tk()
    app = Application(master=win)
    app.mainloop()


if __name__ == "__main__":
    main()
