from telegram import Bot
from globals import TELEGRAM_TOKEN


async def start_agent(message: str, chat_id: str):
    print("Starting agent...")

    # TODO: add agent logic here

    # Agent ending send message to user
    await send_message_to_user(message, chat_id)


async def send_message_to_user(message: str, chat_id: str):

    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=chat_id, text=message)
