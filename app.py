from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import requests

app = Flask(__name__)

# 以下替換為的 Channel Secret 和 Channel Access Token
line_bot_api = LineBotApi('Channel Access Token')
handler = WebhookHandler('Channel Secret')

@app.route("/", methods=['POST'])
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
    r = requests.get('https://tw.rter.info/capi.php')
    currency = r.json()

    currencyDate = currency['USDTWD']['UTC']

    if user_message == '日幣' or user_message ==  'JPY' or user_message ==  'jpy':
        currencyQueryJP = currency['USDJPY']
        currencyQueryTW = currency['USDTWD']
        finalCurrency = currencyQueryTW['Exrate'] /currencyQueryJP['Exrate']
        
    elif user_message == '美金' or user_message == 'USD' or user_message == 'usd':
        currencyQuery = currency['USDTWD']
        finalCurrency = currencyQuery['Exrate']

    msg = f"{currencyDate} exchange accurate = {round(finalCurrency, 4)}"
    reply_text = msg
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()

