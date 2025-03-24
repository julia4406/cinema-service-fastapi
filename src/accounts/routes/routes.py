from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session_postgresql import get_postgresql_db
from src.accounts.schemas import UserCreateRequestSchema, UserCreateResponseSchema
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
