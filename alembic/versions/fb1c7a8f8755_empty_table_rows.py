"""empty table rows

Revision ID: fb1c7a8f8755
Revises: 0bf3eecb94b9
Create Date: 2026-02-07 19:53:34.056711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb1c7a8f8755'
down_revision: Union[str, Sequence[str], None] = '0bf3eecb94b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DELETE FROM messages")
    op.execute("DELETE FROM conversations")


def downgrade() -> None:
    """Downgrade schema."""
    pass
