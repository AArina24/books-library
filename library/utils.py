import json
import xml.etree.ElementTree as ET
import os
import uuid
import re
from django.conf import settings

# Путь к папке с файлами
MEDIA_DIR = os.path.join(settings.BASE_DIR, 'media')


def safe_filename(original_name):
    """
    Генерирует безопасное имя файла.
    Никогда не доверяем имени от пользователя!
    """
    # Берём только расширение (.json или .xml)
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ['.json', '.xml']:
        ext = '.json'  # по умолчанию

    # Генерируем уникальное имя через UUID
    return f"{uuid.uuid4().hex}{ext}"


def save_book_to_json(book_data, filename=None):
    """Сохраняет книгу в JSON-файл"""
    if not filename:
        filename = f"book_{uuid.uuid4().hex[:8]}.json"

    filepath = os.path.join(MEDIA_DIR, filename)

    # Если файл существует — читаем, иначе создаём пустой список
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    # Добавляем новую книгу
    data.append(book_data)

    # Записываем обратно
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filename


def save_book_to_xml(book_data, filename=None):
    """Сохраняет книгу в XML-файл"""
    if not filename:
        filename = f"book_{uuid.uuid4().hex[:8]}.xml"

    filepath = os.path.join(MEDIA_DIR, filename)

    # Если файл существует — читаем
    if os.path.exists(filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()
    else:
        root = ET.Element('books')
        tree = ET.ElementTree(root)

    # Создаём элемент книги
    book_elem = ET.SubElement(root, 'book')
    for key, value in book_data.items():
        child = ET.SubElement(book_elem, key)
        child.text = str(value)

    # Записываем
    tree.write(filepath, encoding='utf-8', xml_declaration=True)

    return filename


def validate_json_file(filepath):
    """Проверяет, валиден ли JSON-файл. Возвращает (успех, данные/ошибка)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Проверяем структуру
        if not isinstance(data, list):
            return False, 'JSON должен содержать список книг'

        for item in data:
            if not isinstance(item, dict):
                return False, 'Каждая книга должна быть объектом'
            for field in ['title', 'author', 'year', 'genre', 'pages']:
                if field not in item:
                    return False, f'Отсутствует поле: {field}'

        return True, data
    except json.JSONDecodeError as e:
        return False, f'Ошибка JSON: {e}'
    except Exception as e:
        return False, f'Ошибка чтения: {e}'


def validate_xml_file(filepath):
    """Проверяет, валиден ли XML-файл. Возвращает (успех, данные/ошибка)"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        books = []
        for book_elem in root.findall('book'):
            book = {}
            for field in ['title', 'author', 'year', 'genre', 'pages']:
                child = book_elem.find(field)
                if child is None:
                    return False, f'Отсутствует поле: {field}'
                book[field] = child.text
            books.append(book)

        if not books:
            return False, 'Файл не содержит книг'

        return True, books
    except ET.ParseError as e:
        return False, f'Ошибка XML: {e}'
    except Exception as e:
        return False, f'Ошибка чтения: {e}'


def get_all_files():
    """Возвращает список всех JSON/XML файлов в папке media"""
    if not os.path.exists(MEDIA_DIR):
        return []

    files = []
    for filename in os.listdir(MEDIA_DIR):
        if filename.endswith('.json') or filename.endswith('.xml'):
            filepath = os.path.join(MEDIA_DIR, filename)
            files.append({
                'name': filename,
                'path': filepath,
                'size': os.path.getsize(filepath),
                'type': 'JSON' if filename.endswith('.json') else 'XML',
            })

    return files


def read_file_content(filepath):
    """Читает содержимое файла (для отображения)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return True, f.read()
    except Exception as e:
        return False, str(e)