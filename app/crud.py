# app/crud.py

from sqlalchemy.orm import Session
from app.models import User, UserPreferences
from app.schemas import UserCreate, UserPreferencesCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db :Session, email :str):
    db_user = get_user_by_email(db, email)
    if not db_user:
        print("User does not exist")
        return
    db.delete(db_user)
    db.commit()
    
    check_deleted_user = get_user_by_email(db, email)
    if check_deleted_user:
        print("Error Deleting the user!")
    else:
        print("User deleted Successfully!")

def create_user_preferences(db: Session, user_id: int, preferences: UserPreferencesCreate):
    db_preferences = UserPreferences(**preferences.dict(), user_id=user_id)
    db.add(db_preferences)
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

def get_user_preferences(db: Session, user_id: int):
    return db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

def update_user_preferences(db: Session, user_id: int, preferences: UserPreferencesCreate):
    db_preferences = get_user_preferences(db, user_id)
    if db_preferences:
        db_preferences.job_title = preferences.job_title
        db_preferences.location = preferences.location
        db_preferences.skills = preferences.skills
        db.commit()
        db.refresh(db_preferences)
    else:
        db_preferences = create_user_preferences(db=db, user_id=user_id, preferences=preferences)
    return db_preferences
