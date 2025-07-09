import openai
from django.conf import settings


def get_gpt_response(prompt: str, history: list[dict] = None) -> str:
    """
    Отправляет запрос к API OpenAI и возвращает синхронный ответ.

    Args:
        prompt: Запрос от пользователя.
        history: Список предыдущих сообщений для контекста.

    Returns:
        Строка с ответом от ИИ или сообщение об ошибке.
    """
    if not history:
        history = []

    try:
        # Примечание: Если settings.GPT_API_KEY не задан, конструктор OpenAI
        # выбросит ошибку, которая будет перехвачена ниже.
        client = openai.OpenAI(api_key=settings.GPT_API_KEY)

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
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()

    except openai.APIError as e:
        # Ошибка со стороны API OpenAI (например, перегрузка серверов)
        print(f"Ошибка API OpenAI: {e}")
        return "К сожалению, сервис временно недоступен. Попробуйте позже."
    except Exception as e:
        # Любая другая ошибка (например, нет ключа, проблема с сетью)
        print(f"Непредвиденная ошибка в gpt_service: {e}")
        return "Произошла внутренняя ошибка. Мы уже работаем над ее устранением."
