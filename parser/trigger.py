from flask import Flask, jsonify
import parser as weather_parser

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger():
    try:
        # Запускаем сбор данных
        temps1 = weather_parser.get_weather_openmeteo()
        for period, temp in temps1.items():
            weather_parser.save_to_db('open-meteo', period, temp)
        
        temps2 = weather_parser.get_weather_7timer()
        if temps2:
            for period, temp in temps2.items():
                weather_parser.save_to_db('7timer', period, temp)
        
        return jsonify({'status': 'success', 'message': 'Данные обновлены'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
