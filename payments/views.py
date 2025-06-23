import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from yookassa.domain.notification import WebhookNotification

from .decorators import yookassa_ip_check
from .models import Payment
from .services import create_yookassa_payment


@login_required
def create_payment_view(request):
    """
    Создает платеж и перенаправляет пользователя на страницу оплаты.
    """
    payment_amount = Decimal("999.00")
    payment_description = "Доступ к расширенным функциям PsyAI"
    return_url = request.build_absolute_uri(reverse("profile"))
    yookassa_payment = create_yookassa_payment(
        amount=payment_amount,
        description=payment_description,
        return_url=return_url
    )
    Payment.objects.create(
        user=request.user,
        yookassa_payment_id=yookassa_payment.id,
        amount=payment_amount,
        status=yookassa_payment.status.upper()
    )
    confirmation_url = yookassa_payment.confirmation.confirmation_url
    return redirect(confirmation_url)


@csrf_exempt
@yookassa_ip_check
def yookassa_webhook_view(request):
    """
    Обрабатывает входящие уведомления (вебхуки) от ЮKassa.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        event_json = json.loads(request.body)
        # ИЗМЕНЕНО: Используем импортированный класс WebhookNotification
        notification = WebhookNotification(event_json)
    except (json.JSONDecodeError, ValueError):
        return HttpResponseBadRequest("Invalid JSON or event format")

    payment_id = notification.object.id
    try:
        payment = Payment.objects.get(yookassa_payment_id=payment_id)
    except Payment.DoesNotExist:
        return HttpResponse(status=200)

    if payment.status == Payment.Status.SUCCEEDED:
        return HttpResponse(status=200)

    new_status = notification.object.status.upper()
    payment.status = new_status
    payment.save()

    if new_status == Payment.Status.SUCCEEDED:
        print(f"✅ Успешный платеж! Пользователю {payment.user.username} предоставлен доступ.")

    return HttpResponse(status=200)