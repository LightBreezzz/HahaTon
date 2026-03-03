// Календарь занятости и бронирование

let allZones = [];

// Загрузка зон для select
async function loadZonesForSelect() {
    try {
        allZones = await api.getZones();
        
        const zoneSelect = document.getElementById('zone-select');
        const bookingZoneSelect = document.getElementById('booking-zone');
        
        if (zoneSelect) {
            zoneSelect.innerHTML = '<option value="">Все зоны</option>' + 
                allZones.map(z => `<option value="${z.id}">${z.name}</option>`).join('');
        }
        
        if (bookingZoneSelect) {
            bookingZoneSelect.innerHTML = '<option value="">Выберите зону</option>' + 
                allZones.map(z => `<option value="${z.id}">${z.name} - ${z.price_per_hour} ₽/час</option>`).join('');
        }
    } catch (error) {
        console.error('Ошибка загрузки зон:', error);
    }
}

// Загрузка расписания
async function loadSchedule() {
    const container = document.getElementById('schedule-container');
    const zoneId = document.getElementById('zone-select').value;
    const dateInput = document.getElementById('date-input').value;
    
    if (!dateInput) {
        container.innerHTML = '<p class="error-state">Выберите дату</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">Загрузка расписания...</div>';
    
    try {
        const date = new Date(dateInput);
        const dateFrom = new Date(date.setHours(0, 0, 0, 0)).toISOString();
        const dateTo = new Date(date.setHours(23, 59, 59, 999)).toISOString();
        
        let allBookings = [];
        
        if (zoneId) {
            // Загрузка для конкретной зоны
            const schedule = await api.getZoneSchedule(zoneId, dateFrom, dateTo);
            allBookings = schedule.bookings || [];
        } else {
            // Загрузка для всех зон
            for (const zone of allZones) {
                try {
                    const schedule = await api.getZoneSchedule(zone.id, dateFrom, dateTo);
                    allBookings = [...allBookings, ...(schedule.bookings || [])];
                } catch (e) {
                    // Игнорируем ошибки для отдельных зон
                }
            }
        }
        
        displaySchedule(allBookings, dateInput);
    } catch (error) {
        container.innerHTML = '<p class="error-state">Ошибка загрузки расписания</p>';
        console.error(error);
    }
}

// Отображение расписания
function displaySchedule(bookings, date) {
    const container = document.getElementById('schedule-container');
    
    if (bookings.length === 0) {
        container.innerHTML = `
            <div class="schedule-grid">
                <p class="empty-state">На эту дату нет бронирований</p>
            </div>
        `;
        return;
    }
    
    // Генерируем временные слоты с 8:00 до 23:00
    const hours = [];
    for (let i = 8; i <= 23; i++) {
        hours.push(i);
    }
    
    const dateObj = new Date(date);
    
    let html = '<div class="schedule-grid">';
    
    for (const hour of hours) {
        const timeString = `${hour.toString().padStart(2, '0')}:00`;
        const slotBookings = bookings.filter(b => {
            const bookingStart = new Date(b.start_time);
            return bookingStart.getHours() === hour;
        });
        
        let statusClass = 'slot-free';
        let statusText = 'Свободно';
        let onClick = `onclick="selectTimeSlot('${timeString}')"`;
        
        if (slotBookings.length > 0) {
            const booking = slotBookings[0];
            statusClass = 'slot-busy';
            statusText = `Занято (${booking.user_name || 'Бронь'})`;
            onClick = '';
        }
        
        html += `
            <div class="time-slot">
                <span class="time-label">${timeString}</span>
                <div class="slot-status ${statusClass}" ${onClick}>
                    ${statusText}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
    
    // Показываем форму бронирования
    const formContainer = document.getElementById('booking-form-container');
    if (formContainer) {
        formContainer.style.display = 'block';
    }
}

// Выбор временного слота
function selectTimeSlot(timeString) {
    const dateInput = document.getElementById('booking-date').value;
    const zoneSelect = document.getElementById('booking-zone');
    
    if (!dateInput) {
        alert('Сначала выберите дату');
        return;
    }
    
    // Устанавливаем время начала
    document.getElementById('booking-start').value = timeString;
    
    // Устанавливаем время окончания (через 1 час)
    const hour = parseInt(timeString.split(':')[0]);
    const endHour = (hour + 1).toString().padStart(2, '0');
    document.getElementById('booking-end').value = `${endHour}:00`;
    
    // Прокручиваем к форме
    document.getElementById('booking-form-container').scrollIntoView({ behavior: 'smooth' });
}

// Обработка формы бронирования
document.addEventListener('DOMContentLoaded', () => {
    const bookingForm = document.getElementById('booking-form');
    const messageDiv = document.getElementById('booking-message');
    
    if (bookingForm) {
        bookingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const user = getUser();
            if (!user) {
                alert('Необходимо войти для бронирования');
                showLoginModal();
                return;
            }
            
            const zoneId = document.getElementById('booking-zone').value;
            const date = document.getElementById('booking-date').value;
            const startTime = document.getElementById('booking-start').value;
            const endTime = document.getElementById('booking-end').value;
            const comment = document.getElementById('booking-comment').value;
            
            if (!zoneId || !date || !startTime || !endTime) {
                messageDiv.innerHTML = '<p class="error-state">Заполните все поля</p>';
                return;
            }
            
            // Создаем datetime строки
            const startDateTime = new Date(`${date}T${startTime}:00`);
            const endDateTime = new Date(`${date}T${endTime}:00`);
            
            if (endDateTime <= startDateTime) {
                messageDiv.innerHTML = '<p class="error-state">Время окончания должно быть позже времени начала</p>';
                return;
            }
            
            try {
                await api.createBooking(
                    parseInt(zoneId),
                    startDateTime.toISOString(),
                    endDateTime.toISOString(),
                    comment
                );
                
                messageDiv.innerHTML = '<p class="success-state" style="color: var(--success-color)">Бронирование успешно создано!</p>';
                
                // Очищаем форму
                bookingForm.reset();
                
                // Перезагружаем расписание
                setTimeout(() => {
                    loadSchedule();
                    messageDiv.innerHTML = '';
                }, 1500);
                
            } catch (error) {
                messageDiv.innerHTML = `<p class="error-state">Ошибка: ${error.message}</p>`;
            }
        });
    }
});
