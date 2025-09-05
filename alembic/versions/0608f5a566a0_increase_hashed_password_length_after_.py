"""Increase hashed password length after change from bcrypt to argon2

Revision ID: 0608f5a566a0
Revises: d2684df9ef08
Create Date: 2025-09-05 14:59:32.505749

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0608f5a566a0'
down_revision: Union[str, Sequence[str], None] = 'd2684df9ef08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'customer',
        'hashed_password',
        existing_type=sa.VARCHAR(length=128),
        type_=sa.String(length=255),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'customer',
        'hashed_password',
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=128),
        existing_nullable=False,
    )
