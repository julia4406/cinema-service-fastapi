"""delete_unique_in_status_order

Revision ID: d36b15461f33
Revises: 57e41eb91f1e
Create Date: 2025-03-25 04:34:48.810367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd36b15461f33'
down_revision: Union[str, None] = '57e41eb91f1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
