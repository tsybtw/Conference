from datetime import datetime
from typing import Dict, Optional
import re

from app.models.user import GenderEnum
from app.core.logging import logger

def validate_password(password: str, password_confirm: Optional[str] = None) -> Dict[str, str]:
    errors = {}
    
    if not password:
        return errors
    
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long"
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        if "password" in errors:
            errors["password"] += ". Must contain at least one uppercase letter"
        else:
            errors["password"] = "Password must contain at least one uppercase letter"
    
    # Check for digit
    if not re.search(r'[0-9]', password):
        if "password" in errors:
            errors["password"] += ". Must contain at least one digit"
        else:
            errors["password"] = "Password must contain at least one digit"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        if "password" in errors:
            errors["password"] += ". Must contain at least one special character"
        else:
            errors["password"] = "Password must contain at least one special character"
    
    if password_confirm is not None and password != password_confirm:
        errors["password_confirm"] = "Passwords do not match"
    
    return errors

def validate_gender(gender: str) -> Dict[str, str]:
    errors = {}
    
    try:
        GenderEnum(gender)
    except ValueError:
        errors["gender"] = "Invalid gender value"
    
    return errors

def validate_birth_date(birth_date_str: str) -> Dict[str, str]:
    errors = {}
    
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        
        today = datetime.now().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            errors["birth_date"] = "You must be at least 18 years old to register"
    except ValueError:
        errors["birth_date"] = "Invalid date format"
    
    return errors 