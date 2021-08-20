import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font

import cv2
import numpy as np

import json


# PEP8に準拠するとimportが先頭に行くので苦肉の策
while True:
    import sys
    sys.path.append("../000_mymodule/")
    import logger
    from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
    break


class Model:
    log = logger.Logger("Model", level=DEBUG)

    def __init__(self):
        self.log.debug("__init__")
        self.distance_x = 999.0
        self.distance_y = 999.0
        self.distance_xy = 999.0

    def camera_open(self, camera_setting):
        # カメラ起動
        self.log.debug("camera_open")

        self.camera_setting = camera_setting

        self.aruco = cv2.aruco
        self.dictionary = self.aruco.getPredefinedDictionary(self.aruco.DICT_4X4_50)

        self.cap = cv2.VideoCapture(self.camera_setting["CAM"]["ID"])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_setting["CAM"]["WIDTH"])
    
    def caremra_release(self):
        # カメラリソース解放
        self.log.debug("camera_release")
        self.cap.release()

    def create_camera_infomations(self):
        # cv2の処理をすべて実施
        self.log.debug("create_camera_infomations")

        # ビデオキャプチャから画像を取得
        ret, frame = self.cap.read()

        self.log.debug(ret)

        # sizeを取得
        # (縦、横、色)

        Height, Width = frame.shape[:2]

        img0 = cv2.resize(frame, (int(200), int(200 * Height / Width)))
        img1 = cv2.resize(frame, (int(Width), int(Height)))

        # 検出
        corners, ids, rejectedImgPoints = self.aruco.detectMarkers(img1, self.dictionary)

        # 検出したマーカに描画する
        # イメージをコピーする
        self.img2 = np.copy(img1)
        self.aruco.drawDetectedMarkers(self.img2, corners, ids, (0, 255, 0))
        self.img2 = cv2.resize(self.img2, (int(400), int(400 * Height / Width)))

        self.log.debug(f"x:400 y:{int(400* Height / Width)}")

        m = np.empty((4, 2))

        self.log.debug(ids)
        self.log.debug(type(ids))

        # ラインを引く準備
        x_start, y_start = 0, 0
        x_end, y_end = 0, 0

        if ids is None:
            img_trans = cv2.resize(frame, (600, 600))
            self.log.debug("None")
        elif np.count_nonzero((2 <= ids) & (ids <= 6)) == 4:
            self.log.debug("Number is 4")
            for i, c in zip(ids, corners):
                # マーカーの赤丸位置を基準としている
                if 2 <= i <= 6:
                    self.log.debug(c)
                    m[i - 2] = c[0][0]

            # 変形後の画像サイズ
            trans_width, trans_height = (600, 600)

            marker_coordinates = np.float32(m)
            true_coordinates = np.float32([[0, 0], [trans_width, 0], [trans_width, trans_height], [0, trans_height]])
            trans_mat = cv2.getPerspectiveTransform(marker_coordinates, true_coordinates)
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
                    self.log.debug(x_start)
                    self.log.debug(y_start)
                    self.log.debug(x_end)
                    self.log.debug(y_end)
                    # id(0と1)の距離を表示
                    self.distance_x, self.distance_y = (x_end - x_start), (y_end - y_start)
                    self.log.info(self.distance_x)
                    self.log.info(self.distance_y)
                    self.distance_xy = ((self.distance_x * self.distance_x + self.distance_y * self.distance_y) ** 0.5) * 135 / 600
                    self.log.info(self.distance_xy)

                    cv2.line(self.img_trans, (x_start, y_start), (x_end, y_end), (0, 0, 255), 1)

        else:
            self.log.debug("others")
            self.img_trans = cv2.resize(frame, (600, 600))
            self.distance_x = 0.0
            self.distance_y = 0.0
            self.distance_xy = 0.0
            


