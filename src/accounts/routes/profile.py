from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from src.config.logging_settings import logger

from src.accounts.schemas import ProfileResponse, ProfileUpdateRequest
from src.accounts.services.accounts import ProfileService
from src.accounts.dependencies import get_current_user, get_profile_service
from src.database.models import UserModel


router = APIRouter(tags=["profile"])


@router.get("/profile/", response_model=ProfileResponse)
async def get_profile(
    current_user: UserModel = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service)
):
    try:
        logger.info(f"Fetching profile for user: {current_user.email}")
        profile = await service.get_profile(current_user)
        return profile
    except ValueError:
        logger.error(f"Invalid data while fetching profile for user: {current_user.email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error while fetching profile for user: {current_user.email}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.patch("/profile/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest = Depends(),
    current_user: UserModel = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service)
):
    try:
        logger.info(f"Updating profile for user: {current_user.email}")
        updated_profile = await service.update_profile(current_user, profile_data)
        return updated_profile
    except ValueError:
        logger.error(f"Invalid data while updating profile for user: {current_user.email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error while updating profile for user: {current_user.email}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/profile/avatar/", response_model=ProfileResponse)
async def upload_avatar(
    avatar_file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service)
):
    try:
        logger.info(f"Uploading avatar for user: {current_user.email}")
        updated_profile = await service.upload_avatar(current_user, avatar_file)
        return updated_profile
    except ValueError:
        logger.error(f"Invalid data while uploading avatar for user: {current_user.email}")
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        logger.error(f"Error while uploading avatar for user: {current_user.email}")
        raise HTTPException(status_code=500, detail="Something went wrong")
