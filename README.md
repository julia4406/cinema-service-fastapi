# Movie Theater API Project


An online cinema is a digital platform that allows users to select, watch, and purchase access to movies and other video materials via the internet. 


** To run database ** 
1.
docker-compose -f docker-compose-local.yml down -v 
docker-compose -f docker-compose-local.yml up --build
2.
Після створення контейнера(він залишаеться запущений) в терміналі:
    alembic upgrade head

Мають завантажитись міграції.
/// If we need a create new migrations
    alembic revision --autogenerate -m "describe_changes"
    alembic upgrade head

3.
Скопіювати налаштування в .env (з .env.sample + для пошти тут нижче є 
налаштування)
4.
Run main.py і перевірити що все працює




для налаштування бази - обрати Postgres
User: admin
Password: some_password
Database: movies_db

.env Change settings in MAIL
# EMAIL
MAIL_USERNAME=testsendingemail228@gmail.com
MAIL_PASSWORD=mgqpmijmgicochgi
MAIL_FROM=testsendingemail228@gmail.com
MAIL_FROM_NAME=YourMovie
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
SERVICE_URL=http://127.0.0.1:8000/

для налаштування пермішинів потрібно:

імпортувати  

    from src.accounts.dependencies import role_required
    from src.database.models import UserGroupEnum

додати через депендс в ендпоїнт:

    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),

приклад:

    @router.get("/users/{user_email}", response_model=UserAdminResponse)
    async def get_user_by_email(
        user_email: EmailStr,
        current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
        db: AsyncSession = Depends(get_postgresql_db)
    ):
