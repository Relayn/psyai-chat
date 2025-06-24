from unittest.mock import MagicMock, patch

import openai
import pytest

from chat.services.gpt_service import get_gpt_response


@patch("chat.services.gpt_service.openai.OpenAI")
def test_get_gpt_response_success(mock_openai_class, settings):
    """
    Тестирует успешный сценарий получения ответа от GPT.
    Проверяет, что функция правильно вызывает API и возвращает текст ответа.
    """
    # 1. Настройка (Arrange)
    # Предоставляем фиктивный ключ, чтобы тест не падал из-за его отсутствия.
    settings.GPT_API_KEY = "dummy_test_key"

    # Создаем мок-объект, имитирующий ответ от API OpenAI
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "  Привет, я мок-ответ!  "

    # Говорим нашему моку, что при вызове метода .create() нужно вернуть наш мок-ответ
    mock_openai_class.return_value.chat.completions.create.return_value = mock_response

    # 2. Действие (Act)
    prompt = "Привет, мир!"
    response_text = get_gpt_response(prompt)

    # 3. Проверка (Assert)
    # Проверяем, что был создан клиент OpenAI с нашим ключом
    mock_openai_class.assert_called_once_with(api_key="dummy_test_key")

    # Проверяем, что метод для получения ответа был вызван
    mock_openai_class.return_value.chat.completions.create.assert_called_once()

    # Проверяем, что функция вернула очищенный от пробелов текст
    assert response_text == "Привет, я мок-ответ!"


@patch("chat.services.gpt_service.openai.OpenAI")
def test_get_gpt_response_api_error(mock_openai_class, settings):
    """
    Тестирует сценарий, когда API OpenAI возвращает ошибку.
    Проверяет, что функция корректно обрабатывает openai.APIError.
    """
    # 1. Настройка
    settings.GPT_API_KEY = "dummy_test_key"

    # Настраиваем мок так, чтобы он "выбрасывал" ошибку APIError при вызове
    error_message = "The server is overloaded or not ready yet."
    mock_openai_class.return_value.chat.completions.create.side_effect = openai.APIError(
        message=error_message, request=None, body=None
    )

    # 2. Действие
    response_text = get_gpt_response("Любой промпт")

    # 3. Проверка
    # Проверяем, что функция вернула наше "запасное" сообщение для пользователя
    assert response_text == "К сожалению, сервис временно недоступен. Попробуйте позже."


@patch("chat.services.gpt_service.openai.OpenAI")
def test_get_gpt_response_generic_error(mock_openai_class, settings):
    """
    Тестирует сценарий с непредвиденной ошибкой (не от API).
    Проверяет, что функция обрабатывает общие исключения.
    """
    # 1. Настройка
    settings.GPT_API_KEY = "dummy_test_key"

    # Настраиваем мок на вызов любой другой ошибки, например, ValueError
    mock_openai_class.return_value.chat.completions.create.side_effect = ValueError(
        "Неожиданная ошибка"
    )

    # 2. Действие
    response_text = get_gpt_response("Любой промпт")

    # 3. Проверка
    assert response_text == "Произошла внутренняя ошибка. Мы уже работаем над ее устранением."