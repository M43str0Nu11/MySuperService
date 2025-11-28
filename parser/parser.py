import requests
import psycopg2
import time
from datetime import datetime
from bs4 import BeautifulSoup

# Координаты Новосибирска
CITY = "Novosibirsk"
LAT = 55.0084
LON = 82.9357

# Подключение к БД
def get_db_connection():
    return psycopg2.connect(
        host="db",
        database="weather_db",
        user="weather_user",
        password="weather_pass"
    )

# Источник 1: Open-Meteo - прогноз на 8:00, 14:00, 20:00
def get_weather_openmeteo():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m&timezone=Asia/Novosibirsk&forecast_days=1"
    response = requests.get(url, timeout=10)
    data = response.json()
    temps = data['hourly']['temperature_2m']
    times = data['hourly']['time']
    
    result = {}
    for i, time_str in enumerate(times):
        hour = int(time_str.split('T')[1].split(':')[0])
        if hour == 7:
            result['morning'] = temps[i]
        elif hour == 13:
            result['day'] = temps[i]
        elif hour == 19:
            result['evening'] = temps[i]
    return result

# Источник 2: wttr.in - бесплатный API погоды
def get_weather_wttr():
    url = f"https://wttr.in/Novosibirsk?format=j1"
    try:
        response = requests.get(url, timeout=60)
        data = response.json()
        
        # Берём почасовой прогноз на сегодня
        hourly = data['weather'][0]['hourly']
        
        # Ищем ближайшие к 8:00, 14:00, 20:00
        temps = {}
        for hour_data in hourly:
            hour = int(hour_data['time']) // 100
            temp = int(hour_data['tempC'])
            
            if hour == 8 or (hour == 9 and 'morning' not in temps):
                temps['morning'] = temp
            elif hour == 14 or (hour == 15 and 'day' not in temps):
                temps['day'] = temp
            elif hour == 20 or (hour == 21 and 'evening' not in temps):
                temps['evening'] = temp
        
        if len(temps) == 3:
            return temps
    except Exception as e:
        print(f"wttr.in error: {e}")
    return None

# Источник 2: 7Timer! - простой API
def get_weather_7timer():
    url = f"http://www.7timer.info/bin/api.pl?lon={LON}&lat={LAT}&product=civil&output=json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        dataseries = data['dataseries']
        
        # init_time - время начала прогноза (YYYYMMDDHH) в UTC
        init_str = str(data['init'])
        init_hour = int(init_str[-2:])
        
        result = {}
        for item in dataseries:
            timepoint = item['timepoint']
            # Переводим в местное время Новосибирска (UTC+7)
            hour_local = (init_hour + timepoint + 7) % 24
            temp = item['temp2m']
            
            # Ищем точные часы: 7am, 1pm, 7pm
            if hour_local == 7 and 'morning' not in result:
                result['morning'] = temp
            elif hour_local == 13 and 'day' not in result:
                result['day'] = temp
            elif hour_local == 19 and 'evening' not in result:
                result['evening'] = temp
            
            if len(result) == 3:
                break
        
        if len(result) == 3:
            return result
    except Exception as e:
        print(f"7Timer error: {e}")
    return None

# Проверка времени обновления (7:00)
def should_update():
    hour = datetime.now().hour
    return hour == 7

# Запись в БД (с нормализацией)
def save_to_db(source, period, temperature):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем ID источника
    cursor.execute("SELECT id FROM weather_sources WHERE name = %s", (source,))
    source_id = cursor.fetchone()[0]
    
    # Получаем ID периода
    cursor.execute("SELECT id FROM weather_periods WHERE name = %s", (period,))
    period_id = cursor.fetchone()[0]
    
    # Записываем данные
    cursor.execute(
        "INSERT INTO weather_data (source_id, period_id, temperature) VALUES (%s, %s, %s)",
        (source_id, period_id, temperature)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Основной цикл
def main():
    print(f"Парсер погоды для {CITY} запущен...")
    print(f"Обновление прогноза каждый день в 7:00")
    print(f"Прогноз на: 7:00 (утро), 13:00 (день), 19:00 (вечер)")
    
    while True:
        current_time = datetime.now()
        print(f"\n[{current_time}] Проверка времени...")
        
        if should_update():
            print("⏰ Время обновления! Собираем прогноз на сегодня...")
            
            # Источник 1: Open-Meteo
            try:
                temps1 = get_weather_openmeteo()
                for period, temp in temps1.items():
                    save_to_db('open-meteo', period, temp)
                print(f"✓ Open-Meteo: утро={temps1.get('morning')}°C, день={temps1.get('day')}°C, вечер={temps1.get('evening')}°C")
            except Exception as e:
                print(f"✗ Open-Meteo: {e}")
            
            # Источник 2: 7Timer!
            temps2 = get_weather_7timer()
            if temps2:
                for period, temp in temps2.items():
                    save_to_db('7timer', period, temp)
                print(f"✓ 7Timer!: утро={temps2.get('morning')}°C, день={temps2.get('day')}°C, вечер={temps2.get('evening')}°C")
            else:
                print(f"✗ 7Timer!: ошибка парсинга")
            
            print(f"✅ Прогноз обновлён! Следующее обновление завтра в 7:00")
        else:
            print(f"⏳ Ждём 7:00 для обновления прогноза...")
        
        time.sleep(3600)  # Проверяем каждый час

if __name__ == "__main__":
    # Для теста: сразу обновляем при запуске
    print("🚀 Первый запуск - собираем данные сразу...")
    try:
        temps1 = get_weather_openmeteo()
        for period, temp in temps1.items():
            save_to_db('open-meteo', period, temp)
        print(f"✓ Open-Meteo готов")
    except Exception as e:
        print(f"✗ Open-Meteo: {e}")
    
    temps2 = get_weather_7timer()
    if temps2:
        for period, temp in temps2.items():
            save_to_db('7timer', period, temp)
        print(f"✓ 7Timer! готов")
    
    print("\n✅ Начальные данные загружены!\n")
    main()
