import time
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ChatMessage, ChatSession
from .services.gpt_service import get_gpt_response


@shared_task
def process_gpt_request(session_id: int, user_prompt: str, channel_name: str):
    """
    Асинхронная задача для обработки запроса к GPT.

    1. Получает ответ от GPT.
    2. Сохраняет ответ в базу данных.
    3. Отправляет сохраненное сообщение обратно клиенту через WebSocket.
    """
    try:
        session = ChatSession.objects.get(id=session_id)

        # 1. Формируем историю и получаем ответ от GPT
        history_queryset = session.messages.order_by("timestamp")
        gpt_history = [
            {"role": "user" if msg.sender_type == ChatMessage.SenderType.USER else "assistant", "content": msg.text}
            for msg in history_queryset
        ]
        ai_response_text = get_gpt_response(prompt=user_prompt, history=gpt_history)

        # 2. Сохраняем ответ ИИ в БД
        ai_message = ChatMessage.objects.create(
            session=session,
            text=ai_response_text,
            sender_type=ChatMessage.SenderType.AI
        )

        # 3. Отправляем сообщение обратно в Consumer через channel layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            channel_name,
            {
                "type": "send.ai.message", # Указываем, какой метод в consumer'е вызвать
                "payload": {
                    "text": ai_message.text,
                    "sender": ai_message.get_sender_type_display(),
                },
            },
        )

    except ChatSession.DoesNotExist:
        print(f"Ошибка в задаче Celery: Сессия чата с ID {session_id} не найдена.")
    except Exception as e:
        print(f"Ошибка в задаче Celery process_gpt_request: {e}")
