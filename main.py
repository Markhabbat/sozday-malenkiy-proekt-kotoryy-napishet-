# main.py
# -*- coding: utf-8 -*-
"""
FastAPI приложение с Hello World endpoint.

Это простое, но полнофункциональное приложение FastAPI,
которое демонстрирует базовые возможности фреймворка.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
# ============================================================================

app = FastAPI(
    title="Hello World API",
    description="Простой API с приветствием на нескольких языках",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# MIDDLEWARE - CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC МОДЕЛИ
# ============================================================================


class GreetingRequest(BaseModel):
    """
    Модель для запроса персонализированного приветствия.
    
    Attributes:
        name: Имя человека для приветствия (по умолчанию "World")
        language: Язык приветствия (по умолчанию "en")
    """
    name: str = Field(default="World", min_length=1, max_length=100)
    language: str = Field(default="en", regex="^(en|ru|fr|es)$")


class GreetingResponse(BaseModel):
    """
    Модель ответа с приветствием.
    
    Attributes:
        message: Текст приветствия
        name: Имя адресата
        timestamp: Время создания ответа
        status: Статус операции
    """
    message: str
    name: str
    timestamp: str
    status: str = "success"


class HealthCheckResponse(BaseModel):
    """Модель ответа проверки здоровья сервиса."""
    status: str
    timestamp: str
    uptime: float


class APIInfoResponse(BaseModel):
    """Модель с информацией об API."""
    name: str
    version: str
    description: str
    endpoints_count: int


# ============================================================================
# ПЕРЕВОДЫ
# ============================================================================

GREETINGS = {
    "en": "Hello, {name}! 🚀",
    "ru": "Привет, {name}! 🚀",
    "fr": "Bonjour, {name}! 🚀",
    "es": "¡Hola, {name}! 🚀"
}

# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get(
    "/",
    response_model=Dict[str, str],
    summary="Основной endpoint",
    tags=["Basic"]
)
def read_root() -> Dict[str, str]:
    """
    Возвращает простое приветствие "Hello World".
    
    Returns:
        dict: Словарь с сообщением приветствия
        
    Example:
        GET /
        Response: {"message": "Hello World"}
    """
    logger.info("Запрос к root endpoint")
    return {"message": "Hello World"}


@app.get(
    "/hello",
    response_model=Dict[str, Any],
    summary="Расширенное приветствие",
    tags=["Basic"]
)
def hello() -> Dict[str, Any]:
    """
    Возвращает приветствие с дополнительной информацией.
    
    Returns:
        dict: Словарь с сообщением, статусом и временем
        
    Example:
        GET /hello
        Response: {
            "message": "Hello World! 🚀",
            "status": "success",
            "timestamp": "2024-01-15T10:30:45.123456"
        }
    """
    logger.info("Запрос к /hello endpoint")
    return {
        "message": "Hello World! 🚀",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }


@app.post(
    "/greet",
    response_model=GreetingResponse,
    summary="Персонализированное приветствие",
    tags=["Greeting"],
    status_code=201
)
def create_greeting(request: GreetingRequest) -> GreetingResponse:
    """
    Создает персонализированное приветствие на выбранном языке.
    
    Args:
        request: Объект с именем и языком
        
    Returns:
        GreetingResponse: Объект с приветствием
        
    Raises:
        HTTPException: Если язык не поддерживается
        
    Example:
        POST /greet
        Body: {"name": "Alice", "language": "en"}
        Response: {
            "message": "Hello, Alice! 🚀",
            "name": "Alice",
            "timestamp": "2024-01-15T10:30:45.123456",
            "status": "success"
        }
    """
    try:
        logger.info(f"Новое приветствие для {request.name} на {request.language}")
        
        if request.language not in GREETINGS:
            logger.warning(f"Неподдерживаемый язык: {request.language}")
            raise HTTPException(
                status_code=400,
                detail=f"Язык '{request.language}' не поддерживается. "
                       f"Доступные языки: {list(GREETINGS.keys())}"
            )
        
        message = GREETINGS[request.language].format(name=request.name)
        
        return GreetingResponse(
            message=message,
            name=request.name,
            timestamp=datetime.now().isoformat(),
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании приветствия: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get(
    "/greet",
    response_model=GreetingResponse,
    summary="Приветствие через query параметры",
    tags=["Greeting"]
)
def greet_with_query(
    name: str = Query("World", min_length=1, max_length=100),
    language: str = Query("en", regex="^(en|ru|fr|es)$")
) -> GreetingResponse:
    """
    Создает приветствие используя query параметры.
    
    Args:
        name: Имя для приветствия (query параметр)
        language: Язык приветствия (query параметр)
        
    Returns:
        GreetingResponse: Объект с приветствием
        
    Example:
        GET /greet?name=Bob&language=ru
        Response: {
            "message": "Привет, Bob! 🚀",
            "name": "Bob",
            "timestamp": "2024-01-15T10:30:45.123456",
            "status": "success"
        }
    """
    logger.info(f"Query приветствие для {name} на {language}")
    
    if language not in GREETINGS:
        raise HTTPException(
            status_code=400,
            detail=f"Язык '{language}' не поддерживается. "
                   f"Доступные: {list(GREETINGS.keys())}"
        )
    
    message = GREETINGS[language].format(name=name)
    
    return GreetingResponse(
        message=message,
        name=name,
        timestamp=datetime.now().isoformat(),
        status="success"
    )


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Проверка здоровья сервиса",
    tags=["Health"],
    status_code=200
)
def health_check() -> HealthCheckResponse:
    """
    Проверяет, что сервис работает корректно.
    
    Returns:
        HealthCheckResponse: Статус здоровья и время
        
    Example:
        GET /health
        Response: {
            "status": "OK",
            "timestamp": "2024-01-15T10:30:45.123456",
            "uptime": 3600.5
        }
    """
    logger.info("Health check запрос")
    return HealthCheckResponse(
        status="OK",
        timestamp=datetime.now().isoformat(),
        uptime=0.0
    )


@app.get(
    "/info",
    response_model=APIInfoResponse,
    summary="Информация об API",
    tags=["Info"]
)
def api_info() -> APIInfoResponse:
    """
    Возвращает информацию об API.
    
    Returns:
        APIInfoResponse: Информация о приложении
        
    Example:
        GET /info
        Response: {
            "name": "Hello World API",
            "version": "1.0.0",
            "description": "Простой API с приветствием...",
            "endpoints_count": 6
        }
    """
    logger.info("Запрос информации об API")
    return APIInfoResponse(
        name=app.title,
        version=app.version,
        description=app.description,
        endpoints_count=len([route for route in app.routes])
    )


# ============================================================================
# ОБРАБОТЧИК ОШИБОК
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Глобальный обработчик исключений.
    
    Args:
        request: Объект запроса
        exc: Исключение
        
    Returns:
        JSONResponse с ошибкой
    """
    logger.error(f"Необработанное исключение: {str(exc)}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": str(exc),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# STARTUP / SHUTDOWN СОБЫТИЯ
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Логирует старт приложения."""
    logger.info("🚀 FastAPI приложение запущено")
    logger.info(f"📚 API документация доступна на http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Логирует остановку приложения."""
    logger.info("⛔ FastAPI приложение остановлено")


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================


if __name__ == "__main__":
    """
    Запуск приложения через Uvicorn сервер.
    
    Параметры:
        - host: 0.0.0.0 (доступно со всех интерфейсов)
        - port: 8000 (стандартный порт)
        - reload: True (перезагрузка при изменении файлов)
        - log_level: info (уровень логирования)
    """
    try:
        logger.info("Запуск Uvicorn сервера...")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {str(e)}", exc_info=True)
        raise