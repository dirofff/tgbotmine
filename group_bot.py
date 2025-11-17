from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import datetime

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # вставь свой

# Проверка ответа на сообщение
def get_target_user(update):
    replied = update.message.reply_to_message
    if not replied:
        return None
    return replied.from_user

# ---------------------------
#       КИК
# ---------------------------
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_target_user(update)
    if not user:
        await update.message.reply_text("⚠️ Напиши команду *в ответ* на сообщение пользователя.")
        return

    try:
        await update.message.chat.ban_member(user.id)
        await update.message.reply_text(f"👢 Пользователь {user.full_name} кикнут!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# ---------------------------
#       БАН
# ---------------------------
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_target_user(update)
    if not user:
        await update.message.reply_text("⚠️ Напиши команду *в ответ* на сообщение пользователя.")
        return

    try:
        await update.message.chat.ban_member(user.id, until_date=None)
        await update.message.reply_text(f"⛔ Пользователь {user.full_name} забанен навсегда!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# ---------------------------
#       МУТ
# ---------------------------
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_target_user(update)
    if not user:
        await update.message.reply_text("⚠️ Напиши команду *в ответ* на сообщение.")
        return

    # Проверяем, указан ли таймер
    try:
        minutes = int(context.args[0]) if context.args else 10
    except ValueError:
        await update.message.reply_text("❗ Укажи время в минутах. Например: /mute 10")
        return

    until_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)

    permissions = ChatPermissions(can_send_messages=False)

    try:
        await update.message.chat.restrict_member(user.id, permissions=permissions, until_date=until_time)
        await update.message.reply_text(
            f"🔇 Пользователь {user.full_name} замучен на {minutes} мин."
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# ---------------------------
# Приветствие новых участников
# ---------------------------
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Привет, {member.full_name}! Добро пожаловать в чат!"
        )

# ---------------------------
# Запуск бота
# ---------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
