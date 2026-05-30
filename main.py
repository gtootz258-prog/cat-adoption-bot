from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

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
        reply = (
            "🐱 雙北市流浪貓收養管道整理：\n\n"
            "【政府官方】\n"
            "① 台北市動物之家\n"
            "https://www.tcapo.gov.taipei\n\n"
            "② 新北市動物之家\n"
            "https://www.nacp.ntpc.gov.tw\n\n"
            "③ 全國動物收容系統\n"
            "https://www.pet.gov.tw/Web/O302.aspx\n\n"
            "【民間認養平台】\n"
            "④ 認養地圖\n"
            "https://www.meetpets.idv.tw\n\n"
            "⑤ 台灣認養地圖 Facebook\n"
            "https://www.facebook.com/groups/taiwan.adopt\n\n"
            "⑥ 流浪動物花園\n"
            "http://www.doghome.org.tw\n\n"
            "⑦ 台北市流浪貓保護協會\n"
            "https://www.facebook.com/TaipeiCatProtection\n\n"
            "💡 小提醒：政府動物之家的貓咪若沒有被認養，"
            "會有安樂死風險，優先認養可以救牠們一命！"
        )
    else:
        reply = "你好！輸入「找貓咪」，我幫你整理雙北市所有浪貓收養管道 🐱"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
