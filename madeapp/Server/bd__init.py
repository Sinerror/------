import sqlite3
import shutil
import unittest

# Подключение к базе данных SQLite (или создание новой, если её нет)
conn = sqlite3.connect('tests.db')

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()

# Создание таблицы для хранения информации о классах тестов
cursor.execute('''CREATE TABLE IF NOT EXISTS test_classes (id INTEGER PRIMARY KEY, class_name TEXT, module_name TEXT)''')

# Функция для загрузки информации о классах тестов в базу данных
def load_test_classes(file_path):
    test_module = __import__(file_path[:-3])  # Импорт модуля с тестами
    for name in dir(test_module):
        obj = getattr(test_module, name)
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
            cursor.execute('''INSERT INTO test_classes (class_name, module_name) VALUES (?, ?)''', (name, file_path))
    conn.commit()

# Загрузка информации о классах тестов из файла test_unit.py
load_test_classes('backup_test_unit.py')

# Сохранение содержимого базы данных в файл
def backup_database(database_file, backup_file):
    shutil.copy(database_file, backup_file)

# Указываем имя файлов базы данных и резервной копии
database_file = 'tests.db'
backup_file = 'tests_backup.db'

# Вызываем функцию для создания резервной копии
backup_database(database_file, backup_file)


