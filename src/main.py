import uvicorn
from fastapi import FastAPI
from src.payments.routes.payments import router as payment_router

from src.shopping_carts.routes.shopping_cart import router as shopping_cart_router
from src.shopping_carts.routes.admin import router as admin_shopping_cart_router
from src.orders.routes.orders import router as orders_router
from src.orders.routes.admin import router as admin_orders_router
from src.accounts.routes.auth import router as auth_router
from src.accounts.routes.profile import router as profile_router
from src.accounts.routes.admin import router as admin_router
from src.movies.routes import router as movies_router

app = FastAPI(
    title="Online Cinema Service"
)

api_version_prefix = "/api/v1"
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(admin_router)

app.include_router(
    payment_router,
    prefix=f"{api_version_prefix}/payments",
    tags=["payments"]
)
app.include_router(
    movies_router,
    prefix=f"{api_version_prefix}/movies",
    tags=["movies"]
)
app.include_router(
    shopping_cart_router,
    prefix=f"{api_version_prefix}/cart",
    tags=["cart"]
)
app.include_router(
    admin_shopping_cart_router,
    prefix=f"{api_version_prefix}/admin/users", tags=["admin_cart"],
)
app.include_router(
    orders_router
)
app.include_router(
    admin_orders_router,
    prefix=f"{api_version_prefix}/admin/orders", tags=["admin_orders"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
