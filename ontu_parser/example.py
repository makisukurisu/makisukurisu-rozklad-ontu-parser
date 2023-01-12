"""Usage example"""
from classes import Parser

parser = Parser()
schedule = parser.parse(all_time=True)
for day_name, pair in schedule.items():
    print(f'{day_name} - {pair}')
