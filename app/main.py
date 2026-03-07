from fastapi import FastAPI
from app.api.router import api_router
from app.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Personal Finance API", version="1.0.0", description="API for managing personal finance, including accounts, transactions, and categories.")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(api_router)