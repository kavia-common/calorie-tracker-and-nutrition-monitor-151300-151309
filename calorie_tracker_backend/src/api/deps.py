from fastapi import Depends
from .auth import get_current_user

# PUBLIC_INTERFACE
def get_active_user(current_user=Depends(get_current_user)):
    """Dependency alias for currently authenticated user."""
    return current_user
