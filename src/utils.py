def item_to_str(item: dict) -> str:
    item_name = item['name'] if 'size' not in item else item['name'] + '/' + item['size']['name']
    item_cost = item['cost'] if 'size' not in item else item['size']['cost']
    return f'{item_name} - {item_cost}'

def order_to_str(order: dict) -> str:
    return f'Вартість: {order["order_cost"]} ,Тип:{"Готівка" if order["order_type"] == "money" else "Картка"} '


def split_in_two_columns(buttons: list) -> tuple:
    result = list()
    for i in range(0, len(buttons), 2):
        result.append(buttons[i:i + 2])
    return tuple(result)


def split_in_three_columns(buttons: list) -> tuple:
    result = list()
    for i in range(0, len(buttons), 3):
        result.append(buttons[i:i + 3])
    return tuple(result)


def count_cost(items: list) -> float:
    return sum(map(lambda item: item['cost'] if 'cost' in item else item['size']['cost']
                   , items))
