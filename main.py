from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import requests

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

def get_cats():
    try:
        url = "https://api.meetpets.idv.tw/v2/pets"
        params = {
            "kind": "cat",
            "city": "台北市",
            "status": "open",
            "limit": 5
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()
        
        cats = []
        for pet in data.get("data", [])[:5]:
            name = pet.get("name", "未命名")
            city = pet.get("city", "雙北")
            sex = "♂ 公" if pet.get("sex") == "M" else "♀ 母"
            color = pet.get("color", "")
            link = f"https://www.meetpets.idv.tw/pets/{pet.get('id')}"
            cats.append(f"🐱 {name}｜{sex}｜{color}\n📍 {city}\n🔗 {link}")
        
        if cats:
            return "🐾 最新待認養貓咪：\n\n" + "\n\n".join(cats)
        else:
            return "目前查無雙北市貓咪資料，請前往認養地圖查詢：\nhttps://www.meetpets.idv.tw"
    except Exception as e:
        return f"查詢失敗，請直接前往認養地圖：\nhttps://www.meetpets.idv.tw"

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
    if '找貓咪' in user_message or '收養' in user_message or '浪貓' in user_message:
        reply = get_cats()
    else:
        reply = "你好！輸入「找貓咪」，我幫你找最新待認養貓咪 🐱"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
