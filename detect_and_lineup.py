import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import cv2

def detect_and_lineup(src: str, desc: str) -> None:
    """顔を見つけてリストアップする
    :params src:
        読み込む画像のパス
    :params desc:
        保存先のパス
    """

    # カスケードファイル（特徴量学習済みデータの分類器）のパスの指定
    cascade_file = './cascade/haarcascade_frontalface_alt2.xml'

    # 画像読み込み
    image = cv2.imread(str(src))
    # グレースケールに変換
    image_gs = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    # 顔認識用特徴量ファイルの読み込み
    cascade = cv2.CascadeClassifier(cascade_file)
    # 顔認識
    face_list = cascade.detectMultiScale(image_gs,
                                        scaleFactor=1.1,
                                        minNeighbors=1,
                                        minSize=(20,20))  # 20x20ピクセル以下の範囲は無視。背景を顔と間違えるのを防ぐため
    
    length = len(face_list)
    # タイル状に pm × pm 枚配置
    pm = 1
    while pm**2 < length:
        pm += 1
    
    # タイル状に画像を一覧表示させる
    fig, ax = plt.subplots(pm, pm, figsize=(10, 10))
    fig.subplots_adjust(hspace=0, wspace=0)

    for k in range(pm**2):
        i = k // pm  # 縦
        j = k % pm  # 横
        ax[i, j].xaxis.set_major_locator(plt.NullLocator())
        ax[i, j].yaxis.set_major_locator(plt.NullLocator())
        if k < length:
            x,y,w,h = face_list[k]
            # 配列アクセスを利用して顔を切り取る
            # imageの型はNumpyの配列(numpy.ndarray)。使い勝手が良い
            face_img = image[y:y+h,x:x+w]
            face_img = np.asarray(face_img)
            face_img = cv2.resize(face_img, (300, 300), cv2.INTER_LANCZOS4)
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            ax[i, j].text(30, 60, str(pm*i+j), fontsize=30, color='red')
            ax[i, j].imshow(face_img)
        else:
            img = cv2.imread('./white.jpg')
            img = np.asarray(img)
            img = cv2.resize(img, (300, 300), cv2.INTER_LANCZOS4)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ax[i, j].imshow(img)

    plt.savefig(desc)
    return face_list