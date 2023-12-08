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
    currency_request = requests.get('https://tw.rter.info/capi.php')
    currency = currency_request.json()

    currencyDate = currency['USDTWD']['UTC']
    # stock
    stock_num = user_message.split(' ', 1 )
    print(stock_num)
    if stock_num[0] == 'stock':
        stock_request = requests.get(f'https://mis.twse.com.tw/stock/api/getStock.jsp?ch={stock_num[1]}.tw')
        stock_information = stock_request.json()
        stock_name = stock_num[1]
        stock_price = stock_information['msgArray']
        print(stock_price)
        msg = f'you want know stock {stock_name} now is {stock_price}'
    # exchange currency
    if user_message ==  'JPY' or user_message ==  'jpy':
        currencyQueryJP = currency['USDJPY']
        currencyQueryTW = currency['USDTWD']
        finalCurrency = currencyQueryTW['Exrate'] /currencyQueryJP['Exrate']
        msg = f"{currencyDate} exchange accurate = {round(finalCurrency, 4)}"
        
    elif user_message == 'USD' or user_message == 'usd':
        currencyQuery = currency['USDTWD']
        finalCurrency = currencyQuery['Exrate']
        msg = f"{currencyDate} exchange accurate = {round(finalCurrency, 4)}"

    
    reply_text = msg
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()

