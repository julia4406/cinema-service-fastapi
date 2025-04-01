from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr

from src.config.logging_settings import logger
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
        logger.info(f"Registering new user with email: {user_data.email}")
        return await service.register_user(user_data)
    except ValueError as e:
        logger.error(f"Error during registration for email: {user_data.email}, error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/activate/{token}/")
async def activate(
    token: str,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"Activating user with token: {token}")
        return await service.activate_user(token)
    except ValueError:
        logger.error(f"Invalid activation token: {token}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error during activation with token: {token}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/resend-activation/")
async def resend_activation(
    email: EmailStr,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"Resending activation email to: {email}")
        return await service.resend_activation(email)
    except ValueError:
        logger.error(f"Invalid email for resend activation: {email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error resending activation email to: {email}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/login/")
async def login(
        request: UserLoginRequest,
        service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"User login attempt with email: {request.email}")
        return await service.login_user(request)
    except ValueError:
        logger.error(f"Invalid login attempt for email: {request.email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error during login for email: {request.email}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/logout/")
async def logout(
    current_user: UserModel = Depends(get_current_user),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"Logging out user with email: {current_user.email}")
        return await service.logout_user(current_user)
    except ValueError:
        logger.error(f"Invalid logout attempt for user: {current_user.email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error during logout for user: {current_user.email}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/refresh/")
async def refresh_token(
        refresh_token: RefreshTokenRequest,
        service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"Refreshing token for user with token: {refresh_token.token}")
        return await service.refresh_access_token(refresh_token)
    except ValueError:
        logger.error(f"Invalid refresh token attempt: {refresh_token.token}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error refreshing token: {refresh_token.token}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/change-password/")
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"Changing password for user: {current_user.email}")
        return await service.change_password(current_user, request.old_password, request.new_password)
    except ValueError:
        logger.error(f"Invalid password change attempt for user: {current_user.email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error changing password for user: {current_user.email}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/forgot-password/")
async def forgot_password(
    request: ForgotPasswordRequest,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"Forgot password request for email: {request.email}")
        return await service.forgot_password(request.email)
    except ValueError:
        logger.error(f"Invalid forgot password request for email: {request.email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error handling forgot password request for email: {request.email}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    request: ResetPasswordRequest,
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        logger.info(f"Resetting password for token: {token}")
        return await service.reset_password(token, request.new_password)
    except ValueError:
        logger.error(f"Invalid reset password attempt with token: {token}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error resetting password with token: {token}")
        raise HTTPException(status_code=500, detail="Something went wrong")
