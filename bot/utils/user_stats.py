import io
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection

def generate_user_stats(user_id: int):
    conn, cursor = get_database_connection(main_database)
    
    # Определяем период последних 7 дней (сегодня + предыдущие 6)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    # 1) Получаем суммарные калории за каждый день
    cursor.execute("""
        SELECT date, SUM(calories) as total_calories
        FROM calorie_intake
        WHERE user_id = ? AND date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
    """, (user_id, start_date, end_date))
    calorie_data = cursor.fetchall()
    
    # 2) Суммарная вода
    cursor.execute("""
        SELECT date, SUM(water_consumed) as total_water
        FROM water_intake
        WHERE user_id = ? AND date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
    """, (user_id, start_date, end_date))
    water_data = cursor.fetchall()
    
    # 3) Суммарная длительность тренировок
    cursor.execute("""
        SELECT date, SUM(duration) as total_workout
        FROM workouts
        WHERE user_id = ? AND date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
    """, (user_id, start_date, end_date))
    workout_data = cursor.fetchall()

    close_database_connection(conn)
    
    days = [start_date + timedelta(days=i) for i in range(7)]
    
    cal_dict = {}
    for row in calorie_data:
        # row[0] = 'YYYY-MM-DD', row[1] = total_calories
        cal_date = datetime.strptime(row[0], '%Y-%m-%d').date()
        cal_dict[cal_date] = row[1] if row[1] else 0
    
    water_dict = {}
    for row in water_data:
        water_date = datetime.strptime(row[0], '%Y-%m-%d').date()
        water_dict[water_date] = row[1] if row[1] else 0
    
    workout_dict = {}
    for row in workout_data:
        workout_date = datetime.strptime(row[0], '%Y-%m-%d').date()
        workout_dict[workout_date] = row[1] if row[1] else 0
    
    cals_list = []
    water_list = []
    workout_list = []
    
    for d in days:
        cals_list.append(cal_dict.get(d, 0))
        water_list.append(water_dict.get(d, 0))
        workout_list.append(workout_dict.get(d, 0))
    
    fig, axes = plt.subplots(3, 1, figsize=(8, 10))
    

    day_labels = [d.strftime("%d.%m") for d in days]

    # Калории
    axes[0].bar(day_labels, cals_list, color='blue')
    axes[0].set_title("Калории")
    axes[0].set_ylabel("ккал")

    # Вода
    axes[1].bar(day_labels, water_list, color='cyan')
    axes[1].set_title("Вода")
    axes[1].set_ylabel("мл")

    # Тренировки
    axes[2].bar(day_labels, workout_list, color='green')
    axes[2].set_title("Тренировки")
    axes[2].set_ylabel("минуты")

    plt.tight_layout()
    

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=80)
    plt.close(fig) 
    buffer.seek(0)
    

    total_calories = sum(cals_list)
    total_water = sum(water_list)
    total_workout = sum(workout_list)
    
    caption = (
        "Ваши результаты за последние 7 дней:\n\n"
        f"• Суммарные калории: {total_calories} ккал\n"
        f"• Суммарно выпито воды: {total_water:.2f} мл\n"
        f"• Суммарная длительность тренировок: {total_workout} мин\n"
    )
    
    return buffer, caption
