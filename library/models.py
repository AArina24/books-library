from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    author = models.CharField(max_length=150, verbose_name='Автор')
    year = models.IntegerField(verbose_name='Год издания')
    genre = models.CharField(max_length=100, verbose_name='Жанр')
    pages = models.IntegerField(verbose_name='Страниц')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'