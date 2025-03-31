from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr

from src.accounts.schemas import (
    UserCreateRequest,
    UserCreateResponse,
    UserLoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from src.database.models import UserModel
from src.accounts.dependencies import get_current_user, get_accounts_service
from src.accounts.services.accounts import AccountsService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/", response_model=UserCreateResponse)
async def register_user(
    user_data: UserCreateRequest,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/activate/{token}/")
async def activate(
    token: str,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.activate_user(token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-activation/")
async def resend_activation(
    email: EmailStr,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.resend_activation(email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/")
async def login(
        request: UserLoginRequest,
        service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.login_user(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout/")
async def logout(
    current_user: UserModel = Depends(get_current_user),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.logout_user(current_user)
    except ValueError:
        raise HTTPException(status_code=400, detail="Logout failed")


@router.post("/refresh/")
async def refresh_token(
        refresh_token: RefreshTokenRequest,
        service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.refresh_access_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-password/")
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.change_password(current_user, request.old_password, request.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forgot-password/")
async def forgot_password(
    request: ForgotPasswordRequest,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.forgot_password(request.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    request: ResetPasswordRequest,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.reset_password(token, request.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
