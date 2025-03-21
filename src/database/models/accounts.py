import enum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class UserGroupEnum(str, enum.Enum):
   USER = "user"
   MODERATOR = "moderator"
   ADMIN = "admin"

class UserGroupModel(Base):
   __tablename__ = "user_groups"


   id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
   name: Mapped[UserGroupEnum] = mapped_column(Enum(UserGroupEnum), nullable=False, unique=True)


   users: Mapped[list["UserModel"]] = relationship("UserModel", back_populates="group")
