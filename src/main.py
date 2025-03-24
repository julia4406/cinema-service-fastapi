import uvicorn
from fastapi import FastAPI
from payments.routes.payments import router as payment_router
from src.accounts.routes.auth import router as auth_router
from src.accounts.routes.profile import router as profile_router

app = FastAPI(
    title="Online Cinema Service"
)

api_version_prefix = "/api/v1"
app.include_router(auth_router)
app.include_router(profile_router)

app.include_router(
    payment_router,
    prefix=f"{api_version_prefix}/payments",
    tags=["payments"]
)
# app.include_router(accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
# app.include_router(profiles_router, prefix=f"{api_version_prefix}/profiles", tags=["profiles"])
# app.include_router(movie_router, prefix=f"{api_version_prefix}/theater", tags=["theater"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
