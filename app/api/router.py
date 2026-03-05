from fastapi import APIRouter
from app.api.routes import accounts, users, categories

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(accounts.router)