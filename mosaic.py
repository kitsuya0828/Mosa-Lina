import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import cv2

def mosaic(src: str, desc: str, numberslist=[], face_list=[]) -> None:
    """
    :params src:
        読み込む画像のパス
    :params desc:
        保存先のパス
    :numberslist:
        ユーザーが入力した番号のリスト
    :face_list:
        detect_and_lineupで認識した顔座標のリスト
    """

    # 画像読み込み
    image = cv2.imread(str(src))

    # ユーザーが残したい顔の番号を指定したとき
    new_numberslist = []
    if numberslist[0] == -1:
        for num in range(len(face_list)):
            if num not in numberslist:
                new_numberslist.append(num)
        numberslist = new_numberslist

    for i,f in enumerate(face_list):
        x,y,w,h = f
        if i not in numberslist:
            continue
        # 切り抜いた画像を指定倍率で縮小する
        face_img = image[y:y+h,x:x+w]
        face_img = cv2.resize(face_img, (min(10,w//10),min(10,h//10)))
        # 縮小した画像を元のサイズに戻す
        # どのようにresizeするかを引数interpolationで指定（cv.INTER_LINEARはモザイクの角が目立たない）
        face_img = cv2.resize(face_img,(w,h),interpolation=cv2.INTER_AREA)
        # 元の画像に貼り付け
        image[y:y+h,x:x+w] = face_img   

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(image)
    im.save(desc)
    return True