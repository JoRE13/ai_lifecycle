"""drop error_type from attempts

Revision ID: f1a2b3c4d5e6
Revises: e8b1d4c3f6a2
Create Date: 2026-04-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e8b1d4c3f6a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("attempts", "error_type")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("attempts", sa.Column("error_type", sa.String(length=64), nullable=True))
