from datetime import datetime
from typing import Dict, List, Optional
import secrets

from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.core.database import get_db
from app.core.security import get_current_user, create_access_token, set_csrf_token, verify_csrf_token, get_password_hash
from app.core.rate_limit import check_login_rate_limit
from app.core.validation import validate_password, validate_gender, validate_birth_date
from app.core.logging import logger
from app.core.email import send_password_reset_email, verify_reset_code
from app.crud.user import create_user, get_users, update_user, authenticate_user, get_user_by_email
from app.models.user import User, GenderEnum
from app.schemas.user import UserCreate, UserUpdate
from app.config import settings

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)


class FlashMessage:
    def __init__(self, request: Request):
        self.request = request
        self.messages: List[Dict[str, str]] = []
    
    def add(self, text: str, type_: str = "info") -> None:
        self.messages.append({"text": text, "type": type_})
    
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
    logger.info(f"Index page accessed by user ID: {user.id if user else 'anonymous'}")
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
    
    csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "user": user, "errors": {}, "form_data": None, "csrf_token": csrf_token}
    )


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
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
    
    if not verify_csrf_token(request, csrf_token):
        errors["csrf"] = "Invalid security token. Please try again."
        logger.warning(f"CSRF validation failed during registration attempt for email: {email}")
    
    password_errors = validate_password(password, password_confirm)
    errors.update(password_errors)
    
    gender_errors = validate_gender(gender)
    errors.update(gender_errors)
    
    birth_date_errors = validate_birth_date(birth_date)
    errors.update(birth_date_errors)
    
    if not errors:
        try:
            gender_enum = GenderEnum(gender)
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
            
            user_data = UserCreate(
                first_name=first_name,
                last_name=last_name,
                gender=gender_enum,
                nationality=nationality,
                organization=organization,
                position=position,
                birth_date=birth_date_obj,
                email=email,
                password=password,
                password_confirm=password_confirm
            )
            
            user = create_user(db, user_data)
            logger.info(f"New user registered: {user.email} (ID: {user.id})")
            
            access_token = create_access_token(subject=user.id)
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                samesite="lax",
                secure=settings.USE_HTTPS
            )
            return response
            
        except HTTPException as e:
            errors["email"] = e.detail
            logger.warning(f"Registration failed for email {email}: {e.detail}")
    
    new_csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": None,
            "errors": errors,
            "form_data": form_data,
            "csrf_token": new_csrf_token
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
    
    csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user": None, "errors": {}, "csrf_token": csrf_token}
    )


@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    csrf_token: str = Form(...),
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    errors = {}
    
    try:
        check_login_rate_limit(request, form_data.username)
    except HTTPException as e:
        errors["form"] = e.detail
        new_csrf_token = set_csrf_token(request)
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "errors": errors,
                "csrf_token": new_csrf_token
            },
            status_code=e.status_code
        )
    
    if not verify_csrf_token(request, csrf_token):
        errors["csrf"] = "Invalid security token. Please try again."
        logger.warning(f"CSRF validation failed during login attempt for email: {form_data.username}")
        new_csrf_token = set_csrf_token(request)
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "errors": errors,
                "csrf_token": new_csrf_token
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        new_csrf_token = set_csrf_token(request)
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "errors": {"form": "Invalid email or password. Please check your credentials and try again."},
                "csrf_token": new_csrf_token
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    access_token = create_access_token(subject=user.id)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.USE_HTTPS
    )
    return response


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, user: Optional[User] = Depends(get_current_user_from_cookie)):
    if user:
        logger.info(f"User logged out: {user.email} (ID: {user.id})")
    
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
    logger.info(f"Users list accessed by: {user.email} (ID: {user.id})")
    
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
    
    csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "errors": {}, "csrf_token": csrf_token}
    )


