import sqlite3
import unittest

# Подключение к базе данных SQLite (или создание новой, если её нет)
conn = sqlite3.connect('tests.db')

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()

# Извлечение информации о классах тестов из базы данных и запуск тестирования
def run_tests():
    cursor.execute("SELECT class_name, module_name FROM test_classes")
    for class_name, module_name in cursor.fetchall():
        test_module = __import__(module_name[:-3])
        test_class = getattr(test_module, class_name)
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        unittest.TextTestRunner().run(suite)

# Запуск тестирования
run_tests()

# Закрытие соединения с базой данных
conn.close()