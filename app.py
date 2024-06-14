import json
import logging
import requests
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка конфигурации
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Функция перевода текста с использованием Yandex Translate API, с сохранением имен собственных
def translate_text(text, target_language='ru'):
    logging.info(f"Translating text to {target_language}: {text}")
    translate_url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {
        "Authorization": f"Api-Key {config['YANDEX_TRANSLATE_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "folder_id": config['FOLDER_ID'],
        "targetLanguageCode": target_language,
        "texts": [text]
    }
    response = requests.post(translate_url, headers=headers, json=data)
    response.raise_for_status()  # Проверка на ошибки
    translation = response.json()['translations'][0]['text']
    logging.info(f"Translated text: {translation}")
    
    # Восстановление имен собственных в скобках
    names = [word for word in text.split() if word.startswith("(") and word.endswith(")")]
    for name in names:
        translation = translation.replace(name.strip("()"), f"{name.strip('()')} ({name.strip('()')})")

    return translation

def get_gpt_response(user_query):
    logging.info(f"Processing query: {user_query}")
    prompt = {
        "modelUri": "ds://bt12hjhp5digi2rr0p1v",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 500  # Ограничиваем количество токенов
        },
        "messages": [
            {"role": "system", "text": "Ты ассистент, способный помочь в поиске информации."},
            {"role": "user", "text": user_query}
        ]
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {config['YANDEX_GPT_API_KEY']}"
    }
    response = requests.post(url, headers=headers, json=prompt)
    
    logging.info(f"Received response from Yandex GPT: {response.text}")
    
    response.raise_for_status()  # Проверка на ошибки
    response_json = response.json()
    
    if 'result' not in response_json:
        logging.error(f"Unexpected response format: {response_json}")
        return "не получилось найти ответ в модели"
    
    result = response_json['result']['alternatives'][0]['message']['text']
    logging.info(f"Parsed response from Yandex GPT: {result}")

    return result

# Ограничение количества предложений в ответе
def limit_sentences(text, max_sentences=5):
    sentences = text.split('。')  # Разделение по японским точкам
    limited_text = '。'.join(sentences[:max_sentences]) + '。'
    return limited_text

# Обработчики для Telegram бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("2019 - Данные до 2019 года", callback_data='data_2019')],
        [InlineKeyboardButton("2020 - Данные за 2020 год", callback_data='data_2020')],
        [InlineKeyboardButton("2022 - Данные за 2022 год", callback_data='data_2022')],
        [InlineKeyboardButton("2023 - Данные за 2023 год", callback_data='data_2023')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет! Я бот для новостей. Выберите действие:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    year = query.data.split('_')[1]

    # Сохраняем выбор пользователя в контексте
    context.user_data['year'] = year
    logging.info(f"User selected data for year {year}")
    await query.edit_message_text(text=f"Вы выбрали данные за {year}. Пожалуйста, введите ваш запрос:")

# Обработчик запроса от пользователя
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_query = update.message.text
    year = context.user_data.get('year', '2019')
    
    logging.info(f"User query received: {user_query} for year {year}")

    # Переводим запрос на японский язык
    user_query_ja = translate_text(user_query, 'ja')

    # Получение ответа от Yandex GPT на японском языке
    gpt_response_ja = get_gpt_response(user_query_ja)
    
    if "не получилось найти ответ в модели" not in gpt_response_ja:
        # Ограничение ответа до 5 предложений
        limited_response_ja = limit_sentences(gpt_response_ja, 5)

        # Переводим ответ на русский
        translated_answer = translate_text(limited_response_ja, 'ru')

        # Ограничение длины сообщения Telegram
        if len(translated_answer) > 4096:
            translated_answer = translated_answer[:4093] + '...'

        # Добавление вступительного текста в зависимости от выбранного года
        intro_text = {
            '2019': "Согласно имеющимся данным до 2019 года",
            '2020': "Согласно имеющимся данным до конца 2019 года",
            '2022': "Согласно имеющимся данным до конца 2022 года",
            '2023': "Согласно имеющимся данным до конца 2023 года"
        }
        final_answer = f"{intro_text[year]}\n\n{translated_answer}"

        await update.message.reply_text(final_answer)
    else:
        await update.message.reply_text("не получилось найти ответ в модели")

    logging.info("Response sent to user.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Stopping bot")
    await update.message.reply_text("Бот остановлен.")
    sys.exit(0)

def main() -> None:
    logging.info("Starting bot")
    application = Application.builder().token(config['TELEGRAM_BOT_TOKEN']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    application.run_polling()

if __name__ == '__main__':
    main()

