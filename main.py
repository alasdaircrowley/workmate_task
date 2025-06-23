import argparse
import csv
import sys

from tabulate import tabulate


def main(args=None):
    parser = argparse.ArgumentParser(description='Обработка CSV-файлов')
    parser.add_argument('file', help='Путь к CSV-файлу')
    parser.add_argument('--filter', nargs='+', help='Фильтр: колонка оператор значение')
    parser.add_argument('--agg', help='Агрегация: функция(колонка)')

    if args is None:
        args = sys.argv[1:]

    try:
        args = parser.parse_args(args)
    except SystemExit:
        output = parser.format_help()
        print(output)
        raise

    with open(args.file, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            print("Файл пуст")
            return

    if args.filter:
        filter_str = " ".join(args.filter)

        operators = ['==', '!=', '>=', '<=', '>', '<']
        op = None
        for possible_op in operators:
            if possible_op in filter_str:
                op = possible_op
                parts = filter_str.split(op, 1)
                col = parts[0].strip()
                value = parts[1].strip()
                break

        if not op:
            print("Не найден поддерживаемый оператор")
            return

        if not col or not value:
            print("Некорректный формат фильтра. Используйте: колонка оператор значение")
            print("Пример: --filter price > 500")
            return

        if col not in reader.fieldnames:
            print(f"Колонка '{col}' не найдена")
            return

        try:
            value = float(value)
            numeric = True
        except ValueError:
            numeric = False

        ops = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '==': lambda a, b: a == b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
        }

        filtered = []
        for row in rows:
            cell = row[col]
            try:
                if numeric:
                    cell = float(cell)
            except ValueError:
                pass

            try:
                if ops[op](cell, value):
                    filtered.append(row)
            except TypeError:
                continue

        if filtered:
            print(tabulate(filtered, headers="keys", tablefmt="grid"))
        else:
            print("Нет данных, соответствующих фильтру")
        return

    if args.agg:
        agg_str = args.agg.strip()
        if '(' not in agg_str or ')' not in agg_str:
            print("Некорректный формат агрегации. Используйте: функция(колонка)")
            return

        func_part, col_part = agg_str.split('(', 1)
        func = func_part.strip().lower()
        col = col_part.rstrip(')').strip()

        if col not in reader.fieldnames:
            print(f"Колонка '{col}' не найдена")
            return

        if func not in ['avg', 'min', 'max']:
            print(f"Неподдерживаемая функция: '{func}'")
            return

        values = []
        for row in rows:
            try:
                values.append(float(row[col]))
            except ValueError:
                print(f"Ошибка: значение '{row[col]}' не является числом")
                return

        if not values:
            print("Нет данных для расчета")
            return

        if func == 'avg':
            result = sum(values) / len(values)
            print(f"{func}({col}) = {result:.2f}")
        elif func == 'min':
            result = min(values)
            print(f"{func}({col}) = {result}")
        elif func == 'max':
            result = max(values)
            print(f"{func}({col}) = {result}")
        return

    print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == '__main__':
    main()