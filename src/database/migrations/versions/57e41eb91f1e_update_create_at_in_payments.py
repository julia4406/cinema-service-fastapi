"""update_create_at_in_payments

Revision ID: 57e41eb91f1e
Revises: 685114be7f91
Create Date: 2025-03-25 00:33:51.809067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57e41eb91f1e'
down_revision: Union[str, None] = '685114be7f91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
