from django import forms


class BookForm(forms.Form):

    title = forms.CharField(
        max_length=200,
        label='Название книги',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Например: Мастер и Маргарита'
        })
    )

    author = forms.CharField(
        max_length=150,
        label='Автор',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Например: Булгаков М.А.'
        })
    )

    year = forms.IntegerField(
        label='Год издания',
        min_value=1000,
        max_value=2026,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '2020'
        })
    )

    genre = forms.CharField(
        max_length=100,
        label='Жанр',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Например: Роман'
        })
    )

    pages = forms.IntegerField(
        label='Количество страниц',
        min_value=1,
        max_value=10000,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '350'
        })
    )