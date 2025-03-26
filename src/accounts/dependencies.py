from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.models import UserGroupEnum
from src.accounts.security.jwt import JWTAuthManager
from src.database.models import UserModel
from src.database.session_postgresql import get_postgresql_db


bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_postgresql_db)
) -> UserModel:
    token = credentials.credentials
    jwt_manager = JWTAuthManager()
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


def role_required(required_role: UserGroupEnum):
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
