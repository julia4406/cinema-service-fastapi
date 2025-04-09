from sqlalchemy.orm import registry

from src.database.models.accounts import *  # noqa F403
from src.database.models.base import *  # noqa F403
from src.database.models.movies import *  # noqa F403
from src.database.models.orders import *  # noqa F403
from src.database.models.payments import *  # noqa F403
from src.database.models.shopping_carts import *  # noqa F403
from src.database.models.tokens import *  # noqa F403

mapper_registry = registry()
mapper_registry.configure()