@router.post("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie),
    csrf_token: str = Form(...),
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
    
    if not verify_csrf_token(request, csrf_token):
        errors["csrf"] = "Invalid security token. Please try again."
        logger.warning(f"CSRF validation failed during profile update for user: {user.email} (ID: {user.id})")
    
    if password:
        password_errors = validate_password(password, password_confirm)
        errors.update(password_errors)
    
    gender_errors = validate_gender(gender)
    errors.update(gender_errors)
    
    birth_date_errors = validate_birth_date(birth_date)
    errors.update(birth_date_errors)
    
    if not errors:
        try:
            gender_enum = GenderEnum(gender)
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
            
            user_update = UserUpdate(
                first_name=first_name,
                last_name=last_name,
                gender=gender_enum,
                nationality=nationality,
                organization=organization,
                position=position,
                birth_date=birth_date_obj,
                email=email,
            )
            
            if password:
                user_update.password = password
                user_update.password_confirm = password_confirm
            
            updated_user = update_user(db, user.id, user_update)
            if not updated_user:
                errors["form"] = "Failed to update profile"
                logger.error(f"Failed to update profile for user: {user.email} (ID: {user.id})")
            else:
                logger.info(f"Profile updated for user: {user.email} (ID: {user.id})")
                response = RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)
                return response
            
        except HTTPException as e:
            errors["form"] = e.detail
            logger.warning(f"Profile update failed for user {user.email} (ID: {user.id}): {e.detail}")
    
    new_csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "errors": errors,
            "form_data": form_data,
            "csrf_token": new_csrf_token
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request, "user": None, "errors": {}, "csrf_token": csrf_token}
    )


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(
    request: Request,
    email: EmailStr = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    errors = {}
    
    if not verify_csrf_token(request, csrf_token):
        errors["csrf"] = "Invalid security token. Please try again."
        logger.warning(f"CSRF validation failed during password reset attempt for email: {email}")
    
    if not errors:
        # Check if user exists
        user = get_user_by_email(db, email)
        if not user:
            errors["email"] = "No account found with this email address"
        else:
            # Send password reset email
            if send_password_reset_email(email):
                logger.info(f"Password reset email sent to: {email}")
                # Redirect to verification page
                response = RedirectResponse(url=f"/verify-reset-code?email={email}", status_code=status.HTTP_303_SEE_OTHER)
                return response
            else:
                errors["email"] = "Failed to send reset email. Please check your email configuration or try again later."
                logger.error(f"Failed to send password reset email to: {email}")
    
    new_csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "forgot_password.html",
        {
            "request": request,
            "user": None,
            "errors": errors,
            "csrf_token": new_csrf_token
        },
        status_code=status.HTTP_400_BAD_REQUEST if errors else status.HTTP_200_OK
    )


@router.get("/verify-reset-code", response_class=HTMLResponse)
async def verify_code_page(
    request: Request,
    email: str,
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "verify_reset_code.html",
        {"request": request, "user": None, "email": email, "errors": {}, "csrf_token": csrf_token}
    )


@router.post("/verify-reset-code", response_class=HTMLResponse)
async def verify_code_submit(
    request: Request,
    email: str = Form(...),
    code: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    errors = {}
    
    if not verify_csrf_token(request, csrf_token):
        errors["csrf"] = "Invalid security token. Please try again."
        logger.warning(f"CSRF validation failed during code verification for email: {email}")
    
    if not errors:
        # Verify the reset code
        if verify_reset_code(email, code):
            logger.info(f"Password reset code verified for: {email}")
            # Redirect to reset password page
            response = RedirectResponse(url=f"/reset-password?email={email}", status_code=status.HTTP_303_SEE_OTHER)
            return response
        else:
            errors["code"] = "Invalid or expired verification code. Please request a new code or check your email again."
            logger.warning(f"Invalid password reset code attempt for: {email}")
    
    new_csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "verify_reset_code.html",
        {
            "request": request,
            "user": None,
            "email": email,
            "errors": errors,
            "csrf_token": new_csrf_token
        },
        status_code=status.HTTP_400_BAD_REQUEST if errors else status.HTTP_200_OK
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(
    request: Request,
    email: str,
    user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "user": None, "email": email, "errors": {}, "csrf_token": csrf_token}
    )


@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    errors = {}
    
    if not verify_csrf_token(request, csrf_token):
        errors["csrf"] = "Invalid security token. Please try again."
        logger.warning(f"CSRF validation failed during password reset for email: {email}")
    
    password_errors = validate_password(password, password_confirm)
    errors.update(password_errors)
    
    if not errors:
        # Update user's password
        user = get_user_by_email(db, email)
        if not user:
            errors["email"] = "User not found"
        else:
            # Update password
            user.hashed_password = get_password_hash(password)
            db.commit()
            logger.info(f"Password reset successful for user: {email}")
            
            # Create flash message
            flash = FlashMessage(request)
            flash.add("Your password has been reset successfully. Please login with your new password.", "success")
            request.session["messages"] = flash.get()
            
            # Redirect to login page
            response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
            return response
    
    new_csrf_token = set_csrf_token(request)
    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "user": None,
            "email": email,
            "errors": errors,
            "csrf_token": new_csrf_token
        },
        status_code=status.HTTP_400_BAD_REQUEST if errors else status.HTTP_200_OK
    ) 