import os

from django.conf import settings
import openai


def get_gpt_response(prompt: str, history: list[dict] = None) -> str:
    """
    Отправляет запрос к API OpenAI и возвращает синхронный ответ.

    Args:
        prompt: Текст запроса от пользователя.
        history: Список предыдущих сообщений для сохранения контекста диалога.

    Returns:
        Строка с ответом от модели GPT.
    """
    if not history:
        history = []

    try:
        # Причина: Используем современный SDK OpenAI, который требует
        # инстанцирования клиента. API-ключ безопасно берется из настроек Django.
        client = openai.OpenAI(api_key=settings.GPT_API_KEY)

        # Причина: Добавляем системное сообщение, чтобы задать модель
        # поведения для ИИ. Это улучшает качество и релевантность ответов.
        system_message = {
            "role": "system",
            "content": (
                "Ты — эмпатичный и поддерживающий ИИ-психолог по имени 'PsyAI'. "
                "Твоя задача — внимательно слушать, задавать уточняющие вопросы "
                "и предлагать конструктивные пути для размышлений. "
                "Не давай прямых советов, а помогай пользователю самому найти ответы. "
                "Твои ответы должны быть короткими и поддерживающими."
            ),
        }

        messages = [system_message] + history + [{"role": "user", "content": prompt}]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Или другая подходящая модель
            messages=messages,
            temperature=0.7,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()

    except openai.APIError as e:
        # Обработка ошибок, связанных с API OpenAI (например, перегрузка сервера)
        print(f"Ошибка API OpenAI: {e}")
        return "К сожалению, сервис временно недоступен. Попробуйте позже."
    except Exception as e:
        # Обработка других непредвиденных ошибок
        print(f"Непредвиденная ошибка в gpt_service: {e}")
        return "Произошла внутренняя ошибка. Мы уже работаем над ее устранением."