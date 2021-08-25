# 022_distance_estimation_by_camera
![](https://img.shields.io/badge/type-python3-brightgreen)  ![](https://img.shields.io/badge/windows%20build-passing-brightgreen) ![](https://img.shields.io/badge/license-MIT-brightgreen)   
![](https://img.shields.io/badge/libraly-OpenCV-blue)  ![](https://img.shields.io/badge/libraly-NumPy-blue)  ![](https://img.shields.io/badge/libraly-Pillow-blue)


## DEMO
### Your webcam can be measured by the distance between id0 and id1 within the enclosed mark.  
<img src="https://user-images.githubusercontent.com/44888139/130731372-a2ff920d-f9e1-45e4-9a34-1c08de441ed3.png" height="500px">  

### You can get webcam infomation.  
<img src="https://user-images.githubusercontent.com/44888139/130731390-9f1213d2-22d7-4adc-a836-7a3951085e01.png" height="300px">  

| Japanese | English | unit | settign.json |
----|----|:---:|:---:
| カメラID | webcam ID | --- |  configurable |
| フレームレート | Refresh rate |  FPS | configurable |
| マーク間の距離 | Distance between the four marks on the sheet |  mm | configurable |
| カメラの横幅 | webcam width |  --- | --- |
| カメラの縦幅 | webcam height |  --- | --- |

## Features
Your webcam can be measured by the distance between id0 and id1 within the enclosed mark. 

### specification
- can select webcam by setting.json if your PC is connected to the cameras.
- can decide standard length by setting.json


## Requirement 
Python 3
 - I ran this program with the following execution environment.
   - Python 3.9
   - Windows 10

Python Library
  - cv2(OpenCV)
  - numpy
  - PIL(Pillow)
  - tkinter
  - json

## Usage
1. Please print out Book1.pdf and cut out id0 and id1.
1. Please change "settign.json" if you need to change.
1. Start this program.
1. Press "開始(<- START>)".
1. You can measure the length between id0 and id1.
1. Press "終了(<- STOP & END>)".


## Note
Nothing in particular

## License
This program is under MIT license.
# 【日本語】


## 機能
カメラに写ったid0とid1の距離を測定します。
- 仕様
  - PCに複数のカメラがある場合、"setting.json"を使って指定します。
  - 4つのマークの距離（基準距離）は、"setting.json"を使って指定します。

## 必要なもの
Python 3
- このプログラムは、Python 3.9とWindows10で動作確認しています。

## 使い方
1. まずBook.pdfを印刷し、id0とid1を切り取ります。
1. 必要ならsetting.jsonを変更します。
1. プログラムを実行します。
1. 開始ボタンを押します。
1. カメラに写せば、id0とid1の距離を測れます。
1. 終了ボタンを押せば、終了します。


## 備考
特にありません

## ライセンス
本プログラムは、MITライセンスです
