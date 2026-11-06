"""Shopping Cart API — минимальный каркас FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Shopping Cart API",
    description="Сравнение цен в израильских сетях (каркас)",
    version="0.1.0",
)

# Разрешаем запросы с локального Vite-сервера во время разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Проверка, что API жив. Браузер или фронт могут дергать этот адрес."""
    return {"status": "ok"}
