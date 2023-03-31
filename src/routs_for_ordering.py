import re

from emoji import emojize
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.utils import item_to_str, split_in_two_columns, count_cost, order_to_str


def create_logic_keyboard():
    return [InlineKeyboardButton(emojize(':pencil:'), callback_data='edit'),
            InlineKeyboardButton(emojize(':next_track_button:'), callback_data='cancel')]


def create_approve_keyboard():
    return [InlineKeyboardButton('Підтвердити замовлення', callback_data='order_approve')]


def create_coffee_keyboard(context):
    coffee_keyboard = [InlineKeyboardButton(item['name'], callback_data=i) for i, item in
                       enumerate(context.bot_data['bar']['coffee'])]
    return [*split_in_two_columns(coffee_keyboard), create_logic_keyboard(), create_approve_keyboard()]


def create_additives_keyboard(context):
    additives_keyboard = [InlineKeyboardButton(item['name'], callback_data=i) for i, item in
                          enumerate(context.bot_data['bar']['additives'])]
    return [*split_in_two_columns(additives_keyboard), create_logic_keyboard(), create_approve_keyboard()]


def create_sweets_keyboard(context):
    sweets_keyboard = [InlineKeyboardButton(item['name'], callback_data=i) for i, item in
                       enumerate(context.bot_data['bar']['sweets'])]
    return [*split_in_two_columns(sweets_keyboard), create_logic_keyboard(), create_approve_keyboard()]


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coffee_keyboard = create_coffee_keyboard(context)
    additives_keyboard = create_additives_keyboard(context)
    sweets_keyboard = create_sweets_keyboard(context)

    query = update.callback_query
    await query.answer()
    callback_data = int(query.data) if query.data.isdigit() else query.data
    message_id = query.message.message_id

    if callback_data == 'edit':
        items_keyboard = [
            [InlineKeyboardButton(emojize(f'{item_to_str(item)} :cross_mark:'), callback_data=f'remove_item_{i}')] for
            i, item in enumerate(context.user_data[f'current_order_{message_id}'])]
        logic_keyboard = [InlineKeyboardButton(emojize(':check_mark_button:'), callback_data=f'save')]
        items_keyboard.append(logic_keyboard)
        await query.edit_message_text(text=f'Відредагувати замовлення',
                                      reply_markup=InlineKeyboardMarkup(items_keyboard))

        return
    elif callback_data == 'save':
        context.user_data[f'order_status_{message_id}'] = 'coffee'
        await query.edit_message_text(
            text=f'+---------------\n|Ваше замовлення\n+---------------\n|' + '\n|'.join(
                list(map(item_to_str, context.user_data[f"current_order_{message_id}"]))) +
                 f'\n+---------------\n|Вартість: {count_cost(context.user_data[f"current_order_{message_id}"])}\n+---------------',
            reply_markup=InlineKeyboardMarkup(coffee_keyboard))

        return
    elif str(callback_data).startswith('remove_item_'):
        item_id_to_remove = int(re.search('(?<=remove_item_)\d', callback_data).group())
        context.user_data[f'current_order_{message_id}'].remove(
            context.user_data[f'current_order_{message_id}'][item_id_to_remove])
        items_keyboard = [
            [InlineKeyboardButton(emojize(f'{item_to_str(item)} :cross_mark:'), callback_data=f'remove_{i}')] for
            i, item in
            enumerate(context.user_data[f'current_order_{message_id}'])]
        logic_keyboard = [InlineKeyboardButton(emojize(':check_mark_button:'), callback_data=f'save')]
        items_keyboard.append(logic_keyboard)
        await query.edit_message_text(text=f'Відредагувати замовлення',
                                      reply_markup=InlineKeyboardMarkup(items_keyboard))

        return
    elif str(callback_data).startswith('remove_order_'):
        order_to_remove_id = int(re.search('(?<=remove_order_)\d', callback_data).group())
        context.user_data['shift']['orders'].remove(context.user_data['shift']['orders'][order_to_remove_id])
        order_list_keyboard = [
            [InlineKeyboardButton(emojize(f'{order_to_str(order)} :cross_mark:'), callback_data=f'remove_order_{i}')]
            for i, order in enumerate(context.user_data[f'shift']['orders'])]
        logic_keyboard = [InlineKeyboardButton(emojize(':check_mark_button:'), callback_data=f'close')]
        order_list_keyboard.append(logic_keyboard)
        await query.edit_message_text(text='Видалити замовлення',
                                      reply_markup=InlineKeyboardMarkup(order_list_keyboard))

        return
    elif callback_data == 'close':
        await query.edit_message_text(text='+---------------\n|' + '\n|'.join(
            list(map(order_to_str, context.user_data['shift']['orders']))) + '\n+---------------')

        return
    elif callback_data == 'order_approve':
        question_keyboard = [InlineKeyboardButton(emojize(':check_mark_button:'), callback_data='confirm_order'),
                             InlineKeyboardButton(emojize(':cross_mark:'), callback_data='save')]
        await query.edit_message_text(
            text=f'+---------------\n|Ваше замовлення\n+---------------\n|' + '\n|'.join(
                list(map(item_to_str, context.user_data[f"current_order_{message_id}"]))) +
                 f'\n+---------------\n|Вартість: {count_cost(context.user_data[f"current_order_{message_id}"])}\n+---------------',
            reply_markup=InlineKeyboardMarkup([question_keyboard]))

        return
    elif callback_data == 'confirm_order':
        question_keyboard = [InlineKeyboardButton(emojize('Готівка:money_with_wings:'), callback_data='money'),
                             InlineKeyboardButton(emojize('Картка:credit_card:'), callback_data='credit_card')]
        await query.edit_message_text(text=f'До сплати: {count_cost(context.user_data[f"current_order_{message_id}"])}',
                                      reply_markup=InlineKeyboardMarkup([question_keyboard]))

        return
    elif callback_data == 'money':
        context.user_data[f'next_message_id'] = message_id
        await query.edit_message_text(text='Введіть отриману готівку')

        return
    elif callback_data == 'credit_card':
        total_cost = count_cost(context.user_data[f"current_order_{message_id}"])
        await query.edit_message_text(f'+---------------\n|Ваше замовлення\n+---------------\n|' + '\n|'.join(
            list(map(item_to_str, context.user_data[f"current_order_{message_id}"]))) +
                                      f'\n+---------------\n|Вартість: {total_cost}\n+---------------')
        context.user_data[f'shift']['orders'].append({'order_type': 'credit_card',
                                                      'order_cost': total_cost,
                                                      'order_list': context.user_data[
                                                          f'current_order_{message_id}'].copy()})
        del context.user_data[f'current_order_{message_id}']
        del context.user_data[f'order_status_{message_id}']

        return
    elif callback_data == 'cancel':
        if context.user_data[f'order_status_{message_id}'] == 'coffee':
            context.user_data[f'order_status_{message_id}'] = 'additives'
            keyboard_to_reply = additives_keyboard
        elif context.user_data[f'order_status_{message_id}'] == 'additives':
            context.user_data[f'order_status_{message_id}'] = 'sweets'
            keyboard_to_reply = sweets_keyboard
        elif context.user_data[f'order_status_{message_id}'] == 'sweets':
            context.user_data[f'order_status_{message_id}'] = 'coffee'
            keyboard_to_reply = coffee_keyboard
        await query.edit_message_text(
            text=f'+---------------\n|Ваше замовлення\n+---------------\n|' + '\n|'.join(
                list(map(item_to_str, context.user_data[f"current_order_{message_id}"]))) +
                 f'\n+---------------\n|Вартість: {count_cost(context.user_data[f"current_order_{message_id}"])}\n+---------------',
            reply_markup=InlineKeyboardMarkup(keyboard_to_reply))

        return
    elif context.user_data[f'order_status_{message_id}'] == 'coffee':
        if len(context.bot_data['bar']['coffee'][callback_data]['sizes']) == 1:
            selected_coffee = {'name': context.bot_data['bar']['coffee'][callback_data]['name'],
                               'size': context.bot_data['bar']['coffee'][callback_data]['sizes'][0]}
            context.user_data[f'current_order_{message_id}'].append(selected_coffee)
            context.user_data[f'order_status_{message_id}'] = 'additives'
            await query.edit_message_text(
                text=f'Обрана кава {selected_coffee["name"]} коштує: {selected_coffee["size"]["cost"]}',
                reply_markup=InlineKeyboardMarkup(additives_keyboard))
        else:
            context.user_data[f'order_status_{message_id}'] = 'size'
            coffee_size_keyboard = [InlineKeyboardButton(size['name'], callback_data=f'{callback_data}/{i}') for i, size
                                    in
                                    enumerate(context.bot_data['bar']['coffee'][callback_data]['sizes'])]
            await query.edit_message_text(
                text=f'Будьласка оберіть розмір кави {context.bot_data["bar"]["coffee"][callback_data]["name"]}',
                reply_markup=InlineKeyboardMarkup([coffee_size_keyboard]))

        return
    elif context.user_data[f'order_status_{message_id}'] == 'size':
        coffee_name, coffee_size = list(map(int, callback_data.split('/', 2)))
        selected_coffee = {'name': context.bot_data['bar']['coffee'][coffee_name]['name'],
                           'size': context.bot_data['bar']['coffee'][coffee_name]['sizes'][coffee_size]}
        context.user_data[f'current_order_{message_id}'].append(selected_coffee)
        context.user_data[f'order_status_{message_id}'] = 'additives'
        await query.edit_message_text(
            text=f'Обрана кава {selected_coffee["name"]}/{selected_coffee["size"]["name"]} коштує: {selected_coffee["size"]["cost"]}',
            reply_markup=InlineKeyboardMarkup(additives_keyboard))

        return
    elif context.user_data[f'order_status_{message_id}'] == 'additives':
        selected_additive = context.bot_data['bar']['additives'][callback_data]
        context.user_data[f'current_order_{message_id}'].append(selected_additive)
        context.user_data[f'order_status_{message_id}'] = 'additives'
        await query.edit_message_text(
            text=f'Обрані додатки {selected_additive["name"]} коштують: {selected_additive["cost"]}',
            reply_markup=InlineKeyboardMarkup(additives_keyboard))

        return
    elif context.user_data[f'order_status_{message_id}'] == 'sweets':
        selected_sweet = context.bot_data['bar']['sweets'][callback_data]
        context.user_data[f'current_order_{message_id}'].append(selected_sweet)
        context.user_data[f'order_status_{message_id}'] = 'sweets'
        await query.edit_message_text(
            text=f'Обрані солодощі {selected_sweet["name"]} коштують: {selected_sweet["cost"]}',
            reply_markup=InlineKeyboardMarkup(sweets_keyboard))

        return
