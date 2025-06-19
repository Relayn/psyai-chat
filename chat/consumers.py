import json
from datetime import timedelta

from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone

from .models import ChatMessage, ChatSession
from .services.gpt_service import get_gpt_response


class ChatConsumer(WebsocketConsumer):
    SESSION_DURATION_LIMIT_MINUTES = 5
    SESSION_MESSAGE_LIMIT = 10

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()
            return
        self.accept()
        self.chat_session = ChatSession.objects.create(user=self.user)
        print(f"WebSocket: Создана новая сессия чата {self.chat_session.id}.")

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            print(f"WebSocket: Соединение закрыто для пользователя {self.user.username}.")

    def receive(self, text_data):
        try:
            self.chat_session.refresh_from_db()

            if self.chat_session.message_count >= self.SESSION_MESSAGE_LIMIT:
                limit_message = f"Достигнут лимит в {self.SESSION_MESSAGE_LIMIT} сообщений."
                print(f"Сессия {self.chat_session.id}: {limit_message}")
                self.send_limit_reached(limit_message)
                return

            duration = timezone.now() - self.chat_session.start_time
            if duration > timedelta(minutes=self.SESSION_DURATION_LIMIT_MINUTES):
                limit_message = f"Время сессии истекло ({self.SESSION_DURATION_LIMIT_MINUTES} мин.)."
                print(f"Сессия {self.chat_session.id}: {limit_message}")
                self.send_limit_reached(limit_message)
                return

            text_data_json = json.loads(text_data)
            message_text = text_data_json.get("message", "").strip()
            if not message_text:
                return

            ChatMessage.objects.create(
                session=self.chat_session,
                text=message_text,
                sender_type=ChatMessage.SenderType.USER,
            )
            self.chat_session.message_count += 1
            self.chat_session.save()

            history_queryset = self.chat_session.messages.order_by("timestamp")
            gpt_history = [{"role": "user" if msg.sender_type == ChatMessage.SenderType.USER else "assistant", "content": msg.text} for msg in history_queryset]
            ai_response_text = get_gpt_response(prompt=message_text, history=gpt_history)
            ChatMessage.objects.create(session=self.chat_session, text=ai_response_text, sender_type=ChatMessage.SenderType.AI)
            self.send(text_data=json.dumps({"type": "chat.message", "payload": {"text": ai_response_text, "sender": "AI"}}))

        except Exception as e:
            print(f"Произошла непредвиденная ошибка в receive: {e}")
            self.send(text_data=json.dumps({"type": "chat.error", "payload": {"text": "На сервере произошла ошибка.", "sender": "System"}}))

    def send_limit_reached(self, message: str):
        self.send(text_data=json.dumps({"type": "limit.reached", "payload": {"message": message}}))
        self.close(code=4001)