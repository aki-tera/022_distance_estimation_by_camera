import cv2
import numpy as np
import json
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


# PEP8に準拠するとimportが先頭に行くので苦肉の策
while True:
    import sys
    sys.path.append("../000_mymodule/")
    import logger
    break

# パラメータの取り出し
setting = json.load(open("setting.json", "r", encoding="utf-8"))

log = logger.Logger("test", level=DEBUG)

aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

cap = cv2.VideoCapture(setting["CAM"]["ID"])
cap.set(cv2.CAP_PROP_FRAME_WIDTH, setting["CAM"]["WIDTH"])


while True:
    # ビデオキャプチャから画像を取得
    ret, frame = cap.read()

    log.debug(ret)
 
    # sizeを取得
    # (縦、横、色)
    Height, Width = frame.shape[:2]
    
    img0 = cv2.resize(frame, (int(200), int(200 * Height / Width)))
    cv2.imshow("origin", img0)
    
    img1 = cv2.resize(frame, (int(Width), int(Height)))
    
    # 検出
    corners, ids, rejectedImgPoints = aruco.detectMarkers(img1, dictionary)
    
    # 検出したマーカに描画する
    # イメージをコピーする
    img2 = np.copy(img1)
    aruco.drawDetectedMarkers(img2, corners, ids, (0, 255, 0))
    img2 = cv2.resize(img2, (int(400), int(400 * Height / Width)))
    cv2.imshow("marker", img2)
       
    m = np.empty((4, 2))

    log.debug(ids)
    log.debug(type(ids))

    # ラインを引く準備
    x_start, y_start = 0, 0
    x_end, y_end = 0, 0


    if ids is None:
        img_trans = cv2.resize(frame, (600, 600))
        log.debug("None")
    elif np.count_nonzero((2 <= ids) & (ids <= 6)) == 4:
        log.debug("Number is 4")
        for i, c in zip(ids, corners):
            # マーカーの赤丸位置を基準としている
            if 2 <= i <= 6:
                log.debug(c)
                m[i - 2] = c[0][0]

        # 変形後の画像サイズ
        trans_width, trans_height = (600, 600)

        marker_coordinates = np.float32(m)
        true_coordinates = np.float32([[0, 0], [trans_width, 0], [trans_width, trans_height], [0, trans_height]])
        trans_mat = cv2.getPerspectiveTransform(marker_coordinates, true_coordinates)
        img_trans = cv2.warpPerspective(img1, trans_mat, (trans_width, trans_height))

        if np.count_nonzero((0 <= ids) & (ids <= 1)) == 2:
            # 変換後の画像でid検索
            corners_trans, ids_trans, rejectedImgPoints_trans = aruco.detectMarkers(img_trans, dictionary)
            # id(0と1)の抽出
            if ids_trans is not None:
                for number, corner in zip(ids_trans, corners_trans):
                    if number == 0:
                        x_start, y_start = int(corner[0][0][0]), int(corner[0][0][1])
                    elif number == 1:
                        x_end, y_end = int(corner[0][0][0]), int(corner[0][0][1])
                log.debug(x_start)
                log.debug(y_start)
                log.debug(x_end)
                log.debug(y_end)
                # id(0と1)の距離を表示
                x, y = (x_end - x_start), (y_end - y_start)
                log.info(x)
                log.info(y)
                dis = ((x * x + y * y) ** 0.5 ) * 135 / 600
                log.info(y)

                cv2.line(img_trans, (x_start, y_start), (x_end, y_end), (0, 0, 255), 1)
                cv2.putText(img_trans, str(f"dis:{dis:.1f}mm ({x:.1f}dot,{y:.1f}dot)"), (0, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3, cv2.LINE_AA)

    else:
        img_trans = cv2.resize(frame, (600, 600))
        log.debug("others")

    cv2.imshow("test", img_trans)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ビデオキャプチャのメモリ解放
cap.release()
# すべてのウィンドウを閉じる
cv2.destroyAllWindows()