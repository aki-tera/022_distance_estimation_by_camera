import cv2
import json
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


# PEP8に準拠するとimportが先頭に行くので苦肉の策
while True:
    import sys
    sys.path.append("../000_mymodule/")
    import logger
    break


def estimation(setting):
    log = logger.Logger("estimation", level=INFO)


    aruco = cv2.aruco
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    cap = cv2.VideoCapture(setting["CAM"]["ID"])

    log.debug(setting["CAM"]["ID"])

    window_width = setting["CAM"]["WIDTH"]
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_width)

    id_start = setting["TARGET"]["START"]
    id_end = setting["TARGET"]["END"]

    log.debug(window_width)
    log.debug(id_start)
    log.debug(id_end)

    while True:
        # ビデオキャプチャから画像を取得
        # ret:True/False
        # frame：画像データ
        ret, frame = cap.read()

        # sizeを取得
        # (縦、横、色)
        Height, Width = frame.shape[:2]

        log.debug(Height)
        log.debug(Width)

        img = cv2.resize(frame, (int(Width), int(Height)))

        # マーカを検出
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)

        log.debug(corners)
        log.debug(ids)

        # 検出したマーカに描画する
        aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 0))

        # ラインを引く
        x_start, y_start = 0, 0
        x_end, y_end = 0, 0

        try:
            for number, corner in zip(ids, corners):

                log.debug(number)

                if number == id_start:
                    x_start, y_start = int(corner[0][0][0]), int(corner[0][0][1])
                elif number == id_end:
                    x_end, y_end = int(corner[0][0][0]), int(corner[0][0][1])
        except:
            pass

        # 0と2の赤角距離を表示
        x, y = (x_end - x_start), (y_end - y_start)

        log.info(x)
        log.info(y)

        cv2.line(img, (x_start, y_start), (x_end, y_end), (0, 0, 255), 1)
        cv2.putText(img, str(f"x:{x:.1f}, y:{y:.1f}"), (0, Height - 10), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3, cv2.LINE_AA)

        # マーカが描画された画像を表示
        cv2.imshow("drawDetectedMarkers", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # ビデオキャプチャのメモリ解放
    cap.release()

    # すべてのウィンドウを閉じる
    cv2.destroyAllWindows()


def main():
    # パラメータの取り出し
    setting = open("setting.json", "r", encoding="utf-8")
    setting_dict = json.load(setting)

    log = logger.Logger("main", level=INFO)
    log.debug("test")

    estimation(setting_dict)

if __name__ == "__main__":
    main()