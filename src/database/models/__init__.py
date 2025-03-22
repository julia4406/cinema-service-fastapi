from sqlalchemy.orm import registry

from src.database.models.base import *
from src.database.models.accounts import *
from src.database.models.movies import *
from src.database.models.orders import *
from src.database.models.payments import *
from src.database.models.shopping_carts import *
from src.database.models.tokens import *

mapper_registry = registry()
mapper_registry.configure()
