"""empty table rows

Revision ID: 7edf508910b3
Revises: 46d01958670b
Create Date: 2026-02-07 09:05:50.189003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7edf508910b3'
down_revision: Union[str, Sequence[str], None] = '46d01958670b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DELETE FROM messages")


def downgrade() -> None:
    """Downgrade schema."""
    pass
