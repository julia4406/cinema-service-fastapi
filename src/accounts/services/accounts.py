from accounts.repositories.accounts import UserRepository
from accounts.repositories.tokens import ActivationTokensRepository
from accounts.services.email_service import EmailService
from src.accounts.schemas import UserCreateResponseSchema, UserCreateRequestSchema


class AccountsService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activation_token_repo = ActivationTokensRepository(db)
        self.email_service = EmailService()

    async def register_user(self, user: UserCreateRequestSchema) -> UserCreateResponseSchema:
        if await self.user_repo.is_email_exists(user.email):
            raise ValueError("This email is already registered")

        new_user = await self.user_repo.create_user(user)
        activation_token = await self.activation_token_repo.create_activation_token(user_id=new_user.id)

        await self.email_service.send_activation_email(user.email, activation_token.token)

        return UserCreateResponseSchema(
            id=new_user.id,
            email=new_user.email,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            message="Activation link has been sent to your email",
        )
