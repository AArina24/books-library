from .models import Book
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
    delete_file,
    MEDIA_DIR,
)
import os


def index(request):
    """Главная страница — форма ввода книги"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book_data = {
                'title': form.cleaned_data['title'],
                'author': form.cleaned_data['author'],
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data['genre'],
                'pages': form.cleaned_data['pages'],
            }

            save_to = request.POST.get('save_to', 'file')

            if save_to == 'db':
                # Проверка на дубликат: ищем книгу с такими же данными
                existing = Book.objects.filter(
                    title=book_data['title'],
                    author=book_data['author'],
                    year=book_data['year'],
                    genre=book_data['genre'],
                    pages=book_data['pages'],
                ).first()

                if existing:
                    messages.error(request, 'Такая книга уже есть в базе данных!')
                else:
                    Book.objects.create(**book_data)
                    messages.success(request, 'Книга сохранена в базу данных')
            else:
                # Сохранение в файл (старая логика)
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

        safe_name = safe_filename(uploaded_file.name)
        filepath = os.path.join(MEDIA_DIR, safe_name)

        with open(filepath, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        if ext == '.json':
            is_valid, result = validate_json_file(filepath)
        else:
            is_valid, result = validate_xml_file(filepath)

        if not is_valid:
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

    ok, content = read_file_content(filepath)
    if not ok:
        messages.error(request, f'Ошибка чтения: {content}')
        return redirect('files')

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
def delete_file_view(request, filename):
    if request.method == 'POST':
        ok, message = delete_file(filename)
        if ok:
            messages.success(request, message)
        else:
            messages.error(request, message)
    return redirect('files')

def db_list(request):
    """Список книг из базы данных"""
    books = Book.objects.all().order_by('-id') # Сначала новые
    return render(request, 'library/db_list.html', {'books': books})


from django.http import JsonResponse


def db_search_ajax(request):
    """AJAX-поиск по книгам в БД"""
    query = request.GET.get('q', '')
    if query:
        # Ищем по названию или автору (icontains = без учета регистра)
        books = Book.objects.filter(
            title__icontains=query
        ) | Book.objects.filter(
            author__icontains=query
        )
    else:
        books = Book.objects.all()

    data = []
    for book in books.order_by('-id'):
        data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'year': book.year,
            'genre': book.genre,
            'pages': book.pages,
        })

    return JsonResponse({'books': data})


from django.shortcuts import get_object_or_404


def edit_book(request, book_id):
    """Редактирование книги в БД"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book.title = form.cleaned_data['title']
            book.author = form.cleaned_data['author']
            book.year = form.cleaned_data['year']
            book.genre = form.cleaned_data['genre']
            book.pages = form.cleaned_data['pages']
            book.save()
            messages.success(request, 'Книга обновлена!')
            return redirect('db_list')
    else:
        # Заполняем форму текущими данными книги
        form = BookForm(initial={
            'title': book.title,
            'author': book.author,
            'year': book.year,
            'genre': book.genre,
            'pages': book.pages,
        })

    return render(request, 'library/edit_book.html', {'form': form, 'book': book})

def delete_book_db(request, book_id):
    """Удаление книги из БД"""
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга удалена из базы данных')
    return redirect('db_list')