import os
from pathlib import Path
from typing import List
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ImageMessage, ImageSendMessage, MessageEvent, TextMessage, TextSendMessage)

from detect_and_lineup import detect_and_lineup
from mosaic import mosaic

app = Flask(__name__,static_url_path="/static")

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

SRC_IMAGE_PATH = "static/images/{}.jpg"
MAIN_IMAGE_PATH = "static/images/{}_main.jpg"
PREVIEW_IMAGE_PATH = "static/images/{}_preview.jpg"
FACE_COORDINATES_PATH = "{}.txt"

@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    user_id = profile.user_id
    if event.message.text == 'レビュー':
        line_bot_api.reply_message(
        event.reply_token, messages=[TextSendMessage(text="https://forms.gle/PBrsEzKBzo5raAij8")]
        )
    else:    
        src_image_path = Path(SRC_IMAGE_PATH.format(user_id)).absolute()
        main_image_path = MAIN_IMAGE_PATH.format(user_id*2)
        preview_image_path = PREVIEW_IMAGE_PATH.format(user_id*2)
        face_coordinates_path = FACE_COORDINATES_PATH.format(user_id)

        numberslist = list(map(int,str(event.message.text).split()))

        with open(face_coordinates_path) as f:
            face_list = [list(map(int,s.strip().split())) for s in f.readlines()]

        mosaic(src=src_image_path, desc=Path(main_image_path).absolute(),numberslist=numberslist,face_list=face_list)
        mosaic(src=src_image_path, desc=Path(preview_image_path).absolute(),numberslist=numberslist,face_list=face_list)
        image_message = ImageSendMessage(
            original_content_url=f"https://<自分のアプリケーション名>.herokuapp.com/{main_image_path}",
            preview_image_url=f"https://<自分のアプリケーション名>.herokuapp.com/{preview_image_path}",
        )
        app.logger.info(f"https://<自分のアプリケーション名>.herokuapp.com/{main_image_path}")
        line_bot_api.reply_message(
            event.reply_token, messages=[image_message,TextSendMessage(text="お気に召さなかったらごめんあそばせ")]
        )
        src_image_path.unlink()
    

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    profile = line_bot_api.get_profile(event.source.user_id)
    user_id = profile.user_id

    src_image_path = Path(SRC_IMAGE_PATH.format(user_id)).absolute()
    main_image_path = MAIN_IMAGE_PATH.format(user_id)
    preview_image_path = PREVIEW_IMAGE_PATH.format(user_id)
    face_coordinates_path = FACE_COORDINATES_PATH.format(user_id)

    # 画像を保存
    save_image(message_id, src_image_path)

    try:
        face_list = detect_and_lineup(src=src_image_path, desc=Path(main_image_path).absolute())
        detect_and_lineup(src=src_image_path, desc=Path(preview_image_path).absolute())
        # 画像の送信
        image_message = ImageSendMessage(
        original_content_url=f"https://<自分のアプリケーション名>.herokuapp.com/{main_image_path}",
        preview_image_url=f"https://<自分のアプリケーション名>.herokuapp.com/{preview_image_path}",
        )
        app.logger.info(f"https://<自分のアプリケーション名>.herokuapp.com/{main_image_path}")
        line_bot_api.reply_message(event.reply_token, messages=[image_message, TextSendMessage(text="モザイクをかけたいお顔の番号を半角空白区切りでご入力いただけるかしら？\n例）1番と3番の顔にモザイクをかけたい\n☞「1 3」と入力\n\n'-1'を先頭に付けると残したいお顔の番号を指定することもできますわよ。\n例）0番と2番以外の顔にモザイクをかけたい\n☞「-1 0 2」と入力")])

        # 顔座標テキストファイルの保存
        with open(face_coordinates_path, "w", encoding='utf-8') as f:
            for i in range(len(face_list)):
                f.write(" ".join([str(x) for x in face_list[i]]) + "\n")
        
    except Exception:
        line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='認識可能なお顔が見つかりませんでしたわ')
        )


def public_attr(obj) -> List[str]:
    return [x for x in obj.__dir__() if not x.startswith("_")]


def save_image(message_id: str, save_path: str) -> None:
    """保存"""
    message_content = line_bot_api.get_message_content(message_id)
    with open(save_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
