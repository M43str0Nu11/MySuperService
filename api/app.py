from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Настройка логирования
logging.basicConfig(
    filename='/app/logs/errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_db_connection():
    return psycopg2.connect(
        host="db",
        database="weather_db",
        user="weather_user",
        password="weather_pass"
    )

@app.route('/api/weather', methods=['GET'])
def get_weather():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Усреднённые данные
    cursor.execute("SELECT period, avg_temp FROM weather_avg ORDER BY CASE period WHEN 'morning' THEN 1 WHEN 'day' THEN 2 WHEN 'evening' THEN 3 END")
    avg_data = cursor.fetchall()
    
    # Данные по источникам
    cursor.execute("""
        SELECT source, period, ROUND(temperature, 0) as temp 
        FROM weather_data 
        WHERE created_at > NOW() - INTERVAL '2 hours'
        ORDER BY source, CASE period WHEN 'morning' THEN 1 WHEN 'day' THEN 2 WHEN 'evening' THEN 3 END
    """)
    source_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Формируем ответ
    result = {
        'average': {row[0]: int(row[1]) for row in avg_data},
        'sources': {}
    }
    
    for source, period, temp in source_data:
        if source not in result['sources']:
            result['sources'][source] = {}
        result['sources'][source][period] = int(temp)
    
    return jsonify(result)

@app.route('/api/refresh', methods=['POST'])
def refresh_weather():
    try:
        import requests as req
        # Вызываем HTTP endpoint парсера
        response = req.post('http://parser:5001/trigger', timeout=90)
        
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Данные обновлены'})
        else:
            error_msg = response.json().get('message', 'Неизвестная ошибка')
            logging.error(f'Parser error: {error_msg}')
            return jsonify({'status': 'error', 'message': error_msg}), 500
            
    except req.exceptions.Timeout:
        error_msg = 'Превышено время ожидания'
        logging.error(f'Parser timeout: {error_msg}')
        return jsonify({'status': 'error', 'message': error_msg}), 500
    except Exception as e:
        error_msg = str(e)
        logging.error(f'Unexpected error: {error_msg}')
        return jsonify({'status': 'error', 'message': error_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
