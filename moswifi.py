import requests
import json
import pandas as pd

api_key_mosru = None


def extract_street(address: str):
    """
    Извлекаем улицу из переданной строки с адресом.
    В данном случае адреса уже достаточно чистые. В исходных строках компоненты адреса отделяются запятыми,
    улица всегда стоит на втором месте. Так что не мудрим, берем просто второй сплит.

    :param address: Строка с адресом
    :return: Наименование улицы
    """
    parts = address.split(',')
    if len(parts) >= 2:
        return (parts[1].strip())
    else:
        return None


if __name__ == '__main__':
    datasets = [
        {'local_id': 102277, 'onlne_id': 60788, 'name': 'Wi-Fi в библиотеках'},
        {'local_id': 102278, 'onlne_id': 60789, 'name': 'Wi-Fi в кинотеатрах'},
        {'local_id': 102279, 'onlne_id': 60790, 'name': 'Wi-Fi в культурных центрах'},
        # {'local_id': 4214, 'onlne_id': 861, 'name': 'Wi-Fi в парках'},
        {'local_id': 9776, 'onlne_id': 2756, 'name': 'Городской Wi-Fi'},
    ]

    # Если указан api_key для mos.ru, делаем запрос к онлайн-сервису.
    # Если не указан - работаем с локальной копией датасетов.

    streets = []
    for ds_desc in datasets:
        # Получаем датасет в json
        if api_key_mosru is not None:
            r = requests.get(f'https://apidata.mos.ru/v1/datasets/{ds_desc["onlne_id"]}/rows',
                             {'api_key': api_key_mosru})
            data = r.json()
        else:
            with open(f'data/data-{ds_desc["local_id"]}.json', 'r', encoding='cp1251') as f:
                data = json.load(f)

        # Проходимся по записям и извлекаем имена улиц
        for rec in data:
            addr = None
            street = None
            cells = rec.get('Cells', None)
            if cells is None:
                cells = rec
            if 'Location' in cells.keys():
                addr = cells['Location']
                street = extract_street(addr)
            elif 'Address' in cells.keys():
                addr = cells['Address']
                street = extract_street(addr)
            elif 'ParkName' in cells.keys():
                addr = cells['ParkName']
                street = addr
            if street is not None:
                streets.append(street)

    # Группируем по имени улицы и считаем количество по группам.
    # Используем pandas для этого, хотя для такого простого таска можно, наверное, обойтись и без них.
    df = pd.DataFrame(streets, columns=['street'])
    df = df.groupby(['street']).size().reset_index(name='counts')

    # Сортируем и выводим топ-5 в консоль
    print('\n'.join(df.sort_values('counts', ascending=False).head(5).street.to_list()))

