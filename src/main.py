from fastapi import FastAPI
from accounts.routes.routes import router


app = FastAPI()
app.include_router(router)

# api_version_prefix = "/api/v1"
#
# app.include_router(accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
# app.include_router(profiles_router, prefix=f"{api_version_prefix}/profiles", tags=["profiles"])
# app.include_router(movie_router, prefix=f"{api_version_prefix}/theater", tags=["theater"])
