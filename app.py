from flask import Flask, request, jsonify
import openai
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 設定 OpenAI API Key
openai.api_key = "你的OpenAI API Key"

# 設定 LINE 官方帳號的 Token & Secret
LINE_ACCESS_TOKEN = "你的 LINE Access Token"
LINE_CHANNEL_SECRET = "你的 LINE Channel Secret"

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 讓 AI 產生回覆
def generate_response(user_message):
    prompt = f"""
    你是一位刺青藝術家，說話風格是友善且帶點個人風格，不會太正式。
    以下是一些範例對話：
    
    使用者：請問小圖能客製嗎？
    AI 回覆：可以喔！不過還是會依照我的風格來調整，細節我們可以再討論～

    使用者：請問你有哪幾天有空？
    AI 回覆：最近檔期有點滿，不過可以看看你想要的時間，我盡量安排喔！

    現在，請根據這種風格回覆以下問題：
    使用者：{user_message}
    AI 回覆：
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response["choices"][0]["message"]["content"].strip()

# 處理 LINE 訊息
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

# 監聽文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_text = generate_response(user_message)  # 讓 AI 產生回覆
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
