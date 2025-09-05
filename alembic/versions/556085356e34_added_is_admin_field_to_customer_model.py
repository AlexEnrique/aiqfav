"""Added is_admin field to Customer model

Revision ID: 556085356e34
Revises: 0608f5a566a0
Create Date: 2025-09-05 15:03:32.920343

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '556085356e34'
down_revision: Union[str, Sequence[str], None] = '0608f5a566a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'customer',
        sa.Column(
            'is_admin', sa.Boolean(), nullable=False, server_default='false'
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('customer', 'is_admin')
