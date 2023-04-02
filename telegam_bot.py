from telegram.ext import Application, MessageHandler, filters, ConversationHandler, \
    CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

count_puzzle = 1


async def get_help(update, context):
    await update.message.reply_text('С помощью нашего бота Вы можете практиковаться в развитии '
                                    'своих навыков решения шахматных задач. Это '
                                    'очень хорошо помогает в игре. Вы почувствуете это сами, когда '
                                    'после решения задач в партии сможете найти блестящий ход, '
                                    'который приведёт к победе.')


async def get_start(update, context):
    reply_keyboard = [['/help', '/solve_puzzle']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text('Я бот-справочник', reply_markup=markup)


async def solve_puzzle(update, context):
    global count_puzzle
    chat_id = update.effective_message.chat_id
    if count_puzzle > 10:
        await update.message.reply_text('К сожалению, на данный момент больше нет задач. Но'
                                        ' со временем они будут добавляться!')
    await context.bot.sendPhoto(chat_id, photo=f'puzzle_{count_puzzle}.png')
    if count_puzzle % 2 == 1:
        await update.message.reply_text(f'Найди лучший ход за белых')
    else:
        await update.message.reply_text(f'Найди лучший ход за чёрных')
    reply_keyboard = [['/a', '/b', '/c'], ['/d', '/e', '/f']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text(reply_markup=markup)
    count_puzzle += 1


def main():
    TOKEN = '5898517881:AAHwSba7YG8Lh_RgX7Z82yQvuDYkocnWKJM'
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('help', get_help))
    application.add_handler(CommandHandler('start', get_start))
    application.add_handler(CommandHandler('solve_puzzle', solve_puzzle))
    application.run_polling()


if __name__ == '__main__':
    main()
