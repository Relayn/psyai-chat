import json
from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import ChatMessage, ChatSession
from .tasks import process_gpt_request


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Асинхронно обрабатывает WebSocket-соединения для чата.
    """

    SESSION_DURATION_LIMIT_MINUTES = 5
    SESSION_MESSAGE_LIMIT = 10

    async def connect(self):
        """Обрабатывает новое подключение."""
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        # Сохраняем имя канала для отправки сообщений
        self.room_channel_name = self.channel_name

        await self.accept()
        self.chat_session = await ChatSession.objects.acreate(user=self.user)
        print(
            f"✅ WebSocket connect: Соединение для {self.user.username} "
            f"принято. Сессия: {self.chat_session.id}."
        )

    async def disconnect(self, close_code):
        """Обрабатывает отключение."""
        if hasattr(self, "user") and self.user.is_authenticated:
            print(
                f"WebSocket disconnect: Соединение закрыто для "
                f"пользователя {self.user.username}."
            )

    async def receive(self, text_data: str):
        """
        Принимает сообщение, сохраняет его и запускает фоновую задачу для GPT.
        """
        try:
            limit_message = await self._check_session_limits()
            if limit_message:
                await self.send_limit_reached(limit_message)
                return

            user_message_text = await self._handle_user_message(text_data)
            if not user_message_text:
                return

            await self.send(
                text_data=json.dumps(
                    {"type": "ai.typing", "payload": {"is_typing": True}}
                )
            )

            process_gpt_request.delay(
                session_id=self.chat_session.id,
                user_prompt=user_message_text,
                channel_name=self.room_channel_name,
            )

        except Exception as e:
            print(f"❌ Произошла непредвиденная ошибка в receive: {e}")
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat.error",
                        "payload": {
                            "text": "На сервере произошла ошибка.",
                            "sender": "System",
                        },
                    }
                )
            )

    async def _check_session_limits(self) -> str | None:
        await sync_to_async(self.chat_session.refresh_from_db)()
        if self.chat_session.message_count >= self.SESSION_MESSAGE_LIMIT:
            return f"Достигнут лимит в {self.SESSION_MESSAGE_LIMIT} сообщений."
        duration = timezone.now() - self.chat_session.start_time
        duration_limit = timedelta(minutes=self.SESSION_DURATION_LIMIT_MINUTES)
        if duration > duration_limit:
            return f"Время сессии истекло ({self.SESSION_DURATION_LIMIT_MINUTES} мин.)."
        return None

    async def _handle_user_message(self, text_data: str) -> str | None:
        text_data_json = json.loads(text_data)
        message_text = text_data_json.get("message", "").strip()
        if not message_text:
            return None
        await ChatMessage.objects.acreate(
            session=self.chat_session,
            text=message_text,
            sender_type=ChatMessage.SenderType.USER,
        )
        self.chat_session.message_count += 1
        await sync_to_async(self.chat_session.save)()
        return message_text

    async def send_limit_reached(self, message: str):
        await self.send(
            text_data=json.dumps(
                {"type": "limit.reached", "payload": {"message": message}}
            )
        )
        await self.close(code=4001)

    async def send_ai_message(self, event: dict):
        payload = event["payload"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat.message",
                    "payload": {"text": payload["text"], "sender": "AI"},
                }
            )
        )
