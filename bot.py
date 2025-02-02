from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from agent import start_agent
from globals import TELEGRAM_TOKEN


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "I'm a 🤖 bot that can help you with your tasks. I can help you with your tasks. I can help you with your tasks."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Agent is starting...")
    await start_agent(update.message.text, str(update.effective_chat.id))


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("add_task", add_task))

print("Bot is running...")
app.run_polling()
