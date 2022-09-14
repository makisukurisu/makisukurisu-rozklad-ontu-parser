import requests
from bs4 import BeautifulSoup

api_link = 'https://rozklad.ontu.edu.ua/guest_n.php'  # "АПИ"
cookies = {'notbot': 'f94a553c09e443b93cd1de89b8003938'}

# Сейчас работает, TTL - неизвестен (взял из реального запроса)
# Возможно существует вариант настроить WhiteList в админке W2AF

home_page = requests.get(api_link, cookies=cookies)

set_cookies = home_page.headers.get('Set-Cookie')
# Для поддержания единства ID в запросах
session_id = None
if set_cookies:
    tmp = set_cookies.split('PHPSESSID=')
    if tmp:
        tmp = tmp[1]
        tmp = tmp.split(';')
        if tmp:
            tmp = tmp[0]
    session_id = tmp or None
if not session_id:
    exit(1)
    # Закончить работу если нет сессии
cookies['PHPSESSID'] = session_id
# В дальнейшем везде используется

faculty_page = BeautifulSoup(home_page.content.decode('utf-8'), 'html.parser')

all_fcs = faculty_page.find_all(attrs={'class': 'fc'})
all_fcs_dict = {}
for fc in all_fcs:
    all_fcs_dict[fc.span.string] = fc['data-id']

for key in all_fcs_dict.keys():
    print(key)
    # Выводит названия всех факультетов (для поиска)

find_id = input('Введите название факультета: ')

groups = requests.post(api_link, cookies=cookies, data={'facultyid':all_fcs_dict[find_id]})
# Лень добавлять проверки, не очепятайтесь, пж

groups_page = BeautifulSoup(groups.content.decode('utf-8'), 'html.parser')

all_groups = groups_page.find_all(attrs={'class': 'grp'})
for group in all_groups:
    print(group.find(attrs={'class': 'branding-bar'}).string, group['data-id'])

# Ну и осталось:
'''
Обязательно:
    Сделать запрос с groupid из 49 строки
    Распарсить таблицу во вменяемый формат данных (к примеру используя Pandas, чек parser.py)
        Замечание: тултипы (при наведении штуки) не попадают в текст используя Pandas, мейби можно решить
Опционально:
    Допускать использование show_all параметра (просмот расписание на всё время) (Хз как это удобно сделать в боте, если честно)
    Добавить поддержку https://rozklad.ontu.edu.ua/view_reassignment_guest.php (Пересдачи)
    Парсить объявления и файлы из ответа с параметром groupid
    ...
'''