"""Usage example"""
from ontu_parser.classes import Parser

parser = Parser()
schedule = parser.parse(all_time=True)
for day_name, pairs in schedule.items():
    print(f'{day_name}:\n')
    for pair in pairs:
        if not pair.lessons:
            continue
        print(f'{pair.pair_no}:')
        for lesson in pair.lessons:
            print(
                f'{lesson.lesson_date}: '
                f'{lesson.teacher["short"]} - '
                f'{lesson.lesson_name["short"]}'
            )
            print(f'Card: {lesson.lesson_info}')
            print()
