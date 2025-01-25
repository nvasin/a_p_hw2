from datetime import datetime, date
from models.db_queries import log_user_norms

def calculate_water_norm(weight):
    """
    Рассчитать норму воды на основе веса.
    """
    base_water = weight * 30  # мл/кг
    return base_water

def calculate_calorie_norm(weight, height, age):
    """
    Рассчитать норму калорий на основе параметров.
    """
    return 10 * weight + 6.25 * height - 5 * age + 5  # Формула Харриса-Бенедикта


def calculate_user_norms(height, weight, age):
    """
    Рассчитывает нормы калорий, воды, макронутриентов и дневной активности для пользователя.
    """
    # Расчет калорий и воды
    calories_goal = weight * 10 + height * 6.25 - age * 5 + 5
    water_goal = weight * 30

    # Макронутриенты
    proteins = calories_goal * 0.3 / 4  # 30% калорий из белков, 1 г = 4 калории
    fats = calories_goal * 0.25 / 9    # 25% калорий из жиров, 1 г = 9 калорий
    carbs = calories_goal * 0.45 / 4   # 45% калорий из углеводов, 1 г = 4 калории

    # Дневная активность (умеренная)
    weekly_activity_minutes = 150  # Рекомендация: 150 минут в неделю
    daily_activity_minutes = weekly_activity_minutes / 7

    return {
        "calories_goal": round(calories_goal, 2),
        "water_goal": round(water_goal, 2),
        "proteins": round(proteins, 2),
        "fats": round(fats, 2),
        "carbs": round(carbs, 2),
        "daily_activity_minutes": round(daily_activity_minutes, 2)
    }

def calculate_additional_water(temperature):
    """
    Рассчитывает дополнительную норму воды в зависимости от температуры.

    :param temperature: Текущая температура в городе пользователя
    :return: Дополнительное количество воды в мл
    """
    if temperature > 25:
        return (temperature - 25) * 50  # 50 мл за каждый градус выше 25°C
    return 0


def calculate_age(birth_date: str | date, date_format: str = "%Y-%m-%d") -> int:
    """
    Рассчитывает возраст на основе даты рождения.

    :param birth_date: Дата рождения в виде строки или объекта datetime.date.
    :param date_format: Формат входящей даты, если передана строка (по умолчанию '%Y-%m-%d').
    :return: Возраст в годах (int).
    """
    if isinstance(birth_date, str):
        birth_date_obj = datetime.strptime(birth_date, date_format).date()
    elif isinstance(birth_date, date):
        birth_date_obj = birth_date
    else:
        raise TypeError("birth_date должен быть строкой или datetime.date")

    current_date = datetime.now().date()
    age = current_date.year - birth_date_obj.year - (
        (current_date.month, current_date.day) < (birth_date_obj.month, birth_date_obj.day)
    )
    return age
