from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ImageUploadForm
from .models import ImageAnalysisResult
from .tasks import analyze_image_task


@login_required
def upload_image_view(request):
    """
    Обрабатывает загрузку изображения, создает объект анализа
    и запускает фоновую задачу.
    """
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Создаем объект в БД со статусом PENDING
            analysis_result = ImageAnalysisResult.objects.create(
                user=request.user,
                source_image=request.FILES["image"],
                status=ImageAnalysisResult.Status.PENDING,
            )

            # Запускаем асинхронную задачу, передав ей ID объекта
            analyze_image_task.delay(analysis_result.id)

            # Перенаправляем пользователя на страницу ожидания результата
            return redirect(
                reverse("analysis:analysis_result", args=[analysis_result.id])
            )
    else:
        form = ImageUploadForm()

    return render(request, "analysis/analysis_form.html", {"form": form})


@login_required
def analysis_result_view(request, result_id: int):
    """
    Отображает страницу, которая будет опрашивать статус анализа.
    """
    result = get_object_or_404(ImageAnalysisResult, id=result_id, user=request.user)
    return render(request, "analysis/analysis_result.html", {"result": result})


@login_required
def get_analysis_status_view(request, result_id: int):
    """
    API-эндпоинт для получения статуса и результата анализа.
    Возвращает JSON.
    """
    result = get_object_or_404(ImageAnalysisResult, id=result_id, user=request.user)

    return JsonResponse(
        {
            "id": result.id,
            "status": result.status,
            "status_display": result.get_status_display(),
            "result_payload": result.result_payload,
            "error_message": result.error_message,
        }
    )
