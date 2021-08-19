import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font


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
        self.label211 = tk.Label(self.frame2, text="　X方向　", font=self.font_label)
        self.label212 = tk.Label(self.frame2, text="0.0", font=self.font_label)
        self.label213 = tk.Label(self.frame2, text="mm", font=self.font_label)
        self.label221 = tk.Label(self.frame2, text="　Y方向　", font=self.font_label)
        self.label222 = tk.Label(self.frame2, text="80.0", font=self.font_label)
        self.label223 = tk.Label(self.frame2, text="mm", font=self.font_label)
        self.label231 = tk.Label(self.frame2, text="　　　距離", font=self.font_label)
        self.label232 = tk.Label(self.frame2, text="128.1", font=self.font_label)
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

    def view_camera_image(self):
        self.log.debug("画像表示")

        self.label212 = tk.Label(self.frame2, text="100.0", font=self.font_label)
        self.label212.grid(column=1, row=0)



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

        self.master = master
        self.model = model
        self.view = view

    def press_start_button(self):
        self.log.debug("press_start_button")
        self.view.view_camera_image()

    def press_close_button(self):
        self.log.debug("press_close_button")
        self.master.destroy()




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

        self.log.debug("ストップコマンドの登録")
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
