from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from datetime import datetime, timedelta

BOT_TOKEN = "8552286080:AAHyr9PzZhzZ3RD8l5Sh8GU7I0F9Xtzmbss"  # вставь сюда токен
warnings_db = {}  # словарь для хранения предупреждений


# -----------------------------
# Вспомогательные функции
# -----------------------------
def add_warning(user_id):
    if user_id not in warnings_db:
        warnings_db[user_id] = 0
    warnings_db[user_id] += 1
    return warnings_db[user_id]


def clear_user_warnings(user_id):
    warnings_db[user_id] = 0


# -----------------------------
# Команды администрирования
# -----------------------------
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text("⚠️ Ответьте на сообщение пользователя, которого хотите кикнуть.")
        return

    user = msg.from_user
    chat_id = update.message.chat.id

    try:
        await context.bot.ban_chat_member(chat_id, user.id)
        await context.bot.unban_chat_member(chat_id, user.id)  # чтобы можно было вернуться
        await update.message.reply_text(f"👢 Пользователь {user.full_name} был кикнут.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text("⚠️ Ответьте на сообщение пользователя, которого хотите забанить.")
        return

    user = msg.from_user
    chat_id = update.message.chat.id

    try:
        await context.bot.ban_chat_member(chat_id, user.id)
        await update.message.reply_text(f"⛔ Пользователь {user.full_name} забанен.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Используйте: /unban ID_пользователя")
        return

    chat_id = update.message.chat.id
    user_id = int(context.args[0])

    try:
        await context.bot.unban_chat_member(chat_id, user_id)
        await update.message.reply_text(f"🔓 Пользователь {user_id} разбанен.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text("⚠️ Ответьте на сообщение пользователя, которого хотите замьютить.")
        return

    user = msg.from_user
    chat_id = update.message.chat.id

    until = datetime.now() + timedelta(days=7)

    try:
        await context.bot.restrict_chat_member(
            chat_id,
            user.id,
            permissions={"can_send_messages": False},
            until_date=until
        )
        await update.message.reply_text(f"🔇 {user.full_name} получил мут на 7 дней.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text("⚠️ Ответьте на сообщение пользователя, чтобы снять мут.")
        return

    user = msg.from_user
    chat_id = update.message.chat.id

    try:
        await context.bot.restrict_chat_member(
            chat_id,
            user.id,
            permissions={"can_send_messages": True}
        )
        await update.message.reply_text(f"🔊 Мут снят с {user.full_name}.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


# -----------------------------
# СИСТЕМА ПРЕДУПРЕЖДЕНИЙ
# -----------------------------
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text("⚠️ Ответьте на сообщение, чтобы выдать предупреждение.")
        return

    user = msg.from_user
    chat_id = update.message.chat.id

    warns = add_warning(user.id)

    await update.message.reply_text(f"⚠️ Предупреждение {warns}/3 для {user.full_name}")

    if warns >= 3:
        # Мут на 7 дней
        until = datetime.now() + timedelta(days=7)
        await context.bot.restrict_chat_member(
            chat_id,
            user.id,
            permissions={"can_send_messages": False},
            until_date=until
        )
        await update.message.reply_text(
            f"🔇 {user.full_name} получил мут на 7 дней за 3 предупреждения!"
        )
        clear_user_warnings(user.id)


async def warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text("Ответьте на сообщение пользователя.")
        return

    user = msg.from_user
    warns = warnings_db.get(user.id, 0)
    await update.message.reply_text(f"У {user.full_name} предупреждений: {warns}/3")


async def clearwarns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text("Ответьте на сообщение, чтобы очистить предупреждения.")
        return

    user = msg.from_user
    clear_user_warnings(user.id)

    await update.message.reply_text(f"♻️ Предупреждения для {user.full_name} очищены.")


# -----------------------------
# Приветствие новых участников
# -----------------------------
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"👋 Добро пожаловать, {member.full_name}!")


# -----------------------------
# ЗАПУСК БОТА
# -----------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("warns", warns))
    app.add_handler(CommandHandler("clearwarns", clearwarns))

    # Приветствие
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet))

    print("Бот запущен…")
    app.run_polling()


if __name__ == "__main__":
    main()

