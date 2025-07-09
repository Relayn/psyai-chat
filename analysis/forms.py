from django import forms


class ImageUploadForm(forms.Form):
    """Форма для загрузки изображения."""

    image = forms.ImageField(
        label="Выберите изображение для анализа",
        help_text="Поддерживаемые форматы: jpg, png, gif",
    )
