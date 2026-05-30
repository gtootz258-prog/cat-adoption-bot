from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

def get_cats():
    try:
        url = "https://www.pet.gov.tw/Web/O302.aspx"
        params = {
            "unit": "63000", # 台北市
            "animal_kind": "貓",
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        cats = []
        items = soup.select(".listitem")[:5]  # 只取前5隻
        
        for item in items:
            try:
                name = item.select_one(".name")
                area = item.select_one(".area")
                link = item.select_one("a")
                
                cat_name = name.text.strip() if name else "未命名"
                cat_area = area.text.strip() if area else "台北市"
                cat_link = "https://www.pet.gov.tw" + link["href"] if link else url
                
                cats.append(f"🐱 {cat_name}\n📍 {cat_area}\n🔗 {cat_link}")
            except:
                continue
        
        if cats:
            return "最新待認養貓咪（雙北市）：\n\n" + "\n\n".join(cats)
        else:
            return "目前查無資料，請直接前往：\nhttps://www.pet.gov.tw/Web/O302.aspx"
    except Exception as e:
        return f"抓取失敗，請直接前往：\nhttps://www.pet.gov.tw/Web/O302.aspx"

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
