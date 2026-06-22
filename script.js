// =========================================================================
// 1. НАСТРОЙКИ И ПЕРЕМЕННЫЕ
// =========================================================================
// РЕЖИМ ТЕСТИРОВАНИЯ:
// true — сайт думает, что ты у Сибириуса (кнопка сразу загорится)
// false — сайт честно проверяет GPS телефона (для защиты проекта)
const DEBUG_MODE = false; 

let currentScore = 0;
const SIBIRIUS_LAT = 61.0118;
const SIBIRIUS_LON = 69.0535;

// Шаблон AR-сцены (взорвется на странице по клику на кнопку)
const arSceneHTML = `
    <a-scene embedded arjs="sourceType: webcam; debugUIEnabled: false;">
        <a-marker preset="hiro" id="marker1">
            <a-box position="0 0.5 0" material="color: #00ff88;"></a-box>
        </a-marker>
        <a-marker preset="kanji" id="marker2">
            <a-sphere position="0 0.5 0" material="color: #ff0055;"></a-sphere>
        </a-marker>
        <a-entity camera></a-entity>
    </a-scene>
`;

// =========================================================================
// 2. ЛОГИКА ГЕОЛОКАЦИИ
// =========================================================================
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Радиус Земли в км
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; 
}

if (DEBUG_MODE) {
    // Если включен тест — мгновенно активируем кнопку старта
    document.getElementById('status-text').innerText = "Режим теста: координаты Сибириуса подтверждены!";
    document.getElementById('start-btn').disabled = false;
} else {
    // Настоящий опрос GPS спутников
    navigator.geolocation.getCurrentPosition((position) => {
        const userLat = position.coords.latitude;
        const userLon = position.coords.longitude;
        const distance = getDistance(userLat, userLon, SIBIRIUS_LAT, SIBIRIUS_LON);

        if (distance <= 1.0) {
            document.getElementById('status-text').innerText = "Ты на месте! Радиус подтвержден.";
            document.getElementById('start-btn').disabled = false;
        } else {
            document.getElementById('status-text').innerText = `Ты слишком далеко. Подойди ближе к Сибириусу (осталось ${distance.toFixed(2)} км).`;
        }
    }, (error) => {
        document.getElementById('status-text').innerText = "Ошибка: разреши доступ к GPS в браузере.";
    });
}

// =========================================================================
// 3. УПРАВЛЕНИЕ ИНТЕРФЕЙСОМ И AR
// =========================================================================

// Слушаем клик по кнопке старта
document.getElementById('start-btn').addEventListener('click', () => {
    // Опечатка исправлена: теперь geo-screen гарантированно исчезнет
    document.getElementById('geo-screen').style.display = 'none';
    document.getElementById('game-ui').style.display = 'block';   

    // Вставляем AR-камеру в пустой контейнер
    document.getElementById('ar-container').innerHTML = arSceneHTML;

    // Запускаем проверку маркеров
    initMarkerListeners();
});

// Функция отслеживания маркеров
function initMarkerListeners() {
    // Задание 1 (Маркер Hiro)
    document.getElementById('marker1').addEventListener('markerFound', () => {
        if (currentScore === 0) {
            currentScore = 1;
            document.getElementById('score').innerText = currentScore;
            document.getElementById('quest-hint').innerText = "Отлично! Задание 2: Найди главный вход и отсканируй маркер там.";
            alert("Задание 1 выполнено!");
        }
    });

    // Задание 2 (Маркер Kanji)
    document.getElementById('marker2').addEventListener('markerFound', () => {
        if (currentScore === 1) {
            currentScore = 2;
            document.getElementById('score').innerText = currentScore;
            document.getElementById('quest-hint').innerText = "Круто! Переходи к заданию 3...";
            alert("Задание 2 выполнено!");
        }
    });
}