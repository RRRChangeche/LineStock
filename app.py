from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import getSentance, sys, twstock, re, datetime, time

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('S3qOJcsWGYNedORcrvQUyD85JoOLuH1AnVAV2M/53YLYjx552QmLfp6bvcb5Y2S6KeOhRgWR1A8dC22zRo777ZjhBQutfnGDk5uXnZeAy9fUf0c71xIg2/bY/dQoa2QhCziSoNu/G1E4dQffOCbMWQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('04cba13430c76f36f2e41687ff3a4f00')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event.message.text)

    # compile identifier
    ti = time.time()
    pattern = re.compile("[0-9]{4}")
    t1 = time.time()

    if "心情不好" in event.message.text:
        reply = "心情不好啊? 跟你說: \n \n"
        reply += getSentance.pick_a_sentence()
    elif pattern.match(event.message.text):
        code = event.message.text
        # reply = getSotckInfo(code)
        info = getSotckInfo(code)
        reply = info[0]
        (t2,t3,t4,t5,t6) = info[1]
        
    else:
        return
    message = TextSendMessage(text=reply)
    line_bot_api.reply_message(event.reply_token, message)

    debugMsg = "Time consumption:\n"
    debugMsg += f"re compile:\t {round(t1-ti, 3)}\n"
    debugMsg += f"realtime get:\t {round(t3-t2, 3)}\n"
    debugMsg += f"Stock get:\t {round(t4-t3, 3)}\n"
    debugMsg += f"price get:\t {round(t6-t5, 3)}\n"
    debugMsg += f"Total :\t {round(t6-ti, 3)}\n"
    print(debugMsg)
    sys.stdout.flush()

def getSotckInfo(keyword):
    try:
        t2 = time.time()
        rtStock = twstock.realtime.get(keyword)
        t3 = time.time()
        preStock = twstock.Stock(keyword)
        t4 = time.time()
        if not rtStock['success']:
            return '代號輸入錯誤'
    except:
        return '代號輸入錯誤'
    
    # identify market close time
    cTime = datetime.datetime.now()
    openTime = datetime.datetime(cTime.year, cTime.month, cTime.day, 9, 0)
    closeTime = datetime.datetime(cTime.year, cTime.month, cTime.day, 14, 30)
    if openTime < cTime < closeTime:
        t5 = time.time()
        rtPrice = float(rtStock['realtime']['latest_trade_price'])
        prePrice = preStock.price[-1] 
        t6 = time.time()
    else:
        t5 = time.time()
        rtPrice = preStock.price[-1]
        prePrice = preStock.price[-2]
        t6 = time.time()

    diff = round(rtPrice-prePrice, 2)
    percentage = round((rtPrice-prePrice)/prePrice*100, 2)
    upDown = "📈+" if diff > 0 else "📉"
    upDown = "(-)" if float(diff) == 0.0 else upDown
    reply = f"{keyword} {rtStock['info']['name']}  {rtPrice}\n漲跌幅 {upDown}{diff} ({percentage}%)"
    return reply, (t2,t3,t4,t5,t6)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
