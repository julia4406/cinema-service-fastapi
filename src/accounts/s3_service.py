import boto3
from fastapi import UploadFile
from src.config.settings import Settings

settings = Settings()


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY
        )

    async def upload_file(self, file: UploadFile, file_key: str) -> str:
        try:
            self.s3_client.upload_fileobj(
                file.file,
                settings.S3_BUCKET,
                file_key
            )
        except Exception as e:
            raise ValueError(f"Failed to upload file to S3: {str(e)}")
        finally:
            await file.close()

        return f"https://{settings.S3_BUCKET}.s3.amazonaws.com/{file_key}"

    async def delete_file(self, file_key: str) -> None:
        try:
            self.s3_client.delete_object(
                Bucket=settings.S3_BUCKET,
                Key=file_key
            )
        except Exception as e:
            raise ValueError(f"Failed to delete file from S3: {str(e)}")


async def get_s3_service() -> S3Service:
    return S3Service()
