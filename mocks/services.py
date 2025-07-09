import random
import time


def mock_image_analysis(image_path: str) -> dict:
    """
    Имитирует длительный и сложный анализ изображения.

    Args:
        image_path: Путь к файлу изображения (в данном MVP не используется,
                    но передается для полноты картины).

    Returns:
        Словарь с вымышленным результатом анализа.
    """
    time.sleep(1.5)

    emotions = ["Радость", "Спокойствие", "Тревога", "Усталость", "Задумчивость"]
    confidence = random.randint(75, 95)
    dominant_emotion = random.choice(emotions)

    return {
        "dominant_emotion": dominant_emotion,
        "confidence": confidence,
        "recommendation": (
            f"Похоже, вы чувствуете '{dominant_emotion.lower()}'. "
            "Возможно, стоит обсудить это с консультантом в нашем чате."
        ),
    }
