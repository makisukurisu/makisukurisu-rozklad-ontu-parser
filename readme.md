# Rozklad ONTU Pareser [![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
Library on [PyPi](https://pypi.org/project/rozklad-ontu-parser-MakisuKurisu/)

Installation: `pip install rozklad-ontu-parser-MakisuKurisu`

Ця бібліотека (поки що її немає в PyPi) призначена для отримання розкладу з [сайту з розкладом ОНТУ](https://rozklad.ontu.edu.ua/guest_n.php)

На поточний момент бібліотека може повернути розклад на поточний тиждень, чи на весь семестр. В подальшому планується додати підтримку розкладу екзаменів, повідомлень та інших розділів сайту.

## А як користуватися?
Ви можете подивитися приклад використання в файлі [example.py](https://github.com/makisukurisu/rozklad-ontu-parser/blob/master/ontu_parser/example.py). Також наразі є окремий метод для отримання розкладу з CLI - parse.

## І нащо мені той CLI парсер?..
Насправді лібу можна використовувати не лише як CLI тулзу, але й додавши пакет (якого наразі немає) до вашого проекту, тим самим створивши будь-яку систему з використанням цієї бібліотеки.
Наприклад - створення яскравого та зручного розкладу за вашим смаком.
Чи мій наступний проект - бот з розкладом для всього вишу.

## System requirements
Вам знадобиться Python 3.10+ і будь-який браузер для роботи з selenium (Я використовую Firefox)

## Honorable Mentions
* Дякую [MarshalX](https://github.com/MarshalX) за [дозвіл](https://t.me/yandex_music_api/29677) позичити метод `to_dict` з його ліби: [yandex-music-api](https://github.com/MarshalX/yandex-music-api). (Було внесено мінімальні зміни через bs4 теги)
