// Профиль пользователя

async function loadProfile() {
    try {
        const user = await api.getProfile();
        const container = document.getElementById('profile-container');
        
        container.innerHTML = `
            <div class="profile-info">
                <div class="profile-info-item">
                    <div class="profile-info-label">Имя</div>
                    <div class="profile-info-value">${user.full_name}</div>
                </div>
                <div class="profile-info-item">
                    <div class="profile-info-label">Email</div>
                    <div class="profile-info-value">${user.email}</div>
                </div>
                <div class="profile-info-item">
                    <div class="profile-info-label">Роль</div>
                    <div class="profile-info-value">${user.role === 'admin' ? '👑 Администратор' : '👤 Пользователь'}</div>
                </div>
                <div class="profile-info-item">
                    <div class="profile-info-label">Дата регистрации</div>
                    <div class="profile-info-value">${new Date(user.created_at).toLocaleDateString('ru-RU')}</div>
                </div>
            </div>
        `;
        
        // Загружаем бронирования и достижения
        loadUserBookings();
        loadUserAchievements();
        
    } catch (error) {
        if (error.message.includes('авторизация')) {
            window.location.href = '/';
        } else {
            document.getElementById('profile-container').innerHTML = 
                '<p class="error-state">Ошибка загрузки профиля</p>';
        }
    }
}

async function loadUserBookings() {
    try {
        const bookings = await api.getMyBookings();
        const container = document.getElementById('bookings-list');
        
        if (bookings.length === 0) {
            container.innerHTML = '<p class="empty-state">У вас пока нет бронирований</p>';
            updateStats({ bookings: 0, activeBookings: 0 });
            return;
        }
        
        let activeCount = 0;
        
        container.innerHTML = bookings.map(booking => {
            const startDate = new Date(booking.start_time);
            const endDate = new Date(booking.end_time);
            
            if (booking.status === 'confirmed' || booking.status === 'pending') {
                activeCount++;
            }
            
            return `
                <div class="booking-item">
                    <div class="booking-info">
                        <h4>${booking.zone_name || 'Зона #' + booking.zone_id}</h4>
                        <div class="booking-details">
                            📅 ${startDate.toLocaleDateString('ru-RU')} 
                            ⏰ ${startDate.toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})} - 
                                 ${endDate.toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})}
                        </div>
                        ${booking.comment ? `<p class="booking-comment">💬 ${booking.comment}</p>` : ''}
                    </div>
                    <div class="booking-actions">
                        <span class="booking-status status-${booking.status}">${getStatusText(booking.status)}</span>
                        ${(booking.status === 'confirmed' || booking.status === 'pending') ? 
                            `<button class="btn btn-danger btn-small" onclick="cancelBooking(${booking.id})">Отменить</button>` : 
                            ''}
                    </div>
                </div>
            `;
        }).join('');
        
        updateStats({ bookings: bookings.length, activeBookings: activeCount });
        
    } catch (error) {
        document.getElementById('bookings-list').innerHTML = 
            '<p class="error-state">Ошибка загрузки бронирований</p>';
    }
}

async function loadUserAchievements() {
    try {
        const achievements = await api.getMyAchievements();
        const container = document.getElementById('achievements-list');
        
        if (achievements.length === 0) {
            container.innerHTML = `
                <p class="empty-state">У вас пока нет достижений</p>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">
                    Бронируйте время и получайте достижения!
                </p>
            `;
            updateStats({ achievements: 0 });
            return;
        }
        
        container.innerHTML = `
            <div class="achievements-grid">
                ${achievements.map(ua => `
                    <div class="achievement-card">
                        <span class="achievement-icon">${ua.achievement?.icon || '🏆'}</span>
                        <div class="achievement-name">${ua.achievement?.name || 'Достижение'}</div>
                        <div class="achievement-description">${ua.achievement?.description || ''}</div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 8px;">
                            ${new Date(ua.earned_at).toLocaleDateString('ru-RU')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        updateStats({ achievements: achievements.length });
        
    } catch (error) {
        document.getElementById('achievements-list').innerHTML = 
            '<p class="error-state">Ошибка загрузки достижений</p>';
    }
}

function getStatusText(status) {
    const texts = {
        'pending': 'Ожидает',
        'confirmed': 'Подтверждено',
        'completed': 'Завершено',
        'cancelled': 'Отменено',
        'no_show': 'Не явился'
    };
    return texts[status] || status;
}

function updateStats(data) {
    if (data.bookings !== undefined) {
        document.getElementById('stat-total-bookings').textContent = data.bookings;
    }
    if (data.activeBookings !== undefined) {
        document.getElementById('stat-active-bookings').textContent = data.activeBookings;
    }
    if (data.achievements !== undefined) {
        document.getElementById('stat-achievements').textContent = data.achievements;
    }
}

async function cancelBooking(bookingId) {
    if (!confirm('Вы уверены, что хотите отменить бронирование?')) {
        return;
    }
    
    try {
        await api.cancelBooking(bookingId);
        alert('Бронирование отменено');
        loadUserBookings(); // Перезагружаем список
    } catch (error) {
        alert('Ошибка отмены: ' + error.message);
    }
}
