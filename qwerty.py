import os
import time
import asyncio
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = "8534953023:AAESqhJoap-KDtLu1e_FL2m3qTcvaV74COo"
CHANNEL_ID = "@ANG3KYAN0N"

# Словарь для защиты от спама
user_last_msg = {}
SPAM_LIMIT = 10

# ========== FLASK ==========
app = Flask(__name__)

@app.route('/')
def health():
    return "Бот работает!", 200

@app.route('/ping')
def ping():
    return "Pong!", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ========== АВТО-ПИНГ ==========
def auto_ping():
    while True:
        time.sleep(600)
        try:
            requests.get('http://localhost:8080/ping')
            print("✅ Авто-пинг выполнен")
        except:
            print("⚠️ Ошибка при авто-пинге")

# ========== ФУНКЦИИ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я анон бот 𝑨𝑵𝑮𝑬𝑳'𝑺𝑲𝒀.\n"
        "Просто напиши мне любое сообщение, и я опубликую его в канале.\n"
    )

def is_spam(user_id: int) -> bool:
    current_time = time.time()
    if user_id in user_last_msg:
        if current_time - user_last_msg[user_id] < SPAM_LIMIT:
            return True
    user_last_msg[user_id] = current_time
    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_spam(user_id):
        await update.message.reply_text(f"Подожди {SPAM_LIMIT} секунд перед новым сообщением!")
        return
    
    try:
        if update.message.text:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"анон: {update.message.text}"
            )
            await update.message.reply_text("✅ Текст опубликован в канале!")
        
        elif update.message.photo:
            photo = update.message.photo[-1]
            caption = update.message.caption or "📸 Анонимное фото"
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo.file_id,
                caption=f"анон: {caption}"
            )
            await update.message.reply_text("✅ Фото опубликовано в канале!")
        
        elif update.message.video:
            video = update.message.video
            caption = update.message.caption or "🎬 Анонимное видео"
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=video.file_id,
                caption=f"анон: {caption}"
            )
            await update.message.reply_text("✅ Видео опубликовано в канале!")
        
        elif update.message.voice:
            voice = update.message.voice
            await context.bot.send_voice(
                chat_id=CHANNEL_ID,
                voice=voice.file_id,
                caption="анон гс"
            )
            await update.message.reply_text("✅ Голосовое опубликовано в канале!")
        
        elif update.message.document:
            doc = update.message.document
            caption = update.message.caption or "📄 Анонимный документ"
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=doc.file_id,
                caption=f"анон: {caption}"
            )
            await update.message.reply_text("✅ Документ опубликован в канале!")
        
        else:
            await update.message.reply_text("Этот тип сообщений пока не поддерживается.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при отправке: {str(e)}")

# ========== ЗАПУСК БОТА ==========
def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, 
        handle_message
    ))
    
    print("Бот запущен и готов к работе!")
    application.run_polling()

# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    ping_thread = Thread(target=auto_ping)
    ping_thread.daemon = True
    ping_thread.start()
    
    run_bot()
