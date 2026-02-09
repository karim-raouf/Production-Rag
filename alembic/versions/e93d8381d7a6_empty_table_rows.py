"""empty table rows

Revision ID: e93d8381d7a6
Revises: 988b8c06777d
Create Date: 2026-02-09 11:01:54.624829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e93d8381d7a6'
down_revision: Union[str, Sequence[str], None] = '988b8c06777d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DELETE FROM messages")
    op.execute("DELETE FROM conversations")
    op.execute("DELETE FROM tokens")
    op.execute("DELETE FROM users")

def downgrade() -> None:
    """Downgrade schema."""
    pass
