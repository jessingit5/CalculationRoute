from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List
from .. import schemas, models, auth
from ..database import get_db

router = APIRouter(
    prefix="/calculations",
    tags=["Calculations"]
)

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/", response_model=schemas.CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(calc: schemas.CalculationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_calc = models.Calculation(**calc.model_dump(), user_id=current_user.id)
    db.add(new_calc)
    db.commit()
    db.refresh(new_calc)
    return new_calc

@router.get("/", response_model=List[schemas.CalculationRead])
def browse_calculations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    calcs = db.query(models.Calculation).filter(models.Calculation.user_id == current_user.id).all()
    return calcs

@router.get("/{id}", response_model=schemas.CalculationRead)
def read_calculation(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == id, models.Calculation.user_id == current_user.id).first()
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    return calc

@router.put("/{id}", response_model=schemas.CalculationRead)
def edit_calculation(id: int, calc_update: schemas.CalculationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_calc_query = db.query(models.Calculation).filter(models.Calculation.id == id, models.Calculation.user_id == current_user.id)
    db_calc = db_calc_query.first()
    
    if not db_calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    
    db_calc_query.update(calc_update.model_dump(), synchronize_session=False)
        
    db.commit()
    return db_calc

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    calc = db.query(models.Calculation).filter(models.Calculation.id == id, models.Calculation.user_id == current_user.id).first()
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    
    db.delete(calc)
    db.commit()
    return