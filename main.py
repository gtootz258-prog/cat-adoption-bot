from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

def search_cats():
    url = "https://www.pet.gov.tw/Web/O302.aspx"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return "🐱 最新浪貓收養資訊：\n請前往動物之家查詢：https://www.pet.gov.tw/Web/O302.aspx\n\n你可以在網站上依縣市篩選，找到離你最近的待認養貓咪！"
        else:
            return "目前無法取得資料，請稍後再試。"
    except:
        return "連線失敗，請稍後再試。"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    if '找貓' in user_message or '收養' in user_message or '浪貓' in user_message:
        reply = search_cats()
    else:
        reply = "你好！輸入「找貓」或「收養」，我會幫你找浪貓收養資訊 🐱"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
