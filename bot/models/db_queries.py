from datetime import datetime

from utils.logging import setup_logger

logger = setup_logger("queries")

def save_user_profile(user_id, username, name, birth_date,
                        city, height, weight, gender,
                        prefered_water, prefered_calories, prefered_workout,
                        conn, cursor):
    cursor.execute("""
        INSERT INTO users (id, name, birth_date, city, height, weight, gender, prefered_water, prefered_calories, prefered_workout, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            birth_date=excluded.birth_date,
            city=excluded.city,
            height=excluded.height,
            weight=excluded.weight,
            gender=excluded.gender,
            prefered_water=excluded.prefered_water, 
            prefered_calories=excluded.prefered_calories, 
            prefered_workout=excluded.prefered_workout       
        ;
    """, (user_id, name, birth_date, city, height, weight, gender,prefered_water, prefered_calories, prefered_workout))
    conn.commit()
    logger.debug(f"Сохранён профиль пользователя {name} (ID: {user_id}) в базу данных.")

def get_user_profile(user_id, cursor):
    logger.debug(f"Поиск профиля для {user_id}")
    cursor.execute("SELECT name, birth_date, city, height, weight, gender FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def get_user_profile_full(user_id, cursor):
    logger.debug(f"Поиск профиля для {user_id}")
    cursor.execute("SELECT name, birth_date, city, height, weight, gender, prefered_water, prefered_calories, prefered_workout, created_at FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def log_user_norms(user_id, calories_goal, water_goal, workout_goal, conn, cursor):
    """
    Сохраняет или обновляет нормы пользователя в таблице user_goals.

    :param user_id: ID пользователя
    :param calories_goal: Целевая норма калорий
    :param water_goal: Целевая норма воды (в литрах)
    :param workout_goal: Целевая норма тренировок (в минутах)
    :param conn: Подключение к базе данных
    :param cursor: Курсор базы данных
    """
    query = """
    INSERT INTO user_goals (
        user_id, calories_goal, water_goal, workout_goal, updated_at
    )
    VALUES (?, ?, ?, ?, ?);
    """
    cursor.execute(query, (
        user_id, calories_goal, water_goal, workout_goal, datetime.now()
    ))
    conn.commit()
    logger.debug(f"Нормы для пользователя {user_id} сохранены или обновлены.")

def check_logged_user_norms(user_id, conn, cursor) -> bool:
    """
    Проверяет, существует ли запись для пользователя за текущую дату.

    :param user_id: ID пользователя
    :param conn: Подключение к базе данных
    :param cursor: Курсор базы данных
    :return: True, если запись существует, иначе False
    """
    today_date = datetime.now().date()
    query = """
    SELECT 1 FROM user_goals
    WHERE user_id = ? AND DATE(updated_at) = ?;
    """
    try:
        cursor.execute(query, (user_id, today_date))
        exists = cursor.fetchone() is not None
        logger.debug(f"Проверка записи за {today_date} для пользователя {user_id}: {'существует' if exists else 'отсутствует'}.")
        return exists
    except Exception as e:
        logger.error(f"Ошибка при проверке записи для пользователя {user_id} за {today_date}: {e}")
        raise


def last_logged_user_norms(user_id, conn, cursor):
    """
    Получает последнюю запись пользователя из таблицы user_goals.

    :param user_id: ID пользователя
    :param conn: Подключение к базе данных
    :param cursor: Курсор базы данных
    :return: Последняя запись или None, если записей нет
    """
    query = """
    SELECT calories_goal, water_goal, workout_goal, updated_at
    FROM user_goals
    WHERE user_id = ?
    ORDER BY updated_at DESC
    LIMIT 1;
    """
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            logger.debug(f"Последняя запись для пользователя {user_id}: {result}.")
        else:
            logger.debug(f"Для пользователя {user_id} нет записей в таблице user_goals.")
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении последней записи для пользователя {user_id}: {e}")
        raise




def log_water(cursor, user_id, amount):
    """
    Логирует количество выпитой воды в таблицу water_intake.

    :param cursor: Курсор базы данных
    :param user_id: ID пользователя
    :param amount: Количество воды (мл)
    """
    query = """
    INSERT INTO water_intake (user_id, date, water_consumed)
    VALUES (?, ?, ?);
    """
    try:
        cursor.execute(query, (user_id, datetime.now().date(), amount))
        logger.debug(f"В таблицу water_intake добавлена запись: user_id={user_id}, water_consumed={amount} мл.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении записи в water_intake для пользователя {user_id}: {e}")
        raise


def get_water_total_today(user_id, cursor):
    """
    Возвращает суммарное количество воды, выпитой пользователем за текущий день.

    :param cursor: Курсор базы данных
    :param user_id: ID пользователя
    :return: Суммарное количество воды за день (мл)
    """
    query = """
    SELECT SUM(water_consumed)
    FROM water_intake
    WHERE user_id = ? AND date = ?;
    """
    try:
        cursor.execute(query, (user_id, datetime.now().date()))
        result = cursor.fetchone()
        total = result[0] if result[0] is not None else 0
        logger.debug(f"Суммарное количество воды за {datetime.now().date()} для пользователя {user_id}: {total} мл.")
        return total
    except Exception as e:
        logger.error(f"Ошибка при получении суммарного количества воды для пользователя {user_id}: {e}")
        raise


def log_calories(cursor, user_id, amount):
    """
    Логирует количество потребленных калорий в таблицу calorie_intake.

    :param cursor: Курсор базы данных
    :param user_id: ID пользователя
    :param amount: Количество калорий (ккал)
    """
    query = """
    INSERT INTO calorie_intake (user_id, date, calories)
    VALUES (?, ?, ?);
    """
    try:
        cursor.execute(query, (user_id, datetime.now().date(), amount))
        logger.debug(f"В таблицу calorie_intake добавлена запись: user_id={user_id}, calories={amount} ккал.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении записи в calorie_intake для пользователя {user_id}: {e}")
        raise



def get_calories_total_today(user_id, cursor):
    """
    Возвращает суммарное количество калорий, потребленных пользователем за текущий день.

    :param cursor: Курсор базы данных
    :param user_id: ID пользователя
    :return: Суммарное количество калорий за день (ккал)
    """
    query = """
    SELECT SUM(calories)
    FROM calorie_intake
    WHERE user_id = ? AND date = ?;
    """
    try:
        cursor.execute(query, (user_id, datetime.now().date()))
        result = cursor.fetchone()
        total = result[0] if result[0] is not None else 0
        logger.debug(f"Суммарное количество калорий за {datetime.now().date()} для пользователя {user_id}: {total} ккал.")
        return total
    except Exception as e:
        logger.error(f"Ошибка при получении суммарного количества калорий для пользователя {user_id}: {e}")
        raise

def is_weather_logged_today(city, cursor):
    """
    Проверяет, записана ли информация о погоде для указанного города на текущий день.

    :param city: Название города
    :param cursor: Курсор базы данных
    :return: True, если запись существует, иначе False
    """
    today_date = datetime.now().date()
    query = """
    SELECT 1 FROM weather
    WHERE city = ? AND date = ?;
    """
    try:
        cursor.execute(query, (city, today_date))
        exists = cursor.fetchone() is not None
        logger.debug(f"Проверка существования записи о погоде для {city} на {today_date}: {'существует' if exists else 'отсутствует'}.")
        return exists
    except Exception as e:
        logger.error(f"Ошибка при проверке записи о погоде для {city}: {e}")
        raise


def log_weather(city, temperature, conn, cursor):
    """
    Сохраняет информацию о погоде в таблицу weather.

    :param city: Название города
    :param temperature: Температура в городе
    :param conn: Подключение к базе данных
    :param cursor: Курсор базы данных
    """
    query = """
    INSERT INTO weather (city, date, temperature)
    VALUES (?, ?, ?);
    """
    try:
        cursor.execute(query, (city, datetime.now().date(), temperature))
        conn.commit()
        logger.debug(f"Добавлена запись о погоде: {city}, {temperature}°C на {datetime.now().date()}.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении записи о погоде для {city}: {e}")
        raise


def get_weather_for_today(city, cursor):
    """
    Возвращает информацию о температуре для города на текущий день.

    :param city: Название города
    :param cursor: Курсор базы данных
    :return: Температура (float) или None, если данных нет
    """
    today_date = datetime.now().date()
    query = """
    SELECT temperature
    FROM weather
    WHERE city = ? AND date = ?;
    """
    try:
        cursor.execute(query, (city, today_date))
        result = cursor.fetchone()
        if result:
            logger.debug(f"Температура для {city} на {today_date}: {result[0]}°C.")
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Ошибка при получении температуры для {city}: {e}")
        raise


def get_user_city(user_id, cursor):
    """
    Возвращает город пользователя из таблицы users.

    :param user_id: ID пользователя
    :param cursor: Курсор базы данных
    :return: Название города или None, если данных нет
    """
    query = """
    SELECT city
    FROM users
    WHERE id = ?;
    """
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            logger.debug(f"Город пользователя {user_id}: {result[0]}.")
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Ошибка при получении города для пользователя {user_id}: {e}")
        raise


def log_workout(cursor, user_id, workout_type, duration, calories_burned):
    """
    Логирует тренировку пользователя в таблицу workouts.

    :param cursor: Курсор базы данных
    :param user_id: ID пользователя
    :param workout_type: Тип тренировки
    :param duration: Длительность в минутах
    :param calories_burned: Сожжённые калории
    """
    query = """
    INSERT INTO workouts (user_id, date, workout_type, duration, calories_burned)
    VALUES (?, ?, ?, ?, ?);
    """
    cursor.execute(query, (user_id, datetime.now().date(), workout_type, duration, calories_burned))


def get_workout_stats_today(user_id, cursor):
    """
    Возвращает суммарное время тренировок и количество сожжённых калорий за текущий день.

    :param cursor: Курсор базы данных
    :param user_id: ID пользователя
    :return: Кортеж (общая продолжительность тренировок в минутах, общее количество сожжённых калорий)
    """
    query = """
    SELECT SUM(duration) AS total_duration, SUM(calories_burned) AS total_calories
    FROM workouts
    WHERE user_id = ? AND date = ?;
    """
    try:
        cursor.execute(query, (user_id, datetime.now().date()))
        result = cursor.fetchone()
        total_duration = result[0] if result[0] is not None else 0
        total_calories = result[1] if result[1] is not None else 0
        logger.debug(
            f"Тренировочная статистика за {datetime.now().date()} для пользователя {user_id}: "
            f"{total_duration} минут, {total_calories} ккал."
        )
        return total_duration, total_calories
    except Exception as e:
        logger.error(f"Ошибка при получении статистики тренировок для пользователя {user_id}: {e}")
        raise
