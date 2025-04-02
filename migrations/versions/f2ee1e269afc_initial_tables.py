"""Initial tables

Revision ID: f2ee1e269afc
Revises:
Create Date: 2025-03-28 14:26:46.802984

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "f2ee1e269afc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