class View:
    log = logger.Logger("View", level=DEBUG)

    def __init__(self, master, model):
        self.log.debug("__init__")

        self.master = master
        self.model = model

        # フォントの設定
        self.log.debug("フォントの設定")
        # ラベルフレーム用
        self.font_frame = font.Font(family="Meiryo UI", size=15, weight="normal")
        # ラベル用
        self.font_label = font.Font(family="Meiryo UI", size=15, weight="bold")
        # ボタン用
        self.font_buttom = font.Font(family="Meiryo UI", size=20, weight="bold")

        self.log.debug("フレームの設定")
        self.frame1 = tk.LabelFrame(self.master, text="元画像", font=self.font_frame)
        self.frame2 = tk.LabelFrame(self.master, text="計測距離", font=self.font_frame)
        self.frame3 = tk.Frame(self.master)
        self.frame4 = tk.LabelFrame(self.master, text="変換画像", font=self.font_frame)

        self.log.debug("グリッドの設定")
        # c=左, r=上, s=全方向に伸ばす, p=10の隙間
        self.frame1.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N, padx=10, pady=10)
        # c=左, r=中, s=全方向に伸ばす, p=10の隙間
        self.frame2.grid(column=0, row=1, sticky=tk.E + tk.W + tk.S + tk.N, padx=10, pady=10)
        # c=左, r=下, p=10の隙間
        self.frame3.grid(column=0, row=2, padx=10, pady=10)
        # c=右, r=上, rp=3個連結, p=10の隙間
        self.frame4.grid(column=1, row=0, rowspan=3, padx=10, pady=10)

        self.log.debug("各フレームの内部詳細")
        # フレーム1：オリジナル画像
        self.canvas1 = tk.Canvas(self.frame1, width=400, height=225)
        # フレーム２：距離関連
        self.label211 = tk.Label(self.frame2, text=" X方向 ", font=self.font_label)
        self.label212 = tk.Label(self.frame2, text=f" {self.model.distance_x:5.1f} ", font=self.font_label)
        self.label213 = tk.Label(self.frame2, text="mm", font=self.font_label)
        self.label221 = tk.Label(self.frame2, text=" Y方向 ", font=self.font_label)
        self.label222 = tk.Label(self.frame2, text=f" {self.model.distance_y:5.1f} ", font=self.font_label)
        # self.label222 = tk.Label(self.frame2, text="          ", font=self.font_label)
        self.label223 = tk.Label(self.frame2, text="mm", font=self.font_label)
        self.label231 = tk.Label(self.frame2, text="  距離", font=self.font_label)
        self.label232 = tk.Label(self.frame2, text=f" {self.model.distance_xy:5.1f} ", font=self.font_label)
        self.label233 = tk.Label(self.frame2, text="mm", font=self.font_label)
        # フレーム３：終了ボタン
        self.button31 = tk.Button(self.frame3, text="開始", font=self.font_buttom)
        self.button32 = tk.Button(self.frame3, text="終了", font=self.font_buttom)
        # フレーム４：変換画像
        self.canvas4 = tk.Canvas(self.frame4, width=600, height=600)

        self.log.debug("各フレームの内部グリッド")
        self.canvas1.grid()
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

    def display_distance_value(self):
        self.log.debug("display_distance_value")

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
        self.img1 = Image.open("test001.png")
        # 複数のインスタンスがある場合、インスタンをmasterで指示しないとエラーが発生する場合がある
        # エラー内容：image "pyimage##" doesn't exist
        self.im1 = ImageTk.PhotoImage(image=self.img1, master=self.frame1)
        self.canvas1.create_image(0, 0, anchor='nw', image=self.im1)

        self.img4 = Image.open("test002.png")
        # 複数のインスタンスがある場合、インスタンをmasterで指示しないとエラーが発生する場合がある
        # エラー内容：image "pyimage##" doesn't exist
        self.im4 = ImageTk.PhotoImage(image=self.img4, master=self.frame4)
        self.canvas4.create_image(0, 0, anchor='nw', image=self.im4)


class Controller():
    log = logger.Logger("Controller", level=DEBUG)

    def __init__(self, master, model, view):
        self.log.debug("__init__")

        # インスタンス化
        self.master = master
        self.model = model
        self.view = view

        # カメラの起動有無
        self.camera_open = False
        # 起動するカメラの設定
        self.camera_setting = json.load(open("setting.json", "r", encoding="utf-8"))
        self.log.debug(str(self.camera_setting))


    def request_camera_open(self):
        self.log.debug("request_camera_open")
        # 1回目のみカメラ起動
        # Model
        self.log.debug(f"camera_open:{str(self.camera_open)}")
        if self.camera_open is False:
            self.log.debug("初回のカメラ起動")
            self.model.camera_open(self.camera_setting)
            self.camera_open = True

    def request_camera_results(self):
        self.log.debug("request_camera_view")

        # カメラ処理（画像取得、距離取得）の実施
        # Moldeクラス
        self.model.create_camera_infomations()

        # 画像取得
        # Viewクラス
        self.view.display_distance_value()

        # 数値出力
        # Viewクラス

        # 繰り返し動作
        self.master.after(100, self.request_camera_results)


    def press_start_button(self):
        self.log.debug("press_start_button")

        # カメラの起動
        self.request_camera_open()

        # カメラの結果を取得
        self.request_camera_results()



    def press_close_button(self):
        self.log.debug("press_close_button")
        self.master.destroy()
        # カメラリソース解放
        self.model.caremra_release()
        
        self.log.debug("終了")




class Application(tk.Frame):
    log = logger.Logger("Application", level=DEBUG)

    def __init__(self, master):
        # tkinterの定型文

        self.log.debug("__init__")
        super().__init__(master)
        self.grid()

        self.log.debug("Modelのインスタンス化")
        self.model = Model()

        self.log.debug("ウインドウ作成")
        master.geometry("1060x660")
        master.title("カメラによる計測アプリ")

        self.log.debug("Viewのインスタンス化")
        self.view = View(master, self.model)

        self.log.debug("Controllerのインスタンス化")
        self.controller = Controller(master, self.model, self.view)

        self.log.debug("ボタンの登録")
        self.view.button31["command"] = self.controller.press_start_button
        self.view.button32["command"] = self.controller.press_close_button
        


def main():
    win = tk.Tk()
    app = Application(master=win)
    app.mainloop()


if __name__ == "__main__":
    main()

# 参考資料

# 【Python】Tkinterを使った雛形（MVCモデル）
# https://qiita.com/michimichix521/items/8687962247cae41625f7

# python: サンプルプログラムでMVCモデルの構成を掴む
# https://moimoiblog.com/programing/python-mvcmodel-study/

# Tkinter GUIアプリケーションの部品 (widgets) をウィンドウ上にどうやって配置するのだろう - 3つのジオメトリマネージャー
# https://cassiopeia.hatenadiary.org/entry/20070905/1189023758

# 【Python】Tkinterのcanvasを使ってみる
# https://qiita.com/nnahito/items/2ab3ad0f3adacc3314e6

# PythonでGUIに画像を表示する
# https://water2litter.net/rum/post/python_tkinter_canvas_create_image/

# 【Python tkinter】LabelFrame（ラベルフレーム）ウィジェットの使い方
# https://office54.net/python/tkinter/python-tkinter-labelframe
