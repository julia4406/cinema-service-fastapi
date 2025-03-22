from fastapi import APIRouter


router = APIRouter()


@router.post("/{order_id}")
async def create_payment():
    return {"message": "Payments endpoint works!"}


@router.get("/")
async def get_payments_list():
    return {"message": "Payments endpoint works!"}


@router.get("/{payment_id}")
async def get_payment_detail():
    return {"message": "Payments endpoint works!"}
