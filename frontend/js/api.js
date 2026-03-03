// API клиент
const API_BASE = '/api';

// Получение токена из localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Сохранение токена
function setToken(token) {
    localStorage.setItem('token', token);
}

// Удаление токена
function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

// Получение пользователя из localStorage
function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Сохранение пользователя
function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

// Выполнение API запроса
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    
    const config = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        
        if (response.status === 401) {
            clearToken();
            window.location.href = '/';
            throw new Error('Необходима авторизация');
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка запроса');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// API методы
const api = {
    // Аутентификация
    async login(email, password) {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        setToken(data.access_token);
        setUser(data.user);
        return data;
    },
    
    async register(email, password, full_name) {
        const data = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, full_name })
        });
        setToken(data.access_token);
        setUser(data.user);
        return data;
    },
    
    logout() {
        clearToken();
        window.location.href = '/';
    },
    
    // Пользователь
    async getProfile() {
        return await apiRequest('/users/me');
    },
    
    async getMyBookings() {
        return await apiRequest('/bookings/my');
    },
    
    async getMyAchievements() {
        return await apiRequest('/achievements/my');
    },
    
    // Зоны
    async getZones(zoneType = null) {
        let url = '/zones?is_active=true';
        if (zoneType) {
            url += `&zone_type=${zoneType}`;
        }
        return await apiRequest(url);
    },
    
    async getZoneSchedule(zoneId, dateFrom, dateTo) {
        return await apiRequest(`/zones/${zoneId}/schedule?date_from=${dateFrom}&date_to=${dateTo}`);
    },
    
    // Бронирования
    async createBooking(zone_id, start_time, end_time, comment = null) {
        return await apiRequest('/bookings', {
            method: 'POST',
            body: JSON.stringify({ zone_id, start_time, end_time, comment })
        });
    },
    
    async cancelBooking(bookingId) {
        return await apiRequest(`/bookings/${bookingId}/cancel`, {
            method: 'POST'
        });
    },
    
    // Админ
    async getAdminStats() {
        return await apiRequest('/admin/stats');
    },
    
    async getAdminBookings() {
        return await apiRequest('/admin/bookings');
    },
    
    async getAdminZones() {
        return await apiRequest('/admin/zones/all');
    },
    
    async getAdminUsers() {
        return await apiRequest('/admin/users');
    },
    
    async createZone(zoneData) {
        return await apiRequest('/zones', {
            method: 'POST',
            body: JSON.stringify(zoneData)
        });
    },
    
    async updateZone(zoneId, zoneData) {
        return await apiRequest(`/zones/${zoneId}`, {
            method: 'PUT',
            body: JSON.stringify(zoneData)
        });
    },
    
    async deleteZone(zoneId) {
        return await apiRequest(`/zones/${zoneId}`, {
            method: 'DELETE'
        });
    }
};
