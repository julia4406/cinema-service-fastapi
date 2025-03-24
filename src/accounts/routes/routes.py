from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session_postgresql import get_postgresql_db
from src.accounts.schemas import (
    UserCreateRequestSchema,
    UserCreateResponseSchema,
    UserLoginRequestSchema,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from src.database.models import UserModel
from src.accounts.dependencies import get_current_user
from src.accounts.services.accounts import AccountsService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/", response_model=UserCreateResponseSchema)
async def register_user(
    user_data: UserCreateRequestSchema,
    db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/activate/{token}/")
async def activate(
    token: str,
    db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.activate_user(token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-activation/")
async def resend_activation(
    email: EmailStr,
    db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.resend_activation(email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/")
async def login(
        request: UserLoginRequestSchema,
        db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.login_user(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh/")
async def refresh_token(
        refresh_token: RefreshTokenRequest,
        db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.refresh_access_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-password/")
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.change_password(current_user, request.old_password, request.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forgot-password/")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.forgot_password(request.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_postgresql_db)
):
    service = AccountsService(db)
    try:
        return await service.reset_password(token, request.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
