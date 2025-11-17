from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8552286080:AAHyr9PzZhzZ3RD8l5Sh8GU7I0F9Xtzmbss"  # <- вставь сюда токен от BotFather

# -----------------------
# Команды
# -----------------------

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/ping — проверка работы бота\n"
        "/kick — забанить пользователя (ответ на сообщение)\n"
        "/help — показать список команд"
    )

# Исправленный kick
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied_msg = update.message.reply_to_message
    if not replied_msg:
        await update.message.reply_text("⚠️ Ответьте на сообщение пользователя, которого хотите забанить.")
        return

    user = replied_msg.from_user
    if user.is_bot:
        await update.message.reply_text("Нельзя кикнуть бота!")
        return

    chat_id = update.message.chat.id
    try:
        await context.bot.ban_chat_member(chat_id, user.id, until_date=None)
        await update.message.reply_text(f"✅ Пользователь {user.full_name} забанен!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при бане: {e}")

# -----------------------
# Авто-приветствие
# -----------------------
async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(
                f"Привет, {member.full_name}! Добро пожаловать в группу 😊"
            )

# -----------------------
# Запуск бота
# -----------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Команды для лички и групп
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kick", kick, filters=filters.ChatType.GROUP | filters.ChatType.SUPERGROUP))

    # Авто-приветствие новых участников
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))

    print("Бот запущен...")
    app.run_polling()  # безопасный запуск на Windows

# -----------------------
# Старт
# -----------------------
if __name__ == "__main__":
    main()
