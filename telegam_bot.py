from telegram.ext import Application, MessageHandler, filters, ConversationHandler, \
    CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import asyncio
import json
import random
import pymorphy2


async def solving_puzzles(update, context):
    cnt = context.user_data['cnt']
    chat_id = update.effective_message.chat_id
    if cnt > 20:
        await update.message.reply_text('К сожалению, на данный момент больше нет задач. Но'
                                        ' со временем они будут добавляться!',
                                        reply_markup=ReplyKeyboardRemove())
        return 0
    if cnt % 2 == 1:
        await context.bot.sendPhoto(chat_id, photo=f'static/img/puzzles/puzzle_{cnt}.png',
                                    caption='Найди лучший ход за белых')
    else:
        await context.bot.sendPhoto(chat_id, photo=f'static/img/puzzles/puzzle_{cnt}.png',
                                    caption='Найди лучший ход за чёрных')
    reply_keyboard = [['Следующая задача'], ['Показать ответ']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text('Введи ход в формате <клетка-клетка>', reply_markup=markup)
    return 7


async def puzzles(update, context):
    cnt = context.user_data['cnt']
    answer = context.user_data['solving_puzzles'][str(cnt)][0]
    req = update.message.text.strip().lower()
    chat_id = update.effective_message.chat_id
    if req == 'следующая задача':
        context.user_data['cnt'] += 1
        cnt = context.user_data['cnt']
        if context.user_data['cnt'] > 20:
            await update.message.reply_text('К сожалению, на данный момент больше нет задач. Но'
                                            ' со временем они будут добавляться!',
                                            reply_markup=ReplyKeyboardRemove())
            return 0
        if cnt % 2 == 1:
            await context.bot.sendPhoto(chat_id, photo=f'static/img/puzzles/puzzle_{cnt}.png',
                                        caption='Найди лучший ход за белых')
        else:
            await context.bot.sendPhoto(chat_id, photo=f'static/img/puzzles/puzzle_{cnt}.png',
                                        caption='Найди лучший ход за чёрных')
    elif req == 'показать ответ':
        await update.message.reply_text(f'Правильный ответ: {answer}.'
                                        f' {context.user_data["solving_puzzles"][str(cnt)][1]}')
    else:
        if len(req.split('-')) != 2:
            await update.message.reply_text(f'Введи ход в формате <клетка-клетка>')
        else:
            if req == answer:
                n = str(cnt)
                await update.message.reply_text(f'Да, это правильный ответ!'
                                                f' {context.user_data["solving_puzzles"][n][1]}')
            else:
                await update.message.reply_text('Неверно. Попробуйте еще.')


async def get_help(update, context):
    await update.message.reply_text('С помощью нашего бота Вы можете практиковаться в развитии '
                                    'своих навыков решения шахматных задач. Это '
                                    'очень хорошо помогает в игре. Вы почувствуете это сами, когда '
                                    'после решения задач в партии сможете найти блестящий ход, '
                                    'который приведёт к победе. А список всех функций вы можете'
                                    ' найти в меню.')


async def empty_function(update, context):
    await update.message.reply_text('Я не понимаю...')


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
        if context.user_data['training level'] >= 14:
            await update.message.reply_text(context.user_data['chess_training'][
                                                str(14)],
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
                                    'Если нет, вы увидите соответствующее сообщение.\n'
                                    'Все термины, которые есть в словаре, доступны при вводе'
                                    ' "все термины"!', reply_markup=ReplyKeyboardRemove())
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
    elif 'все термины' == req:
        terms = 'Сейчас доступны такие термины: ' + '\n'
        terms += ', '.join(context.user_data['chess_dictionary'].keys()) + '.'
        await update.message.reply_text(terms)
    else:
        await update.message.reply_text('Некорректный вид!\n'
                                        'Введите запрос вида "Что такое <термин>?"')


async def start(update, context):
    with open('data/information.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        players = data['chess_players']
        training = data['chess_training']
        dict = data['chess_dictionary']
        facts = data['interesting_facts']
        debuts = data['debuts']
        puzzles = data['solving_puzzles']
    context.user_data['chess_players'] = players
    context.user_data['chess_training'] = training
    context.user_data['chess_dictionary'] = dict
    context.user_data['interesting_facts'] = facts
    context.user_data['debuts'] = debuts
    context.user_data['solving_puzzles'] = puzzles
    context.user_data['cnt'] = 1
    await update.message.reply_text('Я бот Стратег. Я могу рассказать вам многое о шахматах,'
                                    ' игроках, научить вас играть и'
                                    ' потренировать ваше навыки в игре! Все функции доступны'
                                    ' в меню!', reply_markup=ReplyKeyboardRemove())
    return 0


async def interesting_facts(update, context):
    reply_keyboard = [['\u265f\ufe0f случайный факт']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    if __name__ == '__main__':
        await update.message.reply_text("Чтобы узнать случайный факт о шахматах"
                                        " - нажмите на кнопку!", reply_markup=markup)
    return 5


async def random_fact(update, context):
    if update.message.text == '\u265f\ufe0f случайный факт':
        if len(context.user_data['interesting_facts']) == 0:
            await update.message.reply_text('На этом интересные факты закончились. '
                                            'Ждите обновлений!', reply_markup=ReplyKeyboardRemove())
            return 0
        fact = random.choice(context.user_data['interesting_facts'])
        index = context.user_data['interesting_facts'].index(fact)
        context.user_data['interesting_facts'].pop(index)
        if type(fact) == str:
            await update.message.reply_text(fact)
        else:
            await context.bot.send_photo(update.message.chat_id, fact[1], caption=fact[0])
    else:
        await update.message.reply_text('Данная функция не требует ввода.')


async def chess_debuts(update, context):
    reply_keyboard = [['Открытые дебюты', 'Полуоткрытые дебюты'], ['Закрытые и полузакрытые дебюты',
                                                                   'Шахматные гамбиты']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Дебют – это начальная стадия шахматной"
                                    " партии, во время которой игроки могут делать продуманные"
                                    " заранее ходы. Успешный дебют позволяет игроку получить"
                                    " перевес с первых ходов.\n"
                                    "Открытые дебюты – большая группа, целый класс дебютов,"
                                    " возникающих поле первого хода 1. е2-е4 е7-е5\n"
                                    "К полуоткрытым относятся все дебюты, в которых черные в ответ"
                                    " на 1.е2-е4 выбирают другой ход, кроме 1… е7-е5\n"
                                    "Полузакрытые дебюты — дебюты, начинающиеся ходом"
                                    " 1. d2-d4 со стороны белых и любым ходом, кроме 1…d7-d5,"
                                    " со стороны чёрных. Закрытые дебюты — дебюты,"
                                    " где первый ход белых не 1. e2-e4.\n"
                                    "Гамбит – разновидность дебюта, или дебютный вариант,"
                                    " в котором один из игроков готов нести материальные"
                                    " жертвы ради достижения своих целей.\n"
                                    "В данной функции у вас есть возможность познакомиться"
                                    " с некоторыми примерами каждого вида."
                                    " Для этого нажмите на кнопку интересующего вида."
                                    " Вам будет предоставлен список.\n"
                                    "\u2757Чтобы получить корректный ответ введите название"
                                    " так же, как оно написано в списке.", reply_markup=markup)
    return 6


async def debuts(update, context):
    req = update.message.text
    req = req[0].upper() + req[1:]
    if req in ['Открытые дебюты', 'Полуоткрытые дебюты', 'Закрытые и полузакрытые дебюты',
               'Шахматные гамбиты']:
        arr = context.user_data['debuts'][req].keys()
        list_debuts = f'На данный момент в разделе "{req}" доступны такие дебюты:' + " \n \u2714" \
                      + "\n \u2714".join(arr)
        await update.message.reply_text(list_debuts)
        context.user_data['now_chapter'] = req
    else:
        response = context.user_data['debuts'][context.user_data['now_chapter']].get(req, None)
        if response is not None:
            await context.bot.send_photo(update.message.chat_id, response['photo'],
                                         caption=response['text'])
        else:
            await update.message.reply_text(f'Убедитесь что дебют с таким названием есть в разделе'
                                            f" '{context.user_data['now_chapter']}'"
                                            f" или проверьте правильность написания.")


def main():
    TOKEN = '5898517881:AAHwSba7YG8Lh_RgX7Z82yQvuDYkocnWKJM'
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, empty_function)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, information_about_chess_players)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, chess_training)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_terms)],
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, random_fact)],
            6: [MessageHandler(filters.TEXT & ~filters.COMMAND, debuts)],
            7: [MessageHandler(filters.TEXT & ~filters.COMMAND, puzzles)]
        },
        fallbacks=[CommandHandler("training", training),
                   CommandHandler("chess_players", chess_players),
                   CommandHandler("chess_dictionary", chess_dictionary),
                   CommandHandler("interesting_facts", interesting_facts),
                   CommandHandler("chess_debuts", chess_debuts),
                   CommandHandler("solving_puzzles", solving_puzzles)])
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', get_help))
    application.run_polling()


if __name__ == '__main__':
    main()
