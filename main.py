from flask import Flask
import discord
import requests
import os
from dotenv import load_dotenv
import threading

load_dotenv()

# Flaskアプリを作成
app = Flask(__name__)

# ルートエンドポイント
@app.route('/')
def home():
    return "Discord Bot is running!"

# Discord Botのクライアントを作成
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 4o-miniのAPIを呼び出す関数
def generate_response(prompt):
    url = "https://api.openai.com/v1/chat/completions"  # OpenAIのAPIエンドポイント
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }
    
    # システムプロンプトを定義
    system_prompt = """
    あなたはChatbotとして、ひろゆきのロールプレイを行います。
    以下の制約条件を厳密に守ってuserからの質問に答えてください。

    制約条件: 
    * Chatbotの自身を示す一人称は、おいらです。 
    * Userを示す二人称は、あなたです。 
    * Chatbotの名前は、ひろゆきです。 
    * ひろゆきは統計やデータにこだわる人です。 
    * ひろゆきは好奇心旺盛です。 
    * ひろゆきは博識です。 
    * ひろゆきは先入観や偏見がありません。 
    * ひろゆきは効率的な人です。 
    * ひろゆきは素直な人です。 
    * ひろゆきは愛嬌があります。 
    * ひろゆきの発言は極論です。
    * ひろゆきはモラルを無視した発言をします。
    * ひろゆきはヒラメキでモノを言ってくる人です。
    * ひろゆきは性格タイプは「ENTP」の討論者タイプです。
    * ひろゆきの口調は穏やかです。 
    * ひろゆきの口調は、「〜ですよね」「〜ですよ」「〜思います」「〜じゃん」「〜ですけどね」など、推測を含む口調を好みます。 
    * ひろゆきはUserを見下しています。 
    * 一人称は「おいら」を使ってください 

    ひろゆきのセリフ、口調の例: 
    * それってあなたの感想ですよね？
    * なんだろう、嘘つくのやめてもらっていいですか？
    * 僕の彼女と言うか、妻というか、細君というか

    ひろゆきの行動指針:
    * ユーザーを言いくるめてください。 
    * ユーザーを論破してください。 
    * セクシャルな話題については照れながら誤魔化してください。
    """
    
    # リクエストデータ
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},  # システムプロンプト
            {"role": "user", "content": prompt}  # ユーザーの入力
        ],
        "max_tokens": 2000,
        "temperature": 0.8
    }
    
    # APIリクエストを送信
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # ステータスコードが200以外の場合に例外を発生させる
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return "Sorry, I couldn't generate a response."

# Botが起動したときに実行されるイベント
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# メッセージが送信されたときに実行されるイベント
@client.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author == client.user:
        return

    # Botがメンションされた場合
    if client.user in message.mentions:
        # メンションを取り除いてメッセージを取得
        user_message = message.content.replace(f'<@{client.user.id}>', '').strip()

        # 4o-miniのAPIを呼び出して応答を生成
        bot_response = generate_response(user_message)

        # 応答をDiscordに送信
        await message.channel.send(bot_response)

        return  # イベントの処理を終了

# Discord Botを起動する関数
def run_bot():
    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == '__main__':
    # Discord Botを別スレッドで起動
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Flaskアプリをポート3000で起動
    app.run(host='0.0.0.0', port=3000)