import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv
import requests

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")
MODEL_NAME = "yandexgpt-lite"


async def reflect_message(user_text: str) -> str:
    prompt = {
        "modelUri": f"gpt://{YC_FOLDER_ID}/{MODEL_NAME}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 300
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты эмпатичный собеседник, который перефразирует мысли с теплотой. "
                        "Отвечай кратко и с пониманием."
            },
            {
                "role": "user",
                "text": user_text
            }
        ]
    }

    try:
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {YC_API_KEY}",
                "x-folder-id": YC_FOLDER_ID,
                "Content-Type": "application/json"
            },
            json=prompt,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code != 200:
            error_msg = f"Ошибка API (код {response.status_code})"
            if response.text:
                error_msg += f": {response.text}"
            return error_msg

        result = response.json()
        return result["result"]["alternatives"][0]["message"]["text"]

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка подключения: {str(e)}")
        return "Извини, проблемы с соединением. Попробуй позже⏲️"
    except Exception as e:
        logging.error(f"YaLM error: {str(e)}")
        return "Извини, не могу сейчас ответить. Попробуй позже⏲️"


@dp.message_handler(commands=["start"])
async def start(msg: Message):
    await msg.reply("Привет. Я здесь, чтобы выслушать. Что тревожит?")


@dp.message_handler()
async def handle_text(msg: Message):
    reply = await reflect_message(msg.text)
    await msg.reply(reply)


if __name__ == "__main__":
    executor.start_polling(dp)