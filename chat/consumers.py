import json
from datetime import timedelta
from typing import Optional

from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone

from .models import ChatMessage, ChatSession
from .services.gpt_service import get_gpt_response


class ChatConsumer(WebsocketConsumer):
    """
    Обрабатывает WebSocket-соединения для чата.
    """
    SESSION_DURATION_LIMIT_MINUTES = 5
    SESSION_MESSAGE_LIMIT = 10

    def connect(self):
        """Обрабатывает новое подключение."""
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()
            return

        self.accept()
        # Причина: Создаем сессию при подключении, чтобы сразу зафиксировать
        # пользователя и время начала.
        self.chat_session = ChatSession.objects.create(user=self.user)
        print(f"WebSocket: Создана новая сессия чата {self.chat_session.id} для {self.user.username}.")

    def disconnect(self, close_code):
        """Обрабатывает отключение."""
        if hasattr(self, 'user') and self.user.is_authenticated:
            print(f"WebSocket: Соединение закрыто для пользователя {self.user.username}.")

    def receive(self, text_data: str):
        """
        Принимает сообщение от клиента, обрабатывает его и отправляет ответ.
        Этот метод выступает в роли диспетчера.
        """
        try:
            # 1. Проверяем лимиты сессии
            limit_message = self._check_session_limits()
            if limit_message:
                print(f"Сессия {self.chat_session.id}: {limit_message}")
                self.send_limit_reached(limit_message)
                return

            # 2. Обрабатываем сообщение от пользователя
            user_message = self._handle_user_message(text_data)
            if not user_message:
                return  # Игнорируем пустое сообщение

            # 3. Получаем и сохраняем ответ от ИИ
            ai_response_text = self._get_and_save_ai_response(user_message)

            # 4. Отправляем ответ ИИ клиенту
            self.send(text_data=json.dumps({
                "type": "chat.message",
                "payload": {"text": ai_response_text, "sender": "AI"}
            }))

        except Exception as e:
            # Причина: Общий обработчик ошибок для предотвращения падения
            # всего consumer'а из-за непредвиденной ситуации.
            print(f"Произошла непредвиденная ошибка в receive: {e}")
            self.send(text_data=json.dumps({
                "type": "chat.error",
                "payload": {"text": "На сервере произошла ошибка.", "sender": "System"}
            }))

    def _check_session_limits(self) -> Optional[str]:
        """
        Проверяет, не превышены ли лимиты сессии по времени или сообщениям.
        Возвращает строку с причиной, если лимит достигнут, иначе None.
        """
        self.chat_session.refresh_from_db()

        if self.chat_session.message_count >= self.SESSION_MESSAGE_LIMIT:
            return f"Достигнут лимит в {self.SESSION_MESSAGE_LIMIT} сообщений."

        duration = timezone.now() - self.chat_session.start_time
        if duration > timedelta(minutes=self.SESSION_DURATION_LIMIT_MINUTES):
            return f"Время сессии истекло ({self.SESSION_DURATION_LIMIT_MINUTES} мин.)."

        return None

    def _handle_user_message(self, text_data: str) -> Optional[str]:
        """
        Сохраняет сообщение пользователя в БД и обновляет счетчик.
        Возвращает текст сообщения или None, если оно пустое.
        """
        text_data_json = json.loads(text_data)
        message_text = text_data_json.get("message", "").strip()
        if not message_text:
            return None

        ChatMessage.objects.create(
            session=self.chat_session,
            text=message_text,
            sender_type=ChatMessage.SenderType.USER,
        )
        self.chat_session.message_count += 1
        self.chat_session.save()
        return message_text

    def _get_and_save_ai_response(self, user_prompt: str) -> str:
        """
        Формирует историю, получает ответ от GPT и сохраняет его в БД.
        Возвращает текст ответа ИИ.
        """
        history_queryset = self.chat_session.messages.order_by("timestamp")
        gpt_history = [
            {"role": "user" if msg.sender_type == ChatMessage.SenderType.USER else "assistant", "content": msg.text}
            for msg in history_queryset
        ]

        ai_response_text = get_gpt_response(prompt=user_prompt, history=gpt_history)

        ChatMessage.objects.create(
            session=self.chat_session,
            text=ai_response_text,
            sender_type=ChatMessage.SenderType.AI
        )
        return ai_response_text

    def send_limit_reached(self, message: str):
        """Отправляет сообщение о лимите и закрывает соединение."""
        self.send(text_data=json.dumps({
            "type": "limit.reached",
            "payload": {"message": message}
        }))
        self.close(code=4001)