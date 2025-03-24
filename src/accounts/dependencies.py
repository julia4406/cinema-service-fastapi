from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
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
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
