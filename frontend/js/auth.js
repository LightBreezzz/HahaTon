// Аутентификация и навигация

// Проверка авторизации
function checkAuth() {
    const user = getUser();
    const nav = document.getElementById('nav');
    const authButtons = document.getElementById('auth-buttons');
    const userInfo = document.getElementById('user-info');
    
    if (user) {
        // Пользователь авторизован
        if (authButtons) authButtons.style.display = 'none';
        if (userInfo) {
            userInfo.style.display = 'block';
            document.getElementById('user-name').textContent = user.full_name;
        }
        
        // Обновляем навигацию
        if (nav) {
            let adminLink = user.role === 'admin' ? '<a href="/admin.html">Админка</a>' : '';
            nav.innerHTML = `
                <a href="/">Главная</a>
                <a href="/calendar.html">Календарь</a>
                <a href="/profile.html">Профиль</a>
                ${adminLink}
                <a href="#" onclick="logout()">Выход</a>
            `;
        }
    } else {
        // Пользователь не авторизован
        if (authButtons) authButtons.style.display = 'block';
        if (userInfo) userInfo.style.display = 'none';
        
        if (nav) {
            nav.innerHTML = `
                <a href="/">Главная</a>
                <a href="#" onclick="showLoginModal()">Войти</a>
            `;
        }
    }
}

// Проверка авторизации для админки
function checkAdminAuth() {
    const user = getUser();
    
    if (!user) {
        window.location.href = '/';
        return;
    }
    
    if (user.role !== 'admin') {
        alert('Требуется роль администратора');
        window.location.href = '/profile.html';
        return;
    }
    
    // Обновляем навигацию
    const nav = document.getElementById('nav');
    if (nav) {
        nav.innerHTML = `
            <a href="/">Главная</a>
            <a href="/admin.html">Админка</a>
            <a href="/profile.html">Профиль</a>
            <a href="#" onclick="logout()">Выход</a>
        `;
    }
}

// Выход
function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        clearToken();
        window.location.href = '/';
    }
}

// Модальные окна
function showLoginModal() {
    document.getElementById('login-modal').classList.add('active');
}

function showRegisterModal() {
    document.getElementById('register-modal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function switchModal(fromId, toId) {
    closeModal(fromId);
    setTimeout(() => showRegisterModal(toId), 200);
}

// Обработчики форм
document.addEventListener('DOMContentLoaded', () => {
    // Форма входа
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            
            try {
                await api.login(email, password);
                closeModal('login-modal');
                checkAuth();
                window.location.reload();
            } catch (error) {
                alert('Ошибка входа: ' + error.message);
            }
        });
    }
    
    // Форма регистрации
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('register-name').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            
            try {
                await api.register(email, password, name);
                closeModal('register-modal');
                checkAuth();
                window.location.reload();
            } catch (error) {
                alert('Ошибка регистрации: ' + error.message);
            }
        });
    }
});

// Закрытие модального окна по клику вне его
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}
