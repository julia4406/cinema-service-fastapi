from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from src.config.settings import Settings
from src.config.logging_settings import logger

settings = Settings()

logger.info(f"Loading private key from {settings.PRIVATE_KEY_PATH}")
with open(settings.PRIVATE_KEY_PATH, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )
logger.info("Private key loaded successfully.")

logger.info(f"Loading public key from {settings.PUBLIC_KEY_PATH}")
with open(settings.PUBLIC_KEY_PATH, "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )
logger.info("Public key loaded successfully.")

JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
