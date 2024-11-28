import unittest
import converter
import textwrap  # Добавлено для правильного форматирования многострочных строк
import toml  # Используем модуль toml вместо tomllib

class TestConverter(unittest.TestCase):
    def test_simple_conversion(self):
        """Тест простого конвертирования словаря с числами и строками."""
        toml_data = {
            'число': 42,
            'строка': 'значение',
            'словарь': {
                'подключ': 100
            }
        }
        expected_output = (
            "const число = 42\n"
            "const строка = \"значение\"\n"
            "const словарь_подключ = 100\n\n"
            "{\n"
            "    число : @[число];\n"
            "    строка : @[строка];\n"
            "    словарь : {\n"
            "        подключ : @[словарь_подключ];\n"
            "    };\n"
            "}"
        )
        output = converter.convert_toml_to_custom(toml_data)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_invalid_name(self):
        """Тест проверки недопустимых имён."""
        toml_data = {
            'неверное-имя': 123
        }
        with self.assertRaises(converter.ConfigConverterError):
            converter.convert_toml_to_custom(toml_data)

    def test_unsupported_value_type(self):
        """Тест обработки неподдерживаемых типов значений."""
        toml_data = {
            'список': [1, 2, 3]
        }
        with self.assertRaises(converter.ConfigConverterError):
            converter.convert_toml_to_custom(toml_data)

    def test_nested_dictionaries(self):
        """Тест вложенных словарей."""
        toml_data = {
            'уровень1': {
                'уровень2': {
                    'уровень3': 789
                }
            }
        }
        expected_output = (
            "const уровень1_уровень2_уровень3 = 789\n\n"
            "{\n"
            "    уровень1 : {\n"
            "        уровень2 : {\n"
            "            уровень3 : @[уровень1_уровень2_уровень3];\n"
            "        };\n"
            "    };\n"
            "}"
        )
        output = converter.convert_toml_to_custom(toml_data)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_constants_declaration(self):
        """Тест объявления и использования констант."""
        toml_data = {
            'константа1': 1,
            'константа2': 2,
            'словарь': {
                'константа3': 3
            }
        }
        expected_output = (
            "const константа1 = 1\n"
            "const константа2 = 2\n"
            "const словарь_константа3 = 3\n\n"
            "{\n"
            "    константа1 : @[константа1];\n"
            "    константа2 : @[константа2];\n"
            "    словарь : {\n"
            "        константа3 : @[словарь_константа3];\n"
            "    };\n"
            "}"
        )
        output = converter.convert_toml_to_custom(toml_data)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_full_coverage(self):
        """Тест, покрывающий все конструкции, включая ошибки."""
        toml_data = {
            'validName': 100,
            'Неверное-Имя': 200,
            'вложенный': {
                'другое_имя': 300,
                'неверное имя': 400
            },
            'неподдерживаемое': [1, 2, 3],
            'флаг': True  # Булевое значение
        }
        # Проверка на недопустимые имена и неподдерживаемые типы
        with self.assertRaises(converter.ConfigConverterError):
            converter.convert_toml_to_custom(toml_data)

    def test_string_handling(self):
        """Тест обработки строковых значений."""
        toml_data = {
            'приветствие': 'Здравствуйте'
        }
        expected_output = (
            "const приветствие = \"Здравствуйте\"\n\n"
            "{\n"
            "    приветствие : @[приветствие];\n"
            "}"
        )
        output = converter.convert_toml_to_custom(toml_data)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_boolean_handling(self):
        """Тест обработки булевых значений."""
        toml_data = {
            'флаг': True,
            'другой_флаг': False
        }
        expected_output = (
            "const флаг = \"true\"\n"
            "const другой_флаг = \"false\"\n\n"
            "{\n"
            "    флаг : @[флаг];\n"
            "    другой_флаг : @[другой_флаг];\n"
            "}"
        )
        output = converter.convert_toml_to_custom(toml_data)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_comments_in_toml(self):
        """Тест, что комментарии в TOML не влияют на конвертацию."""
        toml_string = textwrap.dedent('''
            # Это комментарий
            ключ = 123  # Это inline-комментарий
        ''').strip()
        try:
            toml_data = toml.loads(toml_string)
        except toml.TomlDecodeError as e:
            self.fail(f"TOML parsing failed: {e}")
        expected_output = (
            "const ключ = 123\n\n"
            "{\n"
            "    ключ : @[ключ];\n"
            "}"
        )
        output = converter.convert_toml_to_custom(toml_data)
        self.assertEqual(output.strip(), expected_output.strip())

if __name__ == '__main__':
    unittest.main()
