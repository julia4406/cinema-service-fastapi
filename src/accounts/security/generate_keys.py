from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from src.config.settings import Settings
from src.config.logging_settings import logger

settings = Settings()


def generate_rsa_keys(private_key_path: Path, public_key_path: Path):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    with open(private_key_path, "wb") as private_pem:
        private_pem.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    public_key = private_key.public_key()

    with open(public_key_path, "wb") as public_pem:
        public_pem.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    logger.info(f"Private key saved to {private_key_path}")
    logger.info(f"Public key saved to {public_key_path}")


if __name__ == "__main__":
    private_key_path = settings.ROOT_DIR / "private_key.pem"
    public_key_path = settings.ROOT_DIR / "public_key.pem"

    generate_rsa_keys(private_key_path, public_key_path)
