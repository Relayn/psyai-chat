import time

import openai
from django.conf import settings


def get_gpt_response(prompt: str, history: list[dict] = None) -> str:
    """
    Отправляет запрос к API OpenAI и возвращает синхронный ответ.
    Включает mock-режим, если API-ключ не задан.
    """
    # --- ВРЕМЕННОЕ ИЗМЕНЕНИЕ ДЛЯ ТЕСТИРОВАНИЯ ---
    if not settings.GPT_API_KEY or settings.GPT_API_KEY == "your-gpt-api-key-goes-here":
        print("--- GPT Service: РАБОТА В MOCK-РЕЖИМЕ (КЛЮЧ НЕ НАЙДЕН) ---")
        time.sleep(3)  # Имитируем задержку ответа от API
        return f"Это mock-ответ на ваш вопрос: '{prompt}'. Асинхронная задача работает!"
    # ---------------------------------------------

    if not history:
        history = []

    try:
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
        print(f"Ошибка API OpenAI: {e}")
        return "К сожалению, сервис временно недоступен. Попробуйте позже."
    except Exception as e:
        print(f"Непредвиденная ошибка в gpt_service: {e}")
        return "Произошла внутренняя ошибка. Мы уже работаем над ее устранением."
