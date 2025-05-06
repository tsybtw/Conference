from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.core.database import get_db
from app.core.security import get_current_user, create_access_token
from app.crud.user import create_user, get_users, get_user, update_user, authenticate_user
from app.models.user import User, GenderEnum
from app.schemas.user import UserCreate, UserUpdate

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)


class FlashMessage:
    def __init__(self, request: Request):
        self.request = request
        self.messages: List[Dict[str, str]] = []
    
    def add(self, text: str, type: str = "info") -> None:
        self.messages.append({"text": text, "type": type})
    
    def get(self) -> List[Dict[str, str]]:
        return self.messages


async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        user = get_current_user(db=db, token=token)
        return user
    except HTTPException:
        return None


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "user": user, "errors": {}, "form_data": None}
    )


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    organization: str = Form(...),
    position: str = Form(...),
    birth_date: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...)
):
    form_data = {
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "nationality": nationality,
        "organization": organization,
        "position": position,
        "birth_date": birth_date,
        "email": email,
        "password": password,
        "password_confirm": password_confirm
    }
    
    errors = {}
    if password != password_confirm:
        errors["password_confirm"] = "Passwords do not match"
    
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long"
    
    try:
        gender_enum = GenderEnum(gender)
    except ValueError:
        errors["gender"] = "Invalid gender value"
    
    try:
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        errors["birth_date"] = "Invalid date format"
    
    if not errors:
        try:
            user_data = UserCreate(
                first_name=first_name,
                last_name=last_name,
                gender=gender_enum,
                nationality=nationality,
                organization=organization,
                position=position,
                birth_date=birth_date,
                email=email,
                password=password,
                password_confirm=password_confirm
            )
            
            user = create_user(db, user_data)
            
            access_token = create_access_token(subject=user.id)
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                max_age=1800,
                samesite="lax"
            )
            return response
            
        except HTTPException as e:
            errors["email"] = e.detail
    
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": None,
            "errors": errors,
            "form_data": form_data
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user": None, "errors": {}}
    )


@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "error": "Incorrect email or password",
                "errors": {"email": "Invalid credentials"}
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    access_token = create_access_token(subject=user.id)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax"
    )
    return response


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response


@router.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    users = get_users(db)
    
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "user": user, "users": users, "current_user": user}
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "errors": {}, "form_data": None}
    )


@router.post("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie),
    first_name: str = Form(...),
    last_name: str = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    organization: str = Form(...),
    position: str = Form(...),
    birth_date: str = Form(...),
    email: EmailStr = Form(...),
    password: Optional[str] = Form(None),
    password_confirm: Optional[str] = Form(None)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    form_data = {
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "nationality": nationality,
        "organization": organization,
        "position": position,
        "birth_date": birth_date,
        "email": email,
    }
    
    if password:
        form_data["password"] = password
        form_data["password_confirm"] = password_confirm
    
    errors = {}
    if password and password != password_confirm:
        errors["password_confirm"] = "Passwords do not match"
    
    if password and len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long"
    
    try:
        gender_enum = GenderEnum(gender)
    except ValueError:
        errors["gender"] = "Invalid gender value"
    
    try:
        birth_date_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        errors["birth_date"] = "Invalid date format"
    
    if not errors:
        try:
            user_update = UserUpdate(
                first_name=first_name,
                last_name=last_name,
                gender=gender_enum,
                nationality=nationality,
                organization=organization,
                position=position,
                birth_date=birth_date_date,
                email=email,
            )
            
            if password:
                user_update.password = password
                user_update.password_confirm = password_confirm
            
            updated_user = update_user(db, user.id, user_update)
            if not updated_user:
                return templates.TemplateResponse(
                    "profile.html",
                    {
                        "request": request,
                        "user": user,
                        "errors": {"form": "Failed to update profile"},
                        "form_data": form_data
                    },
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            response = RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)
            return response
            
        except HTTPException as e:
            errors["form"] = e.detail
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "errors": errors,
            "form_data": form_data
        },
        status_code=status.HTTP_400_BAD_REQUEST
    ) 