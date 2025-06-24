from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from .forms import ImageUploadForm
from .services import mock_image_analysis

@login_required
def mock_payment_view(request):
    """
    Имитирует страницу оплаты.

    При POST-запросе показывает сообщение об "успешной" оплате.
    """
    payment_success = False
    if request.method == "POST":
        payment_success = True

    return render(
        request,
        "mocks/mock_payment.html",
        {"payment_success": payment_success},
    )