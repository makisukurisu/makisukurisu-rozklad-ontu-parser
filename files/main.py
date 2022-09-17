import requests
from bs4 import BeautifulSoup

api_link = 'https://rozklad.ontu.edu.ua/guest_n.php'  # "АПИ"
cookies = {'notbot': 'ab709742d0971929fd95a7e0d618bc4c'}

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

faculty_name = input('Введите название факультета: ')
while True:
    if faculty_name in all_fcs_dict:
        break
    else:
        faculty_name = input('Факультет не найден, попробуйте ещё раз: ')

groups = requests.post(api_link, cookies=cookies, data={'facultyid': all_fcs_dict[faculty_name]})

groups_page = BeautifulSoup(groups.content.decode('utf-8'), 'html.parser')

all_groups = groups_page.find_all(attrs={'class': 'grp'})
all_groups_dict = {}
for group in all_groups:
    all_groups_dict.update({group.find(attrs={'class': 'branding-bar'}).string: group['data-id']})

for key in all_groups_dict.keys():
    print(key)

group_name = input('Введите название группы: ')
while True:
    if group_name in all_groups_dict:
        break
    faculty_name = input('Группа не найдена, попробуйте ещё раз: ')

schedule = requests.post(api_link, cookies=cookies, data={'groupid': all_groups_dict[group_name]})

schedule_page = BeautifulSoup(schedule.content.decode('utf-8'), 'html.parser')
table = schedule_page.find_all(attrs={'class': 'table'})
print(table)
if not table:
    exit(2)
with open('files/schedule.html', 'w', encoding='utf-8') as f:
    f.write(str(table[0]))
with open('files/full_resp.html', 'wb') as f:
    f.write(schedule.content)

# Ну и осталось:
'''
Обязательно:
    Распарсить таблицу во вменяемый формат данных (к примеру используя Pandas, чек parser.py)
        Замечание: тултипы (при наведении штуки) не попадают в текст используя Pandas, мейби можно решить
Опционально:
    Допускать использование show_all параметра (просмот расписание на всё время) (Хз как это удобно сделать в боте, если честно)
    Добавить поддержку https://rozklad.ontu.edu.ua/view_reassignment_guest.php (Пересдачи)
    Парсить объявления и файлы из ответа с параметром groupid
    ...
'''