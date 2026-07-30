import os
import time
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = "8534953023:AAESqhJoap-KDtLu1e_FL2m3qTcvaV74COo"  # Вставь сюда
CHANNEL_ID = "@ANG3KYAN0N"          # Например: @news_channel

# Словарь для защиты от спама {user_id: время_последнего_сообщения}
user_last_msg = {}

# Ограничение: 1 сообщение в 10 секунд
SPAM_LIMIT = 10  

# ========== FLASK (чтобы Render не уснул) ==========
app = Flask(name)

@app.route('/')
def health():
    return "Бот работает!", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ========== ФУНКЦИИ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я анонимный бот .\n"
        "Просто напиши мне любое сообщение, и я опубликую его в канале.\n"
        "!ТВОЕ ИМЯ И НИКНЕЙМ НЕ БУДЕТ ОТОБРАЖАТЬСЯ!"
    )

def is_spam(user_id: int) -> bool:
    """Проверяет, не спамит ли пользователь"""
    current_time = time.time()
    if user_id in user_last_msg:
        if current_time - user_last_msg[user_id] < SPAM_LIMIT:
            return True
    user_last_msg[user_id] = current_time
    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # === ЗАЩИТА ОТ СПАМА ===
    if is_spam(user_id):
        await update.message.reply_text(f"Подожди {SPAM_LIMIT} секунд перед новым сообщением!")
        return
    
    # === ОБРАБОТКА РАЗНЫХ ТИПОВ СООБЩЕНИЙ ===
    try:
        # ТЕКСТ
        if update.message.text:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"📩 Анонимно:\n\n{update.message.text}"
            )
            await update.message.reply_text("✅ Текст опубликован в канале!")
        
        # ФОТО
        elif update.message.photo:
            # Берём самое качественное фото (последнее в списке)
            photo = update.message.photo[-1]
            caption = update.message.caption or "📸 Анонимное фото"
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo.file_id,
                caption=f"📩 Анонимно:\n\n{caption}"
            )
            await update.message.reply_text("✅ Фото опубликовано в канале!")
        
        # ВИДЕО
        elif update.message.video:
            video = update.message.video
            caption = update.message.caption or "🎬 Анонимное видео"
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=video.file_id,
                caption=f"📩 Анонимно:\n\n{caption}"
            )
            await update.message.reply_text("✅ Видео опубликовано в канале!")
        
        # ГОЛОСОВЫЕ СООБЩЕНИЯ
        elif update.message.voice:
            voice = update.message.voice
            await context.bot.send_voice(
                chat_id=CHANNEL_ID,
                voice=voice.file_id,
                caption="🎙️ Анонимное голосовое сообщение"
            )
            await update.message.reply_text("✅ Голосовое опубликовано в канале!")
        
        # ДОКУМЕНТЫ (файлы)
        elif update.message.document:
            doc = update.message.document
            caption = update.message.caption or "📄 Анонимный документ"
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=doc.file_id,
                caption=f"📩 Анонимно:\n\n{caption}"
            )
            await update.message.reply_text("✅ Документ опубликован в канале!")
        
        # ВСЁ ОСТАЛЬНОЕ
        else:
            await update.message.reply_text("Этот тип сообщений пока не поддерживается.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при отправке: {str(e)}")

# ========== ЗАПУСК БОТА ==========
def run_bot():
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, 
        handle_message
    ))
    
    print("Бот запущен и готов к работе!")
    application.run_polling()

# ========== ТОЧКА ВХОДА ==========
if name == "main":
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Запускаем бота
    run_bot()