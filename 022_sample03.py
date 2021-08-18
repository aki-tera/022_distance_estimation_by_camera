import tkinter as tk


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


class Controller():
    log = logger.Logger("Controller", level=DEBUG)

    def __init__(self, master, model, view):
        self.log.debug("__init__")

        self.master = master
        self.model = model
        self.view = view


class Application(tk.Frame):
    log = logger.Logger("Application", level=DEBUG)

    def __init__(self, master):
        # tkinterの定型文
        super().__init__(master)
        self.pack()

        self.model = Model()

        master.geometry()
        master.title("カメラによる計測アプリ")

        self.view = View(master, self.model)
        self.controller = Controller(master, self.model, self.view)

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

