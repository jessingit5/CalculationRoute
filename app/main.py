from fastapi import FastAPI
from .database import engine, Base
from .routers import users, calculations # Import the new routers

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Calculation API")

app.include_router(users.router)
app.include_router(calculations.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Calculation API!"}