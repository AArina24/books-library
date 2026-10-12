from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BookForm
from .utils import (
    save_book_to_json,
    save_book_to_xml,
    validate_json_file,
    validate_xml_file,
    get_all_files,
    read_file_content,
    safe_filename,
    MEDIA_DIR,
)
import os


def index(request):
    """Главная страница — форма ввода книги"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # Получаем очищенные данные
            book_data = {
                'title': form.cleaned_data['title'],
                'author': form.cleaned_data['author'],
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data['genre'],
                'pages': form.cleaned_data['pages'],
            }

            # Формат выбирает пользователь
            file_format = request.POST.get('file_format', 'json')

            if file_format == 'json':
                filename = save_book_to_json(book_data)
                messages.success(request, f'Книга сохранена в JSON: {filename}')
            else:
                filename = save_book_to_xml(book_data)
                messages.success(request, f'Книга сохранена в XML: {filename}')

            return redirect('index')
    else:
        form = BookForm()

    return render(request, 'library/index.html', {'form': form})


def upload_file(request):
    """Загрузка файла JSON/XML на сервер"""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            messages.error(request, 'Файл не выбран')
            return redirect('upload')

        # Проверяем расширение
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ['.json', '.xml']:
            messages.error(request, 'Допустимы только файлы JSON и XML')
            return redirect('upload')

        # Генерируем безопасное имя
        safe_name = safe_filename(uploaded_file.name)
        filepath = os.path.join(MEDIA_DIR, safe_name)

        # Сохраняем файл
        with open(filepath, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Проверяем валидность
        if ext == '.json':
            is_valid, result = validate_json_file(filepath)
        else:
            is_valid, result = validate_xml_file(filepath)

        if not is_valid:
            # Удаляем невалидный файл
            os.remove(filepath)
            messages.error(request, f'Файл невалиден: {result}')
            return redirect('upload')

        messages.success(request, f'Файл {safe_name} успешно загружен и валиден')
        return redirect('files')

    return render(request, 'library/upload.html')


def files_list(request):
    """Список всех загруженных файлов"""
    files = get_all_files()
    return render(request, 'library/files.html', {'files': files})


def file_detail(request, filename):
    """Просмотр содержимого конкретного файла"""
    filepath = os.path.join(MEDIA_DIR, filename)

    if not os.path.exists(filepath):
        messages.error(request, 'Файл не найден')
        return redirect('files')

    # Читаем содержимое
    ok, content = read_file_content(filepath)
    if not ok:
        messages.error(request, f'Ошибка чтения: {content}')
        return redirect('files')

    # Парсим данные для красивого вывода
    if filename.endswith('.json'):
        is_valid, data = validate_json_file(filepath)
    else:
        is_valid, data = validate_xml_file(filepath)

    if not is_valid:
        messages.error(request, f'Файл невалиден: {data}')
        return redirect('files')

    return render(request, 'library/file_detail.html', {
        'filename': filename,
        'content': content,
        'books': data,
    })