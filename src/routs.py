import datetime
import logging

from emoji import emojize, demojize
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from src.utils import item_to_str, count_cost, split_in_two_columns, order_to_str

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Вітаю в кавовому менеджері.", reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Розпочати робочій день")]]))


async def help(update: Update, context: CallbackContext):
    await update.message.reply_text("""Available Commands :-
    /youtube - To get the youtube URL
    /linkedin - To get the LinkedIn profile URL
    /gmail - To get gmail URL
    /geeks - To get the GeeksforGeeks URL""")


async def shift_started(update: Update, context: CallbackContext):
    if update.message.text == 'Розпочати робочій день':
        context.user_data['shift'] = {'orders': list()}
        await update.message.reply_text("Вкажіть готівку у касі.")
        context.user_data['next_message_status'] = 'money'
        return
    elif demojize(update.message.text) == 'Створити нове замовлення:hot_beverage:':
        context.user_data[f'current_order_{update.message.message_id + 1}'] = list()
        context.user_data[f'order_status_{update.message.message_id + 1}'] = 'coffee'
        logic_keyboard = [InlineKeyboardButton(emojize(':pencil:'), callback_data='edit'),
                          InlineKeyboardButton(emojize(':cross_mark:'), callback_data='cancel')]
        keyboard = [InlineKeyboardButton(item['name'], callback_data=i) for i, item in
                    enumerate(context.bot_data['bar']['coffee'])]
        await update.message.reply_text('Створити замовлення',
                                        reply_markup=InlineKeyboardMarkup(
                                            [*split_in_two_columns(keyboard), logic_keyboard]))
        return
    elif demojize(update.message.text) == 'Видалити замовлення:pencil:':
        order_list_keyboard = [
            [InlineKeyboardButton(emojize(f'{order_to_str(order)} :cross_mark:'), callback_data=f'remove_order_{i}')]
            for i, order in enumerate(context.user_data[f'shift']['orders'])]
        logic_keyboard = [InlineKeyboardButton(emojize(':check_mark_button:'), callback_data=f'close')]
        order_list_keyboard.append(logic_keyboard)
        await update.message.reply_text('Видалити замовлення', reply_markup=InlineKeyboardMarkup(order_list_keyboard))
        return
    elif demojize(update.message.text) == 'Завершити робочій день:cross_mark:':
        total_for_shift_money = sum(map(lambda order: order['order_cost'],
                                        filter(lambda order: order['order_type'] == 'money',
                                               context.user_data['shift']['orders'])))
        total_for_shift_credit_card = sum(map(lambda order: order['order_cost'],
                                              filter(lambda order: order['order_type'] == 'credit_card',
                                                     context.user_data['shift']['orders'])))
        order_list_total = sum(list(map(lambda order: order['order_list'], context.user_data['shift']['orders'])), [])
        total_caps_xs = list(filter(lambda cap: cap['name'] == 'XS', context.user_data['shift']['caps']))[0]['count'] - sum(
            map(lambda order: 1,
                filter(lambda order: 'size' in order and order['size']['name'] == 'XS', order_list_total)))
        total_caps_s = list(filter(lambda cap: cap['name'] == 'S', context.user_data['shift']['caps']))[0]['count'] - sum(
            map(lambda order: 1,
                filter(lambda order: 'size' in order and order['size']['name'] == 'S', order_list_total)))
        total_caps_m = list(filter(lambda cap: cap['name'] == 'M', context.user_data['shift']['caps']))[0]['count'] - sum(
            map(lambda order: 1,
                filter(lambda order: 'size' in order and order['size']['name'] == 'M', order_list_total)))
        total_caps_l = list(filter(lambda cap: cap['name'] == 'L', context.user_data['shift']['caps']))[0]['count'] - sum(
            map(lambda order: 1,
                filter(lambda order: 'size' in order and order['size']['name'] == 'l', order_list_total)))
        total_caps_xl = list(filter(lambda cap: cap['name'] == 'XL', context.user_data['shift']['caps']))[0]['count'] - sum(
            map(lambda order: 1,
                filter(lambda order: 'size' in order and order['size']['name'] == 'XL', order_list_total)))
        await update.message.reply_text(
            f'+---------------\n|{datetime.date.today().strftime("%d.%m.%Y")}\n+---------------\n|Готівка: {total_for_shift_money}\n|Картка: {total_for_shift_credit_card}\n|Загальна каса: {total_for_shift_credit_card + total_for_shift_money}\n|Залишок в касі: {context.user_data["shift"]["money"] + total_for_shift_money}\n+---------------\n|Стаканчики\n+---------------\n|XL: {total_caps_xl}\n|L: {total_caps_l}\n|M: {total_caps_m}\n|S: {total_caps_s}\n|XS: {total_caps_xs}\n+---------------',
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Розпочати робочій день")]]))
        return
    elif 'next_message_status' in context.user_data and context.user_data['next_message_status'] == 'money':
        context.user_data['shift']['money'] = int(update.message.text)
        await update.message.reply_text('Вкажіть кількість стаканчиків:\nXS,S,M,L,XL')
        context.user_data['next_message_status'] = 'caps'
        return
    elif 'next_message_status' in context.user_data and context.user_data['next_message_status'] == 'caps':
        xs, s, m, l, xl = list(map(int, update.message.text.split(',', 5)))
        context.user_data['shift']['caps'] = [
            {'name': 'XS',
             'count': xs},
            {'name': 'S',
             'count': s},
            {'name': 'M',
             'count': m},
            {'name': 'L',
             'count': l},
            {'name': 'XL',
             'count': xl}
        ]
        del context.user_data['next_message_status']
        await update.message.reply_text('Створіть своє перше замовлення)', reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(emojize("Створити нове замовлення:hot_beverage:")),
              KeyboardButton(emojize("Видалити замовлення:pencil:"))],
             [KeyboardButton(emojize("Завершити робочій день:cross_mark:"))]]))
        return
    elif 'next_message_id' in context.user_data and context.user_data['next_message_id'] != 'None':
        message_id = context.user_data['next_message_id']
        context.user_data['next_message_id'] = 'None'
        total_cost = count_cost(context.user_data[f"current_order_{message_id}"])
        await update.get_bot().edit_message_text(chat_id=update.effective_chat.id, message_id=message_id,
                                                 text=f'+---------------\n|Ваше замовлення\n+---------------\n|' + '\n|'.join(
                                                     list(map(item_to_str,
                                                              context.user_data[f"current_order_{message_id}"]))) +
                                                      f'\n+---------------\n|Вартість: {total_cost}\n+---------------\n|Внесено: {update.message.text}\n+---------------\n|Решта: {int(update.message.text) - total_cost}\n+---------------')
        context.user_data[f'shift']['orders'].append({'order_type': 'money',
                                                      'order_cost': total_cost,
                                                      'order_list': context.user_data[
                                                          f'current_order_{message_id}'].copy()})
        del context.user_data[f'current_order_{message_id}']
        del context.user_data[f'order_status_{message_id}']
        return
    await update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


async def unknown_text(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)
