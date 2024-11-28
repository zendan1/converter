#!/usr/bin/env python3

import argparse
import sys
import re
import toml

class ConfigConverterError(Exception):
    """Кастомное исключение для ошибок конвертации."""
    pass

class Converter:
    def __init__(self):
        self.constants = {}
        self.output_lines = []
        self.indent_level = 0
        self.current_path = []

    def convert(self, data):
        if isinstance(data, dict):
            self.output_lines.append('{')
            self.indent_level += 1
            self.process_dict(data)
            self.indent_level -= 1
            self.output_lines.append('}')
        else:
            raise ConfigConverterError("Верхний уровень TOML-файла должен быть словарём.")
        return '\n'.join(self.output_lines)

    def process_dict(self, d):
        for key, value in d.items():
            if not self.is_valid_name(key):
                raise ConfigConverterError(f"Недопустимое имя: '{key}'")
            if isinstance(value, dict):
                # Добавляем ключ и открывающую фигурную скобку
                self.output_lines.append(self.indent() + f"{key} : {{")
                self.indent_level += 1
                self.current_path.append(key)
                self.process_dict(value)  # Рекурсивный вызов
                self.current_path.pop()
                self.indent_level -= 1
                # Закрывающая фигурная скобка с точкой с запятой
                self.output_lines.append(self.indent() + "};")
            elif isinstance(value, (int, float, str, bool)):
                val_str = self.process_value(key, value)
                # Добавляем ключ и значение с точкой с запятой
                self.output_lines.append(self.indent() + f"{key} : {val_str};")
            else:
                raise ConfigConverterError(f"Неподдерживаемый тип значения: {type(value)}")

    def process_value(self, key, value):
        if isinstance(value, bool):
            # Обработка булевых значений как строковых констант
            const_name = self.generate_constant_name(key)
            if const_name in self.constants:
                raise ConfigConverterError(f"Дублирование константы: '{const_name}'")
            self.constants[const_name] = '"true"' if value else '"false"'
            return f"@[{const_name}]"
        elif isinstance(value, (int, float)):
            # Обработка чисел как констант
            const_name = self.generate_constant_name(key)
            if const_name in self.constants:
                raise ConfigConverterError(f"Дублирование константы: '{const_name}'")
            self.constants[const_name] = value
            return f"@[{const_name}]"
        elif isinstance(value, str):
            # Обработка строк как констант
            const_name = self.generate_constant_name(key)
            if const_name in self.constants:
                raise ConfigConverterError(f"Дублирование константы: '{const_name}'")
            self.constants[const_name] = f'"{value}"'
            return f"@[{const_name}]"
        else:
            raise ConfigConverterError(f"Неподдерживаемый тип значения: {type(value)}")

    def is_valid_name(self, name):
        # Разрешаем Unicode буквы и символ подчеркивания
        return re.fullmatch(r'^[_\w]+$', name, re.UNICODE) is not None

    def indent(self):
        return '    ' * self.indent_level

    def generate_constant_name(self, key):
        if not self.current_path:
            return key
        else:
            return '_'.join(self.current_path + [key])

def convert_toml_to_custom(toml_data):
    """
    Конвертирует данные TOML в пользовательский конфигурационный язык.
    
    :param toml_data: Словарь, полученный из TOML-файла.
    :return: Строка с конфигурацией в пользовательском формате.
    """
    converter = Converter()
    try:
        output = converter.convert(toml_data)
    except ConfigConverterError as e:
        raise e

    # Объявление констант
    const_lines = []
    for const_name, const_value in converter.constants.items():
        const_lines.append(f"const {const_name} = {const_value}")

    # Объединение констант и основного содержимого
    if const_lines:
        return '\n'.join(const_lines) + '\n\n' + output
    else:
        return output

def main():
    parser = argparse.ArgumentParser(description='Преобразование TOML в пользовательский конфигурационный язык.')
    parser.add_argument('-i', '--input', required=True, help='Путь к входному TOML-файлу')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            try:
                data = toml.load(f)
            except toml.TomlDecodeError as e:
                print(f"Синтаксическая ошибка в TOML-файле: {e}", file=sys.stderr)
                sys.exit(1)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{args.input}' не найден.", file=sys.stderr)
        sys.exit(1)

    try:
        output = convert_toml_to_custom(data)
        print(output)
    except ConfigConverterError as e:
        print(f"Ошибка при конвертации: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
