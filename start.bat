@echo off
echo ========================================
echo   Cyber Arena - Запуск сервера
echo ========================================
echo.

cd /d "%~dp0backend"

REM Проверка наличия виртуального окружения
if not exist "venv" (
    echo [1/3] Создание виртуального окружения...
    python -m venv venv
)

REM Активация виртуального окружения
echo [2/3] Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo [3/3] Проверка зависимостей...
pip install -q -r requirements.txt

echo.
echo ========================================
echo   Запуск сервера...
echo   API: http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo ========================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
