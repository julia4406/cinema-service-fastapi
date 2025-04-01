from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.models import UserModel
from src.accounts.schemas.accounts import (
    UserAdminCreateRequest,
    UserAdminUpdateRequest,
    ProfileUpdateRequest,
    UserAdminResponse
)
from src.accounts.services.accounts import AccountsService, ProfileService
from src.accounts.dependencies import role_required, get_accounts_service, get_profile_service
from src.database.models import UserGroupEnum

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users/{user_email}", response_model=UserAdminResponse)
async def get_user_by_email(
    user_email: EmailStr,
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        user = await service.get_by_email(user_email)
        result = await service.db.execute(
            select(UserModel)
            .filter_by(id=user.id)
            .options(
                joinedload(UserModel.group),
                joinedload(UserModel.profile)
            )
        )
        user_with_data = result.scalar_one_or_none()
        if not user_with_data:
            raise HTTPException(status_code=404, detail="User not found")

        return UserAdminResponse(
            id=user_with_data.id,
            email=user_with_data.email,
            is_active=user_with_data.is_active,
            group=UserGroupEnum(user_with_data.group.name),
            first_name=user_with_data.profile.first_name if user_with_data.profile else None,
            last_name=user_with_data.profile.last_name if user_with_data.profile else None,
            avatar=user_with_data.profile.avatar if user_with_data.profile else None,
            gender=user_with_data.profile.gender if user_with_data.profile else None,
            date_of_birth=user_with_data.profile.date_of_birth if user_with_data.profile else None,
            info=user_with_data.profile.info if user_with_data.profile else None
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/users", response_model=UserAdminResponse)
async def register_user(
    user_data: UserAdminCreateRequest,
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.register_user_by_admin(user_data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.patch("/users/{user_id}", response_model=UserAdminResponse)
async def update_user(
    user_id: int,
    user_data: UserAdminUpdateRequest,
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        return await service.update_user(user_id, user_data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.patch("/profile/{user_id}", response_model=UserAdminResponse)
async def update_profile(
    user_id: int,
    profile_data: ProfileUpdateRequest,
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
    account_service: AccountsService = Depends(get_accounts_service),
    profile_service: ProfileService = Depends(get_profile_service)
):
    try:
        user = await account_service.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await profile_service.update_profile(user, profile_data)

        result = await account_service.db.execute(
            select(UserModel)
            .filter_by(id=user.id)
            .options(
                joinedload(UserModel.group),
                joinedload(UserModel.profile)
            )
        )
        user_with_data = result.scalar_one_or_none()
        if not user_with_data:
            raise HTTPException(status_code=404, detail="User not found")

        return UserAdminResponse(
            id=user_with_data.id,
            email=user_with_data.email,
            is_active=user_with_data.is_active,
            group=UserGroupEnum(user_with_data.group.name.lower()),
            first_name=user_with_data.profile.first_name if user_with_data.profile else None,
            last_name=user_with_data.profile.last_name if user_with_data.profile else None,
            avatar=user_with_data.profile.avatar if user_with_data.profile else None,
            gender=user_with_data.profile.gender if user_with_data.profile else None,
            date_of_birth=user_with_data.profile.date_of_birth if user_with_data.profile else None,
            info=user_with_data.profile.info if user_with_data.profile else None
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
    service: AccountsService = Depends(get_accounts_service)
):
    try:
        await service.delete_user(user_id, current_user)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong")
    return None
