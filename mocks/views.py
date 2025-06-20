from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from .forms import ImageUploadForm
from .services import mock_image_analysis


@login_required
def upload_image_view(request):
    """
    Обрабатывает загрузку изображения для mock-анализа.

    При GET-запросе отображает пустую форму.
    При POST-запросе сохраняет файл, вызывает сервис анализа и отображает
    результаты вместе с загруженным изображением.
    """
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["image"]
            # Причина: Используем FileSystemStorage для простого сохранения файла
            # в папку MEDIA_ROOT. Это самый простой и надежный способ для MVP.
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_url = fs.url(filename)

            # Вызываем функцию-заглушку для "анализа"
            analysis_result = mock_image_analysis(fs.path(filename))

            # Возвращаем ту же страницу, но с результатами
            return render(
                request,
                "mocks/upload_image.html",
                {
                    "form": form,
                    "uploaded_file_url": uploaded_file_url,
                    "analysis_result": analysis_result,
                },
            )
    else:
        form = ImageUploadForm()

    return render(request, "mocks/upload_image.html", {"form": form})


@login_required
def mock_payment_view(request):
    """
    Имитирует страницу оплаты.

    При POST-запросе показывает сообщение об "успешной" оплате.
    """
    payment_success = False
    if request.method == "POST":
        # Причина: В MVP мы просто имитируем успешный платеж без
        # какой-либо логики. Устанавливаем флаг для отображения
        # сообщения в шаблоне.
        payment_success = True

    return render(
        request,
        "mocks/mock_payment.html",
        {"payment_success": payment_success},
    )