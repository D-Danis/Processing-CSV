import argparse
import csv
from abc import ABC, abstractmethod
from tabulate import tabulate
from typing import Dict, Type, List

# Глобальный реестр команд
COMMAND_REGISTRY: Dict[str, Type['Command']] = {}

def register_command(cls):
    """Декоратор для регистрации команды по имени."""
    COMMAND_REGISTRY[cls.name] = cls
    return cls

class Command(ABC):
    """Базовый класс для команд."""
    name: str  # имя команды
    
    @abstractmethod
    def execute(self, data: List[Dict], args: argparse.Namespace):
        pass

# Реализация конкретных команд:
@register_command
class WhereCommand(Command):
    name = 'where'
    
    def execute(self, data, args):
        if not args.where:
            return data
        col, op, val = parse_where_condition(args.where)
        return where_data(data, col, op, val)

@register_command
class AggregateCommand(Command):
    name = 'aggregate'
    
    def execute(self, data, args):
        if not args.aggregate:
            return data
        col, op = parse_aggregate(args.aggregate)
        result = aggregate_data(data, col, op)
        if result:
            return result, op
        return []

@register_command
class OrderByCommand(Command):
    name = 'order-by'
    
    def execute(self, data, args):
        if not args.order_by:
            return data
        col, order = parse_order_by(args.order_by)
        sorted_data = sorted(data, key=lambda x: x[col], reverse=(order=='desc'))
        return sorted_data

@register_command
class MedianCommand(Command):
     name='median'
     
     def execute(self,data,args):
        if not args.median:
            return data
        col = args.median
        median_value = median_data(data, col)
        if median_value:
            return median_value, col
        return []


def parse_order_by(order_str):
    if '=' not in order_str:
        raise ValueError('Некорректный формат --order-by. Ожидается: column=asc|desc')
    column, order = order_str.split('=', 1)
    if order not in ['asc', 'desc']:
        raise ValueError('Значение порядка должно быть "asc" или "desc"')
    return column.strip(), order.strip()

def parse_where_condition(condition):
    parts = condition.strip().split()
    if len(parts) != 3:
        raise ValueError('Некорректный формат --where. Ожидается: column operator value')
    column, op, value = parts
    if op not in ['>', '<', '=']:
        raise ValueError('Поддерживаются только операторы >, < и =')
    return column, op, value

def where_data(data: List[Dict], column:str, op:str, value):
    filtered = []
    for row in data:
        cell_value = row[column]
        if cell_value is None or cell_value == '':
            continue 
        try:
            cell_num = float(cell_value)
            val_num = float(value)
            compare_value = cell_num
            compare_target = val_num
        except ValueError:
            compare_value = cell_value
            compare_target = value

        if op == '>':
            if compare_value > compare_target:
                filtered.append(row)
        elif op == '<':
            if compare_value < compare_target:
                filtered.append(row)
        elif op == '=':
            if compare_value == compare_target:
                filtered.append(row)
    return filtered

def parse_aggregate(aggregate_str):
    if '=' not in aggregate_str:
        raise ValueError('Некорректный формат --aggregate. Ожидается: column=operation')
    column, op = aggregate_str.split('=', 1)
    if op not in ['avg', 'min', 'max']:
        raise ValueError('Поддерживаются только операции avg, min и max')
    return column.strip(), op.strip()

def aggregate_data(data: List[Dict], column: str, operation: str):
    values = []
    for row in data:
        cell_value =row[column]
        if cell_value is None or cell_value == '':
            continue 
        try:
            val=float(cell_value)
            values.append(val)
        except (ValueError, KeyError):
            pass
        
    if not values:
        return None
    if operation=='avg':
        return sum(values)/len(values)
    elif operation=='min':
        return min(values)
    elif operation=='max':
        return max(values)

def read_csv(file_path):
    with open(file_path,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        return list(reader)

def median_data(data: List[Dict], col:str):
    # Находим медиану
    values = []
    for row in data:
        value = row[col]
        if value is None or value == '':
            continue 
        try:
            val = float(value)
            values.append(val)
        except (ValueError,KeyError):
            pass
    if not values:
        print(f'Нет числовых данных в столбце "{col}" для вычисления медианы.')
        return []
    nums = sorted(values)
    mid = len(nums) // 2
    return int((nums[mid] + nums[~mid]) / 2 if len(nums) % 2 == 0 else nums[mid])

def main():
    parser=argparse.ArgumentParser(description='Обработка CSV файла без необходимости указывать команду.')
    
    parser.add_argument('file', help='Путь к CSV файлу')
    parser.add_argument('--where', help='Условие фильтрации "column operator value"')
    parser.add_argument('--aggregate', help='Агрегация "column=operation" (avg/min/max)')
    parser.add_argument('--order-by', help='Сортировка "column=asc|desc"')
    parser.add_argument('--median', help='Вычисление медианы по столбцу')
    
    args=parser.parse_args()

    # Логика выбора команды:
    # Если есть --where — фильтруем
    # Если есть --aggregate — выполняем агрегацию 
    # Иначе если есть --order-by — сортируем
  
    commands_to_run = []

    if args.where:
        commands_to_run.append('where')
    if args.aggregate:
        commands_to_run.append('aggregate')
    elif args.order_by:
        commands_to_run.append('order-by')
    elif args.median:
        commands_to_run.append('median')
    
    # Можно расширить логику для последовательного выполнения нескольких команд.
    
    data=read_csv(args.file)

    for cmd_name in commands_to_run:
        cmd_cls=COMMAND_REGISTRY.get(cmd_name)
        if not cmd_cls:
            print(f'Команда {cmd_name} не найдена.')
            continue
        cmd_instance=cmd_cls()
        result=data  # Передаём текущие данные в следующую команду
        result=cmd_instance.execute(result,args)
        # Обновляем данные после каждой команды (если она возвращает данные для следующей обработки)
        data=result
        if cmd_name == 'median' or cmd_name == 'aggregate':
            val, op = result
            print(tabulate([[val]], headers=[op], tablefmt='grid'))
            return val

    if result and len(result)>0 : # and ('aggregate' not in commands_to_run or result!=[])
        print(tabulate(result, headers='keys', tablefmt='grid'))
        # return result

if __name__=='__main__':
     main()