from typing import Any, Coroutine

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.accounts.repositories.accounts import ProfileRepository, UserRepository
from src.accounts.repositories.tokens import (
    ActivationTokensRepository,
    PasswordResetTokenRepository,
    RefreshTokensRepository,
)
from src.accounts.s3_service import S3Service, get_s3_service
from src.accounts.security.jwt import JWTAuthManager, get_jwt_service
from src.accounts.services.accounts import AccountsService, ProfileService
from src.database.models import UserGroupEnum, UserModel
from src.database.session_postgresql import get_postgresql_db
from src.email.email_service import EmailService, get_email_service

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_postgresql_db),
    jwt_manager: JWTAuthManager = Depends(get_jwt_service),
) -> UserModel:
    token = credentials.credentials
    try:
        user = await jwt_manager.verify_access_token(token, db)
        if not user:
            raise HTTPException(status_code=401, detail="Token is invalid")
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is not active")
        payload = jwt_manager.decode_token(token)
        group_id = payload.get("group")
        if user.group_id != group_id:
            raise HTTPException(status_code=401, detail="Token is invalid")
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def role_required(required_role: UserGroupEnum) -> Depends:
    async def role_checker(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_postgresql_db)
    ) -> UserModel:

        result = await db.execute(
            select(UserModel)
            .filter_by(id=current_user.id)
            .options(joinedload(UserModel.group))
        )
        user_with_group = result.scalar_one_or_none()

        if not user_with_group:
            raise HTTPException(
                status_code=403,
                detail="User not found"
            )

        current_group = UserGroupEnum(user_with_group.group.name)

        if not current_group:
            raise HTTPException(
                status_code=403,
                detail="User group not found"
            )

        current_role_enum = UserGroupEnum(current_group.name.lower())

        if required_role == UserGroupEnum.USER:
            return current_user
        elif required_role == UserGroupEnum.MODERATOR:
            if current_role_enum not in [UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN]:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions. Required role: MODERATOR or higher"
                )
            return current_user
        elif required_role == UserGroupEnum.ADMIN:
            if current_role_enum != UserGroupEnum.ADMIN:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions. Required role: ADMIN"
                )
            return current_user
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid role specified"
            )
    return role_checker


async def get_user_repository(db: AsyncSession = Depends(get_postgresql_db)) -> UserRepository:
    return UserRepository(db)


async def get_profile_repository(
        db: AsyncSession = Depends(get_postgresql_db),
        s3_service: S3Service = Depends(get_s3_service)
) -> ProfileRepository:
    return ProfileRepository(db, s3_service)


async def get_activation_token_repository(
        db: AsyncSession = Depends(get_postgresql_db)
) -> ActivationTokensRepository:
    return ActivationTokensRepository(db)


async def get_password_reset_token_repository(
        db: AsyncSession = Depends(get_postgresql_db)
) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(db)


async def get_refresh_token_repository(
        db: AsyncSession = Depends(get_postgresql_db)
) -> RefreshTokensRepository:
    return RefreshTokensRepository(db)


async def get_accounts_service(
    user_repo: UserRepository = Depends(get_user_repository),
    activation_token_repo: ActivationTokensRepository = Depends(get_activation_token_repository),
    email_service: EmailService = Depends(get_email_service),
    jwt_service: JWTAuthManager = Depends(get_jwt_service),
    reset_token_repo: PasswordResetTokenRepository = Depends(get_password_reset_token_repository)
) -> AccountsService:
    return AccountsService(user_repo, activation_token_repo, email_service, jwt_service, reset_token_repo)


async def get_profile_service(
    profile_repo: ProfileRepository = Depends(get_profile_repository)
) -> ProfileService:
    return ProfileService(profile_repo)
