from telegram.ext import Application, MessageHandler, filters, ConversationHandler, \
    CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import asyncio
import json

count_puzzle = 1


async def get_help(update, context):
    await update.message.reply_text('С помощью нашего бота Вы можете практиковаться в развитии '
                                    'своих навыков решения шахматных задач. Это '
                                    'очень хорошо помогает в игре. Вы почувствуете это сами, когда '
                                    'после решения задач в партии сможете найти блестящий ход, '
                                    'который приведёт к победе.')


async def empty_function(update, context):
    await update.message.reply_text('Я не понимаю...')


async def get_start(update, context):
    with open('data/information.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        players = data['chess_players']
        training = data['chess_training']
        dict = data['chess_dictionary']
    context.user_data['chess_players'] = players
    context.user_data['chess_training'] = training
    context.user_data['chess_dictionary'] = dict
    reply_keyboard = [['/help', '/solve_puzzle']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text('Я бот-справочник', reply_markup=markup)
    return 0


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
    reply_keyboard = [['Ввести ход'], ['/d', '/e', '/f']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text(reply_markup=markup)
    count_puzzle += 1


async def chess_players(update, context):
    await update.message.reply_text("Про кого вы хотите узнать?"
                                    "Сейчас доступна информация о таких людях:\n"
                                    "\u2714 Гарри Каспаров\n"
                                    "\u2714 Анатолий Карпов\n"
                                    "\u2714 Магнус Карлсен\n"
                                    "\u2714 Бобби Фишер\n"
                                    "\u2714 Эмануил Ласкер\n"
                                    "\u2714 Михаил Ботвинник\n"
                                    "\u2714 Вера Менчик\n"
                                    "\u2714 Нона Гаприндашвили\n"
                                    "\u2714 Елизавета Быкова\n"
                                    "\u2714 Юдит Полгар\n"
                                    "\u2757Чтобы узнать о выбранном человеке введите"
                                    " только его фамилию.", reply_markup=ReplyKeyboardRemove())
    return 1


async def information_about_chess_players(update, context):
    response = update.message.text.strip().lower()
    chess_player = context.user_data['chess_players'].get(response, None)
    if chess_player:
        await context.bot.send_photo(
            update.message.chat_id, chess_player['photo'])
        await update.message.reply_text(chess_player['biography'])
    else:
        await update.message.reply_text("Проверьте правильность написания фамилии человека"
                                        " или убедитесь, что он есть в списке доступных")


async def training(update, context):
    if context.user_data.get('training level', -1) == -1:
        introduction = "Желаем удачного обучения!\n"
        context.user_data['training level'] = 0
    elif context.user_data.get('training level', -1) == 0:
        introduction = "Вы начинаете обучение сначала.\n"
    else:
        introduction = "Вы можете продолжить обучение.\n" \
                       "Если же вы хотите начать обучение сначала, " \
                       "то нажмите на соответствующую кнопку."
    introduction += "\nДля продолжения и переходов на следующий " \
                    'уровень нажимайте "▶ продолжить".'
    reply_keyboard = [['🔄 начать заново', '▶ продолжить']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(introduction, reply_markup=markup)
    return 2


async def chess_training(update, context):
    if update.message.text == '▶ продолжить':
        context.user_data['training level'] += 1
        if context.user_data['training level'] == 14:
            await update.message.reply_text(context.user_data['chess_training'][
                                                str(context.user_data['training level'])],
                                            reply_markup=ReplyKeyboardRemove())
            return 0
        if type(context.user_data['chess_training'][
                    str(context.user_data['training level'])]['text']) == list:
            texts = context.user_data['chess_training'][str(context.user_data[
                                                                'training level'])]['text']
            photo = context.user_data['chess_training'][str(context.user_data[
                                                                'training level'])]['photo']
            for i in range(len(texts)):
                await context.bot.send_photo(
                    update.message.chat_id, photo[i], caption=texts[i])
                await asyncio.sleep(5)
        else:
            await update.message.reply_text(
                context.user_data['chess_training'][str(context.user_data['training level'])][
                    'text'])
            await context.bot.send_photo(
                update.message.chat_id,
                context.user_data['chess_training'][str(context.user_data['training level'])][
                    'photo'])
    elif update.message.text == '🔄 начать заново':
        context.user_data['training level'] = 0
        await update.message.reply_text('Вы обнулили текущий прогресс')
    else:
        await update.message.reply_text('Данная функция не требует ввода.')


async def chess_dictionary(update, context):
    await update.message.reply_text('В данной функции у вас есть возможность'
                                    ' узнать определение какого либо шахматного термина.\n'
                                    'Введите запрос вида "Что такое <термин>?"\n'
                                    'И, если в словаре запрос найдется, вы увидите определение.'
                                    'Если нет, вы увидите соответствующее сообщение.')
    return 3


async def search_terms(update, context):
    req = update.message.text.lower()
    if 'что такое' in ' '.join(req.split()) and req[-1] == '?':
        terms = ' '.join(req.split()[2:])[:-1]
        definition = context.user_data['chess_dictionary'].get(terms, None)
        if definition:
            await update.message.reply_text(definition)
        else:
            await update.message.reply_text('В словаре ничего не нашлось...')
    else:
        await update.message.reply_text('Некорректный вид!\n'
                                        'Введите запрос вида "Что такое <термин>?"')


async def stop(update, context):
    await update.message.reply_text("Вы остановили функцию", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    TOKEN = '5898517881:AAHwSba7YG8Lh_RgX7Z82yQvuDYkocnWKJM'
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', get_start)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, empty_function)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, information_about_chess_players)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, chess_training)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_terms)]
        },
        fallbacks=[CommandHandler('stop', stop), CommandHandler("training", training),
                   CommandHandler("chess_players", chess_players),
                   CommandHandler("chess_dictionary", chess_dictionary)]
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', get_help))
    application.add_handler(CommandHandler('solve_puzzle', solve_puzzle))
    application.run_polling()


if __name__ == '__main__':
    main()
