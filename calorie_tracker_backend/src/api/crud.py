from sqlalchemy.orm import Session
from datetime import date
from typing import List

from . import models, schemas
from .auth import get_password_hash

# --- User CRUD ---

# PUBLIC_INTERFACE
def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Creates a new user with hashed password.
    """
    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- Food Log CRUD ---

# PUBLIC_INTERFACE
def create_food_log(db: Session, user_id: int, log_in: schemas.FoodLogCreate) -> models.FoodLog:
    log = models.FoodLog(
        user_id=user_id,
        food=log_in.food,
        calories=log_in.calories,
        protein=log_in.protein,
        carbs=log_in.carbs,
        fat=log_in.fat,
        date=log_in.date,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

# PUBLIC_INTERFACE
def get_food_logs(db: Session, user_id: int, date_filter: date = None, limit: int = 100) -> List[models.FoodLog]:
    query = db.query(models.FoodLog).filter(models.FoodLog.user_id == user_id)
    if date_filter:
        query = query.filter(models.FoodLog.date == date_filter)
    return query.order_by(models.FoodLog.date.desc(), models.FoodLog.created_at.desc()).limit(limit).all()

# PUBLIC_INTERFACE
def delete_food_log(db: Session, user_id: int, food_log_id: int) -> bool:
    log = db.query(models.FoodLog).filter(models.FoodLog.user_id == user_id, models.FoodLog.id == food_log_id).first()
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True

# --- Goal CRUD ---

# PUBLIC_INTERFACE
def upsert_goal(db: Session, user_id: int, goal_in: schemas.GoalCreate) -> models.Goal:
    """
    Set or update calorie/nutrition goal for specific date.
    """
    goal = db.query(models.Goal).filter(models.Goal.user_id == user_id, models.Goal.date == goal_in.date).first()
    if goal:
        goal.calorie_goal = goal_in.calorie_goal
        goal.protein_goal = goal_in.protein_goal
        goal.carbs_goal = goal_in.carbs_goal
        goal.fat_goal = goal_in.fat_goal
    else:
        goal = models.Goal(
            user_id=user_id,
            calorie_goal=goal_in.calorie_goal,
            protein_goal=goal_in.protein_goal,
            carbs_goal=goal_in.carbs_goal,
            fat_goal=goal_in.fat_goal,
            date=goal_in.date,
        )
        db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

# PUBLIC_INTERFACE
def get_goals(db: Session, user_id: int, limit=30) -> List[models.Goal]:
    return db.query(models.Goal).filter(models.Goal.user_id == user_id).order_by(models.Goal.date.desc()).limit(limit).all()

# --- Stats ---

# PUBLIC_INTERFACE
def get_nutrition_stats(db: Session, user_id: int, start_date: date, end_date: date) -> List[schemas.NutritionStats]:
    """
    Returns aggregated nutrition stats between two dates (inclusive) per day.
    """
    # Query and group by date, sum nutrients
    from sqlalchemy import func
    rows = (
        db.query(
            models.FoodLog.date,
            func.sum(models.FoodLog.calories),
            func.sum(models.FoodLog.protein),
            func.sum(models.FoodLog.carbs),
            func.sum(models.FoodLog.fat),
        )
        .filter(models.FoodLog.user_id == user_id)
        .filter(models.FoodLog.date >= start_date)
        .filter(models.FoodLog.date <= end_date)
        .group_by(models.FoodLog.date)
        .order_by(models.FoodLog.date.desc())
        .all()
    )
    result = [
        schemas.NutritionStats(
            date=row[0],
            total_calories=row[1] or 0.0,
            total_protein=row[2] or 0.0,
            total_carbs=row[3] or 0.0,
            total_fat=row[4] or 0.0,
        )
        for row in rows
    ]
    return result
