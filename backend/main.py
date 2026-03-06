from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.database import Base, engine
from routers import transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Kane API",
    description="Personal finance transactions with SQLite + SQLAlchemy",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(transactions.router)


@app.get("/")
def read_root():
    return {"message": "Transaction API is running → open /docs"}
