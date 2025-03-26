
# from fastapi import HTTPException
# from src.payments.schemas.payments import StripeMetadataSchema
#
#
# def get_metadata(session) -> StripeMetadataSchema:
#     metadata = session.metadata
#
#     if not metadata:
#         raise HTTPException(
#             status_code=400,
#             detail="Missing metadata in Stripe session"
#         )
#
#     try:
#         return StripeMetadataSchema(**metadata)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid metadata format: {str(e)}"
#         )
