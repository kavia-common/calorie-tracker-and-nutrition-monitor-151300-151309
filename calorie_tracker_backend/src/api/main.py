from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import date

from . import schemas, auth, crud, deps
from .database import engine, Base

app = FastAPI(
    title="Calorie Tracker API",
    description="Manage users, food logs, goals, and stats.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Auth", "description": "User registration, login, token."},
        {"name": "Users", "description": "User profile."},
        {"name": "Food Logs", "description": "Log, list, and delete food/calorie intakes."},
        {"name": "Goals", "description": "Set and view calorie/nutrition goals."},
        {"name": "Stats", "description": "View calorie and nutrition statistics."},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure tables are created at startup
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Health"])
def health_check():
    """Health Check Endpoint."""
    return {"message": "Healthy"}

# === AUTH ===

@app.post("/api/v1/auth/register", summary="Register new user", tags=["Auth"], response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, db=Depends(auth.get_db)):
    """
    Register a new user.
    """
    if auth.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_in)
    return user

@app.post("/api/v1/auth/token", summary="Login and get token", tags=["Auth"], response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(auth.get_db)):
    """
    Authenticate user and return JWT token.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/users/me", summary="Get current user profile", tags=["Users"], response_model=schemas.UserOut)
def get_me(current_user=Depends(deps.get_active_user)):
    """
    Get info about the currently authenticated user.
    """
    return current_user

# === FOOD LOGS ===

@app.post("/api/v1/food_logs", summary="Add a food log entry", tags=["Food Logs"], response_model=schemas.FoodLogOut)
def add_food_log(log_in: schemas.FoodLogCreate, current_user=Depends(deps.get_active_user), db=Depends(auth.get_db)):
    """
    Log food eaten with its nutritional information.
    """
    log = crud.create_food_log(db, user_id=current_user.id, log_in=log_in)
    return log

@app.get("/api/v1/food_logs", summary="List food logs", tags=["Food Logs"], response_model=List[schemas.FoodLogOut])
def list_food_logs(date: date = None, limit: int = 100, current_user=Depends(deps.get_active_user), db=Depends(auth.get_db)):
    """
    List food logs for user, optionally filtered by date.
    """
    logs = crud.get_food_logs(db, current_user.id, date_filter=date, limit=limit)
    return logs

@app.delete("/api/v1/food_logs/{log_id}", summary="Delete a food log entry", tags=["Food Logs"])
def delete_food_log(log_id: int, current_user=Depends(deps.get_active_user), db=Depends(auth.get_db)):
    """
    Delete a log entry by id.
    """
    if crud.delete_food_log(db, current_user.id, log_id):
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Food log not found")

# === GOALS ===

@app.post("/api/v1/goals", summary="Set or update daily goal", tags=["Goals"], response_model=schemas.GoalOut)
def set_goal(goal_in: schemas.GoalCreate, current_user=Depends(deps.get_active_user), db=Depends(auth.get_db)):
    """
    Set/update calorie and macro goal for the given date.
    """
    goal = crud.upsert_goal(db, user_id=current_user.id, goal_in=goal_in)
    return goal

@app.get("/api/v1/goals", summary="List user's goals", tags=["Goals"], response_model=List[schemas.GoalOut])
def list_goals(current_user=Depends(deps.get_active_user), db=Depends(auth.get_db)):
    """
    View user's history of goals.
    """
    return crud.get_goals(db, current_user.id)

# === STATS ===

@app.get("/api/v1/stats/daily", summary="Get daily calorie/nutrition stats", tags=["Stats"], response_model=schemas.DailyStats)
def stats_daily(
    start: date,
    end: date,
    current_user=Depends(deps.get_active_user),
    db=Depends(auth.get_db)
):
    """
    Get per-day total calories, protein, carbs, and fat between start and end (inclusive).
    """
    stats = crud.get_nutrition_stats(db, user_id=current_user.id, start_date=start, end_date=end)
    return {"stats": stats}

# === OpenAPI usage endpoint for client dev and websocket (if added) ===

@app.get("/api/v1/docs", include_in_schema=False)
def docs_reference():
    """
    Visit /docs for OpenAPI UI. All JWT-secured endpoints require:
    - Authorization: Bearer &lt;token&gt; in the header.
    - Register or login to obtain a token.
    """
    return {"docs_url": "/docs", "info": "For websocket (if used), connect and authenticate via Bearer token."}
