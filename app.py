from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *
from utility import *
import getSentance, sys, twstock, re, datetime, time
import os

app = Flask(__name__)

# Line API
# Channel Access Token
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
# Channel Secret
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# Sinopac API
import shioaji as sj
sjapi = sj.Shioaji()
sjapi.login(
    api_key = os.environ['SINOPAC_API_KEY'],
    secret_key = os.environ['SINOPAC__SECRET_KEY'], 
    contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
)

# home 
@app.route("/", methods=['GET'])
def home():
    return "hello rrrgoodies"

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
    reply = ""
    # Get user id in webhoob event objects
    # https://developers.line.biz/en/reference/messaging-api/#webhook-event-objects
    try:
        json_dict = event.as_json_dict()
        userId = json_dict["source"]["userId"]
        profile = line_bot_api.get_profile(userId)
        print("名稱: " + profile.display_name)
        print("ID: " + profile.user_id)
        reply = profile.display_name + '您好\n\n'
    except Exception as e:
        # error handle
        print("user id not found!")
        handle_error(e)
        
    # compile identifier
    # ti = time.time()
    # pattern = re.compile("[0-9]{4}")
    # t1 = time.time()

    try:
        print("Recieve from client: " + event.message.text)
        if "心情不好" in event.message.text:
            reply = "心情不好啊? 跟你說: \n \n"
            reply += getSentance.pick_a_sentence()
        elif is_valid_stockNumber(event.message.text):
            # get stock value
            code = event.message.text
            reply = get_stockValue_from_sinopacAPI(sjapi, code)

        # reply
        message = TextSendMessage(text=reply)
        line_bot_api.reply_message(event.reply_token, message)

    except Exception as e:
        print("Failed in reply: " + str(e))
        handle_error(e)


    # (t2,t3,t4,t5,t6) = info[1] 
    # debugMsg = "Time consumption:\n"
    # debugMsg += f"re compile:\t {round(t1-ti, 3)}\n"
    # debugMsg += f"realtime get:\t {round(t3-t2, 3)}\n"
    # debugMsg += f"Stock get:\t {round(t4-t3, 3)}\n"
    # debugMsg += f"price get:\t {round(t6-t5, 3)}\n"
    # debugMsg += f"Total :\t {round(t6-ti, 3)}\n"
    # print(debugMsg)
    # sys.stdout.flush()
    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
