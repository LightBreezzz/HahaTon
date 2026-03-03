// Админ-панель

async function loadAdminStats() {
    try {
        const stats = await api.getAdminStats();
        const container = document.getElementById('admin-stats');
        
        container.innerHTML = `
            <div class="stat-card">
                <span class="stat-value">${stats.total_users}</span>
                <span class="stat-label">Пользователей</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.total_zones}</span>
                <span class="stat-label">Зон</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.today_bookings}</span>
                <span class="stat-label">Бронирований сегодня</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.today_revenue} ₽</span>
                <span class="stat-label">Выручка сегодня</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.bookings_by_status?.confirmed || 0}</span>
                <span class="stat-label">Активных броней</span>
            </div>
        `;
        
        // Загружаем данные по умолчанию
        loadAdminBookings();
        
    } catch (error) {
        document.getElementById('admin-stats').innerHTML = 
            '<p class="error-state">Ошибка загрузки статистики</p>';
    }
}

async function loadAdminBookings() {
    try {
        const bookings = await api.getAdminBookings();
        const container = document.getElementById('admin-bookings-list');
        
        if (bookings.length === 0) {
            container.innerHTML = '<p class="empty-state">Нет бронирований</p>';
            return;
        }
        
        container.innerHTML = `
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Пользователь</th>
                        <th>Зона</th>
                        <th>Начало</th>
                        <th>Окончание</th>
                        <th>Статус</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${bookings.map(booking => `
                        <tr>
                            <td>${booking.id}</td>
                            <td>${booking.user_name || 'N/A'}<br><small>${booking.user_email || ''}</small></td>
                            <td>${booking.zone_name || 'N/A'}</td>
                            <td>${new Date(booking.start_time).toLocaleString('ru-RU')}</td>
                            <td>${new Date(booking.end_time).toLocaleString('ru-RU')}</td>
                            <td><span class="booking-status status-${booking.status}">${booking.status}</span></td>
                            <td>
                                <button class="btn btn-small btn-secondary" onclick="editBookingStatus(${booking.id})">Статус</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
    } catch (error) {
        document.getElementById('admin-bookings-list').innerHTML = 
            '<p class="error-state">Ошибка загрузки бронирований</p>';
    }
}

async function loadAdminZones() {
    try {
        const zones = await api.getAdminZones();
        const container = document.getElementById('admin-zones-list');
        
        if (zones.length === 0) {
            container.innerHTML = '<p class="empty-state">Нет зон</p>';
            return;
        }
        
        container.innerHTML = `
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Название</th>
                        <th>Тип</th>
                        <th>Вместимость</th>
                        <th>Цена</th>
                        <th>Статус</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${zones.map(zone => `
                        <tr>
                            <td>${zone.id}</td>
                            <td>${zone.name}</td>
                            <td>${zone.zone_type}</td>
                            <td>${zone.capacity}</td>
                            <td>${zone.price_per_hour} ₽</td>
                            <td>${zone.is_active ? '✅ Активна' : '❌ Неактивна'}</td>
                            <td>
                                <button class="btn btn-small btn-danger" onclick="deleteZone(${zone.id})">Удалить</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
    } catch (error) {
        document.getElementById('admin-zones-list').innerHTML = 
            '<p class="error-state">Ошибка загрузки зон</p>';
    }
}

async function loadAdminUsers() {
    try {
        const users = await api.getAdminUsers();
        const container = document.getElementById('admin-users-list');
        
        if (users.length === 0) {
            container.innerHTML = '<p class="empty-state">Нет пользователей</p>';
            return;
        }
        
        container.innerHTML = `
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Имя</th>
                        <th>Email</th>
                        <th>Роль</th>
                        <th>Дата регистрации</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.full_name}</td>
                            <td>${user.email}</td>
                            <td>${user.role === 'admin' ? '👑 Админ' : '👤 Пользователь'}</td>
                            <td>${new Date(user.created_at).toLocaleDateString('ru-RU')}</td>
                            <td>${user.is_active ? '✅ Активен' : '❌ Неактивен'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
    } catch (error) {
        document.getElementById('admin-users-list').innerHTML = 
            '<p class="error-state">Ошибка загрузки пользователей</p>';
    }
}

// Переключение вкладок
function showTab(tabName) {
    // Скрываем все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Убираем активный класс у кнопок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Показываем нужную вкладку
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Находим кнопку и делаем активной
    event.target.classList.add('active');
    
    // Загружаем данные
    if (tabName === 'bookings') {
        loadAdminBookings();
    } else if (tabName === 'zones') {
        loadAdminZones();
    } else if (tabName === 'users') {
        loadAdminUsers();
    }
}

// Показать форму добавления зоны
function showZoneForm() {
    const container = document.getElementById('zone-form-container');
    container.style.display = container.style.display === 'none' ? 'block' : 'none';
}

// Обработка формы создания зоны
document.addEventListener('DOMContentLoaded', () => {
    const zoneForm = document.getElementById('zone-form');
    
    if (zoneForm) {
        zoneForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const zoneData = {
                name: document.getElementById('zone-name').value,
                description: document.getElementById('zone-description').value,
                zone_type: document.getElementById('zone-type').value,
                capacity: parseInt(document.getElementById('zone-capacity').value),
                price_per_hour: parseInt(document.getElementById('zone-price').value),
                equipment: document.getElementById('zone-equipment').value,
                is_active: true
            };
            
            try {
                await api.createZone(zoneData);
                alert('Зона успешно создана');
                zoneForm.reset();
                showZoneForm();
                loadAdminZones();
            } catch (error) {
                alert('Ошибка создания: ' + error.message);
            }
        });
    }
});

async function deleteZone(zoneId) {
    if (!confirm('Вы уверены, что хотите удалить зону? Это действие нельзя отменить.')) {
        return;
    }
    
    try {
        await api.deleteZone(zoneId);
        alert('Зона удалена');
        loadAdminZones();
    } catch (error) {
        alert('Ошибка удаления: ' + error.message);
    }
}

async function editBookingStatus(bookingId) {
    const newStatus = prompt('Введите новый статус (confirmed, cancelled, completed, pending, no_show):');
    if (!newStatus) return;
    
    // Здесь можно добавить API для обновления статуса
    alert('Функция обновления статуса в разработке');
}
