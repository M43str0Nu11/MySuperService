// Загрузка данных погоды
async function loadWeather() {
    try {
        const response = await fetch('http://localhost:5000/api/weather');
        const data = await response.json();
        
        // Обновляем усреднённые карточки
        updateCard('morning', data.average.morning);
        updateCard('day', data.average.day);
        updateCard('evening', data.average.evening);
        
        // Обновляем таблицу
        updateTable(data.sources);
        
        // Обновляем время
        const now = new Date();
        document.getElementById('last-update').textContent = 
            `Обновлено: ${now.toLocaleString('ru-RU')}`;
        
        // Обновляем дату в заголовке
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = String(now.getFullYear()).slice(-2);
        document.getElementById('forecast-date').textContent = `${day}.${month}.${year}`;
            
    } catch (error) {
        console.error('Ошибка загрузки погоды:', error);
    }
}

function updateCard(period, temp) {
    const cards = document.querySelectorAll('.weather-container');
    const index = period === 'morning' ? 0 : period === 'day' ? 1 : 2;
    const tempElement = cards[index].querySelector('.period-temp');
    tempElement.textContent = temp > 0 ? `+${temp}°` : `${temp}°`;
}

function updateTable(sources) {
    const tbody = document.querySelector('.weather-table tbody');
    const periods = ['morning', 'day', 'evening'];
    const periodNames = ['Утро (7:00)', 'День (13:00)', 'Вечер (19:00)'];
    
    tbody.innerHTML = '';
    
    periods.forEach((period, index) => {
        const row = tbody.insertRow();
        row.insertCell(0).textContent = periodNames[index];
        
        const openmeteo = sources['open-meteo']?.[period];
        const timer7 = sources['7timer']?.[period];
        
        row.insertCell(1).textContent = openmeteo !== undefined ? `${openmeteo > 0 ? '+' : ''}${openmeteo}°` : '-';
        row.insertCell(2).textContent = timer7 !== undefined ? `${timer7 > 0 ? '+' : ''}${timer7}°` : '-';
    });
}

// Показ уведомления
function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Запуск парсера
async function triggerParser() {
    const btn = document.getElementById('refresh-btn');
    btn.disabled = true;
    btn.textContent = 'Обновление...';
    
    try {
        const response = await fetch('http://localhost:5000/api/refresh', {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Ждём 2 секунды чтобы данные записались в БД
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Перезагружаем данные
            await loadWeather();
            
            showNotification('Обновление выполнено успешно', 'success');
        } else {
            throw new Error('Ошибка сервера');
        }
    } catch (error) {
        console.error('Ошибка обновления:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Обновить';
    }
}

// Обработчик кнопки
document.getElementById('refresh-btn').addEventListener('click', triggerParser);

// Загружаем при открытии страницы
loadWeather();

// Обновляем каждые 5 минут
setInterval(loadWeather, 300000);
