import json

from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    """
    Синхронный WebSocket-консьюмер для обработки чата.
    """

    def connect(self):
        """
        Вызывается при установлении WebSocket-соединения.
        Проверяет, аутентифицирован ли пользователь.
        """
        # self.scope['user'] предоставляется AuthMiddlewareStack
        self.user = self.scope["user"]

        # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ ---
        # Проверяем, что пользователь залогинен.
        if self.user.is_authenticated:
            # Принимаем соединение
            self.accept()
            print(f"WebSocket connection accepted for user: {self.user.username}")
        else:
            # Отклоняем соединение для анонимных пользователей
            self.close()
            print("WebSocket connection rejected for anonymous user.")

    def disconnect(self, close_code):
        """
        Вызывается при разрыве WebSocket-соединения.
        """
        # Здесь можно добавить логику, если нужно что-то делать при отключении
        if self.user.is_authenticated:
            print(f"WebSocket connection closed for user: {self.user.username}")
        else:
            print("WebSocket connection closed for anonymous user.")

    def receive(self, text_data):
        """
        Вызывается при получении сообщения от WebSocket.
        """
        # Если соединение не было установлено, этот метод не будет вызван.
        text_data_json = json.loads(text_data)
        message_text = text_data_json.get("message", "")

        print(f"Received message: '{message_text}' from {self.user.username}")

        # --- Логика ЭХО-ответа (временно) ---
        self.send(
            text_data=json.dumps(
                {
                    "type": "chat.message",
                    "payload": {
                        "text": f"Эхо: {message_text}",
                        "sender": "AI",
                    },
                }
            )
        )