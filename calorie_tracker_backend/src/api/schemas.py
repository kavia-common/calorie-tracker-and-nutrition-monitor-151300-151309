from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date

# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """User login credentials."""
    email: EmailStr
    password: str

# PUBLIC_INTERFACE
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class Token(BaseModel):
    access_token: str
    token_type: str

# PUBLIC_INTERFACE
class FoodLogBase(BaseModel):
    food: str
    calories: float
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    date: date = Field(..., description="Date for this food log (YYYY-MM-DD)")

# PUBLIC_INTERFACE
class FoodLogCreate(FoodLogBase):
    pass

# PUBLIC_INTERFACE
class FoodLogOut(FoodLogBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class GoalBase(BaseModel):
    calorie_goal: float
    protein_goal: Optional[float] = 0
    carbs_goal: Optional[float] = 0
    fat_goal: Optional[float] = 0
    date: date = Field(..., description="Date for this goal (YYYY-MM-DD)")

# PUBLIC_INTERFACE
class GoalCreate(GoalBase):
    pass

# PUBLIC_INTERFACE
class GoalOut(GoalBase):
    id: int
    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class NutritionStats(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float

# PUBLIC_INTERFACE
class DailyStats(BaseModel):
    stats: List[NutritionStats]
