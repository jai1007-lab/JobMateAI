# app/main.py
import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import crud, models, schemas, auth
from app.database import engine, get_db
from datetime import datetime, timedelta
from google.cloud import talent_v4
from google.api_core.exceptions import GoogleAPIError

import requests
import time
import json
import os 


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return current_user

@app.delete("/delete_user")
def delete_user(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.email:
        raise HTTPException(status_code=400,detail="User email does not exist")
    return crud.delete_user(db=db, email = current_user.email)

@app.post("/users/preferences", response_model=schemas.UserPreferencesResponse)
def set_user_preferences(preferences: schemas.UserPreferencesCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_user_preferences(db=db, user_id=current_user.id, preferences=preferences)

@app.put("/users/preferences", response_model=schemas.UserPreferencesResponse)
def update_user_preferences(preferences: schemas.UserPreferencesCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.update_user_preferences(db=db, user_id=current_user.id, preferences=preferences)

@app.get("/users/preferences", response_model=schemas.UserPreferencesResponse)
def read_user_preferences(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    preferences = crud.get_user_preferences(db=db, user_id=current_user.id)
    if not preferences:
        raise HTTPException(status_code=404, detail="User Preferences not found")
    return preferences

# Job Scraping

# Set Google Application Credentials
credential_path = "/Users/jadhavjaichandra/Desktop/job_application_tracker/app/google_auth.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

client = talent_v4.JobServiceClient()

project_id = "job-scraper-433319"  # Replace with your Google Cloud project ID
tenant_id = ""  # Set to "" or None if not using tenants

@app.get("/users/jobs")
def get_jobs_based_on_preferences(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    preference = crud.get_user_preferences(db=db, user_id=current_user.id)
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences are missing")

    API_KEY = "7a1e553230d8aea6b056212ee1cbbb73"  # Replace with your correct Adzuna API key
    APP_ID = "14693c18"  # Replace with your correct Adzuna App ID
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    COUNTRY = "us"  # Specify the country code

    # Define the search parameters
    params = {
        "app_id": APP_ID,
        "app_key": API_KEY,
        "what": preference.job_title,  # Job title
        "results_per_page": 100,  # Number of results to return per page
        #"max_days_old": 0,  # Limit to jobs posted within the last 1 day
        "full_time": 1,  # Full-time jobs only
    }

    # Make the API request
    response = requests.get(f"{BASE_URL}/{COUNTRY}/search/1", params=params)

    # Check if the request was successful
    if response.status_code == 200:
        jobs = response.json()
        formatted_jobs = []
        for job in jobs['results']:
            formatted_job = (
                f"Title: {job['title']}\n"
                f"Company: {job['company']['display_name']}\n"
                f"Location: {job['location']['display_name']}\n"
                f"Salary: {job.get('salary_min', 'Not specified')} - {job.get('salary_max', 'Not specified')}\n"
                f"Description: {job['description']}\n"
                f"Apply Here: {job['redirect_url']}\n"
            )
            formatted_jobs.append(formatted_job)
            print(formatted_job)  # Print each formatted job to the console
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error fetching jobs: {response.text}")

    return {"jobs": formatted_jobs}
