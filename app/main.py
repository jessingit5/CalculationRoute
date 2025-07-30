from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta

from . import models, schemas
from .database import SessionLocal, engine
from .auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/users/login")
def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/calculations/", response_model=schemas.Calculation)
def create_calculation(
    calculation: schemas.CalculationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_calculation = models.Calculation(**calculation.dict(), owner_id=current_user.id)
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation

@app.get("/calculations/", response_model=list[schemas.Calculation])
def read_calculations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    calculations = db.query(models.Calculation).filter(models.Calculation.owner_id == current_user.id).offset(skip).limit(limit).all()
    return calculations

@app.get("/calculations/{calculation_id}", response_model=schemas.Calculation)
def read_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_calculation = db.query(models.Calculation).filter(models.Calculation.id == calculation_id, models.Calculation.owner_id == current_user.id).first()
    if db_calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return db_calculation

@app.put("/calculations/{calculation_id}", response_model=schemas.Calculation)
def update_calculation(
    calculation_id: int,
    calculation: schemas.CalculationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_calculation = db.query(models.Calculation).filter(models.Calculation.id == calculation_id, models.Calculation.owner_id == current_user.id).first()
    if db_calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    for var, value in vars(calculation).items():
        setattr(db_calculation, var, value) if value else None
    db.commit()
    db.refresh(db_calculation)
    return db_calculation

@app.delete("/calculations/{calculation_id}", response_model=schemas.Calculation)
def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_calculation = db.query(models.Calculation).filter(models.Calculation.id == calculation_id, models.Calculation.owner_id == current_user.id).first()
    if db_calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(db_calculation)
    db.commit()
    return db_calculation
